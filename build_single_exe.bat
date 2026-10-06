@echo off
setlocal
cd /d "%~dp0"
python build_release.py
endlocal
