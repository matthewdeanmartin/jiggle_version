# jiggle_version
Opinionated, no config build version incrementer. No regex. Drop in and go.

    pip install jiggle_library
    
    cd src
    # should run from same folder with setup.py
    # or parent folder of my_module/__init__.py
    
    jiggle_library here
    # find, bump & update version strings in source code
    
    jiggle_version here --module=my_module
    # specify which module.
    
    git --tag $(jiggle_library find)

Depends on cmp-version, docopt, parver, semantic-version, versio, which your application is unlikely to depend on.

Badges
------

How's it doing?

 ![Read the Docs](https://img.shields.io/readthedocs/pip.svg) 
 [![Coverage Status](https://coveralls.io/repos/github/matthewdeanmartin/jiggle_version/badge.svg?branch=master)](https://coveralls.io/github/matthewdeanmartin/jiggle_version?branch=master)
 [![BCH compliance](https://bettercodehub.com/edge/badge/matthewdeanmartin/jiggle_version?branch=master)](https://bettercodehub.com/) 
 [![Known Vulnerabilities](https://snyk.io/test/github/matthewdeanmartin/jiggle_version/badge.svg?targetFile=requirements.txt)](https://snyk.io/test/github/matthewdeanmartin/jiggle_version?targetFile=requirements.txt)
 [![Total Alerts](https://img.shields.io/lgtm/alerts/g/matthewdeanmartin/jiggle_version.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/matthewdeanmartin/jiggle_version/alerts/)
 [![CodeFactor](https://www.codefactor.io/repository/github/matthewdeanmartin/jiggle_version/badge)](https://www.codefactor.io/repository/github/matthewdeanmartin/jiggle_version)

Python Versions Supported
-------------------------
3.6, 3.7, 3.8, and forward. Pypi still hosts the old version that supported python 2 and earlier.


Opinionated
-----------
A library should have one working, no-options, no questions asked scenario, e.g.

    jiggle_library here
    # find, bump & update version strings in source code

An opinionated library has an opinion about the right way to do it. That said, if the library can discover existing conventions, it should discover them and use them. If you don't like it, see the end for competing opinionated libraries and their philosophy, such as vcs-tag-only, regex-more-regex-all-day-regex.

The following contraints enable "drop in and go"

No Config, No Regex
-------------------
If the config is more complex than re-writing the code from scratch, there is something wrong with a library. Forcing
the developer to write regex to use a utility is a collosal cop out.

Documentation
-------------
- [Design Philosophy](docs/design_philosophy.md)
- [Prior Art](docs/prior_art.md)
- [TODO](docs/todo.md)
- [Authors](docs/AUTHORS)
- [ChangeLog](docs/ChangeLog)
- [Code of Conduct](docs/CODE_OF_CONDUCT.md)