# jiggle_version
Opinionated, no config build version incrementer. No regex. Drop in and go.

    pip install jiggle_library
    
    cd src
    # should run from same folder with setup.py
    # or parent folder of my_project/__init__.py
    
    jiggle_library here
    # find, bump & update version strings in source code
    
    git --tag $(jiggle_library find)

Depends on cmp-version, docopt, parver, semantic-version, versio, which your application is unlikely to depend on.

Badges
------

How's it doing?

 ![Read the Docs](https://img.shields.io/readthedocs/pip.svg) ![Travis](https://travis-ci.com/matthewdeanmartin/jiggle_version.svg?branch=master) [![Coverage Status](https://coveralls.io/repos/github/matthewdeanmartin/jiggle_version/badge.svg?branch=master)](https://coveralls.io/github/matthewdeanmartin/jiggle_version?branch=master) [![BCH compliance](https://bettercodehub.com/edge/badge/matthewdeanmartin/jiggle_version?branch=master)](https://bettercodehub.com/) [![Known Vulnerabilities](https://snyk.io/test/github/matthewdeanmartin/jiggle_version/badge.svg?targetFile=requirements.txt)](https://snyk.io/test/github/matthewdeanmartin/jiggle_version?targetFile=requirements.txt) [![Total Alerts](https://img.shields.io/lgtm/alerts/g/matthewdeanmartin/jiggle_version.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/matthewdeanmartin/jiggle_version/alerts/) [![CodeFactor](https://www.codefactor.io/repository/github/matthewdeanmartin/jiggle_version/badge)](https://www.codefactor.io/repository/github/matthewdeanmartin/jiggle_version)


Where's the bits?

[![PyPI version](https://badge.fury.io/py/jiggle_version.svg)](https://badge.fury.io/py/jiggle_version)  ![GitHub release](https://img.shields.io/github/release/jiggle-version/rubidium.svg)
[![MIT licensed](https://img.shields.io/badge/license-MIT-blue.svg)](https://raw.githubusercontent.com/hyperium/hyper/master/LICENSE)


Problem to be solved
-------------------
There are up to 1/2 dozen places to update a version string. You scoff, 'Can't be!' But for a mature code base, it is
because so many tools expect version strings in different places:

- \_\_init\_\_.py has \_\_version\_\_
- so does \_\_version\_\_.py
- so does the setup function in setup.py
- so does the setup.cfg if you are doing cofig driven setup.py
- your git repo might need a tag matching the library version
- you might need a plain text version.txt

You will need to find the current version, bump the most minor part- which varies depending on if you are using pep440, semantic version or something else, update all the places where you could update and
re-do this as often as each build and at least as often as each package and push to pypi. 

Opinionated
-----------
A library should have one working, no-options, no questions asked scenario, e.g.

    jiggle_library here
    # find, bump & update version strings in source code

An opinionated library has an opinion about the right way to do it. That said, if the library can discover existing conventions, it should discover them and use them. If you don't like it, see the end for competing opinionated libraries and their philosophy, such as vcs-tag-only, regex-more-regex-all-day-regex.

The following contraints enable "drop in and go"

No Config, No Regex
-------------------
If the config is more complex than re-writing the code from scratch, there is something wrong with a library.

Don't contaminate the package
-----------------------------
Other than creating \_\_init\_\_.py, \_\_version\_\_.py, etc, no code should contaminate the users setup.py, nor package folder. No code should have to run in \_\_version\_\_.py or the like, for example, nothing like `__version__ = run_git_command_to_find_version()`, it should be equal to a constant. 

The use of jiggle_version should not increase the number of dependencies. (Not yet achieved- vendorizing a library isn't trivial)

Provide a vendorization option
------
It should be an effortless & license-compatible way to just copy this next to setup.py.

This isn't achieved yet. Python-world doesn't seem to have anything similar to JS minification or bundling.

Don't do too many things unrelated to versioning
------------------------------------------------
Don't run tests, create manifests, create a package, force checkins & tags, etc.

Provide a multiple interfaces
------
A build tool shouldn't assume any particular build system.

- _Bash:_ Command line - e.g. `jiggle_version here`
- _python_: import - e.g. `import jiggle_version; jiggle_version.go()`
- _setup.py_: plugin - e.g. 'setup.py jiggle_version', e.g.


    setup_requires=['jiggle_version'],
    use_jiggle_version=True,
    
or

    cmdclass=jiggle_version_command, # not yet implemented

Don't argue over a patch version
------
If multiple versions are detected, but are close, e.g. 1.2.3 and 1.2.4, just use 1.2.4.  This is the most common real world sync problem.

Don't force the developer to create irrelevant things
--------
For example, if there is no README.md, don't make me create one. 

Don't update natural language files
-----
There is no way to do this without programming-like configuration. Your README.md might say, "In versions 0.1.0 there were bugs and in 2.0.0 they were fixed." There is no way to update that string with a zero-config app.

Don't execute anything at post-deployment runtime
--------
Nothing succeeds as reliably as assigning a constant.

No matter how clever or well tested your code is, executing code
as post-deployment runtime is an additional dependency and failure point.

`__version__.py`:
```
version = query_pyi()
version = query_package_metadata()
version = search_for_and_read_text_or_config()
```



Automatically Bump "Minor"/"Path"/"Build", let user manually update "Major"
----------------
It should be uncommon to need record a big version change. You can do that manually. It would require AI to bump anything but the patch/build number.

 - Major - The change is big.
 - Minor - The change breaks compatibility. This might be detectable with a unit test runner,  or maybe even by detecting
changes to public interfaces (not that such a concept exists in python) but otherwise is too hard for machines.
 - Patch - This is the small number that increases each build. jiggle_version *only* solves the problem of incrementing this
number.

Files Targeted
--------------
TODO: any file with a `__version__` attribute. This is usally "single file" modules and possibly submodules.

/\_\_init\_\_.py  - `__version__ = "1.1.1"`

Other source files with version: `__about__.py', `__meta__.py', '_version.py' and `__version__.py` which I have a problem with.

I don't think `__version__.py` is any sort of standard and it makes for confusing imports, since in an app with a file and attribute named `__version__` you could easily confuse the two. 

version.txt - Some tools put/expect just the version string here. It works well with bash & doesn't require a parser of any sort.

/setup.cfg  

    [metadata] 
    version=1.1.1

If setup.py exists, setup.cfg is created.

`__init__.py` can't be created without making a breaking changes, so it isn't created, only updated.

We make no particular effort to parse wild text. If your current number is so messed up that you need regex to ID it,
then edit it by hand.

Flipside Question
-----------------
What version am I depending on? If you want to check the version of a dependency, you might be better off doing feature detection, i.e. check if name of some function exists and then use it.

    # Don't
    if some_lib.__version__ > Version("1.1.1"):
        some_lib.some_method()
    
    # Do
    try:
       some_lib.some_method
    except:
       some_method = fallback

Which Version Wins?
------------------
You can get a version from your git tag, from anyone of the existing .py or config files.

jiggle_version at the moment demands that all found versions match before bumping. There is no rational way to decide which version of a list of candidates is better.


Conflicts with Build Libraries
--------
If you use certain libraries, e.g. pbr, with jiggle_version you may have conflicts. All-in-one tools are most likely to conflict.

Weird Edge Cases
----------------
Multi-module packages
Submodules
Packages with no python

`__package_info__` Tuples
---------------
This is a standard piece of metadata. It should always derive from the `__version__`. In code in the wild, often this is yet another place to store a copy of the version.


Relevant PEPs
-------------
[Semantic Version](https://semver.org/) Outside of python-world, this is catching on. I *think* SemVer is a subset of PEP 440.
 
[440](https://www.python.org/dev/peps/pep-0440/) - Pythons most mature words on versions.

[PyPA's Advice](https://packaging.python.org/guides/single-sourcing-package-version/)

Some other peps that mention versions tangentially: [345](https://www.python.org/dev/peps/pep-0345/#version) and [396](https://www.python.org/dev/peps/pep-0396/#specification) which is deferred. 386 is superceded.


Parsing the complex Version Object
----------------------------------
There are many libraries for dealing with the version string as a rich structured object with meaningful parts and a PEP to conform to. jiggle_version itself relies on semantic_version.

- Semantic Version Centric
    - [semantic_version](https://pypi.org/project/semantic_version/)
- Pep 440 Centric
    - [Versio](https://pypi.org/project/Versio/) Supports PEP 440, 2 ad-hoc simple schemes and Perl versions. version.bump(). Micro-library- 2 files.
    - [pep440](https://pypi.org/project/pep440/) Is the version string pep440 valid. Microlib, 2 functions, 1 file.
    - [parver](https://pypi.org/project/parver/) PEP 440 centric. Version.bump_release() to increment
    - dist_utils.version - Has a version parsing and comparing object.
- Other
    - [cmp-version](https://pypi.org/project/cmp_version/) - Command line interface only(?) Release-General-Epoch scheme.
    
How are other people solving this problem?
------------------------------------------

| PyPi        | Source Code     | Docs  |
| ------------- |-------------| -----|
| __      | [python-versioneer](https://github.com/warner/python-versioneer) | ___ |
| __      | [python-git-version](https://github.com/aebrahim/python-git-version)      |   ___ |
| [git-bump-version](https://pypi.org/project/git-bump-version/) | ___      |    ___ |
| [pyver](https://pypi.org/project/pyver/) | ___      |    ___ |
| [setupext-gitversion](https://pypi.org/project/setupext-gitversion/) | ___      |    ___ |
| __ | [python-git-version](https://github.com/aebrahim/python-git-version)       |    ___ |
| [git-bump-version](https://pypi.org/project/git-bump-version/) | [git_bump_version](https://github.com/silent-snowman/git_bump_version)       |    ___ |
| [pyver](https://pypi.org/project/pyver/) | [pyver](https://github.com/clearclaw/pyver) | ___ |
| [vdt.version](https://pypi.org/project/vdt.version/) | [vdt.version](https://github.com/devopsconsulting/vdt.version) | ___ |


Git Centric
-----------
These all either run `git describe --tags` to find a version or `git tag %` to bump a version.

 - Git/VCS centric - setup.py plugins
    - [python-versioneer](https://github.com/warner/python-versioneer) Git tags hold canonical version. Setup.py plugin command. `versioneer install`. Vendorizes itself to your souce tree. Edit `setup.py` and `setup.cfg`. Run `python versioneer.py setup` This adds a lot of code to your source tree. Has bug where it only works if the version code file is _version.py. This was just very twitchy to setup. Library code has to run to get the version, e.g. ` python -c "import ver_test1; print(ver_test1.\_\_version\_\_)"` Personally, I don't like how this library infects the production release. I'd rather my build dependencies gone by final release.
    - [setupext-gitversion](https://pypi.org/project/setupext-gitversion/) Git tag driven version bumping. Pep440. Requires [git_version] section in setup.cfg, add `from setupext import gitversion` and wire up a plug-in, then to run, `python setup.py git_version` I couldn't evaluate further because it blew up inspecting my git repo.

- Git/VCS centric
    - [python-git-version](https://github.com/aebrahim/python-git-version) Git holds canonical version. Library is expected to be vendorized (copied next to your setup.py). Code runs in \_\_version\_\_. ` python version.py` returns version found in tag. EXxecute with `python setup.py sdist` - as far as I can tell, it specifies the package version and doesn't expect to be used from code after deployment. 

    - [pyver](https://pypi.org/project/pyver/) SUPERCEDED BY *versioneer* Pep440. Expects tag to already exist. Invoked in setup.py, used for package version.

    - [katversion](https://pypi.org/project/katversion/) Implemented as setup.py 'extension'. Expects \_\_init\_\_.py to exist. Ignores \_\_init\_\_.py and does not update the \_\_version\_\_ value. Does update package version with string drived from git tags and history.

    - [zest releaser](http://zestreleaser.readthedocs.io/en/latest/) - VCS driven versionbump command
    
    - [vdt](https://pypi.org/project/vdt.version/) Git and Jenkins centric version bumping with other actions built in. Command line `version`. Python 2 only. I'm not going to have time to test it out.
    
    - [pbr](https://pypi.org/project/pbr/) - quirky git tag driven version bumping and a bunch of other things. You can't turn off the version bumping, so it will conflict with any other version bumper you use. Appears to affect package version, the one you see in the /dist/ folder.
    
    - bumpversion & bump2version - I don't know how this works. Frustration trying to get bumpversion to work at all drove me to create jiggle-version. bump2version is a fork for fixing bugs because bumpversion is/was dormant. Not linking until the maintainers return 6 hours of my life that they stole.
    
- Only Git Tags
    - [git-bump-version](https://pypi.org/project/git-bump-version/) Command line `git_bump_version` searches for last tag and tags current. Blows up on "v1.2.3" As far as I can tell, this code is agnostic to what your source code is, i.e. it doesn't edit \_\_version\_\_.py, etc.

- Other VCS
    - [mercurial_update_version](https://pypi.org/project/mercurial_update_version/) Merucrial holds your canonical version. Not going to test...I don't use
    - [setuptools_scm](https://pypi.org/project/setuptools_scm/) Git & mercurial. Gets version from tag.  Add this to setup() in setup.py :`use_scm_version=True, setup_requires=['setuptools_scm'],` No version strings in source at all & package still builds to /dist/ with expected version.
    
        

| PyPi        | Source Code     | Docs  |
| ------------- |-------------| -----|
| __      | [changes](https://github.com/michaeljoseph/changes) | ___ |
| [pylease](https://pypi.org/project/pylease/) | [repo here](https://github.com/bagrat/pylease)| ___ |
| [metapensiero.tool.bump_version](https://pypi.org/project/metapensiero.tool.bump_version/) | [metapensiero.tool.bump_version](https://pypi.org/project/metapensiero.tool.bump_version/) | ___ |

 Source Centric
 --------------
 Source centric version bumpers read and update .py or config files. They do not necessarily require or expect you to have source control tagging going on.
 
  - Source Centric -- `\_\_init\_\_.py` or `\_\_version\_\_.py`
    - [changes](https://github.com/michaeljoseph/changes) - Does many release related things. `changes my_module bump_version` to bump version, but this code will not run unless readme.md exists, etc. Detect version from source. Does not suggest new version, you must manually type it.
    - [pylease](https://pypi.org/project/pylease/) Version bumper, release tool [repo here](https://github.com/bagrat/pylease) Not python 3 compatible (blows up on CondigParser on pip install)

  
  - Source Centric - `Version.txt`
    - [metapensiero.tool.bump_version](https://pypi.org/project/metapensiero.tool.bump_version/) Version.txt manager. Looks like it avoids dealing with any python source code, etc. Command line only, supports 4 schemes : auto,pep440,simple2,simple3,simple4. Usage: `bump_version -s simple3 -f tiny
`
  - Source Centric - `setup.py`, e.g. `python setup.py --version`
    - [incremental](https://pypi.org/project/incremental/) `_version.py` updator. If I understand, this lib becomes a dependency of your release app, i.e. it isn't just a build dependency. Pep440 only. Usage `python -m incremental.update my_module --patch`


Version Finders
---------------

- VCS centric
  - [version_hunter](https://pypi.org/project/version-hunter/) Seems to be more focused on finding a version from a source code tree & not in bumping it.

  - [git-version](https://pypi.org/project/git-version/) Version finding from your git repo
 
  - [tcversioner](https://pypi.org/project/tcversioner/) Find version via vcs tag. Writes version.txt

- Source Tree centric
  - [get_version](https://pypi.org/project/get_version/) Searches source tree? Local pip package?
  - [bernardomg.version-extractor](https://pypi.org/project/bernardomg.version-extractor/) Extract version from source code. 2 functions (microlib) that find \_\_version\_\_ inside of \_\_init\_\_.py
 - Other-
    - [package_version pypi](https://pypi.org/project/package-version/) - [package_version](https://github.com/Yuav/python-package-version) Assume pypi has your canoncial version, use pip to find the last version to bump.
    - [setuptools-requirements-vcs-version](https://github.com/danielbrownridge/setuptools-requirements-vcs-version) Find version in requirements.txt found by searching git url! Not sure what scenario this is for.

Django
------
[django-fe-version](https://pypi.org/project/django-fe-version/) Adds a /version/ endpoint to your web app.

[django-project-version](https://pypi.org/project/django-project-version/) same..

