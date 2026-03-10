import os
import shutil
import sys
import subprocess
import platform

VENV_DIR = ".venv"

REQUIRED_MAJOR = 3
REQUIRED_MINOR = 10
MAX_WINDOWS_MAJOR = 3
MAX_WINDOWS_MINOR = 13


def is_windows():
    return platform.system().lower().startswith("win")


def venv_python():
    return os.path.join(
        VENV_DIR,
        "Scripts" if is_windows() else "bin",
        "python.exe" if is_windows() else "python"
    )


def install_requirements():
    requirements = "requirements.txt"
    if not os.path.exists(requirements):
        print("requirements.txt not found — skipping dependency installation.")
        return

    print("Installing dependencies...")
    subprocess.check_call([venv_python(), "-m", "pip", "install", "-r", "requirements.txt"])
    print("Dependencies installed")


def create_venv():
    print("Creating virtual environment...")
    subprocess.check_call([sys.executable, "-m", "venv", VENV_DIR])
    print("Virtual environment created")


def main():
    if (sys.version_info.major, sys.version_info.minor) < (REQUIRED_MAJOR, REQUIRED_MINOR):
        print(f"Error: needed Python {REQUIRED_MAJOR}.{REQUIRED_MINOR}+")
        print(f"Your version: Python {sys.version.split()[0]}")
        sys.exit(1)

    if is_windows() and (sys.version_info.major, sys.version_info.minor) > (MAX_WINDOWS_MAJOR, MAX_WINDOWS_MINOR):
        print(f"Error: max version Windows Python {MAX_WINDOWS_MAJOR}.{MAX_WINDOWS_MINOR}")
        print(f"Your version: Python {sys.version.split()[0]}")
        sys.exit(1)

    if os.path.isdir(VENV_DIR):
        shutil.rmtree(VENV_DIR)

    create_venv()
    install_requirements()

    print("\nEnvironment ready")
    print("To run the project:")

    if is_windows():
        print("\033[32m.venv\\Scripts\\python3.exe main.py or .\.venv\Scripts\\activate\033[0m")
    else:
        print("\033[32m.venv/bin/python3 main.py\033[0m")

if __name__ == "__main__":
    main()