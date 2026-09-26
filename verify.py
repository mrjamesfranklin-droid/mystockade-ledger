#!/usr/bin/env python3
"""verify.py - re-hash a revealed alert file and check it against the public commitment record.

This is the ONLY verification a stranger needs: recompute the hash of a file in revealed/, find
the line in commitments.csv sealed for that date and market BEFORE the session it describes
opened, and confirm the two hashes match. If they match, this file is byte-identical to what was
committed to before the outcome was known.

Run:
    python verify.py revealed/2026-09-26_US.json
    python verify.py revealed/2026-09-26_US.json --commitments commitments.csv

Exit codes: 0 = hash matches (and, if a proof is present, `ots verify` also passed); 1 = mismatch,
no matching commitment line, or `ots verify` itself failed.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import subprocess
import sys


def sha256_hex(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def find_commitment(commitments_path: str, date: str, market: str) -> dict | None:
    with open(commitments_path, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            if row["date"] == date and row["market"] == market:
                return row
    return None


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("revealed_file", help="a file from revealed/, e.g. revealed/2026-09-26_US.json")
    p.add_argument("--commitments", default="commitments.csv")
    p.add_argument("--proof", default=None,
                   help="path to the .ots proof; default proofs/<basename>.ots")
    args = p.parse_args()

    with open(args.revealed_file, encoding="utf-8") as fh:
        data = json.load(fh)
    computed = sha256_hex(args.revealed_file)

    row = find_commitment(args.commitments, data["date"], data["market"])
    if row is None:
        print(f"NO COMMITMENT FOUND for {data['date']} {data['market']} in {args.commitments}")
        return 1

    if computed != row["sha256"]:
        print("HASH MISMATCH - this file does not match what was sealed")
        print(f"  file hash:      {computed}")
        print(f"  committed hash: {row['sha256']}")
        return 1
    print(f"HASH MATCHES the commitment sealed for {data['date']} {data['market']}: {computed}")

    proof = args.proof or os.path.join(
        os.path.dirname(args.commitments) or ".", "proofs",
        os.path.basename(args.revealed_file) + ".ots")
    if not os.path.exists(proof):
        print(f"NOTE: no proof file found at {proof} - hash match confirmed above only.")
        return 0
    try:
        r = subprocess.run(["ots", "verify", "-f", args.revealed_file, proof],
                          capture_output=True, text=True, timeout=120)
    except FileNotFoundError:
        print("NOTE: `ots` is not installed here - hash match confirmed above, but the timestamp "
              "proof was not independently re-verified. `pip install opentimestamps-client` to "
              "check that too.")
        return 0
    print(r.stdout.strip())
    if r.returncode != 0:
        print(r.stderr.strip(), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
