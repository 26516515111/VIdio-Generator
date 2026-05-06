import subprocess
import sys
from pathlib import Path


def build_frontend():
    """构建前端"""
    print("Building frontend...")
    frontend_dir = Path(__file__).parent.parent / "frontend"

    if not frontend_dir.exists():
        print(f"Warning: Frontend directory not found at {frontend_dir}")
        print("Skipping frontend build.")
        return False

    # 安装依赖
    subprocess.run(["npm", "install"], cwd=frontend_dir, check=True)

    # 构建
    subprocess.run(["npm", "run", "build"], cwd=frontend_dir, check=True)

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
