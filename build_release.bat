@echo off
setlocal
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
    call ".venv\Scripts\python.exe" "build_release.py"
) else (
    call python "build_release.py"
)
