#!/usr/bin/env python3
"""Sum counts for each sorted key from Hadoop Streaming."""

import sys

current_key = None
total = 0

for line in sys.stdin:
    line = line.rstrip("\n")
    if "\t" not in line:
        continue
    key, value = line.split("\t", 1)
    try:
        count = int(value)
    except ValueError:
        continue

    if key != current_key:
        if current_key is not None:
            print(f"{current_key}\t{total}")
        current_key = key
        total = count
    else:
        total += count

if current_key is not None:
    print(f"{current_key}\t{total}")
