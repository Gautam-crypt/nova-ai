"""
jarvis/core/tools/system_tools.py
Pre-built system-level tools. Import this file at startup to register all tools
via the @tool decorator.
"""

import os
import subprocess
import shutil
import threading

import psutil
import pyautogui

from .tool_registry import tool


# ═══════════════════════════════════════════════════════
# SYSTEM TOOLS
# ═══════════════════════════════════════════════════════

@tool(name="open_app", desc="Open any application by name", category="system")
def open_app(app_name: str) -> str:
    """Tries: (1) APP_MAP lookup, (2) start command, (3) where command to find exe."""
    APP_MAP = {
        "chrome": "chrome", "notepad": "notepad", "calculator": "calc",
        "terminal": "cmd", "powershell": "powershell", "explorer": "explorer",
        "vscode": "code", "spotify": "spotify", "browser": "chrome",
        "discord": "discord", "telegram": "telegram",
        "whatsapp": "start https://web.whatsapp.com",
        "task manager": "taskmgr", "paint": "mspaint",
        "word": "winword", "excel": "excel", "settings": "ms-settings:",
    }
    cmd = APP_MAP.get(app_name.lower().strip(), app_name)
    try:
        subprocess.Popen(cmd, shell=True)
        return f"Opened {app_name}"
    except Exception as e:
        # Fallback: try 'start' command
        try:
            subprocess.Popen(f"start {app_name}", shell=True)
            return f"Opened {app_name} (via start)"
        except Exception as e2:
            return f"Failed to open {app_name}: {e2}"


@tool(name="close_app", desc="Close/kill an application by name", category="system", permission=True)
def close_app(app_name: str) -> str:
    """Kill all processes matching the name."""
    killed = 0
    for proc in psutil.process_iter(['name']):
        try:
            if app_name.lower() in proc.info['name'].lower():
                proc.kill()
                killed += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return f"Killed {killed} processes matching '{app_name}'" if killed else f"No process found: {app_name}"


@tool(name="screenshot", desc="Take a screenshot of the current screen", category="system")
def take_screenshot(save_path: str = "data/screenshots/latest.png") -> str:
    """Captures screen, saves to path, returns path for vision analysis."""
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    img = pyautogui.screenshot()
    img.save(save_path)
    return f"Screenshot saved: {save_path}"


@tool(name="type_text", desc="Type text into the currently active window", category="system")
def type_text(text: str) -> str:
    """Uses pyautogui to type text with realistic delay."""
    import time
    time.sleep(0.3)  # Small delay to ensure window is focused
    if text.isascii():
        pyautogui.typewrite(text, interval=0.03)
    else:
        # For non-ASCII (Hindi, etc.), use clipboard paste method
        import win32clipboard
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardText(text)
        win32clipboard.CloseClipboard()
        pyautogui.hotkey('ctrl', 'v')
    return f"Typed: {text[:50]}..."


@tool(name="hotkey", desc="Press a keyboard shortcut (e.g. ctrl+c, alt+tab)", category="system")
def press_hotkey(keys: str) -> str:
    """keys format: 'ctrl+c', 'alt+tab', 'win+d'. Split by + and press."""
    key_list = [k.strip() for k in keys.split('+')]
    pyautogui.hotkey(*key_list)
    return f"Pressed: {keys}"


@tool(name="clipboard_read", desc="Read current clipboard content", category="system")
def clipboard_read() -> str:
    import win32clipboard
    win32clipboard.OpenClipboard()
    try:
        data = win32clipboard.GetClipboardData()
    except Exception:
        data = "(clipboard empty or non-text)"
    finally:
        win32clipboard.CloseClipboard()
    return data


@tool(name="clipboard_write", desc="Write text to clipboard", category="system")
def clipboard_write(text: str) -> str:
    import win32clipboard
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardText(text)
    win32clipboard.CloseClipboard()
    return "Text copied to clipboard"


@tool(name="system_status", desc="Get CPU, RAM, disk, battery info", category="system")
def system_status() -> str:
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage('C:\\')
    battery = psutil.sensors_battery()
    bat = f"{battery.percent:.0f}% ({'charging' if battery.power_plugged else 'discharging'})" if battery else "N/A"
    return (
        f"CPU: {cpu}% | RAM: {ram.percent}% ({ram.used // (1024**3)}/{ram.total // (1024**3)} GB) | "
        f"Disk C: {disk.percent}% ({disk.free // (1024**3)} GB free) | Battery: {bat}"
    )


@tool(name="run_command", desc="Execute a shell command and return output", category="system", permission=True)
def run_command(command: str) -> str:
    """Runs shell command, captures stdout+stderr, returns output."""
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True,
            timeout=30, cwd=os.path.expanduser("~")
        )
        output = result.stdout + result.stderr
        return output[:2000] if output else "Command executed (no output)"
    except subprocess.TimeoutExpired:
        return "Command timed out (30s limit)"
    except Exception as e:
        return f"Command failed: {e}"


# ═══════════════════════════════════════════════════════
# MEDIA / HARDWARE TOOLS
# ═══════════════════════════════════════════════════════

@tool(name="set_volume", desc="Set system volume (0-100)", category="media")
def set_volume(level: int) -> str:
    """Uses pycaw on Windows to set master volume."""
    try:
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        volume.SetMasterVolumeLevelScalar(max(0, min(100, level)) / 100, None)
        return f"Volume set to {level}%"
    except Exception as e:
        return f"Volume control failed: {e}"


@tool(name="set_brightness", desc="Set screen brightness (0-100)", category="system")
def set_brightness(level: int) -> str:
    """Uses WMI on Windows to set brightness."""
    try:
        import wmi
        c = wmi.WMI(namespace='wmi')
        methods = c.WmiMonitorBrightnessMethods()[0]
        methods.WmiSetBrightness(max(0, min(100, level)), 0)
        return f"Brightness set to {level}%"
    except Exception as e:
        return f"Brightness control failed: {e}"


# ═══════════════════════════════════════════════════════
# FILE TOOLS
# ═══════════════════════════════════════════════════════

@tool(name="list_files", desc="List files in a directory with sizes", category="file")
def list_files(path: str = ".") -> str:
    try:
        entries = []
        for entry in os.scandir(path):
            if entry.is_file():
                size = entry.stat().st_size
                if size > 1024 * 1024:
                    size_str = f"{size / (1024*1024):.1f} MB"
                elif size > 1024:
                    size_str = f"{size / 1024:.1f} KB"
                else:
                    size_str = f"{size} B"
                entries.append(f"  {entry.name} ({size_str})")
            else:
                entries.append(f"  {entry.name}/ (dir)")
        return f"Files in {os.path.abspath(path)}:\n" + "\n".join(entries[:30])
    except Exception as e:
        return f"Error listing {path}: {e}"


@tool(name="read_file", desc="Read contents of a text file", category="file")
def read_file(file_path: str) -> str:
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(5000)
        return content
    except Exception as e:
        return f"Error reading {file_path}: {e}"


@tool(name="write_file", desc="Write/create a text file with given content", category="file", permission=True)
def write_file(file_path: str, content: str) -> str:
    try:
        os.makedirs(os.path.dirname(file_path) or '.', exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"File written: {file_path}"
    except Exception as e:
        return f"Error writing {file_path}: {e}"


@tool(name="delete_file", desc="Delete a file or folder", category="file", permission=True)
def delete_file(path: str) -> str:
    try:
        if os.path.isfile(path):
            os.remove(path)
            return f"Deleted file: {path}"
        elif os.path.isdir(path):
            shutil.rmtree(path)
            return f"Deleted folder: {path}"
        return f"Path not found: {path}"
    except Exception as e:
        return f"Error deleting {path}: {e}"


# ═══════════════════════════════════════════════════════
# WEB TOOLS
# ═══════════════════════════════════════════════════════

@tool(name="web_search", desc="Search the internet and return results", category="web")
def web_search(query: str) -> str:
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))
            if not results:
                return "No results found"
            return "\n".join([f"- {r['title']}: {r['body']}" for r in results])
    except Exception as e:
        return f"Web search failed: {e}"


@tool(name="open_url", desc="Open a URL in the default browser", category="web")
def open_url(url: str) -> str:
    import webbrowser
    if not url.startswith("http"):
        url = "https://" + url
    webbrowser.open(url)
    return f"Opened: {url}"


# ═══════════════════════════════════════════════════════
# UTILITY TOOLS
# ═══════════════════════════════════════════════════════

@tool(name="set_reminder", desc="Set a timed reminder that NOVA will speak aloud", category="system")
def set_reminder(message: str, seconds: int) -> str:
    """Creates a background thread that waits and then speaks."""
    def _remind():
        import time
        time.sleep(seconds)
        try:
            from jarvis.core.body.voice.speaker import speak
            speak(f"Reminder: {message}")
        except Exception:
            print(f"\n[REMINDER] {message}")
    threading.Thread(target=_remind, daemon=True).start()
    mins = seconds // 60
    time_str = f"{mins} minutes" if mins > 0 else f"{seconds} seconds"
    return f"Reminder set: '{message}' in {time_str}"


@tool(name="play_music", desc="Play music - search YouTube or open Spotify", category="media")
def play_music(query: str = "") -> str:
    import webbrowser
    if query:
        url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
        webbrowser.open(url)
        return f"Playing '{query}' on YouTube"
    try:
        subprocess.Popen("spotify", shell=True)
        return "Opened Spotify"
    except Exception:
        return "Could not open Spotify"


@tool(name="describe_screen", desc="Take screenshot and describe what's on screen using vision AI", category="vision")
def describe_screen(question: str = "What do you see on the screen?") -> str:
    """Screenshots → save → send to LLaVA for analysis."""
    path = "data/screenshots/vision_temp.png"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    pyautogui.screenshot().save(path)
    try:
        import ollama
        response = ollama.generate(model="llava", prompt=question, images=[path])
        return response['response'].strip()
    except Exception as e:
        return f"Vision analysis failed: {e}. Screenshot saved at {path}"
    finally:
        try:
            os.remove(path)
        except Exception:
            pass


@tool(name="get_running_apps", desc="List all currently running applications with resource usage", category="system")
def get_running_apps() -> str:
    """Lists visible running applications with CPU and memory usage."""
    apps = []
    seen = set()
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            name = proc.info['name']
            if name in seen or name.lower() in ['system', 'idle', 'svchost.exe', 'conhost.exe']:
                continue
            seen.add(name)
            cpu = proc.info['cpu_percent'] or 0
            mem = proc.info['memory_percent'] or 0
            if mem > 0.1:  # Only show apps using meaningful memory
                apps.append(f"  {name}: CPU {cpu:.1f}%, RAM {mem:.1f}%")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    apps.sort()
    return f"Running apps ({len(apps)}):\n" + "\n".join(apps[:25])
