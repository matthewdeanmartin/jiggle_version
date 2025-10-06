# jiggle_version/parsers/ast_parsers.py
"""
Parsers for Python source files using the `ast` module.
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path


class SetupCallVisitor(ast.NodeVisitor):
    """
    An AST visitor that looks for a `setup()` call and extracts literal keyword arguments.
    """

    def __init__(self):
        self.version: str | None = None

    def visit_Call(self, node: ast.Call):
        """Visit a Call node in the AST."""
        # Check if the function being called is `setup`
        is_setup_call = False
        if isinstance(node.func, ast.Name) and node.func.id == "setup":
            is_setup_call = True
        elif isinstance(node.func, ast.Attribute) and node.func.attr == "setup":
            # This handles cases like `setuptools.setup()`
            is_setup_call = True

        if is_setup_call:
            # Find the 'version' keyword argument
            for keyword in node.keywords:
                if keyword.arg == "version":
                    try:
                        # ast.literal_eval is a safe way to get the value of a
                        # node, but it only works for literals (strings, numbers, etc.)
                        # If the version is a variable, this will raise an error.
                        self.version = ast.literal_eval(keyword.value)
                    except ValueError:
                        # The version is not a literal, so we ignore it per the PEP.
                        print(
                            "Warning: Could not statically parse 'version' in setup.py; it is not a literal."
                        )
                    # We found the version keyword, no need to check others
                    break

        # Continue traversing the tree
        self.generic_visit(node)


class VersionVisitor(ast.NodeVisitor):
    """
    An AST visitor that looks for a `__version__ = "..."` assignment.
    """

    def __init__(self):
        self.version: str | None = None

    def visit_Assign(self, node: ast.Assign):
        """Visit an assignment node."""
        # We are looking for a simple assignment: `__version__ = "..."`
        # We only consider assignments with a single target.
        if len(node.targets) == 1:
            target = node.targets[0]
            # Check if the target is a Name node with the id `__version__`
            if isinstance(target, ast.Name) and target.id == "__version__":
                try:
                    self.version = ast.literal_eval(node.value)
                except ValueError:
                    print(
                        "Warning: Found `__version__` but its value was not a literal."
                    )
        self.generic_visit(node)


class AllVisitor(ast.NodeVisitor):
    """An AST visitor that looks for `__all__ = [...]` assignments."""

    def __init__(self):
        self.symbols: set[str] = set()

    def visit_Assign(self, node: ast.Assign):
        if len(node.targets) == 1:
            target = node.targets[0]
            if isinstance(target, ast.Name) and target.id == "__all__":
                try:
                    # Safely evaluate the list/tuple of strings
                    value = ast.literal_eval(node.value)
                    if isinstance(value, (list, tuple)):
                        self.symbols.update(str(s) for s in value)
                except ValueError:
                    print(
                        "Warning: Found `__all__` but its value was not a literal list/tuple."
                    )
        self.generic_visit(node)


def parse_setup_py(file_path: Path) -> str | None:
    """
    Finds and returns the version string from a setup.py file using AST.

    Args:
        file_path: The path to the setup.py file.

    Returns:
        The version string if found as a literal, otherwise None.
    """
    if not file_path.is_file():
        return None

    try:
        source_code = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source_code, filename=str(file_path))

        visitor = SetupCallVisitor()
        visitor.visit(tree)

        return visitor.version
    except (SyntaxError, ValueError) as e:
        print(f"Warning: Could not parse '{file_path}'. Error: {e}", file=sys.stderr)
        return None


def parse_python_module(file_path: Path) -> str | None:
    """
    Finds and returns a `__version__` string from a Python module using AST.

    Args:
        file_path: The path to the Python module file.

    Returns:
        The version string if found as a literal, otherwise None.
    """
    if not file_path.is_file():
        return None

    try:
        source_code = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source_code, filename=str(file_path))

        visitor = VersionVisitor()
        visitor.visit(tree)

        return visitor.version
    except (SyntaxError, ValueError) as e:
        print(f"Warning: Could not parse '{file_path}'. Error: {e}", file=sys.stderr)
        return None


def parse_dunder_all(file_path: Path) -> set[str]:
    """
    Finds and returns a set of symbols from `__all__` in a Python module.
    """
    if not file_path.is_file():
        return set()

    try:
        source_code = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source_code, filename=str(file_path))
        visitor = AllVisitor()
        visitor.visit(tree)
        return visitor.symbols
    except (SyntaxError, ValueError):
        # Ignore files that can't be parsed
        return set()
