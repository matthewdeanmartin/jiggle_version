#!/usr/bin/env bash
export PYTHONPATH="$PYTHONPATH":..

pipenv run python -m jiggle_version --source=../sample_src/ --project=sample_lib

pipenv run python -m jiggle_version here