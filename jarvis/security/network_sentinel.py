"""
jarvis/security/network_sentinel.py
DEFENSIVE SECURITY ONLY.
Monitors the local network for suspicious activity targeting this machine.
Detects:
1. ARP Spoofing (someone trying to Man-in-the-Middle the user)
2. Port Scans (someone probing the user's open ports)
3. Suspicious Outbound Traffic (data exfiltration detection)
"""

import threading
import time
import subprocess
import socket
from collections import defaultdict
from datetime import datetime
from typing import Dict, Callable

import psutil
try:
    import scapy.all as scapy
except ImportError:
    pass

from jarvis.core.background.findings_queue import Finding, Priority, ActionType


class NetworkSentinel:
    """
    Continuous network defense monitoring engine.
    Runs as a daemon thread, pushes Findings to the queue if the user is under attack.
    """
    
    def __init__(self, findings_queue, alert_callback: Callable = None):
        self.queue = findings_queue
        self.alert_callback = alert_callback
        self._running = False
        self._known_devices: Dict[str, dict] = {}
        self._port_scan_tracker: Dict[str, list] = defaultdict(list)
        self._blocked_ips: set = set()
        self._arp_table: Dict[str, str] = {}
        self._outbound_tracker: Dict[int, dict] = {}
        
    def start(self):
        """Start defensive monitoring threads."""
        self._running = True
        
        # Thread 1: ARP monitor (every 10 seconds)
        threading.Thread(target=self._arp_monitor_loop, daemon=True, name="sentinel_arp").start()
        
        # Thread 2: Port scan detection (only on incoming traffic)
        try:
            import scapy.all as scapy
            threading.Thread(target=self._packet_monitor_loop, daemon=True, name="sentinel_packets").start()
        except ImportError:
            print("[KAVACH] Scapy not found. Port scan detection disabled.")
            
        # Thread 3: Outbound traffic monitor (every 30 seconds)
        threading.Thread(target=self._outbound_monitor_loop, daemon=True, name="sentinel_outbound").start()
        
        print("[KAVACH] NetworkSentinel started — System defense active")
    
    def stop(self):
        self._running = False
    
    # ── DEFENSIVE ARP MONITORING ────────────────────────────
    
    def _arp_monitor_loop(self):
        """Checks ARP table for gateway spoofing (MitM attack against THIS computer)."""
        while self._running:
            try:
                self._check_arp_table()
            except Exception as e:
                print(f"[KAVACH-ARP] Error: {e}")
            time.sleep(10)
    
    def _check_arp_table(self):
        """Detect if someone is trying to hijack our network traffic."""
        result = subprocess.run("arp -a", capture_output=True, text=True, shell=True)
        lines = result.stdout.strip().split("\n")
        
        current_table = {}
        for line in lines:
            parts = line.split()
            if len(parts) >= 3 and parts[1].count('-') == 5:
                ip = parts[0]
                mac = parts[1].lower()
                current_table[ip] = mac
        
        # Check for ARP spoofing (same MAC for different IPs usually indicates a MitM attack)
        mac_to_ips = defaultdict(list)
        for ip, mac in current_table.items():
            mac_to_ips[mac].append(ip)
        
        for mac, ips in mac_to_ips.items():
            if len(ips) > 2:
                # Exclude broadcast/multicast MACs
                if not mac.startswith("01-00-5e") and not mac.startswith("ff-ff-ff"):
                    self._push_finding(
                        Priority.HIGH,
                        "Under Attack: ARP Spoofing Detected!",
                        f"MAC {mac} is claiming to be {len(ips)} different IPs. Someone might be trying to intercept your traffic.",
                        ActionType.NEEDS_PERMISSION,
                        action_fn=lambda: self.block_ip(ips[0])
                    )
        
        self._arp_table = current_table
    
    # ── DEFENSIVE PACKET MONITORING ─────────────────────────
    
    def _packet_monitor_loop(self):
        """Listen for INCOMING connections to detect port scans targeting THIS computer."""
        try:
            scapy.sniff(
                prn=self._analyze_incoming_packet,
                store=False,
                stop_filter=lambda x: not self._running,
                filter="tcp and tcp[tcpflags] & (tcp-syn) != 0" # Only care about SYN packets
            )
        except Exception as e:
            print(f"[KAVACH-PACKET] Sniffing error: {e}")
    
    def _analyze_incoming_packet(self, packet):
        """Detect if an external IP is rapidly probing our open ports."""
        if packet.haslayer(scapy.TCP) and packet.haslayer(scapy.IP):
            tcp = packet[scapy.TCP]
            src_ip = packet[scapy.IP].src
            dst_ip = packet[scapy.IP].dst
            
            # Get our IPs to ensure the traffic is coming TO us, not FROM us
            my_ips = [addr.address for iface_addrs in psutil.net_if_addrs().values() 
                     for addr in iface_addrs if addr.family == socket.AF_INET]
            
            if dst_ip in my_ips and src_ip not in my_ips:
                self._port_scan_tracker[src_ip].append(tcp.dport)
                
                unique_ports = set(self._port_scan_tracker[src_ip])
                if len(unique_ports) > 15 and src_ip not in self._blocked_ips:
                    self._push_finding(
                        Priority.HIGH,
                        f"Under Attack: Port Scan from {src_ip}!",
                        f"IP {src_ip} is scanning your open ports. This is usually the first step of an attack.",
                        ActionType.NEEDS_PERMISSION,
                        action_fn=lambda ip=src_ip: self.block_ip(ip)
                    )
    
    # ── EXFILTRATION DETECTION ──────────────────────────────
    
    def _outbound_monitor_loop(self):
        """Monitor our own processes to ensure they aren't silently uploading massive data."""
        while self._running:
            try:
                for conn in psutil.net_connections(kind='inet'):
                    if conn.status == 'ESTABLISHED' and conn.raddr:
                        pid = conn.pid
                        if pid:
                            try:
                                proc = psutil.Process(pid)
                                io_counters = proc.io_counters()
                                name = proc.name()
                                
                                # Ignore known browsers/downloaders
                                if name.lower() in ['chrome.exe', 'msedge.exe', 'firefox.exe', 'discord.exe']:
                                    continue
                                
                                if pid not in self._outbound_tracker:
                                    self._outbound_tracker[pid] = {
                                        "name": name,
                                        "bytes_out": io_counters.write_bytes,
                                        "destination": f"{conn.raddr.ip}:{conn.raddr.port}"
                                    }
                                else:
                                    prev = self._outbound_tracker[pid]["bytes_out"]
                                    diff = io_counters.write_bytes - prev
                                    self._outbound_tracker[pid]["bytes_out"] = io_counters.write_bytes
                                    
                                    # >100MB outbound in 30 seconds for an unknown app = highly suspicious
                                    if diff > 100 * 1024 * 1024:
                                        self._push_finding(
                                            Priority.HIGH,
                                            f"Suspicious Data Upload: {name}",
                                            f"Process '{name}' silently uploaded {diff / 1024 / 1024:.1f} MB in 30 seconds. Possible data exfiltration.",
                                            ActionType.NEEDS_PERMISSION,
                                            action_fn=lambda p=pid: psutil.Process(p).kill()
                                        )
                            except (psutil.NoSuchProcess, psutil.AccessDenied):
                                pass
            except Exception as e:
                pass
            time.sleep(30)
    
    # ── SYSTEM DEFENSE ACTIONS ──────────────────────────────
    
    def block_ip(self, ip: str):
        """Block an attacking IP using Windows Firewall."""
        rule_name = f"KAVACH_DEFENSE_BLOCK_{ip.replace('.', '_')}"
        cmd = f'netsh advfirewall firewall add rule name="{rule_name}" dir=in action=block remoteip={ip}'
        subprocess.run(cmd, shell=True, capture_output=True)
        self._blocked_ips.add(ip)
        print(f"[KAVACH] Defense Activated: Blocked incoming traffic from {ip}")
        return f"Blocked {ip} via Windows Firewall"
    
    # ── NETWORK AUDIT ───────────────────────────────────────
    
    def scan_network(self) -> str:
        """Passive self-audit of local network devices (standard arp scan)."""
        result = subprocess.run("arp -a", capture_output=True, text=True, shell=True)
        devices = []
        for line in result.stdout.strip().split("\n"):
            parts = line.split()
            if len(parts) >= 3 and parts[1].count('-') == 5:
                devices.append(f"IP: {parts[0]} | MAC: {parts[1]}")
        
        return f"Local Network Devices (Arp Cache):\n" + "\n".join(devices)
    
    def _push_finding(self, priority, title, detail, action_type, action_fn=None):
        finding = Finding(
            agent_name="kavach",
            priority=priority,
            title=f"KAVACH: {title}",
            detail=detail,
            action_type=action_type,
            action_fn=action_fn
        )
        self.queue.push(finding)
