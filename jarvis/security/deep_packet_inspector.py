import threading
import time
import json
import re
import struct
import sqlite3
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Callable

import scapy.all as scapy
from scapy.layers.http import HTTPRequest, HTTPResponse
from scapy.layers.dns import DNS, DNSQR, DNSRR
from scapy.layers.tls.record import TLS
from scapy.layers.tls.handshake import TLSClientHello




class DeepPacketInspector:
    """
    Captures and decodes network traffic on the local WiFi network.
    
    What it can capture:
    1. HTTP requests/responses (unencrypted) — full URLs, headers, body
    2. DNS queries — which websites every device is visiting
    3. HTTPS SNI — which HTTPS sites are being accessed (domain name visible)
    4. Raw TCP/UDP — src/dst IP, ports, packet sizes, timing patterns
    5. Protocol detection — identify WhatsApp, Instagram, YouTube, etc. by IP/port patterns
    
    What it CANNOT see (due to encryption):
    - HTTPS body content (encrypted by TLS)
    - WhatsApp message content (end-to-end encrypted)
    - Any E2E encrypted app's message content
    
    BUT it CAN see:
    - WHO is talking to WhatsApp servers (by IP)
    - WHEN they're sending messages (timing)
    - HOW MUCH data they're sending (packet sizes → text vs photo vs video)
    - WHICH app they're using (IP-to-service mapping)
    """
    
    # Known service IP ranges / domains for identification
    SERVICE_DOMAINS = {
        "whatsapp": ["whatsapp.net", "whatsapp.com", "wa.me"],
        "instagram": ["instagram.com", "cdninstagram.com", "fbcdn.net"],
        "youtube": ["youtube.com", "googlevideo.com", "ytimg.com"],
        "facebook": ["facebook.com", "fbcdn.net", "fb.com"],
        "telegram": ["telegram.org", "t.me", "telegram.me"],
        "google": ["google.com", "googleapis.com", "gstatic.com"],
        "tiktok": ["tiktok.com", "tiktokcdn.com"],
        "twitter": ["twitter.com", "twimg.com", "x.com"],
    }
    
    def __init__(self, db_path: str = "data/kavach/packet_logs.db"):
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(db_path, check_same_thread=False)
        self._init_db()
        self._running = False
        self._dns_cache: Dict[str, str] = {}       # IP -> domain
        self._device_activity: Dict[str, dict] = defaultdict(lambda: {
            "dns_queries": [],
            "http_requests": [],
            "services_used": set(),
            "bytes_sent": 0,
            "bytes_received": 0,
            "last_seen": None
        })
        self._captured_http_data: List[dict] = []   # Raw HTTP captures
    
    def _init_db(self):
        """Create tables for persistent packet logging."""
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS dns_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT, src_ip TEXT, query_domain TEXT,
                resolved_ip TEXT, device_mac TEXT
            )
        """)
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS http_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT, src_ip TEXT, dst_ip TEXT,
                method TEXT, url TEXT, host TEXT,
                user_agent TEXT, content_type TEXT,
                request_body TEXT, response_body TEXT,
                status_code INTEGER
            )
        """)
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS traffic_summary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT, src_ip TEXT, dst_ip TEXT,
                service TEXT, bytes_sent INTEGER, bytes_received INTEGER,
                packet_count INTEGER, protocol TEXT
            )
        """)
        self.db.commit()
    
    def start_capture(self, interface: str = None, duration: int = 0):
        """
        Start packet capture.
        
        Args:
            interface: Network interface name (None = auto-detect)
            duration: Capture duration in seconds (0 = unlimited)
        """
        self._running = True
        
        def _capture():
            try:
                kwargs = {
                    "prn": self._process_packet,
                    "store": False,
                    "stop_filter": lambda x: not self._running
                }
                if interface:
                    kwargs["iface"] = interface
                if duration > 0:
                    kwargs["timeout"] = duration
                    
                print(f"[KAVACH-DPI] Packet capture started (interface: {interface or 'auto'})")
                scapy.sniff(**kwargs)
            except Exception as e:
                print(f"[KAVACH-DPI] Capture error: {e}")
        
        threading.Thread(target=_capture, daemon=True, name="dpi_capture").start()
    
    def stop_capture(self):
        self._running = False
        print("[KAVACH-DPI] Capture stopped")
    
    def _process_packet(self, packet):
        """Process each captured packet."""
        try:
            # 1. DNS Query Logging — see what websites everyone is visiting
            if packet.haslayer(DNS) and packet.haslayer(DNSQR):
                self._handle_dns(packet)
            
            # 2. HTTP Traffic — capture unencrypted web traffic
            if packet.haslayer(HTTPRequest):
                self._handle_http_request(packet)
            if packet.haslayer(HTTPResponse):
                self._handle_http_response(packet)
            
            # 3. TLS/HTTPS — extract SNI (Server Name Indication)
            if packet.haslayer(TLS):
                self._handle_tls(packet)
            
            # 4. General traffic tracking
            if packet.haslayer(scapy.IP):
                self._track_traffic(packet)
                
        except Exception:
            pass  # Silently skip malformed packets
    
    def _handle_dns(self, packet):
        """Log DNS queries — shows which websites each device visits."""
        dns = packet[DNS]
        query = packet[DNSQR]
        domain = query.qname.decode('utf-8', errors='ignore').rstrip('.')
        src_ip = packet[scapy.IP].src if packet.haslayer(scapy.IP) else "?"
        
        # If it's a response with an answer, cache the IP→domain mapping
        if dns.ancount > 0 and packet.haslayer(DNSRR):
            for i in range(dns.ancount):
                try:
                    rr = dns.an[i]
                    if rr.type == 1:  # A record
                        resolved_ip = rr.rdata
                        self._dns_cache[resolved_ip] = domain
                except:
                    pass
        
        # Log the query
        self._device_activity[src_ip]["dns_queries"].append({
            "domain": domain,
            "time": datetime.now().isoformat()
        })
        
        # Identify service
        for service, domains in self.SERVICE_DOMAINS.items():
            if any(d in domain for d in domains):
                self._device_activity[src_ip]["services_used"].add(service)
        
        # Save to DB
        self.db.execute(
            "INSERT INTO dns_logs (timestamp, src_ip, query_domain, resolved_ip) VALUES (?, ?, ?, ?)",
            (datetime.now().isoformat(), src_ip, domain, "")
        )
        self.db.commit()
    
    def _handle_http_request(self, packet):
        """Capture HTTP request details — URLs, headers, body."""
        http = packet[HTTPRequest]
        src_ip = packet[scapy.IP].src if packet.haslayer(scapy.IP) else "?"
        dst_ip = packet[scapy.IP].dst if packet.haslayer(scapy.IP) else "?"
        
        method = http.Method.decode() if isinstance(http.Method, bytes) else str(http.Method)
        host = http.Host.decode() if isinstance(http.Host, bytes) else str(http.Host) if http.Host else ""
        path = http.Path.decode() if isinstance(http.Path, bytes) else str(http.Path)
        user_agent = http.User_Agent.decode() if isinstance(http.User_Agent, bytes) else "" if http.User_Agent else ""
        
        url = f"http://{host}{path}"
        
        # Try to get request body
        body = ""
        if packet.haslayer(scapy.Raw):
            try:
                body = packet[scapy.Raw].load.decode('utf-8', errors='ignore')[:2000]
            except:
                body = "(binary data)"
        
        entry = {
            "time": datetime.now().isoformat(),
            "src_ip": src_ip, "dst_ip": dst_ip,
            "method": method, "url": url, "host": host,
            "user_agent": user_agent, "body": body
        }
        
        self._captured_http_data.append(entry)
        self._device_activity[src_ip]["http_requests"].append(entry)
        
        # Save to DB
        self.db.execute(
            """INSERT INTO http_logs 
               (timestamp, src_ip, dst_ip, method, url, host, user_agent, request_body)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (entry["time"], src_ip, dst_ip, method, url, host, user_agent, body)
        )
        self.db.commit()
    
    def _handle_http_response(self, packet):
        """Capture HTTP response details."""
        # Response body capture
        if packet.haslayer(scapy.Raw):
            try:
                body = packet[scapy.Raw].load.decode('utf-8', errors='ignore')[:2000]
                src_ip = packet[scapy.IP].src if packet.haslayer(scapy.IP) else "?"
                # Append to last matching request's entry
                for entry in reversed(self._captured_http_data):
                    if entry["dst_ip"] == src_ip:
                        entry["response_body"] = body
                        break
            except:
                pass
    
    def _handle_tls(self, packet):
        """Extract SNI from TLS ClientHello — see which HTTPS sites are visited."""
        try:
            if packet.haslayer(TLSClientHello):
                hello = packet[TLSClientHello]
                # Extract SNI from extensions
                for ext in hello.ext:
                    if hasattr(ext, 'servernames'):
                        for sn in ext.servernames:
                            domain = sn.servername.decode('utf-8', errors='ignore')
                            src_ip = packet[scapy.IP].src if packet.haslayer(scapy.IP) else "?"
                            dst_ip = packet[scapy.IP].dst if packet.haslayer(scapy.IP) else "?"
                            
                            self._dns_cache[dst_ip] = domain
                            self._device_activity[src_ip]["dns_queries"].append({
                                "domain": domain, "type": "TLS_SNI",
                                "time": datetime.now().isoformat()
                            })
                            
                            # Service identification
                            for service, domains in self.SERVICE_DOMAINS.items():
                                if any(d in domain for d in domains):
                                    self._device_activity[src_ip]["services_used"].add(service)
        except:
            pass
    
    def _track_traffic(self, packet):
        """Track general traffic volume per device."""
        ip = packet[scapy.IP]
        src = ip.src
        dst = ip.dst
        size = len(packet)
        
        self._device_activity[src]["bytes_sent"] += size
        self._device_activity[dst]["bytes_received"] += size
        self._device_activity[src]["last_seen"] = datetime.now().isoformat()
        
        # Identify service by destination IP
        service = self._dns_cache.get(dst, "unknown")
        for svc, domains in self.SERVICE_DOMAINS.items():
            if any(d in service for d in domains):
                self._device_activity[src]["services_used"].add(svc)
    
    # ═══ PUBLIC API — for KAVACH agent and ReAct engine ═══
    
    def get_activity_report(self, ip: str = None) -> str:
        """
        Get human-readable activity report.
        If IP specified, show that device's activity.
        If None, show all devices.
        """
        if ip:
            activity = self._device_activity.get(ip)
            if not activity:
                return f"No activity recorded for {ip}"
            return self._format_device_report(ip, activity)
        
        # All devices
        report = f"=== Network Activity Report ({len(self._device_activity)} devices) ===\n\n"
        for device_ip, activity in self._device_activity.items():
            report += self._format_device_report(device_ip, activity) + "\n---\n"
        return report
    
    def _format_device_report(self, ip: str, activity: dict) -> str:
        """Format a single device's activity."""
        hostname = self._dns_cache.get(ip, "Unknown")
        services = ", ".join(activity["services_used"]) or "None detected"
        
        report = f"Device: {ip} ({hostname})\n"
        report += f"  Services Used: {services}\n"
        report += f"  Data Sent: {activity['bytes_sent'] / 1024:.1f} KB\n"
        report += f"  Data Received: {activity['bytes_received'] / 1024:.1f} KB\n"
        
        # Recent DNS queries (last 10)
        recent_dns = activity["dns_queries"][-10:]
        if recent_dns:
            report += f"  Recent Sites:\n"
            for q in recent_dns:
                report += f"    - {q['domain']} ({q['time'][-8:]})\n"
        
        # Recent HTTP requests (last 5)
        recent_http = activity["http_requests"][-5:]
        if recent_http:
            report += f"  HTTP Requests:\n"
            for req in recent_http:
                report += f"    - {req['method']} {req['url'][:80]}\n"
                if req.get("body"):
                    report += f"      Body: {req['body'][:100]}...\n"
        
        return report
    
    def get_who_is_messaging(self) -> str:
        """
        Identify who is using messaging apps based on traffic patterns.
        Shows device IP, which messaging service, and traffic volume.
        """
        report = "=== Messaging Activity ===\n\n"
        messaging_services = {"whatsapp", "telegram", "instagram", "facebook"}
        
        found = False
        for ip, activity in self._device_activity.items():
            active_messaging = activity["services_used"] & messaging_services
            if active_messaging:
                found = True
                report += f"Device {ip}:\n"
                for svc in active_messaging:
                    report += f"  📱 {svc.upper()} — active\n"
                    # Estimate message type by packet sizes
                    report += f"  Data sent: {activity['bytes_sent'] / 1024:.1f} KB\n"
                    if activity['bytes_sent'] > 500 * 1024:
                        report += f"  📸 Likely sending images/videos (large data)\n"
                    elif activity['bytes_sent'] > 10 * 1024:
                        report += f"  💬 Likely sending text messages\n"
                    else:
                        report += f"  👀 Likely just browsing/reading\n"
                report += "\n"
        
        if not found:
            report += "No messaging activity detected yet. Capture needs to run longer.\n"
        
        return report
    
    def get_captured_messages(self) -> str:
        """
        Return any captured plaintext messages from HTTP traffic.
        Note: HTTPS/E2E encrypted messages cannot be read.
        """
        if not self._captured_http_data:
            return "No HTTP traffic captured. Most traffic is HTTPS encrypted."
        
        report = "=== Captured HTTP Traffic (Unencrypted) ===\n\n"
        for entry in self._captured_http_data[-20:]:
            report += f"[{entry['time'][-8:]}] {entry['src_ip']} → {entry['method']} {entry['url'][:80]}\n"
            if entry.get("body"):
                report += f"  Body: {entry['body'][:200]}\n"
            if entry.get("response_body"):
                report += f"  Response: {entry['response_body'][:200]}\n"
            report += "\n"
        
        return report
