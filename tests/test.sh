#!/usr/bin/env bash

for test_file in *.py; do
    echo "$test_file"
    diff <(cd ..; python carotte.py "tests/$test_file") "${test_file%.py}.out"
done
