"""Render the Middle East locator map for a daily brief's Section 1.

Draws a fixed-extent map of the theater with country outlines from the
committed basemap (data/geo/middle_east_countries.geojson) and marks only the
handful of places discussed in that day's brief. Per user preference the map is
deliberately sparse: mark the few places that actually carry the day's events,
not every name mentioned.

Usage:
  python3 tools/make_map.py --date 2026-07-22 [--lang ko]
  python3 tools/make_map.py --date 2026-07-22 --places "Strait of Hormuz,Limah,Yanbu,Bab el-Mandeb"

Place list resolution (first that yields names wins):
  1. --places "A,B,C" on the command line, or
  2. the `map_places: [...]` field in the brief's YAML front matter
     (deliverables/brief_<date>.md).
Every name must exist in data/places.csv (the coordinate gazetteer); unknown
names abort with an error so a typo never silently drops a marker.

Output: deliverables/charts/map_<date>.png (en) or map_<date>_ko.png (ko).
Korean marker labels come from the `name_ko` column of data/places.csv; a place
with no Korean form falls back to its English name.

The base geography is rendered with no network access and no geospatial
libraries beyond matplotlib, so it runs in the same environment as the daily
brief. See tools/prep_basemap.py for how the basemap file was derived.
"""
import argparse
import csv
import json
import math
import pathlib
import re
import subprocess
import sys

try:
    import matplotlib
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "matplotlib"], check=True)
    import matplotlib

matplotlib.use("Agg")
import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPolygon

REPO = pathlib.Path(__file__).resolve().parent.parent
BASEMAP = REPO / "data" / "geo" / "middle_east_countries.geojson"
PLACES = REPO / "data" / "places.csv"
CHARTS = REPO / "deliverables" / "charts"

# Fixed theater extent (lon min, lon max, lat min, lat max).
EXTENT = (30.5, 62.5, 11.0, 39.5)

# Palette aligned with tools/make_charts.py.
SURFACE = "#fcfcfb"
WATER = "#e7eef4"
LAND = "#eae8e1"
BORDER = "#bdb8ac"
MARKER = "#c0392b"      # crimson, distinct from the chart blue/green
STRAIT = "#2a78d6"      # water features in the chart's slot-1 blue
INK = "#0b0b0b"
COUNTRY_INK = "#a7a294"
WATER_INK = "#8199ad"

# Orientation labels (not "locations": these anchor the reader's geography).
COUNTRY_LABELS = [
    # (en, ko, lon, lat)
    ("IRAN", "이란", 54.2, 32.6),
    ("IRAQ", "이라크", 43.4, 32.3),
    ("SAUDI ARABIA", "사우디아라비아", 44.6, 22.8),
    ("EGYPT", "이집트", 31.6, 26.6),
    ("YEMEN", "예멘", 46.8, 15.3),
    ("OMAN", "오만", 56.6, 21.0),
]
WATER_LABELS = [
    ("Persian Gulf", "페르시아만", 51.3, 27.6),
    ("Gulf of Oman", "오만만", 59.0, 24.6),
    ("Red Sea", "홍해", 37.2, 19.5),
    ("Arabian Sea", "아라비아해", 60.0, 14.5),
]


def load_places():
    out = {}
    with PLACES.open() as f:
        for r in csv.DictReader(f):
            out[r["name"]] = {
                "lat": float(r["lat"]),
                "lon": float(r["lon"]),
                "category": r.get("category", "city"),
                "name_ko": (r.get("name_ko") or "").strip(),
            }
    return out


def places_from_frontmatter(date_str):
    brief = REPO / "deliverables" / f"brief_{date_str}.md"
    if not brief.is_file():
        return []
    text = brief.read_text()
    parts = text.split("---", 2)
    fm = parts[1] if len(parts) >= 3 else text
    m = re.search(r"^map_places:\s*(\[.*\])\s*$", fm, re.MULTILINE)
    if not m:
        return []
    return [str(x) for x in json.loads(m.group(1))]


def draw_basemap(ax):
    data = json.loads(BASEMAP.read_text())
    for feat in data["features"]:
        geom = feat["geometry"]
        polys = geom["coordinates"]
        if geom["type"] == "Polygon":
            polys = [polys]
        for poly in polys:
            outer = poly[0]
            ax.add_patch(MplPolygon(
                outer, closed=True, facecolor=LAND, edgecolor=BORDER,
                linewidth=0.45, zorder=1,
            ))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", required=True)
    ap.add_argument("--places", default="")
    ap.add_argument("--lang", choices=["en", "ko"], default="en")
    ap.add_argument("--out", default="")
    args = ap.parse_args()

    if args.lang == "ko":
        import matplotlib.font_manager as fm
        for path in (
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
        ):
            if pathlib.Path(path).is_file():
                fm.fontManager.addfont(path)
        matplotlib.rcParams["font.family"] = ["DejaVu Sans", "Noto Sans CJK KR"]
    matplotlib.rcParams["axes.unicode_minus"] = False

    gaz = load_places()
    ko = args.lang == "ko"

    if args.places.strip():
        names = [n.strip() for n in args.places.split(",") if n.strip()]
    else:
        names = places_from_frontmatter(args.date)
    unknown = [n for n in names if n not in gaz]
    if unknown:
        sys.exit(f"error: not in data/places.csv: {', '.join(unknown)}")

    lon0, lon1, lat0, lat1 = EXTENT
    mean_lat = (lat0 + lat1) / 2
    aspect = 1.0 / max(0.1, math.cos(math.radians(mean_lat)))

    fig, ax = plt.subplots(figsize=(3.25, 3.5), dpi=200)
    ax.set_facecolor(WATER)
    fig.patch.set_facecolor(SURFACE)
    draw_basemap(ax)

    def pick(en, ko_text):
        return ko_text if ko else en

    # Orientation text (fixed geography, not the day's marked "locations").
    for en, ko_text, lon, lat in COUNTRY_LABELS:
        if lon0 < lon < lon1 and lat0 < lat < lat1:
            ax.text(lon, lat, pick(en, ko_text), fontsize=5.6, color=COUNTRY_INK,
                    ha="center", va="center", zorder=2,
                    fontweight="bold", alpha=0.9)
    for en, ko_text, lon, lat in WATER_LABELS:
        if lon0 < lon < lon1 and lat0 < lat < lat1:
            ax.text(lon, lat, pick(en, ko_text), fontsize=5.4, color=WATER_INK,
                    ha="center", va="center", style="italic", zorder=2)

    # Marked places, sparse by design.
    halo = [pe.withStroke(linewidth=1.8, foreground="white")]
    center_lon = (lon0 + lon1) / 2
    placed = []  # (side, label_y) for a light greedy vertical declutter
    min_dy = 1.15
    for name in names:
        info = gaz[name]
        lat, lon, cat = info["lat"], info["lon"], info["category"]
        text = info["name_ko"] if (ko and info["name_ko"]) else name
        if cat == "strait":
            ax.plot(lon, lat, marker="D", color=STRAIT, markersize=4.0,
                    markeredgecolor="white", markeredgewidth=0.5, zorder=5)
        else:
            ax.plot(lon, lat, marker="o", color=MARKER, markersize=4.2,
                    markeredgecolor="white", markeredgewidth=0.5, zorder=5)
        side = "left" if lon > center_lon else "right"
        ha = "right" if side == "left" else "left"
        dx = -0.55 if side == "left" else 0.55
        ly = lat
        for pside, py in placed:
            if pside == side and abs(py - ly) < min_dy:
                ly = py - min_dy
        placed.append((side, ly))
        # Faint leader from the dot to its (possibly nudged) label anchor.
        ax.plot([lon, lon + dx], [lat, ly], color="#8a857a", linewidth=0.4,
                alpha=0.55, zorder=4)
        ax.text(lon + dx, ly, text, fontsize=6.4, color=INK,
                ha=ha, va="center", zorder=6, path_effects=halo)

    ax.set_xlim(lon0, lon1)
    ax.set_ylim(lat0, lat1)
    ax.set_aspect(aspect)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_edgecolor(BORDER)
        spine.set_linewidth(0.6)

    CHARTS.mkdir(parents=True, exist_ok=True)
    suffix = "_ko" if args.lang == "ko" else ""
    out = pathlib.Path(args.out) if args.out else CHARTS / f"map_{args.date}{suffix}.png"
    fig.savefig(out, facecolor=SURFACE, bbox_inches="tight", pad_inches=0.04)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
