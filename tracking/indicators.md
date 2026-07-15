# Indicator Ledger

**Middle East Daily Briefing**

Persistent register of every testable, falsifiable indicator defined in the daily briefs. This is the briefing's forecasting track record: every indicator gets a row the day it is defined and keeps it forever.

**Maintenance rules** (see also `instructions/00-conventions.md`, rule 10):

- IDs are `IND-YYYYMMDD-N`, numbered in the order defined in that day's brief.
- Statuses: **Open** (live), **Confirmed** (the watched condition occurred), **Falsified** (the falsification condition occurred), **Expired** (deadline passed with neither side triggered; note why), **Superseded** (replaced by a refined indicator; link the successor).
- Every daily run checks each Open indicator against the day's research and updates the row with a dated note. Resolutions are announced in that day's brief.
- Do not edit the definition of an indicator after opening it. If the threshold needs refining, supersede it with a new ID so the record stays honest.

_Last updated: 2026-07-16_

## Scoreboard

| | Count |
|---|---|
| Open | 8 |
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
| IND-20260714-4 | 2026-07-14 | Qatari LNG loadings at Ras Laffan | Weekly Qatari LNG export loadings (Kpler/ICIS) | Week-over-week drop >15% signals conflict reaching Korea's gas supply; steady loadings falsify near-term LNG risk | none | Open | | 2026-07-15: no loading disruption reported in window. 2026-07-16: loadings still held at minimum after the July 9 ramp-up pause; empty carriers massing at Ras Laffan awaiting cargoes (OilPrice/Bloomberg); no fresh weekly loading figure in window |
| IND-20260715-1 | 2026-07-15 | Hormuz transit count with recovery test | Daily vessel transits (Kpler via CNBC/Bloomberg) | Below ~20/day sustained two weeks confirms binding disruption regime; recovery above ~30/day within a week of the toll withdrawal shows the collapse was policy driven and falsifies sustained closure | Recovery test by ~2026-07-21; regime test by ~2026-07-28 | Open | | Baseline: 14 transits on 07-13, all six commodity carriers dark. 2026-07-16: 21 transits on 07-14 (Kpler via Bloomberg) — between thresholds; partial recovery consistent with a policy-driven collapse but short of the 30/day falsification line |
| IND-20260715-2 | 2026-07-15 | Substance behind Gulf investment deals | A named Gulf state announcing a specific dollar-denominated US investment package tied to strait security | No package by mid-August means the toll replacement was face saving and the transactional protection model is dead; a formal package (or the ask extended to Asian allies) confirms chokepoint security is being monetized | ~2026-08-14 | Open | | Watch for the ask reaching Korea. 2026-07-16: no named package yet; Trump repeated only that Gulf investments "will be MASSIVE" (Truth Social, via Maritime Executive) |
| IND-20260715-3 | 2026-07-15 | UAE posture escalation | UAE participation in US strikes, invocation of collective defense, or expulsion of Iranian diplomats | Any within two weeks marks the first Gulf shift from hedging to belligerence; response limited to protest and compensation claims falsifies the escalation read | ~2026-07-29 | Open | | Opened after UAE reserved "full right to respond" over the Mombasa/Al Bahiyah tanker deaths. 2026-07-16: response still rhetorical (condemnation only); no participation in strikes, collective defense invocation, or expulsions in window |
| IND-20260715-4 | 2026-07-15 | Won at the 1,500 line, weekly close version | USD/KRW weekly closes and BOK intervention statements | Two consecutive weekly closes below ₩1,490 without intervention falsifies the financial crisis channel for now; renewed break above ₩1,500 with BOK smoothing or an emergency FX statement confirms it | 2 weekly closes | Open | | Baseline: ₩1,493.0 close on 07-14. 2026-07-16: won strengthened to ₩1,484.7 on 07-15 (US CPI relief rally) — below the 1,490 line intraweek; first weekly close test is Friday 07-17 |
| IND-20260716-1 | 2026-07-16 | Execution of the infrastructure ultimatum | Confirmed US strikes on Iranian power plants or bridges (CENTCOM/multi-outlet) | Strikes on grid or bridges by ~2026-07-23 confirm a civilian infrastructure phase (reprice oil, won, war-risk); deadline passing with neither strikes nor resumed talks falsifies the ultimatum as coercive theater, consistent with the toll episode | ~2026-07-23 | Open | | Opened after Trump's "next week comes the power plants... the bridges" ultimatum (brief 2026-07-16, §1.2) |
| IND-20260716-2 | 2026-07-16 | Second chokepoint incident (Bab el-Mandeb / Red Sea) | UKMTO/Kpler-verified attack on shipping in Bab el-Mandeb or southern Red Sea, or explicit Houthi closure declaration coordinated with Tehran | Any verified incident by ~2026-07-29 confirms a multi-chokepoint regime (Korea Europe-route freight and Suez insurance reprice); two quiet weeks falsify the IRGC threat as rhetoric aimed at Riyadh/Abu Dhabi | ~2026-07-29 | Open | | Opened after IRGC's "available to everyone or to no one" statement naming Bab el-Mandeb (brief 2026-07-16, §1.3) |
| IND-20260716-3 | 2026-07-16 | Lebanon pilot zone implementation | Verified IDF withdrawal from Froun, Ghandouriyeh or Zawtar with Lebanese army deployment | Withdrawal within ~10 days confirms the framework has implementation traction (and Tehran is not activating Hezbollah); no movement by ~2026-07-26, or a strike wave collapsing the track, falsifies | ~2026-07-26 | Open | | Opened after the sixth round of Rome talks agreed pilot zone structure "in the coming days" (brief 2026-07-16, §1.5) |
