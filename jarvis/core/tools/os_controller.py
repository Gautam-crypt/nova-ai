"""
jarvis/core/tools/os_controller.py
Low-level Windows OS control — find, focus, type into ANY window.
This is what makes NOVA truly control any software.
"""

import time
import subprocess

import pyautogui
import pygetwindow as gw

from .tool_registry import tool


@tool(name="find_window", desc="Find a window by title (partial match)", category="system")
def find_window(title: str) -> str:
    """Returns list of windows matching the title."""
    windows = gw.getWindowsWithTitle(title)
    if not windows:
        # Try case-insensitive search through all windows
        all_wins = gw.getAllWindows()
        windows = [w for w in all_wins if title.lower() in w.title.lower() and w.title]
    if not windows:
        return f"No window found matching '{title}'"
    return "\n".join([
        f"- '{w.title}' (pos: {w.left},{w.top}, size: {w.width}x{w.height})"
        for w in windows[:10]
    ])


@tool(name="focus_window", desc="Bring a window to foreground by title", category="system")
def focus_window(title: str) -> str:
    """Finds window by partial title match and activates it."""
    windows = gw.getWindowsWithTitle(title)
    if not windows:
        # Case-insensitive fallback
        all_wins = gw.getAllWindows()
        windows = [w for w in all_wins if title.lower() in w.title.lower() and w.title]
    if not windows:
        return f"Window '{title}' not found"
    win = windows[0]
    try:
        if win.isMinimized:
            win.restore()
        win.activate()
        time.sleep(0.3)
        return f"Focused: '{win.title}'"
    except Exception as e:
        # Fallback: use Alt key trick to allow SetForegroundWindow
        try:
            import ctypes
            import win32gui
            import win32con
            hwnd = win32gui.FindWindow(None, win.title)
            if hwnd:
                ctypes.windll.user32.SetForegroundWindow(hwnd)
                return f"Focused (fallback): '{win.title}'"
        except Exception:
            pass
        return f"Attempted focus on '{win.title}': {e}"


@tool(name="list_windows", desc="List all currently open windows", category="system")
def list_windows() -> str:
    """Returns all visible windows."""
    windows = gw.getAllWindows()
    visible = [w for w in windows if w.title and w.visible and len(w.title.strip()) > 0]
    return "\n".join([f"- '{w.title}'" for w in visible[:25]])


@tool(name="minimize_window", desc="Minimize a window by title", category="system")
def minimize_window(title: str) -> str:
    windows = gw.getWindowsWithTitle(title)
    if not windows:
        all_wins = gw.getAllWindows()
        windows = [w for w in all_wins if title.lower() in w.title.lower() and w.title]
    if windows:
        windows[0].minimize()
        return f"Minimized: '{windows[0].title}'"
    return f"Window not found: '{title}'"


@tool(name="maximize_window", desc="Maximize a window by title", category="system")
def maximize_window(title: str) -> str:
    windows = gw.getWindowsWithTitle(title)
    if not windows:
        all_wins = gw.getAllWindows()
        windows = [w for w in all_wins if title.lower() in w.title.lower() and w.title]
    if windows:
        windows[0].maximize()
        return f"Maximized: '{windows[0].title}'"
    return f"Window not found: '{title}'"


@tool(name="close_window", desc="Close a window by title", category="system", permission=True)
def close_window(title: str) -> str:
    windows = gw.getWindowsWithTitle(title)
    if not windows:
        all_wins = gw.getAllWindows()
        windows = [w for w in all_wins if title.lower() in w.title.lower() and w.title]
    if windows:
        windows[0].close()
        return f"Closed: '{windows[0].title}'"
    return f"Window not found: '{title}'"


@tool(name="click_position", desc="Click at specific screen coordinates", category="system")
def click_position(x: int, y: int) -> str:
    pyautogui.click(x, y)
    return f"Clicked at ({x}, {y})"


@tool(name="right_click", desc="Right-click at specific screen coordinates", category="system")
def right_click(x: int, y: int) -> str:
    pyautogui.rightClick(x, y)
    return f"Right-clicked at ({x}, {y})"


@tool(name="double_click", desc="Double-click at specific screen coordinates", category="system")
def double_click(x: int, y: int) -> str:
    pyautogui.doubleClick(x, y)
    return f"Double-clicked at ({x}, {y})"


@tool(name="mouse_move", desc="Move mouse to specific coordinates", category="system")
def mouse_move(x: int, y: int) -> str:
    pyautogui.moveTo(x, y, duration=0.3)
    return f"Mouse moved to ({x}, {y})"


@tool(name="scroll", desc="Scroll up or down (positive=up, negative=down)", category="system")
def scroll(amount: int) -> str:
    pyautogui.scroll(amount)
    direction = "up" if amount > 0 else "down"
    return f"Scrolled {direction} by {abs(amount)}"


@tool(name="get_screen_size", desc="Get the screen resolution", category="system")
def get_screen_size() -> str:
    size = pyautogui.size()
    return f"Screen resolution: {size.width}x{size.height}"


@tool(name="get_mouse_position", desc="Get current mouse cursor position", category="system")
def get_mouse_position() -> str:
    pos = pyautogui.position()
    return f"Mouse at: ({pos.x}, {pos.y})"
