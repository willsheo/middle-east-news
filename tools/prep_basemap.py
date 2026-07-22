"""One-time preparation of the committed Middle East basemap.

The daily briefing map (tools/make_map.py) must render with no network access
and no geospatial libraries, so the country outlines are baked into the repo as
a small GeoJSON. This script derives that file from Natural Earth's public
domain 1:50m Admin-0 countries layer.

Source (public domain, Natural Earth via the nvkelso mirror):
  https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_50m_admin_0_countries.geojson

Usage (only needs re-running if the theater extent or country set changes):
  curl -sSL <source url> -o /tmp/ne50.geojson
  python3 tools/prep_basemap.py /tmp/ne50.geojson

It keeps only the countries in the theater, drops every property except a
display name, and rounds coordinates to 3 decimals (~100 m), which is far more
precision than a 2-inch reference map needs. The result is data/geo/middle_east_countries.geojson.
"""
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "data" / "geo" / "middle_east_countries.geojson"

# Countries whose polygons fall inside or touch the briefing map extent.
KEEP = {
    "Iran", "Iraq", "Kuwait", "Saudi Arabia", "Bahrain", "Qatar",
    "United Arab Emirates", "Oman", "Yemen", "Jordan", "Israel",
    "Lebanon", "Syria", "Egypt", "Turkey", "Cyprus", "Northern Cyprus",
    "Palestine", "Sudan", "Eritrea", "Ethiopia", "Djibouti", "Somaliland",
    "Somalia", "Pakistan", "Afghanistan",
}

DECIMALS = 3


def round_coords(geom):
    def r(x):
        if isinstance(x, (int, float)):
            return round(x, DECIMALS)
        return [r(v) for v in x]
    geom["coordinates"] = r(geom["coordinates"])
    return geom


def main():
    src = Path(sys.argv[1])
    data = json.loads(src.read_text())
    feats = []
    for f in data["features"]:
        p = f["properties"]
        name = p.get("ADMIN") or p.get("NAME")
        if name not in KEEP:
            continue
        feats.append({
            "type": "Feature",
            "properties": {"name": name},
            "geometry": round_coords(f["geometry"]),
        })
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(
        {"type": "FeatureCollection", "features": feats},
        separators=(",", ":"),
    ))
    print(f"wrote {OUT} ({len(feats)} countries, {OUT.stat().st_size/1024:.0f} KB)")


if __name__ == "__main__":
    main()
