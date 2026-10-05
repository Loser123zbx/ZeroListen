import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC_DIR = ROOT / "src"
RELEASE_DIR = ROOT / "release"
PKG_DIR = RELEASE_DIR / "ZeroListen_Installer"
EXE_NAME = "installer.exe"
ZIP_NAME = "src.zip"
VENV_ZIP_NAME = ".venv.zip"
ICON_PATH = SRC_DIR / "logo.ico"


def resolve_python_cmd():
    venv_python = ROOT / ".venv" / "Scripts" / "python.exe"
    if venv_python.exists():
        return [str(venv_python)]
    sys_python = Path(sys.executable)
    if sys_python.exists():
        return [str(sys_python)]
    if shutil.which("py"):
        return ["py", "-3"]
    if shutil.which("python"):
        return ["python"]
    raise RuntimeError("未找到可用的 Python 解释器")


EXCLUDED_DIRS = {
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "release",
    "node",
    "vendor",
    "exports",
    "wordlibs",
    "wxProjects",
}


def bundle_python_venv():
    print("[2/5] 打包当前 Python 虚拟环境到 .venv.zip...")
    venv_dir = ROOT / ".venv"
    if not venv_dir.exists():
        raise FileNotFoundError(f"未找到当前 Python 虚拟环境: {venv_dir}")

    target_zip = PKG_DIR / VENV_ZIP_NAME
    if target_zip.exists():
        target_zip.unlink()

    with zipfile.ZipFile(target_zip, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for file_path in sorted(venv_dir.rglob("*")):
            if file_path.is_dir():
                continue
            rel = file_path.relative_to(venv_dir.parent)
            arcname = rel.as_posix()
            zf.write(file_path, arcname)

    if not target_zip.exists():
        raise FileNotFoundError(f"未生成虚拟环境压缩包: {target_zip}")


def bundle_node_dependencies():
    print("[3/5] 打包 npm 依赖到 src.zip...")
    candidates = [
        shutil.which("npm"),
        shutil.which("npm.cmd"),
        str(ROOT / "src" / "node" / "npm.cmd"),
        str(ROOT / "src" / "node" / "npm"),
        str(ROOT / "node" / "node-v24.21.0-win-x64" / "npm.cmd"),
        str(ROOT / "node" / "node-v24.21.0-win-x64" / "npm"),
    ]
    npm_cmd = next((c for c in candidates if c and os.path.exists(c)), None)
    if npm_cmd is None:
        raise RuntimeError("未找到 npm，可执行文件，无法打包前端依赖")

    node_modules_dir = SRC_DIR / "node_modules"
    if node_modules_dir.exists():
        shutil.rmtree(node_modules_dir)
    node_dir = SRC_DIR / "node"
    env = os.environ.copy()
    path_value = env.get("PATH", "")
    env["PATH"] = str(node_dir) + os.pathsep + path_value if path_value else str(node_dir)
    run([npm_cmd, "install", "--prefix", str(SRC_DIR), "--no-fund", "--no-audit"], cwd=ROOT, env=env)
    if not node_modules_dir.exists():
        raise FileNotFoundError(f"未生成 npm 依赖目录: {node_modules_dir}")

    return node_modules_dir


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
    result = subprocess.run(py_cmd + ["-m", "pip", "show", "pyinstaller"], capture_output=True, text=True)
    if result.returncode != 0:
        run(py_cmd + ["-m", "pip", "install", "--index-url", "https://pypi.tuna.tsinghua.edu.cn/simple", "pyinstaller"], cwd=ROOT)


def build_installer_exe():
    print("[4/5] 打包 installer.exe...")
    if PKG_DIR.exists():
        shutil.rmtree(PKG_DIR)
    PKG_DIR.mkdir(parents=True, exist_ok=True)

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
        "--name",
        "installer",
        "--distpath",
        str(PKG_DIR),
        "--workpath",
        str(work_dir),
        "--specpath",
        str(spec_dir),
    ]
    if ICON_PATH.exists():
        cmd += ["--icon", str(ICON_PATH)]
    cmd += [str(SRC_DIR / "installer.py")]

    run(cmd, cwd=ROOT)

    exe_path = PKG_DIR / EXE_NAME
    if not exe_path.exists():
        raise FileNotFoundError(f"未找到生成的 exe: {exe_path}")

    if ICON_PATH.exists():
        shutil.copy2(ICON_PATH, PKG_DIR / ICON_PATH.name)


def build_source_zip():
    print("[5/5] 打包 src.zip...")
    zip_path = PKG_DIR / ZIP_NAME

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        src_root_name = "src"
        for item in sorted(SRC_DIR.iterdir(), key=lambda p: p.name.lower()):
            name = item.name
            if name in EXCLUDED_DIRS:
                continue
            if item.is_dir():
                for file_path in sorted(item.rglob("*")):
                    if file_path.is_dir():
                        continue
                    rel = file_path.relative_to(SRC_DIR)
                    zf.write(file_path, f"{src_root_name}/{rel.as_posix()}")
            else:
                zf.write(item, f"{src_root_name}/{name}")

    if not zip_path.exists():
        raise FileNotFoundError(f"未生成 zip: {zip_path}")


def print_summary():
    print("\n打包完成")
    print(f"输出目录: {PKG_DIR}")
    print(f"- {PKG_DIR / EXE_NAME}")
    print(f"- {PKG_DIR / VENV_ZIP_NAME}")
    print(f"- {PKG_DIR / ZIP_NAME}")
    if ICON_PATH.exists():
        print(f"- {PKG_DIR / ICON_PATH.name}")


def main():
    if not SRC_DIR.exists():
        raise FileNotFoundError(f"未找到 src 目录: {SRC_DIR}")
    if not (SRC_DIR / "installer.py").exists():
        raise FileNotFoundError(f"未找到安装器入口文件: {SRC_DIR / 'installer.py'}")

    RELEASE_DIR.mkdir(parents=True, exist_ok=True)
    ensure_pyinstaller()
    bundle_python_venv()
    bundle_node_dependencies()
    build_installer_exe()
    build_source_zip()
    print_summary()


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"\n打包失败: {exc}")
        raise
