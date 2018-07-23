# coding=utf-8
"""
How to read version from a well behaved module.

So you have bumped a version, how do you use it?

Scenario groups:
packaging actions - e.g. creating, installing or updating a package.
runtime actions - e.g. using a module's version at runtime
runtime package actions - e.g. A package can have many modules, so you may need a package API

"""

import single_module_example as example

# runtime examples
print()
print("Common scenario- communicating to user or maintenance developer which verson of an module did something, in a log, or UI screen")
# PEP recommeded names and places
print("Logging version : " + example.__version__)
print("Logging version info : " + str(example.__version_info__))

print()
print("Common scenario- is the version installed capable of doing x, y or z?")
print("Use feature testing if possible. If not, fall back to comparing versions.")
# standard lib comparisons, sort of safe
print()
print("Sometimes safe comparison with tuples")
if example.__version_info__ < (1,2,1):
    print("Installed version is less than (1,2,1). Actual installed " +str(example.__version_info__))
elif example.__version_info__ > (1, 2, 1):
    print("Installed version is more than (1,2,1). Actual installed " + str(example.__version_info__))
else:
    print('Versions the same')

print()
print("Safe comparisons with string version")
if example.__version__ == "1.2.3":
    print('Versions the same')
else:
    print("String form of version isn't orderable")

print()
print("To order versions safely, you need to know the schema & use a library, e.g. semantic_version, version, parver")

