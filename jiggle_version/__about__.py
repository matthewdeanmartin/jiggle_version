"""Metadata for jiggle_version."""

__all__ = [
    "__credits__",
    "__dependencies__",
    "__description__",
    "__keywords__",
    "__license__",
    "__readme__",
    "__requires_python__",
    "__status__",
    "__title__",
    "__version__",
]

__title__ = "jiggle_version"
__version__ = "2.2.1"
__description__ = "Increment version number found in source code without regex"
__readme__ = "README.md"
__credits__ = [{"name": "Matthew Martin", "email": "matthewdeanmartin@gmail.com"}]
__keywords__ = ["version", "version-numbers"]
__license__ = "MIT"
__requires_python__ = ">=3.11"
__status__ = "3 - Alpha"
__dependencies__ = [
    "rich-argparse>=1.7.1",
    "pathspec>=0.12",
    "tomlkit>=0.13.3",
    "requests>=2.32.4",
    "packaging>=25.0",
]
