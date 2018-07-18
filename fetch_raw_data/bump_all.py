import os
import sys
import subprocess
import random

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def execute_get_text(command, dir):
    try:
        completed = subprocess.run(
            command,
            check=True,
            shell=True,
            stdout=subprocess.PIPE,
            cwd="packages/{0}".format(dir)
        )
    except subprocess.CalledProcessError as err:
        # dupe.
        # print(err.stdout)
        raise
    else:
        return completed.stdout.decode('utf-8')

things = [x for x in os.listdir("packages")]
random.shuffle(things)
for dir in things:
    if dir.endswith(".gz") or dir.endswith(".zip"):
        continue
    if ".DS_Store" in dir:
        continue
    command = "python3 -m jiggle_version here"
    print("---{0}---".format(dir))
    try:
        _ = execute_get_text(command, dir)
    except subprocess.CalledProcessError as cpe:
        continue

