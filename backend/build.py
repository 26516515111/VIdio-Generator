import os
import subprocess
import sys
import shutil
from pathlib import Path


def find_npm():
    """查找 npm 可执行文件路径"""
    # 1. 检查环境变量
    npm_path = os.environ.get("NPM_PATH")
    if npm_path and Path(npm_path).exists():
        return npm_path

    # 2. 从 PATH 中查找
    npm_in_path = shutil.which("npm")
    if npm_in_path:
        return npm_in_path

    # 3. 常见安装路径
    common_paths = [
        r"C:\Program Files\nodejs\npm.cmd",
        r"C:\Program Files (x86)\nodejs\npm.cmd",
        Path.home() / "AppData" / "Roaming" / "npm" / "npm.cmd",
    ]
    for path in common_paths:
        if Path(path).exists():
            return str(path)

    return None


def build_frontend():
    """构建前端"""
    print("Building frontend...")
    frontend_dir = Path(__file__).parent.parent / "frontend"

    if not frontend_dir.exists():
        print(f"Warning: Frontend directory not found at {frontend_dir}")
        print("Skipping frontend build.")
        return False

    # 查找 npm
    npm_cmd = find_npm()
    if not npm_cmd:
        print("\n❌ Error: npm not found!")
        print("\nPlease ensure Node.js is installed and one of the following:")
        print("  1. Add Node.js to your PATH environment variable")
        print("  2. Set NPM_PATH environment variable to your npm.cmd path")
        print("     Example: set NPM_PATH=C:\\Program Files\\nodejs\\npm.cmd")
        print("\nDownload Node.js from: https://nodejs.org/")
        return False

    print(f"Using npm: {npm_cmd}")

    # 安装依赖
    subprocess.run([npm_cmd, "install"], cwd=frontend_dir, check=True)

    # 构建
    subprocess.run([npm_cmd, "run", "build"], cwd=frontend_dir, check=True)

    print("Frontend built successfully!")
    return True


def build_backend():
    """构建后端"""
    print("Building backend...")
    backend_dir = Path(__file__).parent

    # 安装依赖
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
        cwd=backend_dir,
        check=True,
    )

    # 使用PyInstaller打包
    subprocess.run(
        [sys.executable, "-m", "PyInstaller", "pyinstaller.spec", "--clean"],
        cwd=backend_dir,
        check=True,
    )

    print("Backend built successfully!")


def main():
    """主构建流程"""
    try:
        frontend_ok = build_frontend()
        build_backend()
        print("\n✅ Build completed successfully!")
        if frontend_ok:
            print("Executable: backend/dist/语音转换助手.exe")
        else:
            print("Note: Frontend was not built. The executable may not serve the UI.")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Build failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
