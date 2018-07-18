

from versio.version import Version
from versio.version_scheme import Pep440VersionScheme, VersionScheme, Simple4VersionScheme

from jiggle_version.schema_guesser import version_object_and_next


def test_four_part():
    string ="1.7.1.3"
    print(string)
    Version.supported_version_schemes = [Pep440VersionScheme, Simple4VersionScheme]
    version = Version(string, scheme=Simple4VersionScheme)
    version.bump()
    # _ = Version(str(next_version), scheme=Simple4VersionScheme)
    print(Version(string, scheme=Simple4VersionScheme), version, "simple-4 part (versio)")

def test_four_part_again():
    print(version_object_and_next("1.7.1.3"))
