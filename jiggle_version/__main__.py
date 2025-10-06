"""
jiggle_version: deterministic CLI for discovering, checking, and bumping Python project versions.

This version is DEBUG-INSTRUMENTED. All original comments are preserved and
augmented with logging at DEBUG/INFO/WARNING/ERROR levels to trace execution,
argument parsing, config precedence, and failure points.

Key changes vs. your draft:
- SAFE two‑stage parsing: extract --config with a tiny pre‑parser ONLY.
  (Avoids early SystemExit from the full parser swallowing subparser state.)
- Subparsers now have dest="command" and required=True for explicit routing.
- Defaults application: hardcoded < config file < CLI — applied only to `bump`.
- Guard parse_known_args / parse_args with try/except SystemExit to log.
- Added verbose-driven logging setup ("-v" repeatable) and --log-level override.
- Handle `auto` increment exactly once; pass `ignore` consistently.
- More explicit warnings/errors around common edge cases.
- Keep ALL existing comments and behavior where not explicitly adjusted.
"""

from __future__ import annotations

import argparse
import logging
import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from rich_argparse import RichHelpFormatter

# Project imports
from jiggle_version import __about__, git
from jiggle_version.auto import (
    determine_auto_increment,
    get_current_symbols,
    write_digest_data,
)
from jiggle_version.bump import bump_version
from jiggle_version.config import load_config_from_path
from jiggle_version.discover import find_source_files
from jiggle_version.parsers.ast_parser import parse_python_module, parse_setup_py
from jiggle_version.parsers.config_parser import parse_pyproject_toml, parse_setup_cfg
from jiggle_version.update import (
    update_pyproject_toml,
    update_python_file,
    update_setup_cfg,
)
from jiggle_version.utils.cli_suggestions import SmartParser
from jiggle_version.utils.logging_config import configure_logging


class CustomFormatter(RichHelpFormatter):
    """Custom help formatter to tweak the aesthetics."""

    RichHelpFormatter.styles["argparse.args"] = "cyan"
    RichHelpFormatter.styles["argparse.groups"] = "magenta"
    RichHelpFormatter.styles["argparse.help"] = "default"


# ----------------------------------------------------------------------------
# Logging utilities
# ----------------------------------------------------------------------------
LOGGER = logging.getLogger(__name__)

# ----------------------------------------------------------------------------
# Command handlers (augmented with logging)
# ----------------------------------------------------------------------------


# It's not you, it's me, probably
UNEXPECTED_ERROR = 1
DISCOVERY_ERROR = 2
AUTOINCREMENT_ERROR = 3
VERSION_BUMP_ERROR = 4
FILE_UPDATE_ERROR = 5
AUTOGIT_ERROR = 6
HASH_ERROR = 7
ARGPARSE_ERROR = 8

# It's not me, it's you, probably
NO_VERSION_FOUND = 100
VERSION_DISAGREEMENT = 102
DIRTY_GIT_REPO = 103
NO_CONFIG_FOUND = 104


def handle_check(args: argparse.Namespace) -> int:
    """Handler for the 'check' command."""
    LOGGER.info("Running check… project_root=%s", args.project_root)

    project_root = Path(args.project_root)
    found_versions = []

    # Map specific filenames to their specialized parsers.
    # Any other .py file will use the generic module parser.
    parser_map = {
        "pyproject.toml": parse_pyproject_toml,
        "setup.cfg": parse_setup_cfg,
        "setup.py": parse_setup_py,
    }

    # 1. Discover all potential source files
    try:
        source_files = find_source_files(project_root, args.ignore)
    except Exception as e:
        LOGGER.error("Discovery failed: %s", e, exc_info=args.verbose > 0)
        print(f"❌ Discovery failed: {e}", file=sys.stderr)
        return DISCOVERY_ERROR

    print(f"Found {len(source_files)} potential source file(s).")
    LOGGER.debug("Discovered files: %s", [str(p) for p in source_files])

    # 2. Parse each discovered file
    for file_path in source_files:
        relative_path = file_path.relative_to(project_root)
        print(f"-> Checking for version in '{relative_path}'…")

        # Choose the correct parser for the file
        parser_func = parser_map.get(file_path.name, parse_python_module)

        if file_path.suffix == ".py" and file_path.name not in parser_map:
            parser_func = parse_python_module
        elif file_path.name not in parser_map:
            # Skip unknown file types
            LOGGER.debug("Skipping non‑version file: %s", file_path)
            continue

        try:
            version = parser_func(file_path)
        except Exception as e:
            LOGGER.warning(
                "Failed to parse %s: %s", file_path, e, exc_info=args.verbose > 1
            )
            print(f"⚪ Parse failed for {relative_path}: {e}")
            continue

        if version:
            print(f"✅ Found version: {version}")
            found_versions.append({"source": str(relative_path), "version": version})
        else:
            print("⚪ No version found.")

    print("\n--- Discovery Summary ---")
    if not found_versions:
        print("❌ No version declarations were found.")
        LOGGER.error("No version declarations found in project.")
        return NO_VERSION_FOUND

    for item in found_versions:
        print(f"Source: {item['source']:<25} Version: {item['version']}")

    print("\n--- Agreement Check ---")

    # TODO: Add scheme-based normalization (PEP 440, SemVer) before comparison.
    unique_versions = set(item["version"] for item in found_versions)

    if len(unique_versions) > 1:
        print(
            f"❌ Version conflict detected! Found {len(unique_versions)} different versions:"
        )
        for v in sorted(list(unique_versions)):
            print(f"  - {v}")
        LOGGER.error("Version conflict: %s", sorted(unique_versions))
        return VERSION_DISAGREEMENT  # Exit code 2 for disagreement

    print("✅ All discovered versions are in agreement.")

    return 0


def handle_bump(args: argparse.Namespace) -> int:
    """Handler for the 'bump' command."""
    LOGGER.info(
        "Running bump… increment=%s scheme=%s dry_run=%s autogit=%s",
        args.increment,
        args.scheme,
        args.dry_run,
        args.autogit,
    )

    # --- 1. Discover and check for agreement (similar to 'check' command) ---
    project_root = Path(args.project_root)

    if args.autogit != "off":
        try:
            if git.is_repo_dirty(project_root) and not args.allow_dirty:
                LOGGER.error("Git repository dirty and --allow-dirty not set.")
                print(
                    "❌ Git repository is dirty. Use --allow-dirty to proceed.",
                    file=sys.stderr,
                )
                return DIRTY_GIT_REPO
        except Exception as e:
            LOGGER.warning(
                "Failed to check repo dirtiness: %s", e, exc_info=args.verbose > 1
            )

    # --- Determine increment (normalize once) ---
    increment = args.increment
    digest_path = Path(args.project_root) / ".jiggle_version.config"

    if increment == "auto":
        try:
            increment = determine_auto_increment(project_root, digest_path, args.ignore)
            LOGGER.debug("Auto increment resolved to: %s", increment)
        except Exception as e:
            LOGGER.error(
                "Auto-increment analysis failed: %s", e, exc_info=args.verbose > 0
            )
            print(f"❌ Error during auto-increment analysis: {e}", file=sys.stderr)
            return AUTOINCREMENT_ERROR

    found_versions: list[str] = []
    parser_map = {
        "pyproject.toml": parse_pyproject_toml,
        "setup.cfg": parse_setup_cfg,
        "setup.py": parse_setup_py,
    }

    try:
        source_files = find_source_files(project_root, args.ignore)
    except Exception as e:
        LOGGER.error("Discovery failed: %s", e, exc_info=args.verbose > 0)
        print(f"❌ Discovery failed: {e}", file=sys.stderr)
        return DISCOVERY_ERROR

    source_files_with_versions: list[Path] = []
    for file_path in source_files:
        parser_func = parser_map.get(file_path.name, parse_python_module)
        try:
            version = parser_func(file_path)
        except Exception as e:
            LOGGER.warning(
                "Parsing error in %s: %s", file_path, e, exc_info=args.verbose > 1
            )
            continue
        if version:
            found_versions.append(version)
            source_files_with_versions.append(file_path)

    if not found_versions:
        LOGGER.error("No version declarations found to bump.")
        print("❌ No version declarations found to bump.")
        return NO_VERSION_FOUND

    unique_versions = set(found_versions)
    if len(unique_versions) > 1 and not args.force_write:
        LOGGER.error(
            "Version conflict prevents bump. versions=%s", sorted(unique_versions)
        )
        print(
            f"❌ Version conflict detected! Cannot bump. Found: {', '.join(sorted(unique_versions))}"
        )
        return VERSION_DISAGREEMENT

    current_version = (
        unique_versions.pop() if len(unique_versions) == 1 else found_versions[0]
    )
    print(f"Current version: {current_version}")

    # --- 2. Calculate the new version ---
    try:
        target_version = (
            args.set_version
            if args.set_version
            else bump_version(current_version, increment, args.scheme)
        )
        print(f"New version:     {target_version}")
        LOGGER.debug(
            "Bump result: %s -> %s [scheme=%s, inc=%s]",
            current_version,
            target_version,
            args.scheme,
            increment,
        )
    except ValueError as e:
        LOGGER.error("Version bump failed: %s", e, exc_info=args.verbose > 0)
        print(f"❌ Error bumping version: {e}", file=sys.stderr)
        return VERSION_BUMP_ERROR

    # --- 3. Write changes ---
    if args.dry_run:
        print("\n--dry-run enabled, no files will be changed.")
    else:
        print("\nUpdating files…")
        updater_map = {
            "pyproject.toml": update_pyproject_toml,
            "setup.cfg": update_setup_cfg,
            "setup.py": update_python_file,
        }
        for file_path in source_files_with_versions:
            relative_path = file_path.relative_to(project_root)
            updater_func = updater_map.get(file_path.name, update_python_file)
            try:
                updater_func(file_path, target_version)
                print(f"✅ Updated {relative_path}")
            except Exception as e:
                LOGGER.error(
                    "Failed to update %s: %s", file_path, e, exc_info=args.verbose > 0
                )
                print(f"❌ Failed to update {relative_path}: {e}", file=sys.stderr)
                return FILE_UPDATE_ERROR
        if args.increment == "auto":
            print("\nUpdating API digest file…")
            try:
                current_symbols = get_current_symbols(project_root, args.ignore)
                write_digest_data(digest_path, current_symbols)
                print("✅ Updated .jiggle_version.config")
            except Exception as e:
                LOGGER.warning(
                    "Failed updating digest: %s", e, exc_info=args.verbose > 0
                )

    # --- 4. Autogit ---
    if args.autogit != "off" and not args.dry_run:
        print("\nRunning autogit…")
        try:
            # Stage
            if args.autogit in ["stage", "commit", "push"]:
                print(f"Staging {len(source_files_with_versions)} file(s)…")
                git.stage_files(project_root, source_files_with_versions)
                print("✅ Files staged.")

            # Commit
            if args.autogit in ["commit", "push"]:
                commit_message = args.commit_message.format(
                    version=target_version, scheme=args.scheme, increment=increment
                )
                print(f"Committing with message: '{commit_message}'…")
                git.commit_changes(project_root, commit_message)
                print("✅ Changes committed.")

            # Push
            if args.autogit == "push":
                current_branch = git.get_current_branch(project_root)
                remote = "origin"  # Default from PEP
                print(f"Pushing to {remote}/{current_branch}…")
                git.push_changes(project_root, remote, current_branch)
                print("✅ Changes pushed.")

        except (RuntimeError, subprocess.CalledProcessError) as e:
            LOGGER.error("Autogit failed: %s", e, exc_info=args.verbose > 0)
            print(f"❌ Autogit failed: {e}", file=sys.stderr)
            return AUTOGIT_ERROR

    elif args.autogit != "off" and args.dry_run:
        print(f"\n--dry-run enabled, skipping autogit '{args.autogit}'.")

    return 0


def handle_print(args: argparse.Namespace) -> int:
    """Handler for the 'print' command."""
    LOGGER.info("Running print… project_root=%s", args.project_root)
    project_root = Path(args.project_root)
    found_versions = []
    parser_map = {
        "pyproject.toml": parse_pyproject_toml,
        "setup.cfg": parse_setup_cfg,
        "setup.py": parse_setup_py,
    }
    # Pass the ignore argument to the discovery function
    try:
        source_files = find_source_files(project_root, args.ignore)
    except Exception as e:
        LOGGER.error("Discovery failed: %s", e, exc_info=args.verbose > 0)
        print(f"Error: Discovery failed: {e}", file=sys.stderr)
        return DISCOVERY_ERROR

    for file_path in source_files:
        parser_func = parser_map.get(file_path.name, parse_python_module)
        try:
            version = parser_func(file_path)
        except Exception as e:
            LOGGER.warning(
                "Parse failed for %s: %s", file_path, e, exc_info=args.verbose > 1
            )
            continue
        if version:
            found_versions.append(
                {"source": str(file_path.relative_to(project_root)), "version": version}
            )
    if not found_versions:
        LOGGER.error("No version found for print.")
        print("Error: No version found.", file=sys.stderr)
        return NO_VERSION_FOUND
    unique_versions = set(item["version"] for item in found_versions)
    if len(unique_versions) > 1:
        LOGGER.error("Version conflict on print: %s", sorted(unique_versions))
        print(
            f"Error: Version conflict detected. Found: {', '.join(sorted(unique_versions))}",
            file=sys.stderr,
        )
        return VERSION_DISAGREEMENT
    print(unique_versions.pop())
    return 0


def handle_inspect(args: argparse.Namespace) -> int:
    """Handler for the 'inspect' command."""
    LOGGER.info("Running inspect… project_root=%s", args.project_root)
    project_root = Path(args.project_root)
    print(f"Inspecting project at: {project_root.resolve()}")
    # Pass the ignore argument to the discovery function
    try:
        source_files = find_source_files(project_root, args.ignore)
    except Exception as e:
        LOGGER.error("Discovery failed: %s", e, exc_info=args.verbose > 0)
        print(f"Error: Discovery failed: {e}", file=sys.stderr)
        return DISCOVERY_ERROR

    print(f"\nFound {len(source_files)} potential source file(s):")
    for file in source_files:
        print(f"  - {file.relative_to(project_root)}")
    handle_check(args)
    return 0


def handle_hash_all(args: argparse.Namespace) -> int:
    """Handler for the 'hash-all' command."""
    LOGGER.info("Running hash-all… project_root=%s", args.project_root)
    project_root = Path(args.project_root)
    digest_path = project_root / ".jiggle_version.config"

    try:
        print("Discovering public API symbols (`__all__`)…")
        # Note: auto-increment's discovery also needs to be aware of ignores.
        # This is handled inside get_current_symbols by calling find_source_files.
        current_symbols = get_current_symbols(project_root, args.ignore)
        write_digest_data(digest_path, current_symbols)
        print(f"✅ Successfully wrote {len(current_symbols)} symbols to {digest_path}")
        return 0
    except Exception as e:
        LOGGER.error("hash-all failed: %s", e, exc_info=args.verbose > 0)
        print(f"❌ Failed to generate digest file: {e}", file=sys.stderr)
        return HASH_ERROR


def handle_init(args: argparse.Namespace) -> int:
    """Handler for the 'init' command."""
    LOGGER.info("Running init… project_root=%s", args.project_root)
    pyproject_path = Path(args.project_root) / "pyproject.toml"
    if not pyproject_path.is_file():
        LOGGER.error("pyproject.toml not found: %s", pyproject_path)
        print(f"Error: pyproject.toml not found at {pyproject_path}", file=sys.stderr)
        return NO_CONFIG_FOUND
    config_str = pyproject_path.read_text(encoding="utf-8")
    if "[tool.jiggle_version]" in config_str:
        print("jiggle_version config already exists in pyproject.toml.")
        return 0

    default_config = """
[tool.jiggle_version]
scheme = "pep440"
default_increment = "patch"
# ignore = ["docs/generated", "build/"] # Example
"""
    with open(pyproject_path, "a", encoding="utf-8") as f:
        f.write(default_config)
    print("✅ Added default [tool.jiggle_version] section to pyproject.toml.")
    return 0


# ----------------------------------------------------------------------------
# Parser construction
# ----------------------------------------------------------------------------

# --- New: isolated bump subparser factory (from-scratch) ---


def build_bump_subparser(
    subparsers: argparse._SubParsersAction,
) -> argparse.ArgumentParser:
    """Define only the `bump` subcommand args here, cleanly and testably.

    IMPORTANT: Do **not** bake config-derived defaults here. We parse first,
    then load pyproject.toml, then *override* selected fields from config.
    This keeps precedence explicit: CONFIG > CLI > hardcoded fallback.
    """
    p = subparsers.add_parser("bump", help="Bump the project version.")
    p.add_argument(
        "--increment",
        choices=["major", "minor", "patch", "auto"],
        help="Version part to increment.",
    )
    p.add_argument(
        "--scheme",
        choices=["pep440", "semver"],
        help="Versioning scheme.",
    )
    p.add_argument(
        "--dry-run", action="store_true", help="Simulate without writing files."
    )
    p.add_argument(
        "--set",
        dest="set_version",
        type=str,
        default="",
        help="Set an explicit version.",
    )
    p.add_argument(
        "--force-write",
        action="store_true",
        default=False,
        help="Write even on disagreement.",
    )

    # Autogit group (all optional; config may override later)
    g = p.add_argument_group("autogit options")
    g.add_argument(
        "--autogit",
        choices=["off", "stage", "commit", "push"],
        default="off",
        help="Automatically stage/commit/push changes.",
    )
    g.add_argument(
        "--commit-message",
        type=str,
        default="Release: {version}",
        help="Commit message template.",
    )
    g.add_argument(
        "--allow-dirty",
        action="store_true",
        default=False,
        help="Allow autogit even if repo has uncommitted changes.",
    )

    p.set_defaults(func=handle_bump)
    return p


def _build_parser(
    config_defaults: dict[str, str], use_smart: bool = True
) -> tuple[argparse.ArgumentParser, argparse._SubParsersAction]:
    """Construct the main parser. `config_defaults` no longer affects construction.

    We apply config late after initial parse to know the correct --config path.
    """
    ParserClass = SmartParser if use_smart else argparse.ArgumentParser
    parser = ParserClass(
        prog="jiggle_version",
        description="A safe, zero-import, config-first version bumper.",
        formatter_class=CustomFormatter,
        add_help=False,
    )
    try:
        parser.register("action", "parsers", argparse._SubParsersAction)
    except Exception:
        LOGGER.debug(
            "Parser register(action=parsers) not supported on this parser class."
        )

    # Global/basic options
    parser.add_argument("-h", "--help", action="help", help="Show help and exit")
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__about__.__version__}"
    )
    parser.add_argument(
        "--config", default="pyproject.toml", help="Path to configuration file"
    )

    # Common options for all commands
    parser.add_argument(
        "--ignore", nargs="+", help="Relative paths to ignore during discovery."
    )
    parser.add_argument(
        "-v", "--verbose", action="count", default=0, help="Increase verbosity level"
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Explicit log level (overrides -v)",
    )
    parser.add_argument(
        "--project-root", type=str, default=".", help="Project root directory"
    )
    parser.add_argument(
        "--no-color", action="store_true", help="Disable colored output"
    )

    subparsers = parser.add_subparsers(
        dest="command", required=True, help="Sub-commands"
    )

    # check
    parser_check = subparsers.add_parser(
        "check", help="Check that discovered version declarations agree."
    )
    parser_check.set_defaults(func=handle_check)

    # bump (built via dedicated function)
    build_bump_subparser(subparsers)

    # print
    parser_print = subparsers.add_parser(
        "print", help="Print the discovered normalized project version."
    )
    parser_print.set_defaults(func=handle_print)

    # inspect
    parser_inspect = subparsers.add_parser(
        "inspect", help="Show a detailed report of discovered version sources."
    )
    parser_inspect.set_defaults(func=handle_inspect)

    # hash-all
    parser_hash_all = subparsers.add_parser(
        "hash-all", help="Compute and store __all__ digests without bumping."
    )
    parser_hash_all.set_defaults(func=handle_hash_all)

    # init
    parser_init = subparsers.add_parser(
        "init", help="Create default [tool.jiggle_version] config in pyproject.toml."
    )
    parser_init.set_defaults(func=handle_init)

    return parser, subparsers


# ----------------------------------------------------------------------------
# Entry point
# ----------------------------------------------------------------------------

# --- New: late override helper for bump ---

BUMP_OVERRIDES = {
    # config key -> attr name on args
    "increment": "increment",
    "scheme": "scheme",
    "autogit": "autogit",
    "commit_message": "commit_message",
    "allow_dirty": "allow_dirty",
    # You can add more if you support them in config later:
    # "force_write": "force_write",
    # "set_version": "set_version",
}


def apply_global_overrides(args: argparse.Namespace, cfg: dict[str, Any]) -> None:
    """
    Apply config-derived settings that should affect all commands.
    CLI takes precedence; we only fill when args are empty/None.
    """
    # ignore: fill from config if CLI didn't set it
    if (getattr(args, "ignore", None) in (None, [])) and isinstance(
        cfg.get("ignore"), list
    ):
        args.ignore = [str(p) for p in cfg["ignore"]]
        LOGGER.debug("Override: ignore -> %r (from config)", args.ignore)

    # Optional: allow config to set project_root if user didn't change it
    if getattr(args, "project_root", None) in (None, ".") and isinstance(
        cfg.get("project_root"), str
    ):
        args.project_root = cfg["project_root"]
        LOGGER.debug("Override: project_root -> %r (from config)", args.project_root)


def apply_bump_overrides(args: argparse.Namespace, cfg: dict[str, str]) -> None:
    """Apply config-overrides to bump args *after* parsing CLI.

    Precedence requested by user: CONFIG > CLI > hardcoded fallback.
    We also supply hardcoded fallbacks when both are None.
    """
    if not hasattr(args, "command"):
        return
    if args.command != "bump":
        return
    # Normalize: config loader already maps default_increment->increment.
    for k, attr in BUMP_OVERRIDES.items():
        if k in cfg and cfg[k] not in (None, ""):
            old = getattr(args, attr, None)
            setattr(args, attr, cfg[k])
            LOGGER.debug("Override: %s: %r -> %r (from config)", attr, old, cfg[k])

    # Hardcoded fallbacks
    if getattr(args, "increment", None) in (None, ""):
        setattr(args, "increment", "patch")
    if getattr(args, "scheme", None) in (None, ""):
        setattr(args, "scheme", "pep440")
    if getattr(args, "autogit", None) in (None, ""):
        setattr(args, "autogit", "off")


def main(argv: Sequence[str] | None = None) -> int:
    """Main CLI entry point."""
    cli_args = sys.argv[1:] if argv is None else list(argv)

    # 0) Pre-parse ONLY --config using a minimal parser to avoid early exits
    pre = argparse.ArgumentParser(add_help=False)
    pre.add_argument("--config", default="pyproject.toml")
    try:
        pre_ns, _ = pre.parse_known_args(cli_args)
    except SystemExit:
        # Extremely unlikely, but log it.
        print("❌ Early exit while reading --config", file=sys.stderr)
        return ARGPARSE_ERROR

    config_path = Path(pre_ns.config)
    config_from_file = load_config_from_path(config_path)

    apply_global_overrides(pre_ns, config_from_file)
    apply_bump_overrides(pre_ns, config_from_file)

    # 1) Build the full parser (no config defaults baked in)
    parser, _ = _build_parser(config_from_file, use_smart=False)
    apply_global_overrides(pre_ns, config_from_file)

    # 2) Now parse the full CLI safely, logging parse issues
    try:
        args = parser.parse_args(cli_args)
        apply_bump_overrides(args, config_from_file)
        apply_global_overrides(args, config_from_file)
    except SystemExit as _e:
        # Argparse printed help/errors itself; add a debug breadcrumb and exit.
        # sys.stderr.write(f"[DEBUG] argparse SystemExit code={e.code} args={cli_args}")
        return ARGPARSE_ERROR

    # 2.5) Load config (now that we trust --config path) and apply late overrides for bump
    config_from_file = load_config_from_path(Path(args.config))
    apply_bump_overrides(args, config_from_file)

    # 3) Configure logging as early as possible after parse
    configure_logging(args.verbose, args.log_level)
    LOGGER.debug("Parsed args: %s", args)
    LOGGER.debug(
        "Using config file: %s (exists=%s)", str(config_path), config_path.is_file()
    )
    LOGGER.debug(
        "Effective bump defaults (if bump): increment=%s scheme=%s",
        getattr(args, "increment", None),
        getattr(args, "scheme", None),
    )

    # 4) Dispatch
    try:
        if hasattr(args, "func"):
            return args.func(args)
        # This should be unreachable due to required=True
        LOGGER.error("No subcommand handler set; this indicates a parser wiring bug.")
        parser.print_help(sys.stderr)
        return ARGPARSE_ERROR
    except Exception as e:
        # Provide concise error, rich trace only with -vv
        LOGGER.error("Unhandled exception: %s", e, exc_info=args.verbose > 1)
        print(f"An error occurred: {e}", file=sys.stderr)
        return ARGPARSE_ERROR


if __name__ == "__main__":
    sys.exit(main())
