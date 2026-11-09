#!/usr/bin/env python3
"""Required check `data-fix-scan` (framework layer 3 "Database changes"; ADR-0011; OD48) [design].

A data fix lives in git forever and every engineer and agent session can read it, so it may name
records only by opaque internal IDs. Sensitive values a fix needs (a corrected bank account, a
national ID) are not written in the file: the data owner puts them in a values file in the
`db-change` bucket, which only the in-VPC task reads, and the SQL refers to them as psql
variables (`:'new_account'`) [design].

This check fails a PR when a file under db/<service>/data-fixes/ contains:
  F1  a match for one of the custom identifiers of the CloudWatch masking policy (E14), i.e. a
      field name such as `bank_account` or `national_id` followed by a value;
  F2  a run of 9 or more digits, the shape of national IDs, bank accounts and phone numbers.
It prints the file, line number and rule, never the matched text.

Usage: check_data_fixes.py <repo root> <masking policy json>
  exit 0 clean · exit 1 findings · exit 2 unreadable input (fail closed)
"""
import json
import os
import re
import sys

DIGITS = re.compile(r"(?<![0-9A-Za-z_])[0-9]{9,}(?![0-9])")
DATA_FIX_DIR = re.compile(r"^db/[^/]+/data-fixes/")


def identifiers(policy):
    custom = policy.get("Configuration", {}).get("CustomDataIdentifier", [])
    return [(c["Name"], re.compile(c["Regex"])) for c in custom]


def scan(root, ids):
    findings = []
    for dirpath, _, files in os.walk(os.path.join(root, "db")):
        for name in sorted(files):
            path = os.path.relpath(os.path.join(dirpath, name), root).replace(os.sep, "/")
            if not DATA_FIX_DIR.match(path):
                continue
            with open(os.path.join(root, path), encoding="utf-8") as f:
                for n, line in enumerate(f, 1):
                    for ident, rx in ids:
                        if rx.search(line):
                            findings.append(f"{path}:{n}: F1 {ident}")
                    if DIGITS.search(line):
                        findings.append(f"{path}:{n}: F2 a run of 9 or more digits")
    return findings


def main(argv):
    try:
        root, policy_path = argv
        with open(policy_path) as f:
            ids = identifiers(json.load(f))
        if not ids:
            raise ValueError("no identifiers in the masking policy")
        findings = scan(root, ids)
    except (OSError, ValueError, KeyError, re.error) as e:
        print(f"data-fix-scan: cannot read input ({e})", file=sys.stderr)
        return 2
    for line in findings:
        print(line)
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
