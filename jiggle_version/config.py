# jiggle_version/config.py
"""
Handles loading and parsing of the [tool.jiggle_version] section
from a pyproject.toml file.
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Any

# For Python < 3.11, we need tomli
if sys.version_info < (3, 11):
    import tomli as tomllib
else:
    import tomllib

LOGGER = logging.getLogger(__name__)


def load_config_from_path(config_path: Path) -> dict[str, Any]:
    """
    Loads configuration from pyproject.toml and returns it as a dictionary.

    Args:
        config_path: The path to the pyproject.toml file.

    Returns:
        A dictionary of configuration values.
    """
    if not config_path.is_file():
        return {}

    try:
        config_data = tomllib.loads(config_path.read_text(encoding="utf-8"))
        jiggle_config: dict[str, Any] = (
            config_data.get("tool", {}).get("jiggle_version", {}) or {}
        )
        if jiggle_config:
            LOGGER.debug("Config found")

        # The config uses 'default_increment', but argparse dest is 'increment'.
        # We'll normalize the key here to make it compatible with argparse.
        if "default_increment" in jiggle_config:
            jiggle_config["increment"] = jiggle_config.pop("default_increment")
            LOGGER.debug(f"increment: {jiggle_config.get('increment')}")

        # >>> ADD THIS: normalize [tool.jiggle_version].ignore to list[str]
        if "ignore" in jiggle_config:
            ig = jiggle_config["ignore"]
            if isinstance(ig, str):
                jiggle_config["ignore"] = [ig]
            elif isinstance(ig, (tuple, set)):
                jiggle_config["ignore"] = list(ig)
            elif not isinstance(ig, list):
                print(
                    "Warning: [tool.jiggle_version].ignore must be a list of paths or a string.",
                    file=sys.stderr,
                )
                jiggle_config.pop("ignore", None)
        # <<< END ADD
        LOGGER.debug(f"ignore: {jiggle_config.get('ignore')}")
        # print(f"ignore: {jiggle_config.get('ignore')}")
        return jiggle_config
    except tomllib.TOMLDecodeError:
        print(
            f"Warning: Could not parse '{config_path}'. Invalid TOML.", file=sys.stderr
        )
        return {}
