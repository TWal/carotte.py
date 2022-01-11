#!/usr/bin/env bash
cd "$(dirname "$0")" || exit

export MYPY_FORCE_COLOR=1

pylint -j 0 ./*.py examples/*.py \
    | grep -v -- "---------------------------" \
    | grep -v "Your code has been rated at" \
    | grep -v "^$"

mypy --disallow-untyped-defs ./*.py examples/*.py
