#!/usr/bin/env python3
"""Replace the author's work email addresses in Claude Code transcripts with a fixed placeholder.

The addresses are matched by SHA-256 of the lower-cased address, so this file does not contain
them. Every other email-shaped string (the author's personal address, public addresses quoted from
documentation, `git@github.com`, config keys) is left exactly as it is.

JSON escapes such as `\\n` put a stray letter in front of an address in the raw text
(`\\nname@host` is seen as `nname@host`), so every suffix of the local part is tried and only the
matching suffix is replaced; the escape stays intact.

Each file is changed only if every line that parsed as JSON before still parses after.

Usage:
  redact-emails.py <file-or-dir>...          rewrite *.jsonl files in place, print counts
  redact-emails.py --check <file-or-dir>...  change nothing; exit 1 if an address is found
"""
import hashlib
import json
import os
import re
import sys

HASHES = {
    "5a0cb54b56a3bfe0010ab1e43fb013d0ad67bf078919560dd3cdcce7e154b40d",  # work address 1
    "6d3f0b53e9e8cbfc8d40dc88ca9748f78b74bd130eb7eecf1b9f9100990767a4",  # work address 2
}
PLACEHOLDER = b"<redacted-work-email>"
CANDIDATE = re.compile(rb"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")


def _known(addr: bytes) -> bool:
    return hashlib.sha256(addr.lower()).hexdigest() in HASHES


def redact(data: bytes):
    out, pos, count = [], 0, 0
    for m in CANDIDATE.finditer(data):
        s = m.group(0)
        at = s.index(b"@")
        for i in range(at):
            if _known(s[i:]):
                out += [data[pos:m.start() + i], PLACEHOLDER]
                pos = m.end()
                count += 1
                break
    out.append(data[pos:])
    return b"".join(out), count


def parsable_lines(data: bytes):
    ok = set()
    for n, line in enumerate(data.split(b"\n")):
        if line.strip():
            try:
                json.loads(line)
                ok.add(n)
            except ValueError:
                pass
    return ok


def files(paths):
    for p in paths:
        if os.path.isdir(p):
            for d, _, names in os.walk(p):
                for name in sorted(names):
                    if name.endswith(".jsonl"):
                        yield os.path.join(d, name)
        elif p.endswith(".jsonl"):
            yield p


def main(argv):
    check = argv[:1] == ["--check"]
    paths = argv[1:] if check else argv
    if not paths:
        print(__doc__)
        return 2
    total = 0
    for f in files(paths):
        with open(f, "rb") as fh:
            data = fh.read()
        new, n = redact(data)
        if not n:
            continue
        total += n
        if check:
            print(f"FOUND {n:5d}  {f}")
            continue
        before, after = parsable_lines(data), parsable_lines(new)
        if not before <= after:
            print(f"ABORT {f}: lines {sorted(before - after)[:5]} no longer parse as JSON")
            return 3
        with open(f, "wb") as fh:
            fh.write(new)
        print(f"redacted {n:5d}  {f}")
    print(f"total: {total}")
    return 1 if (check and total) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
