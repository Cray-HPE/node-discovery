#!/bin/sh
# Copyright 2019-2021 Hewlett Packard Enterprise Development LP

set -ex
set -o pipefail

mkdir -p /results
PYTHONPATH=./src:$PYTHONPATH
pip freeze 2>&1 | tee /results/pip_freeze.out
pytest -v \
 --cov-report html:/results/coverage \
 --cov=src/nd \
 --junit-xml=/results/pytest.xml \
 2>&1 | tee /results/pytest.out
