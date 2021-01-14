Problem to be solved
-------------------
There are up to 1/2 dozen places to update a version string. You scoff, 'Can't be!' But for a mature code base, it is
because so many tools expect version strings in different places:

- \_\_init\_\_.py has \_\_version\_\_
- so does \_\_version\_\_.py
- so does the setup function in setup.py
- so does the setup.cfg if you are doing config driven setup.py
- your git repo might need a tag matching the library version
- you might need a plain text version.txt

You will need to find the current version, bump the most minor part- which varies depending on if you are using pep440, semantic version or something else, update all the places where you could update and
re-do this as often as each build and at least as often as each package and push to pypi. 

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
