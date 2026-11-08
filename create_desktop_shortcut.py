#!/usr/bin/env python3
"""
Creates a Windows Desktop Shortcut for Bangladesh Inland Vessel Scantlings Suite.
"""

import os
import sys

def create_shortcut():
    try:
        import win32com.client
    except ImportError:
        win32com = None

    base_dir = os.path.dirname(os.path.abspath(__file__))
    desktop_dir = os.path.join(os.environ["USERPROFILE"], "Desktop")
    shortcut_path = os.path.join(desktop_dir, "Bangladesh Scantlings Suite.lnk")
    icon_path = os.path.join(base_dir, "app_icon.ico")
    target_vbs = os.path.join(base_dir, "BanglaScantling.vbs")

    # Use PowerShell to create the .lnk shortcut reliably without extra python packages
    ps_command = f"""
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut('{shortcut_path}')
$Shortcut.TargetPath = '{target_vbs}'
$Shortcut.WorkingDirectory = '{base_dir}'
$Shortcut.Description = 'Bangladesh Inland Vessel Statutory Compliance & Scantlings Suite'
if (Test-Path '{icon_path}') {{
    $Shortcut.IconLocation = '{icon_path}, 0'
}}
$Shortcut.Save()
"""
    import subprocess
    res = subprocess.run(["powershell", "-NoProfile", "-Command", ps_command], capture_output=True, text=True)
    if res.returncode == 0 and os.path.exists(shortcut_path):
        print(f"[SUCCESS] Desktop shortcut created at: {shortcut_path}")
        return True
    else:
        print(f"[WARNING] Could not create desktop shortcut automatically: {res.stderr}")
        return False

if __name__ == "__main__":
    create_shortcut()
