# jiggle_version
Opinionated, no config build version incrementer. No regex. Drop in and go.

Opinionated
-----------
There already are two ways to "do it the way you want to": 

- write your own bumpversion library from scratch
- configure bumpversion, which has no opinions, you must provide all behavior via config

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

/setup.cfg  version=1.1.1

We take the first of these, increment the patch, and re-write those 3 files. If they don't exist, they will be created
with only the version number filled in.

We make no particular effort to parse wild text. If your current number is so messed up that you need regex to ID it,
then edit it by hand.



