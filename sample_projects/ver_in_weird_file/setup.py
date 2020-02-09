from setup_helpers import require_python, get_version
from setuptools import setup, find_packages


require_python(0x30400F0)
__version__ = get_version("aiosmtpd/smtp.py")


setup(
    name="ver_in_weird_file",
    version=__version__,
    description="ver_in_weird_file",
    long_description="""ver_in_weird_file""",
    author="ver_in_weird_file",
    url="ver_in_weird_file",
    keywords="email",
    packages=find_packages(),
)
