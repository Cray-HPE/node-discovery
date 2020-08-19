#!/bin/sh
# Copyright 2019, Cray Inc. All Rights Reserved.

set -ex
set -o pipefail

mkdir -p /results
pip freeze 2>&1 | tee /results/pip_freeze.out
flake8 --ignore E501,E402 2>&1 | tee /results/flake8.out