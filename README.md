# jiggle_version
Opinionated, no config build version incrementer. No regex. Drop in and go.

Badges
------
[![MIT licensed](https://img.shields.io/badge/license-MIT-blue.svg)](https://raw.githubusercontent.com/hyperium/hyper/master/LICENSE) ![Read the Docs](https://img.shields.io/readthedocs/pip.svg) ![Travis](https://travis-ci.com/matthewdeanmartin/jiggle_version.svg?branch=master) [![Coverage Status](https://coveralls.io/repos/github/matthewdeanmartin/jiggle_version/badge.svg?branch=master)](https://coveralls.io/github/matthewdeanmartin/jiggle_version?branch=master) [![BCH compliance](https://bettercodehub.com/edge/badge/matthewdeanmartin/jiggle_version?branch=master)](https://bettercodehub.com/)


Opinionated
-----------
It is a design smell that a library opens with asking you a lot of questions or to fill in a lot of twitchy config before simple scenarious work.

An opinionated library has an opinion about the right way to do it. That said, if the library can discover existing conventions, it should discover them and used them.

No Config, No Regex
-------------------
If the config is more complex than re-writing the code from scratch, there is something wrong with a library.

These contraints enable "drop in and go"

Build Incremeter
----------------
 - Major - The change is big.
 - Minor - The change breaks compatibility. This might be detectable with a unit test runner,  or maybe even by detecting
changes to public interfaces (not that such a concept exists in python) but otherwise is too hard for machines.
 - Patch - This is the small number that increases each build. jiggle_version *only* solves the problem of incrementing this
number.

Files Targeted
--------------
/__init__.py  - __version__ = "1.1.1"

/__version__.py - __version__ = "1.1.1"

TODO: _version.py - I think this is a place to pipe a version string from a version control system that isn't expected to be executable? Not sure. It is a common convention.

TODO: version.txt - Some tools put/expect just the version string here.

/setup.cfg  version=1.1.1

We take the first of these, increment the patch, and re-write those 3 files. If they don't exist, they will be created
with only the version number filled in.

We make no particular effort to parse wild text. If your current number is so messed up that you need regex to ID it,
then edit it by hand.

Other way to get/provide version:

https://stackoverflow.com/questions/7079735/how-do-i-get-the-version-of-an-installed-module-in-python-programatically

    import pkg_resources
    version = pkg_resources.get_distribution("nose").version

Flipside Question
-----------------
What version am I depending on? If you want to check the version of a dependency, you might be better off doing feature detection, i.e. check if name of some function exists and then use it.

Which Version Wins?
------------------
You can get a version from your git tag, from anyone of the existing .py or config files.

I think the tagger should set tags based on what is in the __version__.py file. Forcing the user to check in, tag
and so on before bumping a version is no fun.


Relevant PEPs
------------- 
345 - https://www.python.org/dev/peps/pep-0345/#version

386 - SUPERCEDED https://www.python.org/dev/peps/pep-0386/

396- https://www.python.org/dev/peps/pep-0396/#specification

440 - https://www.python.org/dev/peps/pep-0440/

Conflicts
--------
If you use pbr or bumpversion with jiggle_version you may have conflicts

How are other people solving this problem?
------------------------------------------

 - Git/VCS centric
    - [python-versioneer](https://github.com/warner/python-versioneer) Git tags hold canonical version

    - [python-git-version](https://github.com/aebrahim/python-git-version) Git holds canonical version

    - [git-bump-version](https://pypi.org/project/git-bump-version/) same

    - [pyver](https://pypi.org/project/pyver/) same

    - [setupext-gitversion](https://pypi.org/project/setupext-gitversion/) Git tag driven version bumping

    - [katversion](https://pypi.org/project/katversion/) same

    - [mercurial_update_version](https://pypi.org/project/mercurial_update_version/) Merucrial holds your canonical version.
    
    - [zest releaser](http://zestreleaser.readthedocs.io/en/latest/) - VCS driven versionbump command

[pylease](https://pypi.org/project/pylease/) Version bumper, release tool [repo here](https://github.com/bagrat/pylease)

bumpversion & bump2version - I don't know how this works. Frustration trying to get bumpversion to work at all drove me to create jiggle-version. bump2version is a fork for fixing bugs because bumpversion is/was dormant.

[changes](https://github.com/michaeljoseph/changes) - I haven't tried it. Does things other than version bumping


pbr - quirky version bumping and a bunch of other things. You can't turn off the version bumping, so it will conflict with any other version bumper you use.

[vdt](https://pypi.org/project/vdt.version/) Git and Jenkins centric version bumping with other actions built in.

[metapensiero.tool.bump_version](https://pypi.org/project/metapensiero.tool.bump_version/) Version.txt manager. Looks like it avoids dealing with any python source code, etc.

[incremental](https://pypi.org/project/incremental/) _version.py updator. If I understand, this lib becomes a dependency of your release app, i.e. it isn't just a build dependency.


Parsing the complex Version Object
----------------------------------
There are many libraries for dealing with the version string as a rich structured object with meaningful parts and a PEP to conform to. jiggle_version itself relies on semantic_version.

[semantic_version](https://pypi.org/project/semantic_version/)

[cmp-version](https://pypi.org/project/cmp_version/)

[Versio](https://pypi.org/project/Versio/) 

[pep440](https://pypi.org/project/pep440/) Is the version string pep440 valid

[parver](https://pypi.org/project/parver/) PEP 440 centric.


Version Finders
---------------
[https://pypi.org/project/package-version/](https://github.com/Yuav/python-package-version) Assume pypi has your canoncial version, use pip to find the last version to bump.


[get_version](https://pypi.org/project/get_version/) Searches source tree? Local pip package?

[version_hunter](https://pypi.org/project/version-hunter/) Seems to be more focused on finding a version from a source code tree & not in bumping it.

[git-version](https://pypi.org/project/git-version/) Version finding from your git repo

[tcversioner](https://pypi.org/project/tcversioner/) Find version via vcs tag. Writes version.txt

[bernardomg.version-extractor](https://pypi.org/project/bernardomg.version-extractor/) Extract version from source code (only 2 functions? an ast version and a regex version)

[setuptools-requirements-vcs-version](https://github.com/danielbrownridge/setuptools-requirements-vcs-version) Find version in requirements.txt found by searching git url! Not sure what scenario this is for.



Django
------
[django-fe-version](https://pypi.org/project/django-fe-version/) Adds a /version/ endpoint to your web app.

[django-project-version](https://pypi.org/project/django-project-version/) same..


Design Decisions
----------------
- What version is canonical? 
    - User supplied 
    - Discovered in source
    - Discovered in pip/pip package/pypi
    - VCS supplied, e.g. git/mercurial, etc
- What is the next version?
    - User supplies
    - Search for it, increment it
    - Provide default, e.g. 0.1.0
- How do you parse the version?
    - User supplied regex (ha, ha, wait... some libs do this)
    - ast (i.e. eval the source code)
    - string parsing
    - library supplied regex
- How do you interpret the version or compare versions?
    - [PEP 440](https://www.python.org/dev/peps/pep-0440/)
    - Semantic Version
    - User supplied ad-hoc 
    - Opaque strings (no way to auto-bump)
    - Other, e.g. Microsoft versions, for cross platform deployment
- How do you record the new versin?
    - Update files
    - Update VCS (commit, push, tag, etc)
- How do you integrat with other build steps?
    - stand alone
    - bump version along with other steps, like packaging and pushing to pypi

    

