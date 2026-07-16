"""Render the briefing time series (data/observations.csv) as a chart image.

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

data/observations.csv is long format: series,date,value,basis,source.
When one (series, date) has several observations, the best basis wins
(settle/close/daily_count > intraday > morning_quote > monthly_avg/
baseline). Dense series draw as plain daily lines; sparse series keep
per-point markers; gaps longer than ~3 weeks draw dotted so sparse
coverage is not mistaken for a smooth path.
"""

import csv
import pathlib
import subprocess
import sys
from datetime import date, timedelta

try:
    import matplotlib
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "matplotlib"], check=True)
    import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

REPO = pathlib.Path(__file__).resolve().parent.parent
OBS = REPO / "data" / "observations.csv"
EVENTS = REPO / "data" / "events.csv"
CHART_START = date(2026, 1, 1)

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

EVENT_LABELS_KO = {
    "War begins": "전쟁 발발",
    "US Iran MOU": "미·이란 양해각서",
    "Ceasefire collapses": "휴전 붕괴",
    "Blockade and toll": "봉쇄·통행료 발표",
    "Toll withdrawn": "통행료 철회",
}


def setup_korean_font():
    import matplotlib.font_manager as fm

    for path in (
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    ):
        if pathlib.Path(path).is_file():
            fm.fontManager.addfont(path)
    matplotlib.rcParams["font.family"] = ["DejaVu Sans", "Noto Sans CJK KR"]
    matplotlib.rcParams["axes.unicode_minus"] = False


def load():
    """Best observation per (series, date) -> {series: ([dates], [values])}."""
    best = {}
    with open(OBS) as f:
        for r in csv.DictReader(f):
            key = (r["series"].strip(), date.fromisoformat(r["date"]))
            rank = BASIS_RANK.get((r.get("basis") or "").strip(), 0)
            if key not in best or rank > best[key][0]:
                best[key] = (rank, float(r["value"]))
    out = {}
    for (series_name, d), (_, v) in sorted(best.items(), key=lambda kv: kv[0][1]):
        out.setdefault(series_name, ([], []))
        out[series_name][0].append(d)
        out[series_name][1].append(v)
    return out


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


def plot_series(ax, xs, ys, color, gap_days=21):
    """Solid line within dense runs; dotted connector across gaps > gap_days.
    Markers only when the series is sparse enough for points to matter."""
    if not xs:
        return
    msize = 2.6 if len(xs) <= 40 else 0
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
    ax.legend(
        handles=[Line2D([], [], color=SERIES_1, linewidth=1.5, label="Brent"),
                 Line2D([], [], color=SERIES_2, linewidth=1.5, label="WTI")],
        fontsize=7, frameon=False, labelcolor=INK_2, loc="lower left",
    )

    ax = axes[0][1]
    style_axis(ax, titles["transits"], date_fmt)
    xs, ys = data.get("hormuz_transits", ([], []))
    plot_series(ax, xs, ys, SERIES_1)
    label_last(ax, xs, ys, SERIES_1)

    ax = axes[1][0]
    style_axis(ax, titles["kospi"], date_fmt)
    xs, ys = data.get("kospi", ([], []))
    plot_series(ax, xs, ys, SERIES_1)
    label_last(ax, xs, ys, SERIES_1)

    ax = axes[1][1]
    style_axis(ax, titles["usdkrw"], date_fmt)
    xs, ys = data.get("usdkrw", ([], []))
    plot_series(ax, xs, ys, SERIES_1)
    label_last(ax, xs, ys, SERIES_1)

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
