# coding=utf-8
"""
Get some sample version strings from the wild.
"""
# https://python-forum.io/Thread-pip-list-available-packages

# download file
# curl!

# parse out version strings

# https://pypi.org/simple/epicurus/

import requests
import os
import subprocess

def execute_get_text(command):
    try:
        result = subprocess.check_output(
            command,
            stderr=subprocess.STDOUT,
            shell=True)
    except subprocess.CalledProcessError as err:
        raise

    return result


def download_package(rows):
    url = package_info(rows)
    if url =="nozips":
        print("no zips")
        return
    base = os.path.basename(url).split("#")[0]
    if os.path.isfile("packages/{0}".format(base)):
        print("Already have packages/{0}".format(base))
        return
    command ="curl -0 {0} -o packages/{1}".format(url, base)
    print(command)
    result = execute_get_text(command)
    print(result)


def package_info(rows):
    last = "nozips"
    for row in rows:
        try:
            url =row.split("\"")[1]
            if ".zip" in url or ".gz" in url:
                print(url)
                last = url
        except:
            pass
    return last

def done_packages():
    packages = []
    for dir in os.listdir("packages"):
        if dir.endswith(".gz") or dir.endswith(".zip"):
            continue
        packages.append(dir)
    print("Have " + str(len(packages)) + " packages")
    return packages


def read_packages():
    i = 0
    done = done_packages()
    for row in open("packages.html"):
        try:
            url = "https://pypi.org" + row.split("\"")[1]
            package_name = row.split("\"")[1].replace("simple/","").replace("/","")
            if package_name in done:
                continue
            print(url)
        except:
            continue

        response = requests.get(url)

        with open("meta/" + url.split("/")[-2], "w") as file:
            download_package(response.text.split("\n"))
            # file.write(response.text)

        i += 1
        if i>1000:
            exit(1)
read_packages()



