#!/usr/bin/env python3
"""Radon quality gates: fail on CC rank E/F and low Maintainability Index."""

import re
import subprocess
import sys

MIN_MI = 65


def run(cmd: list[str]) -> str:
    return subprocess.check_output(cmd, text=True, encoding="utf-8")


def check_cc(paths: list[str]) -> None:
    out = run(["uv", "run", "radon", "cc", "-s", *paths])
    # Rank goes right before the parentheses:  - E (12)  or  - F (20)
    if re.search(r"-\s+[EF]\s+\(", out):
        print("FAILED Radon CC: found functions with complexity E/F")
        sys.exit(1)
    print("OK Radon CC: no functions with E/F")


def check_mi(paths: list[str]) -> None:
    out = run(["uv", "run", "radon", "mi", *paths])
    bad = []
    for line in out.splitlines():
        m = re.search(r"\(([0-9.]+)\)\s*$", line)
        if m and float(m.group(1)) < MIN_MI:
            bad.append(line)
    if bad:
        print(f"FAILED Radon MI: found MI < {MIN_MI}")
        for line in bad:
            print(" ", line)
        sys.exit(1)
    print(f"OK Radon MI: all files >= {MIN_MI}")


if __name__ == "__main__":
    paths = sys.argv[1:] or ["delivery"]
    check_cc(paths)
    check_mi(paths)