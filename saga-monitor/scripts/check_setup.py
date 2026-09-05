from __future__ import annotations

import platform
import shutil
import subprocess
import sys
from importlib.metadata import version
from pathlib import Path


# ============================================================
# Configuration
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROJECT_NAME = PROJECT_ROOT.name


# ============================================================
# Output helpers
# ============================================================

def section(title: str) -> None:
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


def success(message: str) -> None:
    print(f"[✓] {message}")


def warning(message: str) -> None:
    print(f"[!] {message}")


def failure(message: str) -> None:
    print(f"[✗] {message}")


def info(message: str) -> None:
    print(f"[→] {message}")


# ============================================================
# Command helper
# ============================================================

def run_command(
    command: list[str],
    cwd: Path | None = None,
) -> tuple[int, str, str]:
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=30,
        )

        return (
            result.returncode,
            result.stdout.strip(),
            result.stderr.strip(),
        )

    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        return 1, "", str(exc)


# ============================================================
# Python
# ============================================================

def check_python_version() -> bool:
    section("Python")

    v = sys.version_info

    print(f"Python version: {v.major}.{v.minor}.{v.micro}")

    if v >= (3, 13):
        success("Python 3.13+ detected")
        return True

    failure("Python 3.13+ is required")
    return False


# ============================================================
# Virtual environment
# ============================================================

def check_virtual_environment() -> bool:
    section("Virtual Environment")

    venv_path = PROJECT_ROOT / ".venv"

    if not venv_path.exists():
        failure(".venv directory does not exist")
        info("Create it with:")
        info("  python -m venv .venv")
        return False

    success(".venv directory exists")

    current_python = Path(sys.executable).resolve()

    try:
        current_python.relative_to(venv_path.resolve())
        success("Current Python is running from this project's .venv")
        return True

    except ValueError:
        warning("Current Python is NOT running from this project's .venv")
        info("Activate it with:")
        info(r"  .\.venv\Scripts\Activate.ps1")
        return False


def check_python_executable() -> bool:
    section("Python Executable")

    expected = PROJECT_ROOT / ".venv" / "Scripts" / "python.exe"

    if not expected.exists():
        failure("Virtual-environment Python executable not found")
        info(str(expected))
        return False

    success("Virtual-environment Python executable exists")
    info(str(expected))

    return True


# ============================================================
# pip
# ============================================================

def check_pip() -> bool:
    section("pip")

    code, stdout, stderr = run_command(
        [sys.executable, "-m", "pip", "--version"],
        cwd=PROJECT_ROOT,
    )

    if code == 0:
        success(f"pip detected: {stdout}")
        return True

    failure("pip could not be executed")

    if stderr:
        info(stderr)

    return False


# ============================================================
# Project structure
# ============================================================

def check_project_structure() -> bool:
    section("Project Structure")

    required_paths = {
        "Project root": PROJECT_ROOT,
        ".venv directory": PROJECT_ROOT / ".venv",
        "scripts directory": PROJECT_ROOT / "scripts",
        "check_setup.py": PROJECT_ROOT / "scripts" / "check_setup.py",
        ".gitignore": PROJECT_ROOT / ".gitignore",
        "LICENSE": PROJECT_ROOT / "LICENSE",
        "README.md": PROJECT_ROOT / "README.md",
    }

    all_ok = True

    for name, path in required_paths.items():
        if path.exists():
            success(f"{name} exists")
        else:
            failure(f"{name} is missing")
            all_ok = False

    return all_ok


# ============================================================
# Python packages
# ============================================================

def check_python_package(
    package_name: str,
    display_name: str | None = None,
) -> bool:

    display_name = display_name or package_name

    try:
        package_version = version(package_name)
        success(
            f"{display_name} installed: "
            f"{package_version}"
        )
        return True

    except Exception:
        failure(f"{display_name} is not installed")
        info(f"Install with:")
        info(f"  python -m pip install {package_name}")
        return False


# ============================================================
# Playwright
# ============================================================

def check_playwright() -> bool:
    section("Playwright")

    package_ok = check_python_package(
        "playwright",
        "Playwright",
    )

    if not package_ok:
        return False

    test_script = """
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("about:blank")
    browser.close()
"""

    code, stdout, stderr = run_command(
        [sys.executable, "-c", test_script],
        cwd=PROJECT_ROOT,
    )

    if code == 0:
        success("Playwright Chromium launches successfully")
        return True

    failure("Playwright Chromium could not be launched")

    if stderr:
        print(stderr)

    info("Install Chromium with:")
    info("  python -m playwright install chromium")

    return False


# ============================================================
# Git
# ============================================================

def check_git() -> bool:
    section("Git")

    if shutil.which("git") is None:
        failure("Git is not installed or not available in PATH")
        return False

    code, stdout, stderr = run_command(
        ["git", "--version"],
        cwd=PROJECT_ROOT,
    )

    if code == 0:
        success(f"Git detected: {stdout}")
        return True

    failure("Git was found but could not be executed")

    if stderr:
        info(stderr)

    return False


def find_git_root() -> Path | None:
    """
    Find the Git repository containing this project.

    This intentionally allows saga-monitor to be a project
    inside a larger Git repository.
    """

    if shutil.which("git") is None:
        return None

    code, stdout, _ = run_command(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=PROJECT_ROOT,
    )

    if code != 0 or not stdout:
        return None

    return Path(stdout).resolve()


def check_git_repository() -> bool:
    section("Git Repository")

    git_root = find_git_root()

    if git_root is None:
        failure("No Git repository found")
        info("The project should be inside a Git repository.")
        return False

    project_root = PROJECT_ROOT.resolve()

    if git_root == project_root:
        success("saga-monitor is a Git repository")
        info(f"Repository root: {git_root}")
        return True

    # saga-monitor is intentionally a project inside another
    # repository. This is valid and therefore NOT a warning.
    try:
        project_root.relative_to(git_root)

        success("Git repository detected")
        info(f"Repository root: {git_root}")
        info(f"Project root:    {project_root}")
        info("saga-monitor is a project inside this repository")

        return True

    except ValueError:
        failure("Could not determine Git repository relationship")
        return False


# ============================================================
# SAGA connectivity
# ============================================================

def check_saga_direct_http() -> bool:
    section("SAGA Connectivity")

    import urllib.error
    import urllib.request

    url = (
        "https://www.saga.hamburg/"
        "immobiliensuche?Kategorie=APARTMENT"
    )

    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/140.0 Safari/537.36"
            )
        },
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=15,
        ) as response:

            status = response.status

            if 200 <= status < 300:
                success(
                    f"SAGA direct HTTP request succeeded "
                    f"(HTTP {status})"
                )
                return True

            warning(
                f"SAGA returned HTTP {status} "
                "for direct HTTP access"
            )

            return True

    except urllib.error.HTTPError as exc:

        if exc.code in (401, 403, 429):
            warning(
                f"SAGA returned HTTP {exc.code} "
                "for direct HTTP access"
            )

            info(
                "This is not considered an installation failure."
            )

            info(
                "The monitor will use Playwright/Chromium."
            )

            return True

        failure(
            f"SAGA returned unexpected HTTP error: "
            f"{exc.code}"
        )

        return False

    except Exception as exc:
        warning(f"Could not directly connect to SAGA: {exc}")
        info(
            "This does not necessarily mean Playwright will fail."
        )

        return True


# ============================================================
# Environment information
# ============================================================

def show_environment() -> None:
    section("Environment")

    print(f"Project:      {PROJECT_NAME}")
    print(f"Project root: {PROJECT_ROOT}")
    print(f"OS:           {platform.system()} {platform.release()}")
    print(f"Architecture: {platform.machine()}")
    print(f"Python:       {sys.executable}")


# ============================================================
# Main
# ============================================================

def main() -> int:

    print()
    print("=" * 70)
    print("SAGA MONITOR - SETUP CHECK")
    print("=" * 70)

    show_environment()

    results = [
        check_python_version(),
        check_virtual_environment(),
        check_python_executable(),
        check_pip(),
        check_project_structure(),
        check_playwright(),
        check_git(),
        check_git_repository(),
        check_saga_direct_http(),
    ]

    section("Summary")

    failures = sum(not result for result in results)

    if failures == 0:
        success("All setup checks passed!")
        print()
        info("The development environment is ready.")
        return 0

    failure(f"{failures} check(s) failed or need attention.")

    return 1


if __name__ == "__main__":
    raise SystemExit(main())