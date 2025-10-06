from __future__ import annotations

import logging
import sys

LOGGER = logging.getLogger(__name__)


def configure_logging(verbosity: int, explicit_level: str | None) -> None:
    """Configure logging based on -v and/or --log-level.

    Precedence: explicit level > verbosity; default INFO.
    -v => INFO, -vv => DEBUG, -vvv => DEBUG with very chatty modules enabled.
    """
    if explicit_level:
        level = getattr(logging, explicit_level.upper(), logging.INFO)
    else:
        level = logging.WARNING
        if verbosity >= 2:
            level = logging.DEBUG
        elif verbosity == 1:
            level = logging.INFO

    handler = logging.StreamHandler(sys.stderr)
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )
    handler.setFormatter(formatter)

    root = logging.getLogger()
    # Clear any prior handlers if running in REPL/tests
    for h in list(root.handlers):
        root.removeHandler(h)
    root.addHandler(handler)
    root.setLevel(level)

    # Tame noisy libs unless -vvv
    if verbosity < 3 and not explicit_level:
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        logging.getLogger("tomllib").setLevel(logging.WARNING)

    LOGGER.debug(
        "Logging configured: level=%s verbosity=%s",
        logging.getLevelName(root.level),
        verbosity,
    )
