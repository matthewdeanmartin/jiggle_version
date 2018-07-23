#!/usr/bin/env bash
rm -rf /tmp/freezer
mkdir /tmp/freezer
mkdir /tmp/freezer/jiggle_version
cp -r ./jiggle_version/ /tmp/freezer/jiggle_version/
cp ./Pipfile_nodev /tmp/freezer/Pipfile
cd /tmp/freezer
pipenv lock
pipenv lock -r
rm -rf /tmp/freezer