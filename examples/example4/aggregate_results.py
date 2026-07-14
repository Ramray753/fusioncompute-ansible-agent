#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aggregate per-VM temporary CSV result files into a single final output CSV.

Reads all vm_tools_*.csv temp files from /tmp, concatenates the data lines,
prepends the header row, and writes the merged output to ./vm_tools.csv.
Cleans up the temporary files after successful aggregation.
"""

import os
import glob
import sys

# Configuration constants
TEMP_DIR = '/tmp'
TEMP_PATTERN = 'vm_tools_*.csv'
OUTPUT_FILE = './vm_tools.csv'
HEADER = '\u865a\u62df\u673a\u540d,ID,Tools\u72b6\u6001,Tools\u7248\u672c'


def main():
    """Aggregate all per-VM temp CSV files into the final output CSV."""
    temp_files = glob.glob(os.path.join(TEMP_DIR, TEMP_PATTERN))

    if not temp_files:
        print("Warning: No temporary VM Tools result files found in {}".format(TEMP_DIR))
        # Still write header-only CSV
        with open(OUTPUT_FILE, 'w') as f:
            f.write(HEADER + '\n')
        print("Created empty output file: {}".format(OUTPUT_FILE))
        return 0

    lines = []
    for tf in sorted(temp_files):
        try:
            with open(tf, 'r') as f:
                content = f.read().strip()
                if content:
                    lines.append(content)
        except IOError as e:
            print("Error reading temp file {}: {}".format(tf, e))
            return 1

    try:
        with open(OUTPUT_FILE, 'w') as f:
            f.write(HEADER + '\n')
            for line in lines:
                f.write(line)
        print("Aggregated {} VM record(s) into {}".format(len(lines), OUTPUT_FILE))
    except IOError as e:
        print("Error writing output file {}: {}".format(OUTPUT_FILE, e))
        return 1

    # Cleanup temporary files
    for tf in temp_files:
        try:
            os.remove(tf)
            print("Removed temp file: {}".format(tf))
        except OSError as e:
            print("Warning: Could not remove temp file {}: {}".format(tf, e))

    return 0


if __name__ == '__main__':
    sys.exit(main())
