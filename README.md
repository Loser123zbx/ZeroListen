# 零听 ZeroListen

> 本地离线中/英文词句 TTS 批量生成工具

零听（ZeroListen）是一款运行在 Windows 上的桌面软件，用于把**词句库**（单词、短语、句子）批量合成为真人级语音，并支持两种导出方式：**独立音频文件**（WAV）和**可跟读的网页播放器**（HTML）。所有语音合成均在本地完成，不调用任何云端语音接口；同时内置**离线英译中**能力（弃用），可自动为词句补充中文释义。

- **纯本地离线**：语音由本地 ONNX 模型（Kokoro-82M）+ kokoro-js 引擎合成，不上传任何文本到云端。
- **中英文双语**：内置 36 种声音（美音、英音、普通话，男女声齐全）。
- **批量生成**：一次可为整库或勾选的任意词句批量生成音频。
- **离线机翻**：可自动把英文词句翻译成中文释义（Argos Translate，英→中）。
- **网页跟读播放器**：导出一个自包含的 HTML 播放器，支持跟读模式、连播、变速等。

> 📖 日常使用请参阅 [用户手册](用户手册.md)。

---

## 目录结构

```
ZeroListen零听/
├── 用户手册.md          # 使用说明
├── src/
│   ├── main.py          # 程序入口（wxPython GUI）
│   ├── all_panels.py    # wxFormBuilder 生成的界面面板（请勿编辑）
│   ├── html_player.py   # HTML 播放器生成器
│   ├── translator.py    # 离线机翻（Argos Translate）封装
│   ├── tts_cli.js       # Node 语音合成批处理引擎（程序内部调用）
│   ├── tts.js           # kokoro-js 单句合成示例脚本（开发用）
│   ├── tts.py           # onnxruntime 直接推理示例脚本（开发用）
│   ├── package.json     # Node 依赖（kokoro-js）
│   ├── zerolisten.spec  # PyInstaller 打包配置
│   ├── build.bat        # 一键打包脚本
│   └── config.json      # 音频导出配置（程序自动读写）
├── .venv/               # Python 虚拟环境（不入库）
└── .gitignore
```

> 模型文件（`model.onnx`、`kokoro-v1.0.onnx`、`af.bin` 等）、`node_modules/`、`dist/` 等构建/运行产物均不入库，请按下方指南自行准备。

---

## 开发运行（源码方式）

### 环境要求

| 依赖 | 版本要求 | 用途 |
| --- | --- | --- |
| Python | **64 位 3.11**（Argos Translate 的 ctranslate2 无 32 位包） | 桌面 GUI 主程序 |
| Node.js | 较新的 LTS 即可，需加入 `PATH` | kokoro-js 语音合成引擎 |
| npm | 随 Node.js 安装 | 安装 Node 依赖 |

### 1. 创建虚拟环境并安装 Python 依赖

在项目根目录执行：

```bat
python -m venv .venv
.venv\Scripts\activate
pip install wxPython openpyxl argostranslate
```

### 2. 安装 Node 依赖

```bat
cd src
npm install
cd ..
```

这会安装 `kokoro-js`（见 `src/package.json`）。

### 3. 准备语音模型

首次生成语音时，程序会自动从 `hf-mirror.com` 镜像下载 Kokoro-82M 模型并缓存到本地，之后完全离线运行。若网络不通，可手动把以下文件放入 `src/` 目录：

- `model.onnx` —— Kokoro 主模型（来自 `onnx-community/Kokoro-82M-ONNX`）
- `af.bin` —— 语音风格向量（来自 Kokoro 仓库的 voices 文件）

### 4. 安装离线机翻语言包（可选）

```bat
python -c "import argostranslate.package as p; p.update_package_index(); pkgs=[x for x in p.get_available_packages() if x.from_code=='en' and x.to_code=='zh']; p.install_from_path(pkgs[0].download()); print('language package installed')"
```

### 5. 启动

```bat
cd src
python main.py
```

---

## 构建指南（打包为 exe）

打包使用 PyInstaller（onedir 模式），配置文件为 `src/zerolisten.spec`。**必须使用 64 位 Python 3.11**。

### 一键打包（推荐）

在项目根目录激活虚拟环境后，直接运行：

```bat
src\build.bat
```

脚本会依次完成：

1. 升级 pip；
2. 安装依赖（wxPython、openpyxl、argostranslate、pyinstaller）；
3. 下载并安装 Argos Translate 英→中语言包；
4. 用 PyInstaller 执行 `zerolisten.spec` 打包；
5. 把 `tts_cli.js`、`node_modules/`、模型文件拷贝到 `dist\ZeroListen\`。

打包完成后，可执行文件位于：`src\dist\ZeroListen\ZeroListen.exe`。

### 手动打包（分步执行）

在 `src/` 目录下：

```bat
REM 1. 安装打包工具
pip install pyinstaller

REM 2. 执行 PyInstaller（--noconfirm 覆盖旧产物，--clean 清理缓存）
python -m PyInstaller --noconfirm --clean zerolisten.spec

REM 3. 拷贝 Node 运行时资源到打包目录
xcopy /E /I /Y tts_cli.js dist\ZeroListen\ >nul
xcopy /E /I /Y node_modules dist\ZeroListen\node_modules\ >nul

REM 4. 拷贝模型文件（若需要离线可用）
copy /Y model.onnx dist\ZeroListen\ >nul
copy /Y kokoro-v1.0.onnx dist\ZeroListen\ >nul
copy /Y af.bin dist\ZeroListen\ >nul
```

> **注意**：目标机器上若没有安装 Node.js，需要把 `node.exe` 一并放到 `dist\ZeroListen\` 目录，否则导出音频时会提示「未找到 Node.js」。

### 打包产物说明

| 路径 | 说明 |
| --- | --- |
| `dist\ZeroListen\ZeroListen.exe` | 主程序 |
| `dist\ZeroListen\tts_cli.js` | 语音合成引擎（程序内部调用） |
| `dist\ZeroListen\node_modules\` | kokoro-js 等 Node 依赖 |
| `dist\ZeroListen\model.onnx` 等 | 语音模型（离线可用必需） |
| `dist\ZeroListen\node.exe` | Node 运行时（目标机未装 Node 时必需） |

首次在目标机器上生成语音时仍需联网下载一次模型（之后走本地缓存）。

---

## 常见问题

| 现象 | 解决办法 |
| --- | --- |
| `import wx` 失败 | 确认已 `pip install wxPython` 且用的是 Python 3.10+ |
| `npm install` 缓慢/失败 | 检查网络；必要时配置 npm 国内镜像 |
| 提示「未找到 Node.js」 | 安装 Node.js，或将 `node.exe` 放到程序/打包目录 |
| 模型下载失败 | 检查网络能否访问 `hf-mirror.com`；或手动放置模型文件到 `src/` |
| 打包后 exe 无法启动 | 确认用 Python 3.10+ 打包，且 `node_modules` 与模型文件已拷入 `dist\ZeroListen\` |

---

## 许可证

Copyright © 2026 Loser_123_zero(Loser_123_zbx/Stanzero_)

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.