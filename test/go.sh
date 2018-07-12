#!/usr/bin/env bash
export PYTHONPATH="$PYTHONPATH":..

pipenv run python -m jiggle_version --source=../ --project=sample_lib