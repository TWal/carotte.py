#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
IFS=$'\n\t'

for i in {0..4}_*.py; do
    echo "$i"
    diff \
        <(echo -e "1,/# Expected output/d\n %s/^# //\n%p\nq\nq\n" | ed -l --quiet "$i" | head -n -1) \
        <(cd ..; python carotte.py "tutorial/$i")
done

