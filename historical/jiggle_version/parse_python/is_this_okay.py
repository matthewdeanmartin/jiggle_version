"""
Is that python source code we are about to write really python?
"""

from __future__ import annotations

import ast
import logging
import sys

logger = logging.getLogger(__name__)


def check(src: str, dst: str) -> None:
    """
    Code take from black formatter. Just want to see if this is still python.
    """
    was_bad = False
    try:
        _ = ast.parse(src)
    except Exception as exc:
        was_bad = True
        major, minor = sys.version_info[:2]
        logger.warning(
            "failed to parse source file "
            f"with Python {major}.{minor}'s builtin AST. Switch to manual "
            f"or stop using deprecated Python 2 syntax. AST error message: {exc}"
        )

    try:
        _ = ast.parse(dst)
    except Exception as exc:
        if was_bad:
            # I didn't make it worse.
            pass
        else:
            # ok, this made the file worse. It must be jiggle_version's fault.
            logger.error(exc, dst)
            logger.error(dst)
            raise
