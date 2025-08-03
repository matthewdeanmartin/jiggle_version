import os


def find_packages_recursively(start_dir: str) -> list[str]:
    """
    Walks a directory from a starting path and finds all packages.
    A package is any directory with an __init__.py file.
    This is a simplified replacement for setuptools.find_packages.
    """
    packages = []
    for root, dirs, files in os.walk(start_dir, topdown=True):
        # Prune common non-code directories to avoid walking them
        dirs[:] = [
            d
            for d in dirs
            if d
            not in (
                "tests",
                "test",
                "docs",
                "examples",
                ".git",
                ".tox",
                "venv",
                "__pycache__",
            )
            and not d.endswith(".egg-info")
        ]

        if "__init__.py" in files:
            # This directory is a package.
            relative_path = os.path.relpath(root, start_dir)
            if relative_path == ".":
                # This occurs if the start_dir itself is a package. We are
                # interested in the packages *within* it.
                continue

            package_name = relative_path.replace(os.sep, ".")
            packages.append(package_name)
    return packages
