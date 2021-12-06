# jiggle_version
Version bumper that finds version numbers in source code and increases the build number by modifying source.

With jiggle-version, the source code is authoritative, as compared to some tools where the source control
tag is authoritative, or the pyproject.toml is authoritative. You should consider instead using `poetry version patch` and looking up the `__version__` from the 
package metadata.

Special attention to making sure you don't have to write regex or do complex configuration.

    pip install jiggle-version
     
    jiggle-version here
    # find, bump & update version strings in source code
    
    jiggle_version here --module=my_module
    
    git --tag $(jiggle-version find)

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

    jiggle-version here
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