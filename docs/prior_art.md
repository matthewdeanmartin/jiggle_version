How are other people solving this problem?
------------------------------------------

| PyPi                                                                 | Source Code                                                                 | Docs |
|----------------------------------------------------------------------|-----------------------------------------------------------------------------|------|
| __                                                                   | [python-versioneer](https://github.com/warner/python-versioneer)            | ___  |
| __                                                                   | [python-git-version](https://github.com/aebrahim/python-git-version)        | ___  |
| [git-bump-version](https://pypi.org/project/git-bump-version/)       | ___                                                                         | ___  |
| [setupext-gitversion](https://pypi.org/project/setupext-gitversion/) | ___                                                                         | ___  |
| __                                                                   | [python-git-version](https://github.com/aebrahim/python-git-version)        | ___  |
| [git-bump-version](https://pypi.org/project/git-bump-version/)       | [git_bump_version (GH)](https://github.com/silent-snowman/git_bump_version) | ___  |
| [pyver](https://pypi.org/project/pyver/)                             | [pyver (GH)](https://github.com/clearclaw/pyver)                            | ___  |
| [vdt.version](https://pypi.org/project/vdt.version/)                 | [vdt.version (GH)](https://github.com/devopsconsulting/vdt.version)         | ___  |

Git Centric
-----------
These all either run `git describe --tags` to find a version or `git tag %` to bump a version.

- Git/VCS centric - setup.py plugins
    - [python-versioneer](https://github.com/warner/python-versioneer) Git tags hold canonical version. Setup.py plugin
      command. `versioneer install`. Vendorizes itself to your souce tree. Edit `setup.py` and `setup.cfg`. Run
      `python versioneer.py setup` This adds a lot of code to your source tree. Has bug where it only works if the
      version code file is _version.py. This was just very twitchy to setup. Library code has to run to get the version,
      e.g. ` python -c "import ver_test1; print(ver_test1.\_\_version\_\_)"` Personally, I don't like how this library
      infects the production release. I'd rather my build dependencies gone by final release.
    - [setupext-gitversion](https://pypi.org/project/setupext-gitversion/) Git tag driven version bumping. Pep440.
      Requires [git_version] section in setup.cfg, add `from setupext import gitversion` and wire up a plug-in, then to
      run, `python setup.py git_version` I couldn't evaluate further because it blew up inspecting my git repo.

- Git/VCS centric
    - [python-git-version](https://github.com/aebrahim/python-git-version) Git holds canonical version. Library is
      expected to be vendorized (copied next to your setup.py). Code runs in \_\_version\_\_. ` python version.py`
      returns version found in tag. EXxecute with `python setup.py sdist` - as far as I can tell, it specifies the
      package version and doesn't expect to be used from code after deployment.

    - [pyver](https://pypi.org/project/pyver/) SUPERCEDED BY *versioneer* Pep440. Expects tag to already exist. Invoked
      in setup.py, used for package version.

    - [katversion](https://pypi.org/project/katversion/) Implemented as setup.py 'extension'. Expects \_\_init\_\_.py to
      exist. Ignores \_\_init\_\_.py and does not update the \_\_version\_\_ value. Does update package version with
      string drived from git tags and history.

    - [zest releaser](http://zestreleaser.readthedocs.io/en/latest/) - VCS driven versionbump command

    - [vdt](https://pypi.org/project/vdt.version/) Git and Jenkins centric version bumping with other actions built in.
      Command line `version`. Python 2 only. I'm not going to have time to test it out.

    - [pbr](https://pypi.org/project/pbr/) - quirky git tag driven version bumping and a bunch of other things. You
      can't turn off the version bumping, so it will conflict with any other version bumper you use. Appears to affect
      package version, the one you see in the /dist/ folder.

    - bumpversion & bump2version - I don't know how this works. Frustration trying to get bumpversion to work at all
      drove me to create jiggle-version. bump2version is a fork for fixing bugs because bumpversion is/was dormant. Not
      linking until the maintainers return 6 hours of my life that they stole.

- Only Git Tags
    - [git-bump-version](https://pypi.org/project/git-bump-version/) Command line `git_bump_version` searches for last
      tag and tags current. Blows up on "v1.2.3" As far as I can tell, this code is agnostic to what your source code
      is, i.e. it doesn't edit \_\_version\_\_.py, etc.

- Other VCS
    - [mercurial_update_version](https://pypi.org/project/mercurial_update_version/) Merucrial holds your canonical
      version. Not going to test...I don't use
    - [setuptools_scm](https://pypi.org/project/setuptools_scm/) Git & mercurial. Gets version from tag. Add this to
      setup() in setup.py :`use_scm_version=True, setup_requires=['setuptools_scm'],` No version strings in source at
      all & package still builds to /dist/ with expected version.

| PyPi                                                                                       | Source Code                                                                                | Docs |
|--------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------|------|
| __                                                                                         | [changes](https://github.com/michaeljoseph/changes)                                        | ___  |
| [pylease](https://pypi.org/project/pylease/)                                               | [repo here](https://github.com/bagrat/pylease)                                             | ___  |
| [metapensiero.tool.bump_version](https://pypi.org/project/metapensiero.tool.bump_version/) | [metapensiero.tool.bump_version](https://pypi.org/project/metapensiero.tool.bump_version/) | ___  |

Source Centric
--------------
Source centric version bumpers read and update .py or config files. They do not necessarily require or expect you to
have source control tagging going on.

- Source Centric -- `\_\_init\_\_.py` or `\_\_version\_\_.py`
    - [changes](https://github.com/michaeljoseph/changes) - Does many release related things.
      `changes my_module bump_version` to bump version, but this code will not run unless readme.md exists, etc. Detect
      version from source. Does not suggest new version, you must manually type it.
    - [pylease](https://pypi.org/project/pylease/) Version bumper, release
      tool [repo here](https://github.com/bagrat/pylease) Not python 3 compatible (blows up on CondigParser on pip
      install)


- Source Centric - `Version.txt`
    - [metapensiero.tool.bump_version](https://pypi.org/project/metapensiero.tool.bump_version/) Version.txt manager.
      Looks like it avoids dealing with any python source code, etc. Command line only, supports 4 schemes :
      auto,pep440,simple2,simple3,simple4. Usage: `bump_version -s simple3 -f tiny
`
- Source Centric - `setup.py`, e.g. `python setup.py --version`
    - [incremental](https://pypi.org/project/incremental/) `_version.py` updator. If I understand, this lib becomes a
      dependency of your release app, i.e. it isn't just a build dependency. Pep440 only. Usage
      `python -m incremental.update my_module --patch`

Version Finders
---------------

- VCS centric
    - [version_hunter](https://pypi.org/project/version-hunter/) Seems to be more focused on finding a version from a
      source code tree & not in bumping it.

    - [git-version](https://pypi.org/project/git-version/) Version finding from your git repo

    - [tcversioner](https://pypi.org/project/tcversioner/) Find version via vcs tag. Writes version.txt

- Source Tree centric
    - [get_version](https://pypi.org/project/get_version/) Searches source tree? Local pip package?
    - [bernardomg.version-extractor](https://pypi.org/project/bernardomg.version-extractor/) Extract version from source
      code. 2 functions (microlib) that find \_\_version\_\_ inside of \_\_init\_\_.py
- Other-
    - [package_version pypi](https://pypi.org/project/package-version/) - [package_version](https://github.com/Yuav/python-package-version)
      Assume pypi has your canoncial version, use pip to find the last version to bump.
    - [setuptools-requirements-vcs-version](https://github.com/danielbrownridge/setuptools-requirements-vcs-version)
      Find version in requirements.txt found by searching git url! Not sure what scenario this is for.

Django Version Finders
----------------------
These are finding the version so they can display it, not to increment it.

[django-fe-version](https://pypi.org/project/django-fe-version/) Adds a /version/ endpoint to your web app.

[django-project-version](https://pypi.org/project/django-project-version/) same

