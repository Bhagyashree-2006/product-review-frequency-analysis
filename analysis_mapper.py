#!/usr/bin/env python3
"""Emit (dimension, group) -> 1 records for Hadoop Streaming."""

import csv
import sys
from datetime import datetime


def parse_date(value: str):
    value = value.strip()
    for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%m/%d/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            pass
    return None


reader = csv.reader(sys.stdin)
for row in reader:
    if not row:
        continue
    # Ignore the CSV header, if present.
    if row[0].strip().lower() == "review_id":
        continue
    # Expected order: review_id, product_id, category, review_date, rating
    if len(row) < 4:
        continue

    product_id = row[1].strip()
    category = row[2].strip()
    review_date = parse_date(row[3])
    if not product_id or not category or review_date is None:
        continue

    groups = (
        ("MONTH", review_date.strftime("%Y-%m")),
        ("PRODUCT", product_id),
        ("CATEGORY", category),
    )
    for dimension, group in groups:
        # Hadoop Streaming uses the first tab as the key/value separator.
        safe_group = group.replace("\t", " ").replace("\n", " ")
        print(f"{dimension}|{safe_group}\t1")
