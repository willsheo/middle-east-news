"""Render the briefing time series as a chart image.

Usage: python3 tools/make_charts.py [output.png] [--lang ko]
Default output: deliverables/charts/series_overview.png
With --lang ko: Korean panel titles, default output series_overview_ko.png

Produces a 2x2 small-multiples panel: Brent & WTI, Hormuz transits,
KOSPI close, KRW/USD. All four panels share the same x-axis range
(starting 2026-01-01) so vertical comparisons across panels line up.
Reference events from data/events.csv flagged major=1 are drawn as
dashed vertical lines on every panel, labeled on the top row. Each
panel has its own single axis (no dual-axis charts). Colors are
validated categorical slots from the briefing's chart palette: blue
#2a78d6 (slot 1) and green #008300 (slot 2) on a near-white print
surface, with text in near-black/gray ink.

Two kinds of input feed the chart, merged per series (see HISTORY):

1. **Full daily history files** in data/ (wide format, one row per
   calendar date) — the daily backbone that gives each panel its real
   day-to-day shape from 2026-01-01 onward. These are bulk datasets
   maintained outside the daily briefing run.
2. **data/observations.csv** — the briefing's own curated long-format
   log (series,date,value,basis,source), appended one day at a time by
   each daily run. When one (series, date) has several observations the
   best basis wins (settle/close/daily_count > intraday > morning_quote
   > monthly_avg/baseline).

Where the two overlap, the winner depends on the series. For the dense
official series (oil, FX, KOSPI) the history file wins, because one
consistently sourced series makes a truthful daily line and mixing two
providers' levels day to day would inject step artifacts of several
percent. For hormuz_transits neither file is a consistent daily
backbone — both are sparse and the published counting bases genuinely
conflict (all-vessel vs tanker counts) — so the briefing's curated
observation wins and the history file only fills dates the briefing
never recorded. Observations always supply dates beyond the history
file's last row, so the most recent point matches the day's brief.

A history file that is absent is simply skipped, so a series with no
bulk dataset yet (currently KOSPI) still plots from observations alone.

Dense series draw as plain daily lines; sparse series keep per-point
markers and are annotated with their reported-day count; gaps longer
than ~3 weeks draw dotted so sparse coverage is not mistaken for a
smooth path.
"""

import csv
import pathlib
import subprocess
import sys
from collections import namedtuple
from datetime import date, timedelta

try:
    import matplotlib
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "matplotlib"], check=True)
    import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

REPO = pathlib.Path(__file__).resolve().parent.parent
DATA = REPO / "data"
OBS = DATA / "observations.csv"
EVENTS = DATA / "events.csv"
CHART_START = date(2026, 1, 1)

# Bulk daily history datasets that give each panel its day-to-day shape.
# columns: first non-empty one wins, so a preferred provider can fall back
# to a second. wins_overlap: True when this file (not observations.csv)
# should own dates both files cover — see the module docstring.
History = namedtuple("History", "series file columns wins_overlap")

HISTORY = (
    History("brent", "oil_prices_daily.csv", ("brent_usd",), True),
    History("wti", "oil_prices_daily.csv", ("wti_usd",), True),
    History("usdkrw", "usdkrw_daily.csv", ("usdkrw_bok", "usdkrw_fed_ny"), True),
    History("kospi", "kospi_daily.csv", ("kospi_close",), True),
    History("hormuz_transits", "hormuz_daily.csv", ("verified_crossings_all",), False),
)

# Below this many points a series is treated as sparse: keep per-point
# markers and annotate the panel with how many days were actually reported.
SPARSE_MAX = 60

SERIES_1 = "#2a78d6"  # categorical slot 1, blue
SERIES_2 = "#008300"  # categorical slot 2, green
INK = "#0b0b0b"
INK_2 = "#52514e"
GRID = "#d9d8d4"
EVENT = "#9c9a94"
SURFACE = "#fcfcfb"

BASIS_RANK = {
    "settle": 5,
    "close": 5,
    "daily_count": 5,
    "intraday": 3,
    "morning_quote": 2,
    "monthly_avg": 1,
    "baseline": 1,
}

TITLES = {
    "en": {
        "oil": "Crude oil, USD per barrel",
        "transits": "Hormuz transits per day",
        "kospi": "KOSPI close",
        "usdkrw": "KRW/USD exchange rate",
    },
    "ko": {
        "oil": "국제유가, 배럴당 달러",
        "transits": "호르무즈 해협 일일 통항 척수",
        "kospi": "코스피 종가",
        "usdkrw": "원-달러 환율",
    },
}

COVERAGE_NOTE = {"en": "{} reported days", "ko": "관측 {}일"}

EVENT_LABELS_KO = {
    "War begins": "전쟁 발발",
    "US Iran MOU": "미·이란 양해각서",
    "Ceasefire collapses": "휴전 붕괴",
    "Blockade and toll": "봉쇄·통행료 발표",
    "Toll withdrawn": "통행료 철회",
}


NOTO_CJK = (
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
)


def setup_korean_font():
    import matplotlib.font_manager as fm

    # Test for the font file, not `fc-list :lang=ko`: that also matches Unifont
    # and WenQuanYi, which are installed here but which matplotlib will not use
    # for Hangul, so the guard would pass and every Korean label would render as
    # a tofu box.
    if not any(pathlib.Path(p).is_file() for p in NOTO_CJK):
        print("installing fonts-noto-cjk for Korean chart labels...", file=sys.stderr)
        subprocess.run(["apt-get", "update", "-q"], capture_output=True)
        subprocess.run(
            ["apt-get", "install", "-y", "-q", "fonts-noto-cjk"],
            capture_output=True,
        )

    added = [p for p in NOTO_CJK if pathlib.Path(p).is_file()]
    for path in added:
        fm.fontManager.addfont(path)
    if not added:
        # Better to fail the run than to publish a chart of empty boxes.
        sys.exit(
            "error: no Noto CJK font available, so Korean labels would render as "
            "tofu boxes. Install fonts-noto-cjk and re-run."
        )
    matplotlib.rcParams["font.family"] = ["DejaVu Sans", "Noto Sans CJK KR"]
    matplotlib.rcParams["axes.unicode_minus"] = False


def parse_day(raw):
    """Chart-range date, or None for junk and anything before CHART_START."""
    try:
        d = date.fromisoformat((raw or "").strip())
    except ValueError:
        return None
    return d if d >= CHART_START else None


def load_observations():
    """Best observation per (series, date) -> {series: {date: value}}."""
    best, out = {}, {}
    with open(OBS) as f:
        for r in csv.DictReader(f):
            d = parse_day(r.get("date"))
            if d is None:
                continue
            key = (r["series"].strip(), d)
            rank = BASIS_RANK.get((r.get("basis") or "").strip(), 0)
            if key not in best or rank > best[key]:
                best[key] = rank
                out.setdefault(key[0], {})[d] = float(r["value"])
    return out


def load_history(spec):
    """{date: value} from a bulk daily file; empty when the file is absent."""
    path = DATA / spec.file
    if not path.is_file():
        return {}
    vals = {}
    with open(path) as f:
        for r in csv.DictReader(f):
            d = parse_day(r.get("date"))
            if d is None:
                continue
            for col in spec.columns:
                raw = (r.get(col) or "").strip()
                if raw:
                    vals[d] = float(raw)
                    break
    return vals


def load():
    """Merge daily history with the briefing log -> {series: ([dates], [values])}."""
    obs = load_observations()
    merged = {s: dict(v) for s, v in obs.items()}
    for spec in HISTORY:
        hist = load_history(spec)
        if not hist:
            continue
        base = merged.setdefault(spec.series, {})
        if spec.wins_overlap:
            # History owns its covered range; observations still supply every
            # date it does not carry, including everything past its last row.
            # The one date history never takes is the briefing's most recent
            # observation: that point carries the endpoint label, and it has
            # to read the same as the figure quoted in the day's brief and
            # front matter, even when the bulk file measures it differently
            # (an official reference rate against a market close, say).
            tip = max(obs.get(spec.series, {}), default=None)
            base.update({d: v for d, v in hist.items() if d != tip})
        else:
            for d, v in hist.items():
                base.setdefault(d, v)
    return {
        s: (sorted(vals), [vals[d] for d in sorted(vals)])
        for s, vals in merged.items()
        if vals
    }


def load_events():
    if not EVENTS.is_file():
        return []
    with open(EVENTS) as f:
        return [
            (date.fromisoformat(r["date"]), r["label"].strip())
            for r in csv.DictReader(f)
            if (r.get("label") or "").strip()
            and (r.get("major") or "1").strip() == "1"
        ]


def style_axis(ax, title, date_fmt="%b"):
    ax.set_facecolor(SURFACE)
    ax.set_title(title, fontsize=9, color=INK, loc="left", fontweight="bold")
    ax.grid(True, color=GRID, linewidth=0.6)
    ax.tick_params(colors=INK_2, labelsize=7)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    for spine in ("left", "bottom"):
        ax.spines[spine].set_color(GRID)
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter(date_fmt))


def draw_events(ax, events, labeled):
    for i, (d, label) in enumerate(events):
        ax.axvline(d, color=EVENT, linewidth=0.9, linestyle=(0, (4, 3)), zorder=1)
        if labeled:
            ax.annotate(
                label,
                (mdates.date2num(d), 0.99),
                xycoords=("data", "axes fraction"),
                rotation=90,
                va="top",
                ha="right" if i % 2 == 0 else "left",
                fontsize=6,
                color=INK_2,
            )


def note_coverage(ax, xs, label_fmt):
    """Flag panels whose series is reported on only a handful of days, so a
    thin line is not read as the same daily coverage the dense panels have.

    Sits under the axis rather than inside it: a sparse panel's few points can
    sit anywhere, the top row also carries the rotated event labels, and the
    title row is already long enough to crowd on some panels.
    """
    if xs and len(xs) <= SPARSE_MAX:
        ax.set_xlabel(
            label_fmt.format(len(xs)),
            loc="right",
            fontsize=6,
            color=INK_2,
            fontstyle="italic",
            labelpad=1,
        )


def plot_series(ax, xs, ys, color, gap_days=21):
    """Solid line within dense runs; dotted connector across gaps > gap_days.
    Markers only when the series is sparse enough for points to matter."""
    if not xs:
        return
    msize = 2.6 if len(xs) <= SPARSE_MAX else 0
    run_x, run_y = [xs[0]], [ys[0]]
    for i in range(1, len(xs)):
        if (xs[i] - xs[i - 1]).days > gap_days:
            ax.plot(run_x, run_y, color=color, linewidth=1.5, marker="o", markersize=msize)
            ax.plot(xs[i - 1 : i + 1], ys[i - 1 : i + 1], color=color, linewidth=1.0,
                    linestyle=(0, (1, 3)))
            run_x, run_y = [xs[i]], [ys[i]]
        else:
            run_x.append(xs[i]); run_y.append(ys[i])
    ax.plot(run_x, run_y, color=color, linewidth=1.5, marker="o", markersize=msize)


def label_last(ax, xs, ys, color, fmt="{:,.0f}"):
    if xs:
        ax.annotate(
            fmt.format(ys[-1]),
            (xs[-1], ys[-1]),
            textcoords="offset points",
            xytext=(4, 4),
            fontsize=7,
            color=color,
            fontweight="bold",
        )


def main():
    args = sys.argv[1:]
    lang = "ko" if "--lang" in args and "ko" in args else "en"
    paths = [a for a in args if not a.startswith("--") and a != "ko"]
    default_name = "series_overview_ko.png" if lang == "ko" else "series_overview.png"
    out = pathlib.Path(paths[0]) if paths else REPO / "deliverables" / "charts" / default_name
    out.parent.mkdir(parents=True, exist_ok=True)

    if lang == "ko":
        setup_korean_font()
    titles = TITLES[lang]
    date_fmt = "%-m월" if lang == "ko" else "%b"

    data = load()
    events = load_events()
    if lang == "ko":
        events = [(d, EVENT_LABELS_KO.get(label, label)) for d, label in events]

    all_dates = [d for xs, _ in data.values() for d in xs] + [e[0] for e in events]
    xlim = (min([CHART_START] + all_dates), max(all_dates) + timedelta(days=2))

    fig, axes = plt.subplots(2, 2, figsize=(6.9, 4.6), dpi=200)
    fig.patch.set_facecolor(SURFACE)

    ax = axes[0][0]
    style_axis(ax, titles["oil"], date_fmt)
    for key, color, name in (("brent", SERIES_1, "Brent"), ("wti", SERIES_2, "WTI")):
        xs, ys = data.get(key, ([], []))
        plot_series(ax, xs, ys, color)
        if xs:
            ax.annotate(
                f"{name} {ys[-1]:,.2f}",
                (xs[-1], ys[-1]),
                textcoords="offset points",
                xytext=(4, -2),
                fontsize=7,
                color=color,
                fontweight="bold",
            )
    # No legend box: with a full daily series there is no empty corner left to
    # put one in, and the endpoint annotations already name both lines in their
    # own colors.

    single = (
        (axes[0][1], "transits", "hormuz_transits"),
        (axes[1][0], "kospi", "kospi"),
        (axes[1][1], "usdkrw", "usdkrw"),
    )
    for ax, key, series_key in single:
        style_axis(ax, titles[key], date_fmt)
        xs, ys = data.get(series_key, ([], []))
        plot_series(ax, xs, ys, SERIES_1)
        label_last(ax, xs, ys, SERIES_1)
        note_coverage(ax, xs, COVERAGE_NOTE[lang])

    for row_i in (0, 1):
        for col_i in (0, 1):
            ax = axes[row_i][col_i]
            ax.set_xlim(xlim)
            draw_events(ax, events, labeled=(row_i == 0))

    fig.tight_layout(pad=1.2)
    fig.savefig(out, facecolor=SURFACE)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
