jiggle_version
==============

Opinionated, no config build version incrementer. No regex. Drop in and
go.

Badges
------

|MIT licensed| |Read the Docs| |Travis| |Coverage Status| |BCH
compliance|

Opinionated
-----------

It is a design smell that a library opens with asking you a lot of
questions or to fill in a lot of twitchy config before simple scenarious
work.

An opinionated library has an opinion about the right way to do it. That
said, if the library can discover existing conventions, it should
discover them and used them.

Other libraries with different opinions exist, see below.

No Config, No Regex
-------------------

If the config is more complex than re-writing the code from scratch,
there is something wrong with a library.

These contraints enable “drop in and go”

Don’t contaminate the package
-----------------------------

Other than creating **init**.py, **version**.py, etc, no code should
contaminate the users setup.py, nor package folder. No code should have
to run in **version**.py or the like, for example, nothing like
``__version__ = run_git_command_to_find_version()``, it should be equal
to a constant. The use of jiggle_version should not increase the number
of dependencies.

Provide a vendorization option
------------------------------

It should be an effortless & license-compatible way to just copy this
next to setup.py

Don’t do too many things unrelated to versioning
------------------------------------------------

Don’t run tests, create manifests, etc.

Provide a multiple interfaces
-----------------------------

-  Command line - e.g. ``jiggle_version here``
-  import - e.g. ``import jiggle_version; jiggle_version.go()``
-  setup plugin - e.g. ‘setup.py jiggle_version’, e.g.

   setup_requires=[‘jiggle_version’], use_jiggle_version=True,

or

::

    cmdclass=jiggle_version_command,

Don’t force the developer to create irrelevant things
-----------------------------------------------------

For example, if there is no README.md, don’t make me create one.

Don’t update natural language files
-----------------------------------

There is no way to do this without programming-like configuration. Your
README.md might say, “In versions 0.1.0 there were bugs and in 2.0.0
they were fixed.” There is no way to update that string with a
zero-config app.

Build Incremeter
----------------

-  Major - The change is big.
-  Minor - The change breaks compatibility. This might be detectable
   with a unit test runner, or maybe even by detecting changes to public
   interfaces (not that such a concept exists in python) but otherwise
   is too hard for machines.
-  Patch - This is the small number that increases each build.
   jiggle_version *only* solves the problem of incrementing this number.

Files Targeted
--------------

/**init**.py - **version** = “1.1.1”

/**version**.py - **version** = “1.1.1”

TODO: \_version.py - I think this is a place to pipe a version string
from a version control system that isn’t expected to be executable? Not
sure. It is a common convention. Versioneer puts library code here.

TODO: version.txt - Some tools put/expect just the version string here.

/setup.cfg version=1.1.1

We take the first of these, increment the patch, and re-write those 3
files. If they don’t exist, they will be created with only the version
number filled in.

We make no particular effort to parse wild text. If your current number
is so messed up that you need regex to ID it, then edit it by hand.

Other way to get/provide version:

https://stackoverflow.com/questions/7079735/how-do-i-get-the-version-of-an-installed-module-in-python-programatically

::

    import pkg_resources
    version = pkg_resources.get_distribution("nose").version

Flipside Question
-----------------

What version am I depending on? If you want to check the version of a
dependency, you might be better off doing feature detection, i.e. check
if name of some function exists and then use it.

Which Version Wins?
-------------------

You can get a version from your git tag, from anyone of the existing .py
or config files.

I think the tagger should set tags based on what is in the
**version**.py file. Forcing the user to check in, tag and so on before
bumping a version is no fun.

Relevant PEPs
-------------

Semantic Version - https://semver.org/ - Outside of python-world, this
is catching on.

345 - https://www.python.org/dev/peps/pep-0345/#version

386 - SUPERCEDED https://www.python.org/dev/peps/pep-0386/

396- https://www.python.org/dev/peps/pep-0396/#specification

440 - https://www.python.org/dev/peps/pep-0440/ - Most libraries use
this.

Conflicts
---------

If you use pbr or bumpversion with jiggle_version you may have
conflicts. All-in-one tools are most likely to conflict.

How are other people solving this problem?
------------------------------------------

+-----------------------+-----------------------+-----------------------+
| PyPi                  | Source Code           | Docs                  |
+=======================+=======================+=======================+
| \_\_                  | `python-versioneer <h | \__\_                 |
|                       | ttps://github.com/war |                       |
|                       | ner/python-versioneer |                       |
|                       | >`__                  |                       |
+-----------------------+-----------------------+-----------------------+
| \_\_                  | `python-git-version < | \__\_                 |
|                       | https://github.com/ae |                       |
|                       | brahim/python-git-ver |                       |
|                       | sion>`__              |                       |
+-----------------------+-----------------------+-----------------------+
| `git-bump-version <ht | \__\_                 | \__\_                 |
| tps://pypi.org/projec |                       |                       |
| t/git-bump-version/>` |                       |                       |
| __                    |                       |                       |
+-----------------------+-----------------------+-----------------------+
| `pyver <https://pypi. | \__\_                 | \__\_                 |
| org/project/pyver/>`_ |                       |                       |
| _                     |                       |                       |
+-----------------------+-----------------------+-----------------------+
| `setupext-gitversion  | \__\_                 | \__\_                 |
| <https://pypi.org/pro |                       |                       |
| ject/setupext-gitvers |                       |                       |
| ion/>`__              |                       |                       |
+-----------------------+-----------------------+-----------------------+
| \_\_                  | `python-git-version < | \__\_                 |
|                       | https://github.com/ae |                       |
|                       | brahim/python-git-ver |                       |
|                       | sion>`__              |                       |
+-----------------------+-----------------------+-----------------------+
| `git-bump-version <ht | `git_bump_version <ht | \__\_                 |
| tps://pypi.org/projec | tps://github.com/sile |                       |
| t/git-bump-version/>` | nt-snowman/git_bump_v |                       |
| __                    | ersion>`__            |                       |
+-----------------------+-----------------------+-----------------------+
| `pyver <https://pypi. | `pyver <https://githu | \__\_                 |
| org/project/pyver/>`_ | b.com/clearclaw/pyver |                       |
| _                     | >`__                  |                       |
+-----------------------+-----------------------+-----------------------+
| `vdt.version <https:/ | `vdt.version <https:/ | \__\_                 |
| /pypi.org/project/vdt | /github.com/devopscon |                       |
| .version/>`__         | sulting/vdt.version>` |                       |
|                       | __                    |                       |
+-----------------------+-----------------------+-----------------------+

Git Centric
-----------

These all either run ``git describe --tags`` to find a version or
``git tag %`` to bump a version.

-  Git/VCS centric - setup.py plugins

   -  `python-versioneer <https://github.com/warner/python-versioneer>`__
      Git tags hold canonical version. Setup.py plugin command.
      ``versioneer install``. Vendorizes itself to your souce tree. Edit
      ``setup.py`` and ``setup.cfg``. Run ``python versioneer.py setup``
      This adds a lot of code to your source tree. Has bug where it only
      works if the version code file is \_version.py. This was just very
      twitchy to setup. Library code has to run to get the version, e.g.
      ``python -c "import ver_test1; print(ver_test1.__version__)"``
      Personally, I don’t like how this library infects the production
      release. I’d rather my build dependencies gone by final release.
   -  `setupext-gitversion <https://pypi.org/project/setupext-gitversion/>`__
      Git tag driven version bumping. Pep440. Requires [git_version]
      section in setup.cfg, add ``from setupext import gitversion`` and
      wire up a plug-in, then to run, ``python setup.py git_version`` I
      couldn’t evaluate further because it blew up inspecting my git
      repo.

-  Git/VCS centric

   -  `python-git-version <https://github.com/aebrahim/python-git-version>`__
      Git holds canonical version. Library is expected to be vendorized
      (copied next to your setup.py). Code runs in **version**.
      ``python version.py`` returns version found in tag. EXxecute with
      ``python setup.py sdist`` - as far as I can tell, it specifies the
      package version and doesn’t expect to be used from code after
      deployment.

   -  `pyver <https://pypi.org/project/pyver/>`__ SUPERCEDED BY
      *versioneer* Pep440. Expects tag to already exist. Invoked in
      setup.py, used for package version.

   -  `katversion <https://pypi.org/project/katversion/>`__ Implemented
      as setup.py ‘extension’. Expects **init**.py to exist. Ignores
      **init**.py and does not update the **version** value. Does update
      package version with string drived from git tags and history.

   -  `zest releaser <http://zestreleaser.readthedocs.io/en/latest/>`__
      - VCS driven versionbump command

   -  `vdt <https://pypi.org/project/vdt.version/>`__ Git and Jenkins
      centric version bumping with other actions built in. Command line
      ``version``. Python 2 only. I’m not going to have time to test it
      out.

   -  `pbr <https://pypi.org/project/pbr/>`__ - quirky git tag driven
      version bumping and a bunch of other things. You can’t turn off
      the version bumping, so it will conflict with any other version
      bumper you use. Appears to affect package version, the one you see
      in the /dist/ folder.

   -  bumpversion & bump2version - I don’t know how this works.
      Frustration trying to get bumpversion to work at all drove me to
      create jiggle-version. bump2version is a fork for fixing bugs
      because bumpversion is/was dormant. Not linking until the
      maintainers return 6 hours of my life that they stole.

-  Only Git Tags

   -  `git-bump-version <https://pypi.org/project/git-bump-version/>`__
      Command line ``git_bump_version`` searches for last tag and tags
      current. Blows up on “v1.2.3” As far as I can tell, this code is
      agnostic to what your source code is, i.e. it doesn’t edit
      **version**.py, etc.

-  Other VCS

   -  `mercurial_update_version <https://pypi.org/project/mercurial_update_version/>`__
      Merucrial holds your canonical version. Not going to test…I don’t
      use

+-----------------------+-----------------------+-----------------------+
| PyPi                  | Source Code           | Docs                  |
+=======================+=======================+=======================+
| \_\_                  | `changes <https://git | \__\_                 |
|                       | hub.com/michaeljoseph |                       |
|                       | /changes>`__          |                       |
+-----------------------+-----------------------+-----------------------+
| `pylease <https://pyp | `repo                 | \__\_                 |
| i.org/project/pylease | here <https://github. |                       |
| />`__                 | com/bagrat/pylease>`_ |                       |
|                       | _                     |                       |
+-----------------------+-----------------------+-----------------------+
| `metapensiero.tool.bu | `metapensiero.tool.bu | \__\_                 |
| mp_version <https://p | mp_version <https://p |                       |
| ypi.org/project/metap | ypi.org/project/metap |                       |
| ensiero.tool.bump_ver | ensiero.tool.bump_ver |                       |
| sion/>`__             | sion/>`__             |                       |
+-----------------------+-----------------------+-----------------------+

+-----------------------------------------------------------------------+
| Source Centric                                                        |
+=======================================================================+
| Source centric version bumpers read and update .py or config files.   |
| They do not necessarily require or expect you to have source control  |
| tagging going on.                                                     |
+-----------------------------------------------------------------------+

-  Source Centric – ``__init__.py`` or ``__version__.py``

   -  `changes <https://github.com/michaeljoseph/changes>`__ - Does many
      release related things. ``changes my_module bump_version`` to bump
      version, but this code will not run unless readme.md exists, etc.
      Detect version from source. Does not suggest new version, you must
      manually type it.
   -  `pylease <https://pypi.org/project/pylease/>`__ Version bumper,
      release tool `repo here <https://github.com/bagrat/pylease>`__ Not
      python 3 compatible (blows up on CondigParser on pip install)

-  Source Centric - ``Version.txt``

   -  `metapensiero.tool.bump_version <https://pypi.org/project/metapensiero.tool.bump_version/>`__
      Version.txt manager. Looks like it avoids dealing with any python
      source code, etc. Command line only, supports 4 schemes :
      auto,pep440,simple2,simple3,simple4. Usage:
      ``bump_version -s simple3 -f tiny``

-  Source Centric - ``setup.py``, e.g. ``python setup.py --version``

   -  `incremental <https://pypi.org/project/incremental/>`__
      ``_version.py`` updator. If I understand, this lib becomes a
      dependency of your release app, i.e. it isn’t just a build
      dependency. Pep440 only. Usage
      ``python -m incremental.update my_module --patch``

Parsing the complex Version Object
----------------------------------

There are many libraries for dealing with the version string as a rich
structured object with meaningful parts and a PEP to conform to.
jiggle_version itself relies on semantic_version.

-  Semantic Version Centric

   -  `semantic_version <https://pypi.org/project/semantic_version/>`__

-  Pep 440 Centric

   -  `Versio <https://pypi.org/project/Versio/>`__ Supports PEP 440, 2
      ad-hoc simple schemes and Perl versions. version.bump().
      Micro-library- 2 files.
   -  `pep440 <https://pypi.org/project/pep440/>`__ Is the version
      string pep440 valid. Microlib, 2 functions, 1 file.
   -  `parver <https://pypi.org/project/parver/>`__ PEP 440 centric.
      Version.bump_release() to increment
   -  dist_utils.version - Has a version parsing and comparing object.

-  Other

   -  `cmp-version <https://pypi.org/project/cmp_version/>`__ - Command
      line interface only(?) Release-General-Epoch scheme.

Version Finders
---------------

-  VCS centric

   -  `version_hunter <https://pypi.org/project/version-hunter/>`__
      Seems to be more focused on finding a version from a source code
      tree & not in bumping it.

   -  `git-version <https://pypi.org/project/git-version/>`__ Version
      finding from your git repo

   -  `tcversioner <https://pypi.org/project/tcversioner/>`__ Find
      version via vcs tag. Writes version.txt

-  Source Tree centric

   -  `get_version <https://pypi.org/project/get_version/>`__ Searches
      source tree? Local pip package?
   -  `bernardomg.version-extractor <https://pypi.org/project/bernardomg.version-extractor/>`__
      Extract version from source code. 2 functions (microlib) that find
      **version** inside of **init**.py

-  Other-

   -  `package_version
      pypi <https://pypi.org/project/package-version/>`__ -
      `package_version <https://github.com/Yuav/python-package-version>`__
      Assume pypi has your canoncial version, use pip to find the last
      version to bump.
   -  `setuptools-requirements-vcs-version <https://github.com/danielbrownridge/setuptools-requirements-vcs-version>`__
      Find version in requirements.txt found by searching git url! Not
      sure what scenario this is for.

Django
------

`django-fe-version <https://pypi.org/project/django-fe-version/>`__ Adds
a /version/ endpoint to your web app.

`django-project-version <https://pypi.org/project/django-project-version/>`__
same..

.. |MIT licensed| image:: https://img.shields.io/badge/license-MIT-blue.svg
   :target: https://raw.githubusercontent.com/hyperium/hyper/master/LICENSE
.. |Read the Docs| image:: https://img.shields.io/readthedocs/pip.svg
.. |Travis| image:: https://travis-ci.com/matthewdeanmartin/jiggle_version.svg?branch=master
.. |Coverage Status| image:: https://coveralls.io/repos/github/matthewdeanmartin/jiggle_version/badge.svg?branch=master
   :target: https://coveralls.io/github/matthewdeanmartin/jiggle_version?branch=master
.. |BCH compliance| image:: https://bettercodehub.com/edge/badge/matthewdeanmartin/jiggle_version?branch=master
   :target: https://bettercodehub.com/
