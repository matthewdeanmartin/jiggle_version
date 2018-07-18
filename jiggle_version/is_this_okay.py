"""
Is that python source code we are about to write really python?
"""
import ast
import sys
import logging

logger = logging.getLogger(__name__)


def check(src, dst):  # type: (str,str)->None
    """
    Code take from black formatter. Just want to see if this is still python.
    :param src:
    :return:
    """
    was_bad = False
    try:
        _ = ast.parse(src)
    except Exception as exc:
        was_bad = True
        major, minor = sys.version_info[:2]
        logger.warning(
            "failed to parse source file "
            "with Python {0}.{1}'s builtin AST. Switch to manual "
            "or stop using deprecated Python 2 syntax. AST error message: {2}".format(
                major, minor, exc
            )
        )

    try:
        _ = ast.parse(dst)
    except Exception as exc:
        if was_bad:
            # I didn't make it worse.
            pass
        else:
            logger.error(dst)
            raise
