' DouTracker - Silent Launcher (no console window)
' Usage: wscript launch_doutracker.vbs
Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

appDir = fso.GetParentFolderName(WScript.ScriptFullName)

' Run python app.py silently (window style 0 = hidden)
WshShell.Run "python """ & appDir & "\app.py""", 0, False
