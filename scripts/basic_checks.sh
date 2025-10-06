#! /bin/bash
set -eou pipefail
set -x
jiggle_version --help || true
jiggle_version print
jiggle_version inspect
jiggle_version check
jiggle_version hash-all
jiggle_version bump --dry-run
