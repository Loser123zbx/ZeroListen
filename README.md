# ZeroListen

ZeroListen 是一款面向 Windows 的本地离线语音生成工具，适合批量处理词句、短语和句子，并将其转换为自然语音。它支持输出独立音频文件和可跟读的 HTML 播放页面，适合语言学习、口语训练和离线词库制作。

本项目的核心目标是：在本地完成语音合成，不依赖云端语音接口，避免隐私泄露和网络依赖。

## 功能概览

- 本地离线语音合成
- 中英文双语词句处理
- 批量生成音频
- 导出 WAV 音频文件
- 导出可播放的 HTML 跟读页面
- 支持多种发音人和语速设置

## 使用说明

日常使用请参考 [用户手册](用户手册.md)。

## 项目结构

```text
ZeroListen/
├── .gitignore
├── LICENSE
├── README.md
├── 用户手册.md
├── src/
│   ├── all_panels.py
│   ├── build.bat
│   ├── config.json
│   ├── download_source.json
│   ├── html_player.py
│   ├── installer.py
│   ├── main.py
│   ├── package.json
│   ├── tts_cli.js
│   ├── tts.js
│   ├── tts.py
│   ├── zerolisten.spec
│   └── wxProjects/
│       ├── panels.fbp
│       └── ZeroListenInstaller.fbp
```

说明：

- `src/` 下为主程序代码和语音生成相关脚本。
- `node/` 中保留了本地 Node 运行环境，便于在离线环境中使用。
- 模型文件、缓存目录和构建产物一般不建议直接提交到仓库，需要按实际使用环境准备。

## 环境要求

- Python 3.11 64 位
- Node.js 和 npm
- Windows 10/11

## 运行方式

### 1. 安装 Python 依赖

在项目根目录执行：

```bat
python -m venv .venv
.venv\Scripts\activate
pip install wxPython openpyxl
```

### 2. 安装 Node 依赖

```bat
cd src
npm install
cd ..
```

### 3. 启动程序

```bat
cd src
python main.py
```

## 模型准备

首次生成语音时，程序通常会自动下载或缓存所需模型。如果网络不稳定，可以手动准备以下文件并放到 `src/` 目录中：

- `model.onnx`
- `af.bin`
- `kokoro-v1.0.onnx`

这些文件用于完成本地语音合成。若网络可用，通常可以由程序自动处理下载与缓存。

## 打包说明

项目使用 PyInstaller 进行打包。打包脚本位于 `src/build.bat`，流程包括依赖安装、语言包准备以及程序打包。推荐使用 64 位 Python 3.11。

在项目根目录执行：

```bat
src\build.bat
```

打包后，生成物通常位于：

```text
src\dist\ZeroListen\
```

## 常见问题

### 1. import wx 失败

确认已安装 wxPython，并使用正确的 Python 3.11 解释器。

### 2. npm install 失败

检查网络连接，必要时更换 npm 镜像源。

### 3. 提示未找到 Node.js

在系统中安装 Node.js，或者将 `node.exe` 放入打包目录中。

### 4. 模型下载失败

检查网络是否能访问目标镜像源，或者手动放置所需模型文件到 `src/` 目录。

## 许可证

本项目采用 MIT License。详细内容见 [LICENSE](LICENSE)。

Copyright (c) 2026 Loser_123_zero(Loser_123_zbx/Stanzero_)

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
