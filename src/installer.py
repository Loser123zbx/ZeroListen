# -*- coding: utf-8 -*-
"""ZeroListen 安装器.

使用方式:
1. 将 installer.exe 和源代码压缩包放在同一目录。
2. 程序会自动检测 Windows 版本与 CPU 架构，下载对应的便携版 Python 和 Node.js。
3. 解压源码到固定安装目录，并创建启动脚本与桌面快捷方式。
"""

import os
import sys
import json
import shutil
import platform
import subprocess
import threading
import zipfile
import urllib.request
import urllib.error
import tempfile
import time
from pathlib import Path

try:
    import wx
except Exception:  # pragma: no cover - 运行时才由 PyInstaller 注入 wxPython
    wx = None


APP_ROOT = Path(__file__).resolve().parent if not getattr(sys, "frozen", False) else Path(sys.executable).resolve().parent
DESKTOP_DIR = os.path.join(os.environ.get("USERPROFILE", ""), "Desktop")
INSTALL_ROOT = APP_ROOT

PYTHON_VERSION = "3.11.9"
NODE_VERSION = "v20.19.4"
NODE_ARCH = "win-x64"
NODE_MODULES_ZIP_NAME = "node_modules.zip"


def log(msg):
    print(msg)


def detect_system():
    machine = platform.machine().lower()
    if machine in {"amd64", "x86_64"}:
        arch = "x64"
    elif machine in {"arm64", "aarch64"}:
        arch = "arm64"
    else:
        arch = "x64"

    winver = platform.win32_ver()[0]
    major = int(str(winver).split(".")[0]) if str(winver).strip() else 10
    system_name = "Windows 11" if major >= 11 else "Windows 10" if major >= 10 else "Windows 7/8"
    return system_name, arch, major


def is_windows():
    return os.name == "nt"


def find_source_zip():
    search_paths = [APP_ROOT]
    for root in search_paths:
        if not root.exists():
            continue
        candidates = []
        for p in root.iterdir():
            if p.is_file() and p.suffix.lower() == ".zip":
                name = p.name.lower()
                if "zero" in name or "src" in name or "source" in name:
                    candidates.append(p)
        if candidates:
            return sorted(candidates, key=lambda p: len(p.name))[0]
    return None


def _estimate_eta(start_time, progress, total):
    if total <= 0 or progress <= 0:
        return "预计剩余时间：计算中"
    elapsed = max(time.monotonic() - start_time, 0.1)
    done = max(progress, 0)
    remaining = max(total - done, 0)
    rate = done / elapsed
    if rate <= 0:
        return "预计剩余时间：计算中"
    eta_seconds = remaining / rate
    hours, rem = divmod(int(eta_seconds), 3600)
    minutes, seconds = divmod(rem, 60)
    return f"预计剩余时间：{hours:02d}:{minutes:02d}:{seconds:02d}"


def _emit_progress(callback, progress, total, message, start_time=None):
    if callback is None:
        return
    msg = message
    if start_time is not None:
        msg = f"{message} | {_estimate_eta(start_time, progress, total)}"
    try:
        callback(progress, total, msg)
    except TypeError:
        try:
            callback(progress)
        except TypeError:
            callback()


def download_file(url, dest_path, callback=None, message="下载中", start_time=None):
    with urllib.request.urlopen(url, timeout=90) as resp, open(dest_path, "wb") as f:
        total = int(resp.headers.get("Content-Length", "0") or "0")
        downloaded = 0
        while True:
            chunk = resp.read(1024 * 1024)
            if not chunk:
                break
            f.write(chunk)
            downloaded += len(chunk)
            if callback and total:
                pct = min(95, int(downloaded * 100 / total))
                _emit_progress(callback, pct, 100, message, start_time)
    if callback:
        _emit_progress(callback, 100, 100, message, start_time)


def download_with_fallback(candidate_urls, dest_path, callback=None):
    last_error = None
    start_time = time.monotonic()
    for url in candidate_urls:
        try:
            _emit_progress(callback, 0, 100, f"尝试下载源：{url}", start_time)
            if dest_path.exists():
                dest_path.unlink()
            download_file(
                url,
                dest_path,
                lambda p, total=100, msg="下载中": _emit_progress(callback, p, total, msg, start_time),
                message=f"下载中：{url}",
                start_time=start_time,
            )
            _emit_progress(callback, 100, 100, f"下载成功：{url}", start_time)
            return url
        except Exception as exc:  # pragma: no cover - depends on network
            last_error = exc
            _emit_progress(callback, 0, 100, f"下载失败，切换到下一个源：{url}", start_time)
            if dest_path.exists():
                try:
                    dest_path.unlink()
                except Exception:
                    pass
    if last_error is not None:
        raise last_error
    raise RuntimeError("下载失败：没有可用的下载地址")


def _extract_to_directory(zip_path, target_dir, progress_cb=None, start_time=None):
    target_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "r") as zf:
        infos = zf.infolist()
        total = len(infos) or 1
        for idx, info in enumerate(infos, start=1):
            dest = target_dir / info.filename
            if progress_cb:
                progress_cb(int((idx - 1) * 100 / total), 100, f"准备解压：{info.filename} ({info.file_size} bytes)")
            zf.extract(info, target_dir)
            if progress_cb:
                progress_cb(int(idx * 100 / total), 100, f"已解压：{info.filename} -> {dest} ({info.file_size} bytes)")


def _run_logged_command(cmd, progress_cb=None, label="命令执行", cwd=None):
    if progress_cb:
        progress_cb(0, 100, f"{label}：{' '.join(str(part) for part in cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(cwd) if cwd else None)
    if result.stdout and progress_cb:
        progress_cb(0, 100, result.stdout.strip())
    if result.stderr and progress_cb:
        progress_cb(0, 100, result.stderr.strip())
    return result


def _run_streaming_command(cmd, progress_cb=None, label="命令执行", progress_base=0, env=None):
    if progress_cb:
        progress_cb(progress_base, 100, f"{label}：{' '.join(str(part) for part in cmd)}")
    final_env = os.environ.copy()
    if env:
        final_env.update(env)
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        shell=False,
        env=final_env,
    )

    def _drain_stream(stream):
        try:
            for line in iter(stream.readline, ""):
                text = line.rstrip()
                if text and progress_cb:
                    progress_cb(progress_base, 100, text)
        finally:
            stream.close()

    stdout_thread = threading.Thread(target=_drain_stream, args=(process.stdout,), daemon=True)
    stdout_thread.start()
    return_code = process.wait()
    stdout_thread.join(timeout=5)
    return return_code


def _ensure_python_pip(python_exe, python_dir, progress_cb=None):
    for cmd in (
        [str(python_exe), "-m", "ensurepip", "--upgrade"],
        [str(python_exe), "-m", "ensurepip", "--default-pip"],
    ):
        result = _run_logged_command(cmd, progress_cb, "自举 pip")
        if result.returncode == 0:
            verify = _run_logged_command([str(python_exe), "-m", "pip", "--version"], progress_cb, "检查 pip")
            if verify.returncode == 0:
                return True

    get_pip_path = python_dir / "get-pip.py"
    try:
        if progress_cb:
            progress_cb(0, 100, "pip 不存在，尝试从官方源下载 get-pip.py 进行手动安装…")
        urllib.request.urlretrieve("https://bootstrap.pypa.io/get-pip.py", str(get_pip_path))
        env = os.environ.copy()
        env["PIP_INDEX_URL"] = "https://pypi.org/simple"
        env["PIP_EXTRA_INDEX_URL"] = "https://pypi.org/simple"
        env["PYTHONHTTPSVERIFY"] = "1"
        result = _run_logged_command([
            str(python_exe),
            str(get_pip_path),
            "--trusted-host",
            "mirrors.aliyun.com",
        ], progress_cb, "安装 pip")
        if result.returncode == 0:
            verify = _run_logged_command([str(python_exe), "-m", "pip", "--version"], progress_cb, "检查 pip")
            if verify.returncode == 0:
                return True
    except Exception as exc:
        if progress_cb:
            progress_cb(0, 100, f"get-pip.py bootstrap 失败：{exc}")

    return False


def _move_contents(src_dir, dest_dir):
    if not src_dir.exists():
        return
    for item in src_dir.iterdir():
        dst = dest_dir / item.name
        if dst.exists() or dst.is_symlink():
            if dst.is_dir():
                shutil.rmtree(dst)
            else:
                dst.unlink()
        shutil.move(str(item), str(dst))


def _venv_has_installed_packages(python_dir):
    site_packages = python_dir / "Lib" / "site-packages"
    if not site_packages.exists():
        return False
    for item in site_packages.iterdir():
        if item.name in {"__pycache__", "pip", "pip-", "setuptools", "wheel"}:
            continue
        if item.name.endswith(".dist-info") or item.name.endswith(".egg-info") or item.suffix.lower() == ".pth":
            return True
        if item.is_dir():
            return True
    return False


def sanitize_venv_cfg(venv_dir):
    cfg_path = venv_dir / "pyvenv.cfg"
    if not cfg_path.exists():
        return

    scripts_dir = venv_dir / "Scripts"
    python_exe = (scripts_dir / "python.exe").resolve()
    if not scripts_dir.exists() or not python_exe.exists():
        return

    base_home = Path(sys.base_prefix).resolve() if getattr(sys, "base_prefix", None) else Path(sys.executable).resolve().parent.parent
    actual_lines = [
        f"home = {base_home}",
        f"include-system-site-packages = false",
        f"version = {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        f"executable = {python_exe}",
        f"command = {python_exe} -m venv {venv_dir.resolve()}",
    ]
    cfg_path.write_text("\n".join(actual_lines) + "\n", encoding="utf-8")


def ensure_python_install(root_dir, progress_cb=None):
    python_dir = root_dir / ".venv"
    py_exe = python_dir / "Scripts" / "python.exe"
    if py_exe.exists():
        return python_dir

    zip_path = APP_ROOT / ".venv.zip"
    if not zip_path.exists():
        raise FileNotFoundError("未找到 .venv.zip。请把当前项目的 Python 虚拟环境压缩包与 installer.exe 放在同一目录。")

    if progress_cb:
        progress_cb(0, 100, "正在解压当前 Python 虚拟环境到 .venv 目录…")
    if python_dir.exists():
        shutil.rmtree(python_dir)

    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(root_dir)

    sanitize_venv_cfg(python_dir)

    if not py_exe.exists():
        raise FileNotFoundError("Python 虚拟环境未正确解压，未找到 .venv\Scripts\python.exe")

    probe = subprocess.run([str(py_exe), "-c", "import sys; print(sys.executable)"], capture_output=True, text=True)
    if probe.returncode != 0:
        raise RuntimeError(f"Python 虚拟环境安装后仍无法启动：{probe.stderr.strip() or probe.stdout.strip()}")

    if progress_cb:
        progress_cb(100, 100, "Python 虚拟环境解压完成")

    if zip_path.exists():
        zip_path.unlink()
    return python_dir


def ensure_node_install(root_dir, progress_cb=None):
    node_dir = root_dir / "node"
    node_exe = node_dir / "node.exe"
    if node_exe.exists():
        return node_dir

    system_name, arch, _ = detect_system()
    node_arch = "win-x64" if arch == "x64" else "win-arm64" if arch == "arm64" else "win-x64"
    node_zip_name = f"node-{NODE_VERSION}-{node_arch}.zip"
    node_urls = [
        f"https://registry.npmmirror.com/-/binary/node/{NODE_VERSION}/{node_zip_name}",
        f"https://npm.taobao.org/mirrors/node/{NODE_VERSION}/{node_zip_name}",
        f"https://mirrors.huaweicloud.com/nodejs/{NODE_VERSION}/{node_zip_name}",
        f"https://nodejs.org/dist/{NODE_VERSION}/{node_zip_name}",
    ]

    zip_path = root_dir / "node-portable.zip"
    if progress_cb:
        progress_cb(0, 100, f"正在下载便携版 Node.js ({system_name}, {arch})…")
    download_with_fallback(
        node_urls,
        zip_path,
        lambda p, total, msg: progress_cb(p, total, msg) if progress_cb else None,
    )

    if progress_cb:
        progress_cb(0, 100, "正在解压 Node.js 到 node 目录…")
    extracted_dir = None
    for child in root_dir.iterdir():
        if child.is_dir() and child.name.startswith("node-"):
            extracted_dir = child
            break
    if extracted_dir and not node_dir.exists():
        shutil.move(str(extracted_dir), str(node_dir))
    if not node_dir.exists():
        _extract_to_directory(zip_path, root_dir, progress_cb)
        for child in root_dir.iterdir():
            if child.is_dir() and child.name.startswith("node-"):
                extracted_dir = child
                break
        if extracted_dir and not node_dir.exists():
            shutil.move(str(extracted_dir), str(node_dir))
    if progress_cb:
        progress_cb(100, 100, "Node.js 解压完成")

    if zip_path.exists():
        zip_path.unlink()

    if not node_exe.exists():
        raise FileNotFoundError("Node.js portable runtime 未正确解压，未找到 node.exe")
    return node_dir


def install_dependencies(python_dir, node_dir, app_dir, progress_cb=None):
    py_exe = python_dir / "Scripts" / "python.exe"
    if not py_exe.exists():
        raise FileNotFoundError("Python 虚拟环境未就绪，无法安装依赖")

    has_installed_libs = _venv_has_installed_packages(python_dir)
    pip_probe = _run_logged_command([str(py_exe), "-m", "pip", "--version"], progress_cb, "检查 pip")

    if pip_probe.returncode != 0:
        if has_installed_libs:
            if progress_cb:
                progress_cb(0, 100, ".venv 中已存在第三方库，直接使用现有环境；未安装 pip 时跳过 bootstrap")
            has_pip = False
        else:
            if progress_cb:
                progress_cb(0, 100, "Python 虚拟环境未安装 pip，且未发现现成第三方库，尝试自举 pip…")
            has_pip = _ensure_python_pip(py_exe, python_dir, progress_cb)
            if not has_pip:
                raise RuntimeError("Python 虚拟环境未能安装 pip，且未发现现成第三方库，无法继续安装依赖")
    else:
        has_pip = True

    if not has_pip and not has_installed_libs:
        raise RuntimeError("Python 虚拟环境缺少 pip 与已安装第三方库，无法继续安装依赖")

    node_modules_zip = APP_ROOT / NODE_MODULES_ZIP_NAME
    if not node_modules_zip.exists():
        raise FileNotFoundError(f"未找到 {NODE_MODULES_ZIP_NAME}，请确认与 installer.exe 同目录存在 Node 依赖压缩包")

    node_modules_dir = app_dir / "node_modules"
    if node_modules_dir.exists():
        shutil.rmtree(node_modules_dir)

    if progress_cb:
        progress_cb(50, 100, "正在解压 Node.js 依赖包到安装目录…")
    _extract_to_directory(node_modules_zip, app_dir, progress_cb)

    if not node_modules_dir.exists():
        raise FileNotFoundError("Node.js 依赖解压失败，未生成 node_modules 目录")

    if progress_cb:
        progress_cb(100, 100, "依赖安装完成")


def create_launcher_bat(target_root, python_dir, node_dir, app_dir):
    launcher = target_root / "ZeroListen.bat"
    content = (
        "@echo off\r\n"
        "setlocal\r\n"
        "set \"ROOT=%~dp0\"\r\n"
        "set \"PYTHON_DIR=%ROOT%\\.venv\"\r\n"
        "set \"NODE_DIR=%ROOT%\\node\"\r\n"
        "set \"APP_DIR=%ROOT%\\ZeroListen\"\r\n"
        "set \"PYTHON_EXE=%PYTHON_DIR%\\Scripts\\python.exe\"\r\n"
        "if not exist \"%PYTHON_EXE%\" set \"PYTHON_EXE=%APP_DIR%\\.venv\\Scripts\\python.exe\"\r\n"
        "if not exist \"%PYTHON_EXE%\" set \"PYTHON_EXE=%ROOT%\\ZeroListen\\.venv\\Scripts\\python.exe\"\r\n"
        "if not exist \"%PYTHON_EXE%\" (\r\n"
        "  echo No Python at '\"%PYTHON_EXE%\"'\r\n"
        "  exit /b 1\r\n"
        ")\r\n"
        "set \"PATH=%PYTHON_DIR%\\Scripts;%PYTHON_DIR%;%NODE_DIR%;%PATH%\"\r\n"
        "cd /d \"%APP_DIR%\"\r\n"
        "\"%PYTHON_EXE%\" \"%APP_DIR%\\main.py\"\r\n"
        "exit /b %ERRORLEVEL%\r\n"
    )
    launcher.write_text(content, encoding="utf-8")
    return launcher


def create_desktop_shortcut(launcher_path, icon_path):
    desktop = os.path.join(os.environ.get("USERPROFILE", ""), "Desktop")
    if not desktop:
        return None

    shortcut_path = os.path.join(desktop, "ZeroListen.lnk")
    vbs = f"""
    Set oWS = WScript.CreateObject("WScript.Shell")
    sLinkFile = "{shortcut_path}"
    Set oLink = oWS.CreateShortcut(sLinkFile)
    oLink.TargetPath = "{launcher_path}"
    oLink.WorkingDirectory = "{os.path.dirname(launcher_path)}"
    oLink.IconLocation = "{icon_path},0"
    oLink.Description = "ZeroListen"
    oLink.WindowStyle = 7
    oLink.Save
    """
    vbs_path = os.path.join(os.environ.get("TEMP", os.getcwd()), "create_zerolisten_shortcut.vbs")
    Path(vbs_path).write_text(vbs, encoding="utf-8")
    subprocess.run(["cscript.exe", "//nologo", vbs_path], check=False, shell=True)
    if Path(vbs_path).exists():
        try:
            Path(vbs_path).unlink()
        except Exception:
            pass
    return shortcut_path


def install_zero_listen(source_zip, install_root, progress_cb=None):
    if not is_windows():
        raise RuntimeError("当前安装器仅支持 Windows 系统")

    if source_zip is None or not source_zip.exists():
        raise FileNotFoundError("未找到源码压缩包。请把 src 源码压缩包与 installer.exe 放在同一目录。")

    install_root.mkdir(parents=True, exist_ok=True)
    app_dir = install_root / "ZeroListen"
    app_dir.mkdir(parents=True, exist_ok=True)

    if progress_cb:
        progress_cb(5, 100, "正在检测系统环境…")
    _ = detect_system()

    python_dir = ensure_python_install(install_root, progress_cb=lambda p, total, msg: progress_cb(p, total, msg) if progress_cb else None)
    node_dir = ensure_node_install(install_root, progress_cb=lambda p, total, msg: progress_cb(p, total, msg) if progress_cb else None)

    if progress_cb:
        progress_cb(35, 100, "正在解压源码到安装目录…")
    temp_extract_dir = install_root / "_tmp_src"
    if temp_extract_dir.exists():
        shutil.rmtree(temp_extract_dir)
    temp_extract_dir.mkdir(parents=True, exist_ok=True)
    _extract_to_directory(source_zip, temp_extract_dir, progress_cb)

    src_root = None
    for child in temp_extract_dir.iterdir():
        if child.is_dir() and (child.name.lower() == "src" or "zero" in child.name.lower()):
            src_root = child
            break
    if src_root is None:
        candidates = [p for p in temp_extract_dir.iterdir() if p.is_dir()]
        if candidates:
            src_root = candidates[0]
    if src_root is None:
        raise RuntimeError("源码压缩包内容结构不正确，找不到 src 目录")

    src_dir = src_root / "src" if (src_root / "src").exists() else src_root
    for item in src_dir.iterdir():
        dest = app_dir / item.name
        if item.is_dir():
            if item.name.lower() in {"node", "exports", "wordlibs"}:
                continue
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(item, dest, dirs_exist_ok=True)
        else:
            shutil.copy2(item, dest)

    if source_zip.exists():
        source_zip.unlink()
    if temp_extract_dir.exists():
        shutil.rmtree(temp_extract_dir)

    launcher = create_launcher_bat(install_root, python_dir, node_dir, app_dir)
    icon_path = APP_ROOT / "logo.ico"
    if not icon_path.exists():
        icon_path = APP_ROOT / "logo.png"
    if not icon_path.exists():
        icon_path = str(APP_ROOT / "logo.ico")
    create_desktop_shortcut(str(launcher), str(icon_path))

    install_dependencies(python_dir, node_dir, app_dir, progress_cb)
    return install_root, launcher


if wx is not None:
    class InstallerFrame(wx.Frame):
        def __init__(self):
            super().__init__(None, title="ZeroListen 安装", size=(760, 440))
            self.panel = wx.Panel(self)
            self.panel.SetBackgroundColour(wx.Colour(245, 245, 245))

            sizer = wx.BoxSizer(wx.VERTICAL)
            self.label = wx.StaticText(self.panel, label="ZeroListen 安装向导")
            self.label.SetFont(wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
            sizer.Add(self.label, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 20)

            self.info = wx.TextCtrl(self.panel, style=wx.TE_MULTILINE | wx.TE_READONLY)
            self.info.SetValue("安装流程：\n1. 检测系统版本并下载便携版 Python / Node.js\n2. 下载与安装所需依赖\n3. 解压源码到安装目录\n4. 创建启动脚本并发送桌面快捷方式")
            sizer.Add(self.info, 1, wx.EXPAND | wx.ALL, 10)

            self.progress = wx.Gauge(self.panel, id=wx.ID_ANY, range=100)
            self.progress.SetValue(0)
            sizer.Add(self.progress, 0, wx.EXPAND | wx.ALL, 10)

            btns = wx.BoxSizer(wx.HORIZONTAL)
            self.install_btn = wx.Button(self.panel, label="开始安装")
            self.cancel_btn = wx.Button(self.panel, label="退出")
            btns.Add(self.install_btn, 0, wx.ALL, 10)
            btns.Add(self.cancel_btn, 0, wx.ALL, 10)
            sizer.Add(btns, 0, wx.ALIGN_RIGHT | wx.RIGHT, 10)

            self.panel.SetSizer(sizer)

            self.install_btn.Bind(wx.EVT_BUTTON, self.on_install)
            self.cancel_btn.Bind(wx.EVT_BUTTON, lambda evt: self.Close())

        def on_install(self, _event):
            self.install_btn.Disable()
            self.cancel_btn.Disable()

            thread = threading.Thread(target=self._do_install, daemon=True)
            thread.start()

        def _do_install(self):
            try:
                source_zip = find_source_zip()
                if not source_zip:
                    raise FileNotFoundError("未找到源码压缩包，请确认与 installer.exe 同目录存在 zip 源码包")

                start_time = time.monotonic()

                def update(progress, total, message):
                    pct = int(progress * 100 / total) if total else 0
                    elapsed = max(time.monotonic() - start_time, 0.1)
                    if total and progress > 0:
                        remaining = max(total - progress, 0)
                        rate = progress / elapsed
                        eta_seconds = remaining / rate if rate > 0 else 0
                        hours, rem = divmod(int(eta_seconds), 3600)
                        minutes, seconds = divmod(rem, 60)
                        eta_text = f" | 预计剩余时间：{hours:02d}:{minutes:02d}:{seconds:02d}"
                    else:
                        eta_text = " | 预计剩余时间：计算中"
                    wx.CallAfter(self.progress.SetValue, pct)
                    wx.CallAfter(self.info.AppendText, f"\n[{pct}%] {message}{eta_text}")

                result = install_zero_listen(source_zip, INSTALL_ROOT, update)
                wx.CallAfter(self.progress.SetValue, 100)
                wx.CallAfter(self.info.AppendText, f"\n安装完成：{result[0]}\n启动脚本：{result[1]}\n快捷方式已创建到桌面。")
                wx.CallAfter(wx.MessageBox, "安装完成，ZeroListen 已成功安装并已创建桌面快捷方式。", "安装完成", wx.OK | wx.ICON_INFORMATION)
            except Exception as exc:
                wx.CallAfter(self.info.AppendText, f"\n安装失败：{exc}")
                wx.CallAfter(wx.MessageBox, f"安装失败：{exc}", "安装失败", wx.OK | wx.ICON_ERROR)
            finally:
                wx.CallAfter(self.install_btn.Enable)
                wx.CallAfter(self.cancel_btn.Enable)
else:
    class InstallerFrame:
        def __init__(self, *args, **kwargs):
            raise RuntimeError("wxPython 未安装，无法启动图形界面")


def main():
    if not is_windows():
        print("当前安装器仅支持 Windows。")
        input("按 Enter 退出...")
        return 1

    if wx is None:
        print("未检测到 wxPython，无法弹出安装界面。请先在 Python 3.11 环境中安装 wxPython 或使用带 wxPython 的打包环境。")
        input("按 Enter 退出...")
        return 1

    app = wx.App(False)
    frame = InstallerFrame()
    frame.Show()
    return app.MainLoop()


if __name__ == "__main__":
    raise SystemExit(main())
