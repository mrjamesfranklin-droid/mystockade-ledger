# mystockade-ledger — verification note

A public, append-only record of paper-trading alerts, sealed before each session opens.

**Why:** each night's alerts are sealed here as a hash only, before the market they concern opens.
The file is published to `revealed/` later, so anyone can check that nothing was edited after the
outcome was known. Publishing live alerts would give the paid product away; publishing a hash is
not a recommendation.

## What's here
- `commitments.csv` — one line per sealed night: `date,market,sha256,alerts_count,closed_count`.
  Append-only: a line is never edited or removed once written.
- `proofs/*.ots` — an OpenTimestamps proof anchoring each hash to a public timestamp nobody can
  back-date.
- `revealed/*.json` — the night's file, byte-identical to what was hashed, published **30 days
  after the last trade in it closed**. It shows each alert's strategy name, ticker, direction,
  entry price and size, and each closed trade's dates, prices, days held and result.
  **Strategy rules are never published** — no entry rules, stops, exit rules or hold limits.
- `verify.py` — checks a revealed file against its commitment.

## Releases
- `releases.csv` — one line per release: `release,date,rules,rules_removed,sha256_of_rules`. The set of rules
  changes only on a monthly release day; a rule is retired only on a release day and its sealed record stays.
  Counts and a hash only — never the rules themselves.
- Release 1 was revised before its first sealed night; the second row is the rule set in force. 23 rules, 0 retired.

## How to verify a revealed file
```
python verify.py revealed/2026-09-28_US.json
```
This re-hashes the file, finds its line in `commitments.csv`, and confirms the hashes match.
If a `.ots` proof is present it also runs `ots verify` (`pip install opentimestamps-client`).

## What this is not
Not investment advice, not a recommendation, not a track record for marketing. It is a proof
that a private record was not edited after the fact — nothing more.
