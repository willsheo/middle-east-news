"""Render the briefing time series (data/series.csv) as a chart image.

Usage: python3 tools/make_charts.py [output.png] [--lang ko]
Default output: deliverables/charts/series_overview.png
With --lang ko: Korean panel titles, default output series_overview_ko.png

Produces a 2x2 small-multiples panel: Brent & WTI, Hormuz transits,
KOSPI close, USD/KRW. All four panels share the same x-axis range so
vertical comparisons across panels line up. Reference events from
data/events.csv are drawn as dashed vertical lines on every panel,
labeled on the top row. Each panel has its own single axis (no
dual-axis charts). Colors are validated categorical slots from the
briefing's chart palette: blue #2a78d6 (slot 1) and green #008300
(slot 2) on a near-white print surface, with text in near-black/gray
ink. Missing days leave gaps in the marker series; lines connect
available observations.
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

REPO = pathlib.Path(__file__).resolve().parent.parent
CSV = REPO / "data" / "series.csv"
EVENTS = REPO / "data" / "events.csv"

SERIES_1 = "#2a78d6"  # categorical slot 1, blue
SERIES_2 = "#008300"  # categorical slot 2, green
INK = "#0b0b0b"
INK_2 = "#52514e"
GRID = "#d9d8d4"
EVENT = "#9c9a94"
SURFACE = "#fcfcfb"

TITLES = {
    "en": {
        "oil": "Crude oil, USD per barrel",
        "transits": "Hormuz transits per day",
        "kospi": "KOSPI close",
        "usdkrw": "Won per US dollar, higher = weaker won",
    },
    "ko": {
        "oil": "국제유가, 배럴당 달러",
        "transits": "호르무즈 해협 일일 통항 척수",
        "kospi": "코스피 종가",
        "usdkrw": "원/달러 환율, 상승 = 원화 약세",
    },
}

EVENT_LABELS_KO = {
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
    rows = []
    with open(CSV) as f:
        for r in csv.DictReader(f):
            d = date.fromisoformat(r["date"])
            def num(key):
                v = (r.get(key) or "").strip()
                return float(v) if v else None
            rows.append(
                {
                    "date": d,
                    "brent": num("brent_usd"),
                    "wti": num("wti_usd"),
                    "kospi": num("kospi_close"),
                    "usdkrw": num("usdkrw"),
                    "transits": num("hormuz_transits"),
                }
            )
    return sorted(rows, key=lambda r: r["date"])


def load_events():
    if not EVENTS.is_file():
        return []
    with open(EVENTS) as f:
        return [
            (date.fromisoformat(r["date"]), r["label"].strip())
            for r in csv.DictReader(f)
            if (r.get("label") or "").strip()
        ]


def series(rows, key):
    pts = [(r["date"], r[key]) for r in rows if r[key] is not None]
    return [p[0] for p in pts], [p[1] for p in pts]


def style_axis(ax, title, date_fmt="%b %d"):
    ax.set_facecolor(SURFACE)
    ax.set_title(title, fontsize=9, color=INK, loc="left", fontweight="bold")
    ax.grid(True, color=GRID, linewidth=0.6)
    ax.tick_params(colors=INK_2, labelsize=7)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    for spine in ("left", "bottom"):
        ax.spines[spine].set_color(GRID)
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MO))
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
    date_fmt = "%-m.%-d." if lang == "ko" else "%b %d"

    rows = load()
    events = load_events()
    if lang == "ko":
        events = [(d, EVENT_LABELS_KO.get(label, label)) for d, label in events]

    all_dates = [r["date"] for r in rows] + [e[0] for e in events]
    xlim = (min(all_dates) - timedelta(days=1), max(all_dates) + timedelta(days=2))

    fig, axes = plt.subplots(2, 2, figsize=(6.9, 4.6), dpi=200)
    fig.patch.set_facecolor(SURFACE)

    ax = axes[0][0]
    style_axis(ax, titles["oil"], date_fmt)
    for key, color, name in (("brent", SERIES_1, "Brent"), ("wti", SERIES_2, "WTI")):
        xs, ys = series(rows, key)
        ax.plot(xs, ys, color=color, linewidth=1.6, marker="o", markersize=2.6)
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
        ["Brent", "WTI"], fontsize=7, frameon=False, labelcolor=INK_2, loc="lower left"
    )

    ax = axes[0][1]
    style_axis(ax, titles["transits"], date_fmt)
    xs, ys = series(rows, "transits")
    ax.plot(xs, ys, color=SERIES_1, linewidth=1.6, marker="o", markersize=2.6)
    label_last(ax, xs, ys, SERIES_1)

    ax = axes[1][0]
    style_axis(ax, titles["kospi"], date_fmt)
    xs, ys = series(rows, "kospi")
    ax.plot(xs, ys, color=SERIES_1, linewidth=1.6, marker="o", markersize=2.6)
    label_last(ax, xs, ys, SERIES_1)

    ax = axes[1][1]
    style_axis(ax, titles["usdkrw"], date_fmt)
    xs, ys = series(rows, "usdkrw")
    ax.plot(xs, ys, color=SERIES_1, linewidth=1.6, marker="o", markersize=2.6)
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
