#!/usr/bin/env python3
"""
==============================================================================
BANGLADESH INLAND VESSEL STATUTORY COMPLIANCE & SCANTLINGS SUITE
Native Windows App-Mode Desktop Launcher
==============================================================================

Uses Microsoft Edge in dedicated Application Mode (--app=...).
- Zero new dependencies: Edge is built into every Windows 10/11 system.
- Zero download size: 0 MB.
- Window style: Clean, standalone application window with no browser tabs,
  no address bar, and no navigation buttons.
- Isolated storage: Uses %LOCALAPPDATA%\\BanglaScantlingApp\\EdgeProfile
  to prevent interference with personal browsing or browser extensions.
- Lifecycle management: Launches the FastAPI backend silently in the background,
  waits for health readiness, and cleanly closes the server upon app exit.
==============================================================================
"""

import sys
import os
import time
import shutil
import subprocess
import urllib.request
import urllib.error

APP_PORT = 8055
APP_URL = f"http://127.0.0.1:{APP_PORT}"
APP_TITLE = "ShipLab-BD - Naval Architecture Suite"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def is_server_running(url: str, timeout: float = 0.8) -> bool:
    """Checks if the local backend server is running and responding."""
    try:
        req = urllib.request.Request(
            f"{url}/api/v1/initial-state",
            headers={"User-Agent": "BanglaScantlingLauncher/1.0"}
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status == 200
    except Exception:
        return False

def find_browser_executable() -> str:
    """Locates Microsoft Edge (or Google Chrome as fallback) on Windows."""
    candidates = [
        # Microsoft Edge (Standard Windows 10 / 11)
        os.path.expandvars(r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"),
        os.path.expandvars(r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"),
        os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Edge\Application\msedge.exe"),
        shutil.which("msedge"),
        # Google Chrome fallback
        os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
        shutil.which("chrome"),
    ]
    for c in candidates:
        if c and os.path.isfile(c):
            return os.path.abspath(c)
    return ""

def kill_process_tree(pid: int):
    """Cleanly terminates a process tree on Windows."""
    try:
        subprocess.run(
            ["taskkill", "/F", "/T", "/PID", str(pid)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except Exception:
        pass

def start_backend_server() -> subprocess.Popen:
    """Starts the FastAPI backend server as a background subprocess."""
    server_script = os.path.join(BASE_DIR, "run_server.py")
    python_exe = sys.executable

    # Prevent command prompt window from popping up when running via pythonw/vbs
    flags = 0
    if sys.platform == "win32":
        flags = subprocess.CREATE_NO_WINDOW

    proc = subprocess.Popen(
        [python_exe, server_script, str(APP_PORT), "--no-reload"],
        cwd=BASE_DIR,
        creationflags=flags,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    return proc

def launch_app():
    browser_exe = find_browser_executable()
    if not browser_exe:
        print("[ERROR] Microsoft Edge (or Chrome) was not found on this system.")
        print("Please ensure Microsoft Edge is installed to run in native App Mode.")
        sys.exit(1)

    started_server = False
    server_proc = None

    # 1. Ensure backend server is running
    if not is_server_running(APP_URL):
        print("Starting Bangladesh Scantlings backend server...")
        server_proc = start_backend_server()
        started_server = True

        # Wait up to 12 seconds for the server to initialize
        max_retries = 24
        for _ in range(max_retries):
            time.sleep(0.5)
            if is_server_running(APP_URL):
                print(f"Backend server ready at {APP_URL}")
                break
        else:
            print("[ERROR] Timed out waiting for backend server to start.")
            if server_proc:
                kill_process_tree(server_proc.pid)
            sys.exit(1)
    else:
        print(f"Connected to running backend server at {APP_URL}")

    # 2. Configure dedicated isolated user data directory
    app_data_dir = os.path.join(
        os.environ.get("LOCALAPPDATA", os.path.expanduser("~")),
        "BanglaScantlingApp",
        "EdgeProfile"
    )
    os.makedirs(app_data_dir, exist_ok=True)

    # 3. Launch Edge in dedicated chromeless App Mode
    cmd = [
        browser_exe,
        f"--app={APP_URL}",
        f"--user-data-dir={app_data_dir}",
        "--window-size=1440,900",
        "--window-position=100,50",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-features=Translate,InterestFeedContentSuggestions",
        "--app-title=" + APP_TITLE
    ]

    print(f"Launching {APP_TITLE} in Native Windows App Mode...")
    edge_proc = subprocess.Popen(cmd)

    # 4. Monitor the application window
    try:
        edge_proc.wait()
    except KeyboardInterrupt:
        pass
    finally:
        # 5. Clean shutdown: if we started the server, terminate it when the window is closed
        if started_server and server_proc:
            print("Application window closed. Shutting down background server...")
            kill_process_tree(server_proc.pid)
            print("Application shutdown complete.")

if __name__ == "__main__":
    launch_app()
