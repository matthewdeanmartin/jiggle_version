
import parver

def test_pep440():
    string = "1.0.4.dev1"
    version = parver.Version.parse(string)
    next_version = version.bump_dev()
    _ = parver.Version.parse(str(next_version))
    print(version, next_version, "pep440 (parver)")