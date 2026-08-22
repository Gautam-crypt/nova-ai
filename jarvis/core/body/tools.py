"""
jarvis/core/body/tools.py
ALL actions NOVA can take — but only when YOU command.
"""

import subprocess
import os
import webbrowser
import sys
import pyautogui
import psutil

# ── MUSIC CONTROL ────────────────────────────────────────────

def play_music(query: str = "") -> str:
    """Play music — opens Spotify or YouTube."""
    if query:
        # Open YouTube search
        url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
        webbrowser.open(url)
        return f"YouTube pe '{query}' search kar diya, Sir."
    else:
        # Try Spotify
        try:
            # On Windows, 'spotify' might not be in PATH, try common location or just use 'start spotify'
            os.system("start spotify")
            return "Spotify open kar diya, Sir."
        except:
            return "Spotify nahi mila. Koi specific song batao?"

def pause_music() -> str:
    pyautogui.press('playpause')
    return "Music pause kar diya, Sir."

def next_track() -> str:
    pyautogui.press('nexttrack')
    return "Next track, Sir."

def set_volume(level: int) -> str:
    """level = 0 to 100"""
    try:
        level = int(level)
    except:
        return "Volume level valid nahi hai."
        
    level = max(0, min(100, level))
    
    if sys.platform == "win32":
        try:
            from ctypes import cast, POINTER
            from comtypes import CLSCTX_ALL
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            volume.SetMasterVolumeLevelScalar(level / 100, None)
            return f"Volume {level}% kar diya, Sir."
        except Exception as e:
            return f"Volume set nahi ho saka: {e}"
    return f"System volume control abhi sirf Windows ke liye hai."

# ── APP CONTROL ───────────────────────────────────────────────

APP_MAP = {
    "chrome":    "chrome",
    "notepad":   "notepad",
    "calculator":"calc",
    "terminal":  "cmd",
    "explorer":  "explorer",
    "vs code":   "code",
    "spotify":   "spotify",
    "browser":   "chrome"
}

def open_app(app_name: str) -> str:
    name = app_name.lower().strip()
    cmd  = APP_MAP.get(name, name)
    try:
        subprocess.Popen(cmd, shell=True)
        return f"{app_name} open kar diya, Sir."
    except Exception as e:
        return f"'{app_name}' open nahi ho saka: {e}"

def close_app(app_name: str) -> str:
    found = False
    for proc in psutil.process_iter(['name']):
        try:
            if app_name.lower() in proc.info['name'].lower():
                proc.kill()
                found = True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
            
    if found:
        return f"{app_name} band kar diya, Sir."
    return f"{app_name} chal nahi raha tha."

# ── BROWSER & SEARCH CONTROL ──────────────────────────────────

def web_search(query: str) -> str:
    """Performs a real-time search and returns snippets."""
    print(f"[NOVA] Searching the web for: {query}")
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))
            if not results:
                return "Maaf kijiye Sir, koi results nahi mile."
            
            snippets = []
            for r in results:
                snippets.append(f"- {r['title']}: {r['body']}")
            
            return "\n".join(snippets)
    except Exception as e:
        # Fallback to browser open if search fails
        url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        webbrowser.open(url)
        return f"Internet search error ({e}). Browser mein Google open kar diya hai."

def open_url(url: str) -> str:
    if not url.startswith("http"):
        url = "https://" + url
    webbrowser.open(url)
    return f"Browser mein open kar diya, Sir."

# ── SYSTEM INFO ───────────────────────────────────────────────

def get_system_status() -> str:
    cpu    = psutil.cpu_percent(interval=1)
    ram    = psutil.virtual_memory()
    disk   = psutil.disk_usage('/')
    battery = psutil.sensors_battery()
    bat_pct = f"{battery.percent:.0f}%" if battery else "N/A"

    return (
        f"System status, Sir: CPU {cpu}%, RAM {ram.percent}% used, "
        f"Disk {disk.percent}% used, Battery {bat_pct}."
    )

# ── VISION & KNOWLEDGE TOOLS ─────────────────────────────────

def describe_scene(query: str = "What do you see?") -> str:
    """Uses the camera to describe what's happening."""
    from jarvis.core.senses.vision.analyzer import VisionAnalyzer
    analyzer = VisionAnalyzer() # Ideally, this should be a singleton
    return analyzer.describe_current_frame(prompt=query)

def index_file(file_path: str) -> str:
    """Reads a file and remembers its contents."""
    from jarvis.core.brain.knowledge import KnowledgeBase
    # We need access to the brain's memory instance here
    # For now, we'll initialize a new one or pass it via a global
    from jarvis.core.brain.memory import LongTermMemory
    kb = KnowledgeBase(LongTermMemory())
    return kb.index_file(file_path)

def learn_from_web(query: str) -> str:
    """Searches the internet and saves key facts into memory."""
    print(f"[NOVA] Learning about: {query}...")
    try:
        from duckduckgo_search import DDGS
        from jarvis.core.brain.knowledge import KnowledgeBase
        from jarvis.core.brain.memory import LongTermMemory
        
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))
            if not results:
                return "Maaf kijiye Sir, internet par kuch mila nahi."
            
            kb = KnowledgeBase(LongTermMemory())
            for r in results:
                fact = f"RESEARCH ON {query}: {r['title']} - {r['body']}"
                kb.memory.store_fact(fact)
            
            return f"Maine '{query}' ke bare me internet se padh kar yaad kar liya hai, Sir."
    except Exception as e:
        return f"Learning failed: {e}"

def system_command(param: str) -> str:
    """Handles system level commands like shutdown or restart."""
    cmd = param.lower().strip()
    if "shutdown" in cmd or "band" in cmd:
        if sys.platform == "win32":
            os.system("shutdown /s /t 1")
            return "System shutdown kar rahi hoon. Shubh Ratri, Sir."
    elif "restart" in cmd:
        if sys.platform == "win32":
            os.system("shutdown /r /t 1")
            return "System restart kar rahi hoon, Sir."
    return f"System command '{param}' mujhe nahi pata, Sir."

# ── TOOL REGISTRY — NOVA picks from this ─────────────────────

TOOLS = {
    "play_music":       play_music,
    "pause_music":      pause_music,
    "next_track":       next_track,
    "set_volume":       set_volume,
    "open_app":         open_app,
    "close_app":        close_app,
    "web_search":       web_search,
    "open_url":         open_url,
    "system_status":    get_system_status,
    "describe_scene":   describe_scene,
    "index_file":       index_file,
    "learn_from_web":   learn_from_web,
    "system_command":   system_command
}

def execute_tool(tool_name: str, **kwargs) -> str:
    fn = TOOLS.get(tool_name)
    if not fn:
        return f"Tool '{tool_name}' mujhe nahi pata, Sir."
    
    try:
        import inspect
        sig = inspect.signature(fn)
        # Filter kwargs to only those that the function accepts
        filtered_kwargs = {k: v for k, v in kwargs.items() if k in sig.parameters}
        
        # If the function takes 'query' but we only have 'app_name' (or vice-versa), bridge them
        param = kwargs.get('param') or kwargs.get('query') or kwargs.get('app_name') or kwargs.get('file_path') or kwargs.get('url')
        
        if 'query' in sig.parameters and 'query' not in filtered_kwargs:
            filtered_kwargs['query'] = param
        if 'app_name' in sig.parameters and 'app_name' not in filtered_kwargs:
            filtered_kwargs['app_name'] = param
        if 'file_path' in sig.parameters and 'file_path' not in filtered_kwargs:
            filtered_kwargs['file_path'] = param
        if 'url' in sig.parameters and 'url' not in filtered_kwargs:
            filtered_kwargs['url'] = param
        if 'level' in sig.parameters and 'level' not in filtered_kwargs:
            filtered_kwargs['level'] = param
            
        return fn(**filtered_kwargs)
    except Exception as e:
        return f"Error executing {tool_name}: {e}"
