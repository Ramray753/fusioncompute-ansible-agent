#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aggregate temporary per-VM CSV row files into a single final CSV with a header.

Input:  ./.tmp_vm_tools/*.csv  (each file contains a single comma-separated row:
        VMName,VM_ID,pvDriverStatus,toolsVersion, no header row)
Output: ./vm_tools.csv (UTF-8 with BOM, header row + all data rows)
"""

import csv
import glob
import os
import sys


def collect_temp_files(temp_dir):
    # type: (str) -> list[str]
    """Scan the specified temporary directory and return all .csv file paths.
    Gracefully handles the case where the directory does not exist."""
    if not os.path.isdir(temp_dir):
        return []
    return sorted(glob.glob(os.path.join(temp_dir, '*.csv')))


def parse_temp_row(filepath):
    # type: (str) -> tuple | None
    """Parse a single temporary CSV file and return a (vm_name, vm_id, pv_status, tools_ver) tuple.
    Returns None if the file is empty or cannot be parsed."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 4:
                    return (row[0].strip(), row[1].strip(), row[2].strip(), row[3].strip())
    except Exception:
        pass
    return None


def write_aggregated_csv(rows, output_path):
    # type: (list[tuple], str) -> None
    """Write the final aggregated CSV file with a header row and all data rows.
    Uses UTF-8 encoding with BOM for Excel compatibility."""
    header = ['虚拟机名', 'ID', 'Tools状态', 'Tools版本']
    with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f, lineterminator='\n')
        writer.writerow(header)
        for row in rows:
            writer.writerow(row)


def main():
    # type: () -> None
    """Top-level orchestration entry point."""
    temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.tmp_vm_tools')
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'vm_tools.csv')

    temp_files = collect_temp_files(temp_dir)

    rows = []
    for fpath in temp_files:
        parsed = parse_temp_row(fpath)
        if parsed:
            rows.append(parsed)

    write_aggregated_csv(rows, output_path)

    print(f"Aggregation complete: {len(rows)} VM(s) written to {output_path}")
    sys.exit(0)


if __name__ == '__main__':
    main()
