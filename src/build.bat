@echo off
REM ============================================================
REM  ZeroListen 一键打包脚本 (在 64 位 Python 3.11 环境下运行)
REM  运行后产物在 dist\ZeroListen\ZeroListen.exe
REM ============================================================
setlocal
cd /d "%~dp0"

set PY=python

echo [1/5] 升级 pip...
%PY% -m pip install --upgrade pip

echo [2/5] 安装依赖 (wxPython, openpyxl, argostranslate, pyinstaller)...
%PY% -m pip install wxPython openpyxl argostranslate pyinstaller

echo [3/5] 下载并安装 Argos Translate 英→中(zh) 语言包...
%PY% -c "import argostranslate.package as p; p.update_package_index(); pkgs=[x for x in p.get_available_packages() if x.from_code=='en' and x.to_code=='zh']; p.install_from_path(pkgs[0].download()); print('language package installed')"

echo [4/5] PyInstaller 打包...
%PY% -m PyInstaller --noconfirm --clean zerolisten.spec

echo [5/5] 拷贝 Node 运行时资源到 dist\ZeroListen\...
xcopy /E /I /Y tts_cli.js dist\ZeroListen\ >nul
xcopy /E /I /Y node_modules dist\ZeroListen\node_modules\ >nul
if exist model.onnx copy /Y model.onnx dist\ZeroListen\ >nul
if exist kokoro-v1.0.onnx copy /Y kokoro-v1.0.onnx dist\ZeroListen\ >nul
if exist af.bin copy /Y af.bin dist\ZeroListen\ >nul

echo.
echo 完成! 可执行文件: dist\ZeroListen\ZeroListen.exe
echo 注意: 目标机器需安装 Node.js, 或把 node.exe 放到 dist\ZeroListen\ 目录。
echo 首次生成语音需联网下载一次模型(之后使用缓存)。
endlocal
