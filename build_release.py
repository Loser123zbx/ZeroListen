import os
import shutil
import subprocess
import sys
from pathlib import Path

if sys.version_info < (3, 10):
    py_launcher = shutil.which("py")
    if py_launcher:
        os.execv(py_launcher, [py_launcher, "-3.11", __file__, *sys.argv[1:]])
    raise RuntimeError("当前脚本要求 Python 3.10+，请用 py -3.11 运行此脚本")

ROOT = Path(__file__).resolve().parent
SRC_DIR = ROOT / "src"
RELEASE_DIR = ROOT / "release"
PKG_DIR = RELEASE_DIR
EXE_NAME = "ZeroListen.exe"
APP_ENTRY = SRC_DIR / "main.py"
ICON_PATH = SRC_DIR / "logo.ico"
LOCK_PATH = ROOT / ".build_release.lock"


def _pid_is_alive(pid):
    if pid is None:
        return False
    try:
        pid = int(pid)
        if pid <= 0:
            return False
        os.kill(pid, 0)
        return True
    except Exception:
        return False


def acquire_single_instance():
    try:
        if LOCK_PATH.exists():
            pid_text = LOCK_PATH.read_text(encoding="utf-8").strip()
            if pid_text and pid_text.isdigit() and _pid_is_alive(pid_text):
                raise RuntimeError(f"已有另一个打包进程在运行，PID={pid_text}")
        LOCK_PATH.write_text(str(os.getpid()), encoding="utf-8")
        return True
    except RuntimeError:
        raise
    except Exception as exc:
        raise RuntimeError(f"无法获取打包锁: {exc}") from exc


def release_single_instance():
    try:
        if LOCK_PATH.exists():
            current_pid = LOCK_PATH.read_text(encoding="utf-8").strip()
            if current_pid and current_pid.isdigit() and int(current_pid) == os.getpid():
                LOCK_PATH.unlink()
    except Exception:
        pass


def _probe_python_version(python_exe):
    try:
        result = subprocess.run(
            [str(python_exe), "-c", "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            return None
        text = result.stdout.strip()
        if not text:
            return None
        parts = text.split(".")[:3]
        if len(parts) < 3:
            parts += ["0"] * (3 - len(parts))
        return tuple(int(p) for p in parts)
    except Exception:
        return None


def ensure_build_venv():
    venv_python = ROOT / ".venv" / "Scripts" / "python.exe"
    version = _probe_python_version(venv_python) if venv_python.exists() else None
    if version and version >= (3, 10):
        return venv_python

    if venv_python.exists():
        shutil.rmtree(ROOT / ".venv", ignore_errors=True)

    py_cmd = None
    if shutil.which("py"):
        py_cmd = ["py", "-3.11"]
    elif shutil.which("python3"):
        py_cmd = ["python3"]
    elif shutil.which("python"):
        py_cmd = ["python"]

    if py_cmd is None:
        raise RuntimeError("未找到可用的 Python 3.11+ 解释器，无法重建项目虚拟环境")

    cmd = py_cmd + ["-m", "venv", str(ROOT / ".venv")]
    print(f"[repair] 正在重建项目虚拟环境: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)

    rebuilt = ROOT / ".venv" / "Scripts" / "python.exe"
    if not rebuilt.exists():
        raise FileNotFoundError(f"重建后的 .venv 未生成: {rebuilt}")
    version = _probe_python_version(rebuilt)
    if not version or version < (3, 10):
        raise RuntimeError(f"重建后的 .venv 版本不满足 PyInstaller 需求: {version}")
    return rebuilt


def resolve_python_cmd():
    venv_python = ROOT / ".venv" / "Scripts" / "python.exe"
    if venv_python.exists():
        version = _probe_python_version(venv_python)
        if version and version >= (3, 10):
            return [str(venv_python)]

    if shutil.which("py"):
        return ["py", "-3.11"]
    if shutil.which("python3"):
        return ["python3"]
    if shutil.which("python"):
        return ["python"]
    raise RuntimeError("未找到可用的 Python 解释器")


def run(cmd, cwd=None, env=None):
    print("\n>>>", " ".join(cmd))
    final_env = os.environ.copy()
    if env:
        final_env.update(env)
    result = subprocess.run(cmd, cwd=str(cwd) if cwd else None, env=final_env)
    if result.returncode != 0:
        raise RuntimeError(f"命令失败: {' '.join(cmd)} (退出码={result.returncode})")


def ensure_pyinstaller():
    print("[1/4] 检查 PyInstaller...")
    py_cmd = resolve_python_cmd()
    venv_python = ROOT / ".venv" / "Scripts" / "python.exe"
    if venv_python.exists():
        venv_version = _probe_python_version(venv_python)
        if not venv_version or venv_version < (3, 10):
            ensure_build_venv()
            py_cmd = resolve_python_cmd()

    wheel_dir = SRC_DIR / "vendor" / "python_wheels"
    wx_wheel = next(iter(sorted(wheel_dir.glob("wxpython-*.whl"))), None)
    if wx_wheel is None:
        raise FileNotFoundError(f"未找到 wxPython 安装包，缺少: {wheel_dir} 中的 wxpython-*.whl")

    result = subprocess.run(py_cmd + ["-m", "pip", "show", "pyinstaller"], capture_output=True, text=True)
    if result.returncode != 0:
        install_attempts = [
            ["--index-url", "https://pypi.tuna.tsinghua.edu.cn/simple", "pyinstaller"],
            ["--index-url", "https://pypi.org/simple", "pyinstaller"],
            ["pyinstaller"],
        ]
        last_error = None
        for attempt in install_attempts:
            try:
                run(py_cmd + ["-m", "pip", "install", *attempt], cwd=ROOT)
                break
            except RuntimeError as exc:
                last_error = exc
                print(f"[warn] PyInstaller 安装尝试失败: {attempt} -> {exc}")
        else:
            raise last_error or RuntimeError("PyInstaller 安装失败")

    result = subprocess.run(py_cmd + ["-m", "pip", "show", "wxpython"], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[repair] 正在安装本地 wxPython 运行时依赖: {wx_wheel.parent}")
        run(py_cmd + ["-m", "pip", "install", "--no-index", "--find-links", str(wx_wheel.parent), "numpy", "wxpython", "openpyxl", "et_xmlfile"], cwd=ROOT)


def ensure_node_modules():
    node_modules_dir = SRC_DIR / "node_modules"
    if node_modules_dir.exists():
        return node_modules_dir

    candidates = [
        shutil.which("npm"),
        shutil.which("npm.cmd"),
        str(SRC_DIR / "node" / "npm.cmd"),
        str(SRC_DIR / "node" / "npm"),
        str(ROOT / "node" / "node-v24.21.0-win-x64" / "npm.cmd"),
        str(ROOT / "node" / "node-v24.21.0-win-x64" / "npm"),
    ]
    npm_cmd = next((c for c in candidates if c and os.path.exists(c)), None)
    if npm_cmd is None:
        raise RuntimeError("未找到 npm，可执行文件，无法安装项目依赖")

    node_dir = SRC_DIR / "node"
    env = os.environ.copy()
    path_value = env.get("PATH", "")
    env["PATH"] = str(node_dir) + os.pathsep + path_value if path_value else str(node_dir)
    run([npm_cmd, "install", "--prefix", str(SRC_DIR), "--no-fund", "--no-audit"], cwd=ROOT, env=env)

    if not node_modules_dir.exists():
        raise FileNotFoundError(f"未生成 node_modules 目录: {node_modules_dir}")
    return node_modules_dir


def copy_runtime_resources(target_dir):
    target_dir.mkdir(parents=True, exist_ok=True)
    for rel_name in ["tts_cli.js", "package.json", "config.json"]:
        src = SRC_DIR / rel_name
        if src.exists():
            shutil.copy2(src, target_dir / rel_name)

    for folder_name in ["wordlibs", "exports"]:
        src = SRC_DIR / folder_name
        if src.exists():
            dst = target_dir / folder_name
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)

    node_modules_dir = ensure_node_modules()
    dst_node_modules = target_dir / "node_modules"
    if dst_node_modules.exists():
        shutil.rmtree(dst_node_modules)
    shutil.copytree(node_modules_dir, dst_node_modules)

    node_dir = SRC_DIR / "node"
    if node_dir.exists():
        dst_node = target_dir / "node"
        if dst_node.exists():
            shutil.rmtree(dst_node)
        shutil.copytree(node_dir, dst_node)


def build_single_exe():
    print("[4/5] 打包 ZeroListen.exe...")
    RELEASE_DIR.mkdir(parents=True, exist_ok=True)

    spec_dir = ROOT / "_build_spec"
    work_dir = ROOT / "_build_work"
    if spec_dir.exists():
        shutil.rmtree(spec_dir)
    if work_dir.exists():
        shutil.rmtree(work_dir)

    py_cmd = resolve_python_cmd()
    cmd = py_cmd + [
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--onefile",
        "--windowed",
        "--name",
        "ZeroListen",
        "--distpath",
        str(PKG_DIR),
        "--workpath",
        str(work_dir),
        "--specpath",
        str(spec_dir),
    ]
    if ICON_PATH.exists():
        cmd += ["--icon", str(ICON_PATH)]
    cmd += [str(APP_ENTRY)]

    run(cmd, cwd=ROOT)

    exe_path = PKG_DIR / EXE_NAME
    if not exe_path.exists():
        raise FileNotFoundError(f"未找到生成的 exe: {exe_path}")

    copy_runtime_resources(PKG_DIR)

    if ICON_PATH.exists():
        shutil.copy2(ICON_PATH, PKG_DIR / ICON_PATH.name)


def print_summary():
    print("\n打包完成")
    print(f"输出目录: {PKG_DIR}")
    print(f"- {PKG_DIR / EXE_NAME}")
    print(f"- {PKG_DIR / 'node_modules'}")
    print(f"- {PKG_DIR / 'wordlibs'}")
    print(f"- {PKG_DIR / 'exports'}")
    if ICON_PATH.exists():
        print(f"- {PKG_DIR / ICON_PATH.name}")


def main():
    acquire_single_instance()
    print("开始打包实现：直接生成单文件 exe...")
    try:
        if not SRC_DIR.exists():
            raise FileNotFoundError(f"未找到 src 目录: {SRC_DIR}")
        if not APP_ENTRY.exists():
            raise FileNotFoundError(f"未找到程序入口文件: {APP_ENTRY}")

        print("[step1]创建输出目录...")
        RELEASE_DIR.mkdir(parents=True, exist_ok=True)
        print("[step2]检查 PyInstaller...")
        ensure_pyinstaller()
        print("[step3]安装项目 Node 依赖...")
        ensure_node_modules()
        print("[step4]打包单文件 exe...")
        build_single_exe()
        print("\n打包完成")
        print_summary()
    finally:
        release_single_instance()


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"\n打包失败: {exc}")
        raise
