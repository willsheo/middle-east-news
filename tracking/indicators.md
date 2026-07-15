# Indicator Ledger

**Middle East Daily Briefing**

Persistent register of every testable, falsifiable indicator defined in the daily briefs. This is the briefing's forecasting track record: every indicator gets a row the day it is defined and keeps it forever.

**Maintenance rules** (see also `instructions/00-conventions.md`, rule 10):

- IDs are `IND-YYYYMMDD-N`, numbered in the order defined in that day's brief.
- Statuses: **Open** (live), **Confirmed** (the watched condition occurred), **Falsified** (the falsification condition occurred), **Expired** (deadline passed with neither side triggered; note why), **Superseded** (replaced by a refined indicator; link the successor).
- Every daily run checks each Open indicator against the day's research and updates the row with a dated note. Resolutions are announced in that day's brief.
- Do not edit the definition of an indicator after opening it. If the threshold needs refining, supersede it with a new ID so the record stays honest.

_Last updated: 2026-07-15_

## Scoreboard

| | Count |
|---|---|
| Open | 5 |
| Confirmed | 1 |
| Falsified | 0 |
| Expired | 0 |
| Superseded | 2 |

## Ledger

| ID | Opened | Indicator | Metric | Resolution / falsification condition | Deadline | Status | Resolved | Notes |
|---|---|---|---|---|---|---|---|---|
| IND-20260714-1 | 2026-07-14 | Hormuz daily transit count | Daily vessel transits (Kpler/MarineTraffic) | Below ~20/day for two consecutive weeks confirms binding toll/blockade regime; recovery above ~30/day falsifies sustained closure | 2 weeks | Superseded | 2026-07-15 | Refined by IND-20260715-1 after the toll withdrawal added a policy-driven recovery test |
| IND-20260714-2 | 2026-07-14 | Won at the 1,500 line with BOK response | USD/KRW plus BOK emergency FX measures | Sustained break above ₩1,500 plus emergency measures confirms financial transmission; stabilization below ₩1,480 without intervention falsifies | none | Superseded | 2026-07-15 | Refined by IND-20260715-4 using weekly closes; won closed ₩1,493 on 07-14 |
| IND-20260714-3 | 2026-07-14 | Actual collection of the 20% Hormuz toll | Documented toll charge on any vessel (escort fee or port-state enforcement) | No collection mechanism within 14 days means coercive signaling, discount direct price impact; first documented collection forces repricing of Korea-bound Gulf cargo | 14 days | **Confirmed** | 2026-07-15 | Resolved on the signaling side in 1 day: no mechanism ever materialized and Trump withdrew the toll within 24 hours, replacing it with Gulf "trade and investment deals" (brief 2026-07-15, §1.1) |
| IND-20260714-4 | 2026-07-14 | Qatari LNG loadings at Ras Laffan | Weekly Qatari LNG export loadings (Kpler/ICIS) | Week-over-week drop >15% signals conflict reaching Korea's gas supply; steady loadings falsify near-term LNG risk | none | Open | | 2026-07-15: no loading disruption reported in window |
| IND-20260715-1 | 2026-07-15 | Hormuz transit count with recovery test | Daily vessel transits (Kpler via CNBC/Bloomberg) | Below ~20/day sustained two weeks confirms binding disruption regime; recovery above ~30/day within a week of the toll withdrawal shows the collapse was policy driven and falsifies sustained closure | Recovery test by ~2026-07-21; regime test by ~2026-07-28 | Open | | Baseline: 14 transits on 07-13, all six commodity carriers dark |
| IND-20260715-2 | 2026-07-15 | Substance behind Gulf investment deals | A named Gulf state announcing a specific dollar-denominated US investment package tied to strait security | No package by mid-August means the toll replacement was face saving and the transactional protection model is dead; a formal package (or the ask extended to Asian allies) confirms chokepoint security is being monetized | ~2026-08-14 | Open | | Watch for the ask reaching Korea |
| IND-20260715-3 | 2026-07-15 | UAE posture escalation | UAE participation in US strikes, invocation of collective defense, or expulsion of Iranian diplomats | Any within two weeks marks the first Gulf shift from hedging to belligerence; response limited to protest and compensation claims falsifies the escalation read | ~2026-07-29 | Open | | Opened after UAE reserved "full right to respond" over the Mombasa/Al Bahiyah tanker deaths |
| IND-20260715-4 | 2026-07-15 | Won at the 1,500 line, weekly close version | USD/KRW weekly closes and BOK intervention statements | Two consecutive weekly closes below ₩1,490 without intervention falsifies the financial crisis channel for now; renewed break above ₩1,500 with BOK smoothing or an emergency FX statement confirms it | 2 weekly closes | Open | | Baseline: ₩1,493.0 close on 07-14 |
