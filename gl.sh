#!/usr/bin/env bash
export GOPATH=$HOME/gocode
export PATH=$PATH:$GOPATH/bin
# TO INSTALL
# go get -u -v -fix github.com/zricethezav/gitleaks

# finds nothing!
# gitleaks --github-user=matthewdeanmartin

# fails!
gitleaks --repo-path=/Users/martinmat/GitKraken/jiggle_version/

# works! Finds only 1 thing!
#gitleaks --repo-path=/Users/martinmat/GitKraken/takoma/ --report=/Users/martinmat/.burson_secrets/data.csv
#gitleaks --repo-path=/Users/martinmat/GitKraken/takoma_mapper/ --report=/Users/martinmat/.burson_secrets/data2.csv
#gitleaks --repo-path=/Users/martinmat/GitKraken/takoma_workers/ --report=/Users/martinmat/.burson_secrets/data3.csv

# unusably slow!
# gitleaks --repo-path=/Users/martinmat/code/db_ts/burson_tools --report=/Users/martinmat/.burson_secrets/data4.csv

# fails! no clear way to set credentials!
# gitleaks --github-org=Burson-Marsteller
# --repo=https://github.com/Burson-Marsteller/takoma
# --entropy=4
