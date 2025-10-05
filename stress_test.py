import platform
import shutil
import subprocess
import sys
import tempfile
import venv
from pathlib import Path


def get_site_packages_path() -> Path | None:
    """
    Finds the site-packages directory for the current Python environment.

    This is more robust than assuming a '.venv' folder structure.
    """
    # In a virtual environment, sys.prefix points to the venv directory
    if hasattr(sys, 'prefix'):
        if platform.system() == "Windows":
            return Path(sys.prefix) / "Lib" / "site-packages"
        else:
            # For Linux/macOS, the path can vary (e.g., lib/pythonX.Y/site-packages)
            # We can search for it to be more reliable.
            lib_dir = Path(sys.prefix) / "lib"
            if lib_dir.is_dir():
                site_packages_dirs = list(lib_dir.glob("python*/site-packages"))
                if site_packages_dirs:
                    return site_packages_dirs[0]

    # Fallback for other configurations, though less common for this script's purpose
    try:
        import site
        return Path(site.getsitepackages()[0])
    except (ImportError, IndexError):
        print("Could not automatically determine the site-packages directory.")
        return None


def run_jiggle_command(command: list[str]) -> tuple[bool, str, str]:
    """
    Runs a jiggle_version command as a subprocess and captures its output.

    Args:
        command: A list of strings representing the command and its arguments.

    Returns:
        A tuple containing:
        - bool: True if the command succeeded (exit code 0), False otherwise.
        - str: The captured standard output.
        - str: The captured standard error.
    """
    try:
        process = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,  # Don't raise an exception on non-zero exit codes
            encoding='utf-8',
            errors='replace'
        )
        success = process.returncode == 0
        print(process.stdout)
        print(process.stderr)
        return success, process.stdout, process.stderr
    except FileNotFoundError:
        msg = "Error: 'jiggle_version' command not found.\n" \
              "Please ensure that the tool is installed in your environment and that the\n" \
              "virtual environment's scripts directory is in your system's PATH."
        return False, "", msg
    except Exception as e:
        return False, "", f"An unexpected error occurred: {e}"


def try_out_package(package_path: Path) -> tuple[str, str, str | None]:
    """
    Tests a single package by running 'current' and 'bump' commands.

    Args:
        package_path: The path to the package directory to test.

    Returns:
        A tuple containing (status, details, error_output).
        - status: 'SUCCESS', 'CURRENT_FAIL', or 'BUMP_FAIL'.
        - details: A summary of what was attempted.
        - error_output: The stderr content if a command failed.
    """
    package_name = package_path.name
    print(f"--- Testing Package: {package_name} ---")

    # 1. Test the 'current' command on the original directory
    print(f"  -> Running 'current' command...")
    current_command = ["uv", "run", "jiggle_version","current", str(package_path)]

    success, stdout, stderr = run_jiggle_command(current_command)

    if not success:
        details = f"Failed to find version in '{package_name}'."
        print(f"  [FAIL] 'current' command failed.")
        return "CURRENT_FAIL", details, stderr

    print(f"  [OK] 'current' command succeeded. Found version info:\n{stdout.strip()}")

    # 2. Test the 'bump' command in a temporary, isolated directory
    print(f"  -> Running 'bump' command in a temporary directory...")
    with tempfile.TemporaryDirectory(prefix=f"jiggle-test-{package_name}-") as temp_dir_str:
        temp_dir = Path(temp_dir_str)

        # Copy the package to the temporary directory to avoid modifying the venv
        try:
            shutil.copytree(package_path, temp_dir, dirs_exist_ok=True)
        except Exception as e:
            details = f"Failed to copy '{package_name}' to a temporary directory."
            print(f"  [FAIL] Could not prepare for bump test.")
            return "BUMP_FAIL", details, str(e)

        bump_command = ["jiggle_version", "bump", "package", str(temp_dir), "--init"]
        success, stdout, stderr = run_jiggle_command(bump_command)

        if not success:
            details = f"Failed to bump version for '{package_name}' in isolated test."
            print(f"  [FAIL] 'bump' command failed.")
            return "BUMP_FAIL", details, stderr

    print(f"  [OK] 'bump' command succeeded.")
    return "SUCCESS", f"Successfully processed '{package_name}'.", None


def main():
    """
    Main function to orchestrate the integration test.
    """
    print("Starting Jiggle Version Integration Test...")

    site_packages = get_site_packages_path()
    if not site_packages or not site_packages.is_dir():
        print(f"Error: site-packages directory not found or is not a directory.")
        sys.exit(1)

    print(f"Found site-packages at: {site_packages}\n")

    # Find all top-level directories in site-packages that are likely packages
    # Excludes .dist-info, .egg-info, and private directories like __pycache__
    packages_to_test = [
        p for p in site_packages.iterdir()
        if p.is_dir() and not p.name.startswith('_') and not p.name.endswith(('.dist-info', '.egg-info'))
    ]

    if not packages_to_test:
        print("No packages found to test in the site-packages directory.")
        sys.exit(0)

    print(f"Found {len(packages_to_test)} potential packages to test.\n")

    results = {
        "SUCCESS": [],
        "CURRENT_FAIL": [],
        "BUMP_FAIL": [],
    }
    errors = {}

    for package_path in packages_to_test:
        status, details, error_output = try_out_package(package_path)
        results[status].append(package_path.name)
        if error_output:
            errors[package_path.name] = error_output
        print("-" * (len(package_path.name) + 22))
        print("\n")

    # --- Final Report ---
    print("\n" + "=" * 50)
    print("Integration Test Report")
    print("=" * 50)
    print(f"Total Packages Tested: {len(packages_to_test)}")

    print(f"\n✅ Successful ({len(results['SUCCESS'])} packages):")
    if results['SUCCESS']:
        for pkg in sorted(results['SUCCESS']):
            print(f"  - {pkg}")
    else:
        print("  None")

    print(f"\n❌ Failed on 'current' ({len(results['CURRENT_FAIL'])} packages):")
    if results['CURRENT_FAIL']:
        for pkg in sorted(results['CURRENT_FAIL']):
            print(f"  - {pkg}")
    else:
        print("  None")

    print(f"\n❌ Failed on 'bump' ({len(results['BUMP_FAIL'])} packages):")
    if results['BUMP_FAIL']:
        for pkg in sorted(results['BUMP_FAIL']):
            print(f"  - {pkg}")
    else:
        print("  None")

    if errors:
        print("\n" + "=" * 50)
        print("Error Details")
        print("=" * 50)
        all_failed = sorted(results['CURRENT_FAIL'] + results['BUMP_FAIL'])
        for pkg_name in all_failed:
            print(f"\n--- Errors for: {pkg_name} ---")
            print(errors.get(pkg_name, "No error output captured.").strip())
            print("-" * (18 + len(pkg_name)))


if __name__ == "__main__":
    main()
