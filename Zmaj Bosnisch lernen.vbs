' Zmaj – Bosnisch lernen – Starter ohne schwarzes Fenster.
' Doppelklick: startet start.py unsichtbar im Hintergrund, der Browser öffnet sich.
' Ein zweiter Doppelklick öffnet nur den Browser. Den Knopf "App beenden"
' gibt es nicht mehr; beenden über pythonw.exe im Task-Manager (oder einfach
' laufen lassen, start.py schreibt seit dem 04.10.2026 nur noch start.log).
Option Explicit
Dim fso, sh, ordner, python, pythonw
Set fso = CreateObject("Scripting.FileSystemObject")
Set sh = CreateObject("WScript.Shell")
ordner = fso.GetParentFolderName(WScript.ScriptFullName)

' Python aus Thonny, ohne Konsolenfenster
pythonw = sh.ExpandEnvironmentStrings("%LOCALAPPDATA%") & "\Programs\Thonny\pythonw.exe"
python  = sh.ExpandEnvironmentStrings("%LOCALAPPDATA%") & "\Programs\Thonny\python.exe"

If fso.FileExists(pythonw) Then
    sh.CurrentDirectory = ordner
    sh.Run """" & pythonw & """ -X utf8 """ & ordner & "\start.py""", 0, False
ElseIf fso.FileExists(python) Then
    sh.CurrentDirectory = ordner
    sh.Run """" & python & """ -X utf8 """ & ordner & "\start.py""", 0, False
Else
    MsgBox "Thonny (Python) wurde nicht gefunden unter:" & vbCrLf & pythonw & vbCrLf & vbCrLf & _
           "Bitte Thonny installieren oder start.py in Thonny öffnen und auf Run drücken.", _
           vbExclamation, "Zmaj – Bosnisch lernen"
End If
