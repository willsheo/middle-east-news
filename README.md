# Middle East news data

Structured, source-linked data used to monitor Middle East developments and their economic relevance to South Korea.

## Strait of Hormuz transit dataset

The Hormuz dataset covers every calendar date from 2026-01-01 through the latest research cutoff. It records only values explicitly reported by a media source. A blank cell means that no defensible public daily observation was found; it never means zero.

- data/hormuz_daily.csv: one row per date, convenient wide-form daily view
- data/hormuz_observations.csv: canonical long-form observations, including period totals, averages, lower bounds, partial windows, and conflicting estimates
- data/hormuz_sources.csv: source registry with publication date, URL, and underlying data provider
- docs/hormuz_methodology.md: metric definitions, Korea relevance, and manual update rules
- scripts/validate_hormuz.mjs: deterministic integrity checks

Run the checks with:

    node scripts/validate_hormuz.mjs

The repository also contains event, market-price, place, and other series data in data/ and research deliverables in deliverables/.
