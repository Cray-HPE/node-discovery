#!/bin/bash
# Copyright 2019-2020 Hewlett Packard Enterprise Development LP

set -ex
set -o pipefail

mkdir -p /results
pip freeze 2>&1 | tee /results/pip_freeze.out
flake8 --ignore E501,E402 2>&1 | tee /results/flake8.out
