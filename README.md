# mystockade-ledger — verification note

A public, append-only record of paper-trading alerts, sealed before each session opens.

**Why:** each alert is sealed here as a hash only, before the market it concerns opens. The full
alert is published to `revealed/` only once every trade in it has closed, so anyone can check
that nothing was edited after the outcome was known. Publishing live alerts would give the paid
product away; publishing a hash is not a recommendation.

## What's here
- `commitments.csv` — one line per sealed night: `date,market,sha256,alerts_count,closed_count`.
  Append-only: a line is never edited or removed once written.
- `proofs/*.ots` — an OpenTimestamps proof anchoring each hash to a public timestamp nobody can
  back-date.
- `revealed/*.json` — the full alert file, once every trade in it has closed, byte-identical to
  what was hashed.
- `verify.py` — checks a revealed file against its commitment.

## How to verify a revealed file
```
python verify.py revealed/2026-09-26_US.json
```
This re-hashes the file, finds its line in `commitments.csv`, and confirms the hashes match.
If a `.ots` proof is present it also runs `ots verify` (`pip install opentimestamps-client`).

## What this is not
Not investment advice, not a recommendation, not a track record for marketing. It is a proof
that a private record was not edited after the fact — nothing more.
