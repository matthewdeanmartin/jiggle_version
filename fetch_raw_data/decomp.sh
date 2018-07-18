#!/usr/bin/env bash

cd packages
unzip "*.zip"

for a in `ls -1 *.tar.gz`; do gzip -dc $a | tar xf -; done
