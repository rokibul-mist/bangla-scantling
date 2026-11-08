' ==============================================================================
' BANGLADESH INLAND VESSEL SCANTLINGS SUITE - DESKTOP APP LAUNCHER
' Launches the application in native Edge App Mode with NO black command window.
' ==============================================================================

Set WshShell = CreateObject("WScript.Shell")
Set FSO = CreateObject("Scripting.FileSystemObject")

' Set working directory to this script's directory
ScriptDir = FSO.GetParentFolderName(WScript.ScriptFullName)
WshShell.CurrentDirectory = ScriptDir

' Run with pythonw.exe (windowless python)
cmd = "pythonw.exe """ & ScriptDir & "\run_app.py"""

' 0 = hide console window entirely; False = asynchronous return
WshShell.Run cmd, 0, False
