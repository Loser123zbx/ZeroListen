@echo off
REM ============================================================
REM  ZeroListen 单文件 EXE 打包脚本
REM  运行后产物在 ..\release\ZeroListen.exe
REM  注意：程序运行时需要相邻的 node_modules / wordlibs / exports / node 等目录
REM ============================================================
setlocal
cd /d "%~dp0"

set PY=python

if not exist "%~dp0node_modules" (
    echo [1/3] 安装项目 Node 依赖...
    if exist "%~dp0node\npm.cmd" (
        call "%~dp0node\npm.cmd" install --prefix "%~dp0" --no-fund --no-audit
    ) else (
        %PY% -m pip install --upgrade pip
        %PY% -m pip install wxPython openpyxl argostranslate pyinstaller
        %PY% -c "import argostranslate.package as p; p.update_package_index(); pkgs=[x for x in p.get_available_packages() if x.from_code=='en' and x.to_code=='zh']; p.install_from_path(pkgs[0].download()); print('language package installed')"
        call npm install --prefix "%~dp0" --no-fund --no-audit
    )
)

echo [2/3] PyInstaller 打包单文件 EXE...
%PY% -m PyInstaller --noconfirm --clean --onefile --windowed --name ZeroListen --distpath ..\release --workpath ..\_build_work --specpath ..\_build_spec --icon logo.ico main.py

echo [3/3] 拷贝运行时资源...
if exist tts_cli.js copy /Y tts_cli.js ..\release\ >nul
if exist package.json copy /Y package.json ..\release\ >nul
if exist config.json copy /Y config.json ..\release\ >nul
if exist wordlibs xcopy /E /I /Y wordlibs ..\release\wordlibs\ >nul
if exist exports xcopy /E /I /Y exports ..\release\exports\ >nul
if exist node_modules xcopy /E /I /Y node_modules ..\release\node_modules\ >nul
if exist node xcopy /E /I /Y node ..\release\node\ >nul

echo.
echo 完成! 可执行文件: ..\release\ZeroListen.exe
echo 说明: 程序运行时会优先使用同目录下的 node / node_modules 资源。
endlocal
