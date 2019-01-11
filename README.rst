jiggle_version
==============

Opinionated, no config build version incrementer. No regex. Drop in and
go.

::

    pip install jiggle_library

    cd src
    # should run from same folder with setup.py
    # or parent folder of my_module/__init__.py

    jiggle_library here
    # find, bump & update version strings in source code

    jiggle_version here --module=my_module
    # specify which module.

    git --tag $(jiggle_library find)

Depends on cmp-version, docopt, parver, semantic-version, versio, which
your application is unlikely to depend on.

Problem to be solved
--------------------

There are up to 1/2 dozen places to update a version string. You scoff,
‘Can’t be!’ But for a mature code base, it is because so many tools
expect version strings in different places:

-  \__init__.py has \__version_\_
-  so does \__version__.py
-  so does the setup function in setup.py
-  so does the setup.cfg if you are doing config driven setup.py
-  your git repo might need a tag matching the library version
-  you might need a plain text version.txt

You will need to find the current version, bump the most minor part-
which varies depending on if you are using pep440, semantic version or
something else, update all the places where you could update and re-do
this as often as each build and at least as often as each package and
push to pypi.

Opinionated
-----------

A library should have one working, no-options, no questions asked
scenario, e.g.

::

    jiggle_library here
    # find, bump & update version strings in source code

An opinionated library has an opinion about the right way to do it. That
said, if the library can discover existing conventions, it should
discover them and use them. If you don’t like it, see the end for
competing opinionated libraries and their philosophy, such as
vcs-tag-only, regex-more-regex-all-day-regex.

The following contraints enable “drop in and go”

No Config, No Regex
-------------------

If the config is more complex than re-writing the code from scratch,
there is something wrong with a library.

Don’t contaminate the package
-----------------------------

Other than creating \__init__.py, \__version__.py, etc, no code should
contaminate the users setup.py, nor package folder. No code should have
to run in \__version__.py or the like, for example, nothing like
``__version__ = run_git_command_to_find_version()``, it should be equal
to a constant.

The use of jiggle_version should not increase the number of
dependencies. (Not yet achieved- vendorizing a library isn’t trivial)

Provide a vendorization option
------------------------------

It should be an effortless & license-compatible way to just copy this
next to setup.py.

This isn’t achieved yet. Python-world doesn’t seem to have anything
similar to JS minification or bundling.

Don’t do too many things unrelated to versioning
------------------------------------------------

Don’t run tests, create manifests, create a package, force checkins &
tags, etc.

Provide a multiple interfaces
-----------------------------

A build tool shouldn’t assume any particular build system.

-  *Bash:* Command line - e.g. ``jiggle_version here``
-  *python*: import - e.g.
   ``import jiggle_version; jiggle_version.go()``
-  *setup.py*: plugin - e.g. ‘setup.py jiggle_version’, e.g.

   setup_requires=[‘jiggle_version’], use_jiggle_version=True,

or

::

    cmdclass=jiggle_version_command, # not yet implemented

Don’t argue over a patch version
--------------------------------

If multiple versions are detected, but are close, e.g. 1.2.3 and 1.2.4,
just use 1.2.4. This is the most common real world sync problem.

Don’t force the developer to create irrelevant things
-----------------------------------------------------

For example, if there is no README.md, don’t make me create one.

Don’t update natural language files
-----------------------------------

There is no way to do this without programming-like configuration. Your
README.md might say, “In versions 0.1.0 there were bugs and in 2.0.0
they were fixed.” There is no way to update that string with a
zero-config app.

Don’t execute anything at post-deployment runtime
-------------------------------------------------

Nothing succeeds as reliably as assigning a constant.

No matter how clever or well tested your code is, executing code as
post-deployment runtime is an additional dependency and failure point.

``__version__.py``:

::

    version = query_pyi()
    version = query_package_metadata()
    version = search_for_and_read_text_or_config()

Automatically Bump “Minor”/“Path”/“Build”, let user manually update “Major”
---------------------------------------------------------------------------

It should be uncommon to need record a big version change. You can do
that manually. It would require AI to bump anything but the patch/build
number.

-  Major - The change is big.
-  Minor - The change breaks compatibility. This might be detectable
   with a unit test runner, or maybe even by detecting changes to public
   interfaces (not that such a concept exists in python) but otherwise
   is too hard for machines.
-  Patch - This is the small number that increases each build.
   jiggle_version *only* solves the problem of incrementing this number.

Files Targeted
--------------

TODO: any file with a ``__version__`` attribute. This is usally “single
file” modules and possibly submodules.

/__init__.py - ``__version__ = "1.1.1"``

Other source files with version: ``__about__.py',``\ **meta**.py’,
’_version.py’ and ``__version__.py`` which I have a problem with.

I don’t think ``__version__.py`` is any sort of standard and it makes
for confusing imports, since in an app with a file and attribute named
``__version__`` you could easily confuse the two.

version.txt - Some tools put/expect just the version string here. It
works well with bash & doesn’t require a parser of any sort.

/setup.cfg

::

    [metadata] 
    version=1.1.1

If setup.py exists, setup.cfg is created.

``__init__.py`` can’t be created without making a breaking changes, so
it isn’t created, only updated.

We make no particular effort to parse wild text. If your current number
is so messed up that you need regex to ID it, then edit it by hand.