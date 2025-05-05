@echo off
cd /d "%~dp0"

:: Start listener first
start "" py listener.py

:: Give it a moment to start
timeout /t 2 >nul

:: Run the main Python script
py ScriptingProject\ScriptingProject\ScriptingProject.py

pause