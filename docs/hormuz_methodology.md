# Strait of Hormuz transit methodology

## Purpose

This dataset tracks public evidence about traffic through the Strait of Hormuz, with emphasis on measures that matter most for South Korea: crude and refined-product flows, LNG and LPG carriers, direction of travel, cargo volumes, and Korea-bound or Korean-operated vessels.

The initial research window is 2026-01-01 through 2026-07-24 (Asia/Seoul research cutoff). Public articles do not publish a complete daily series. The dataset therefore separates the calendar scaffold from the observations that the sources actually support.

## Files and authority

data/hormuz_observations.csv is the canonical evidence table. It preserves the source's observation window, scope, qualifier, and provider. data/hormuz_daily.csv is a convenience view for exact or date-attributable daily observations. data/hormuz_sources.csv is the citation registry.

Never infer an unreported daily value from a weekly or monthly total. Never turn a blank into zero. A zero is entered only when a media report explicitly says that no vessel in the stated category crossed.

## Metric priority for Korea

1. korea_bound_oil_million_bbl and korea_bound_energy_crossings: direct evidence of supply headed to South Korea.
2. korea_operated_crossings: operational exposure of Korean shipping, even when the cargo destination is elsewhere.
3. oil_volume_million_bbl, crude_tanker_crossings, oil_product_tanker_crossings, lng_carrier_crossings, and lpg_carrier_crossings: the closest public proxies for Korean energy availability and freight risk.
4. inbound_crossings and outbound_crossings: distinguishes vessels entering the Gulf to load from cargo leaving toward Asian buyers.
5. verified_crossings_all and commodity_vessel_crossings: broad indicators of whether the chokepoint is functioning, but they include vessels that do not carry energy.

South Korea imports substantial Middle Eastern crude and LNG, so cargo-specific and Korea-bound measures should be preferred over an undifferentiated ship count when both are available.

## Definitions

- verified_crossings_all: all vessel passages in the source/provider's stated universe.
- commodity_vessel_crossings: commodity-carrying commercial vessels; this is narrower than all verified crossings.
- tanker_crossings: all reported tanker types combined when the article uses that category.
- crude_tanker_crossings and oil_product_tanker_crossings: cargo-specific tanker counts.
- lng_carrier_crossings and lpg_carrier_crossings: liquefied natural gas and liquefied petroleum gas carrier counts.
- oil_volume_million_bbl: oil or oil-product cargo volume explicitly associated with a passage or observation window. Capacity is not treated as loaded cargo unless the source says the vessel was carrying that amount.
- direction: inbound means toward Gulf loading ports; outbound means away from the Gulf toward destination markets.
- korea_bound: the source identifies South Korea or a Korean port/refiner as the destination.
- korea_operated: the source identifies a vessel as Korean-operated; this is not automatically Korea-bound.

Counts from different providers or articles are not automatically comparable. Kpler, LSEG, MarineTraffic, Bloomberg tracking, JMIC, and other sources may use different vessel universes, AIS treatments, time zones, and snapshot times.

## Qualifiers and quality flags

- exact: the article gives an unqualified value for a full day or stated period.
- approximate: words such as about, around, or roughly.
- lower_bound: at least, more than, or a conservative tally.
- upper_bound: at most or maximum capacity.
- partial_window: a 12-hour, intraday, or rolling 24-hour observation that is not safely equivalent to a calendar day.
- conflict: credible sources give different values for what appears to be the same date; both are retained.
- aggregate_only: a multi-day or monthly value that must not be allocated across days.

The daily file uses verified_crossings_all_alt only to preserve a conflicting all-vessel count. Details and both citations remain in the canonical observation table.

## Manual update procedure

1. Add every media article to data/hormuz_sources.csv before entering a value. Prefer Reuters, AP, Bloomberg, CNBC, and other outlets that name the tracking provider.
2. Add one row per reported fact to data/hormuz_observations.csv. Preserve the article's dates, units, scope, direction, qualifier, and provider.
3. Add a value to data/hormuz_daily.csv only when it can be attributed to a particular date. Use semicolon-separated source IDs when multiple sources support or conflict on that row.
4. For a rolling or partial window, retain the fact in the long table and mark the daily row reported_partial; do not silently relabel it as a calendar-day count.
5. If an article reports zero for a category, enter 0 and cite it. Otherwise leave the cell blank.
6. For a newly elapsed date with no public observation, append the date and use no_daily_report_found. For the current research date, use provisional.
7. Run node scripts/validate_hormuz.mjs before committing.

## Known limitations

AIS gaps, deliberate transponder shutdowns, spoofing, dark voyages, delayed port records, and provider-specific route geofences can all change a reported count. Publication time and the observation cutoff may also differ. This is a media-evidence dataset, not a reconstruction of every physical transit. It stores short factual paraphrases and links rather than copyrighted article text.
