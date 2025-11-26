# google_sheets_client.py

import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection

# We now read the spreadsheet URL/name from .streamlit/secrets.toml
# under [connections.gsheets], so no need to keep SHEET_ID here.

# Map (city, grid_size, poi_type) -> worksheet/tab name
# 👉 Extend this as you add more city/grid/poi combos
WORKSHEET_MAP = {
    ("Delhi", "1km", "Google Pois"): "delhi_1km",
    ("Delhi", "1km", "OSM Pois"): "delhi_1km_2",
    # ("Delhi", "200m", "Google Pois"): "delhi_200m",
    # ("Mumbai", "1km", "Google Pois"): "mumbai_1km",
    # ...
}

# Map output dropdown to column name in sheet
METRIC_COL_MAP = {
    "Exposure": "exposure",
    "Volume": "predicted_total_trips",  # or "log_max_volume" if you prefer
    "Crash": "sum",                     # change when you have a real crash col
}


def _parse_wkt_point(series: pd.Series) -> tuple[pd.Series, pd.Series]:
    """Parse 'POINT (lon lat)' WKT strings into lon/lat series."""
    coords = (
        series.astype(str)
        .str.replace("POINT", "", regex=False)
        .str.strip(" ()")
    )
    lon_lat = coords.str.split(expand=True)
    if lon_lat.shape[1] < 2:
        return pd.Series(dtype="float64"), pd.Series(dtype="float64")

    lon = pd.to_numeric(lon_lat[0], errors="coerce")
    lat = pd.to_numeric(lon_lat[1], errors="coerce")
    return lon, lat


def _parse_wkt_polygon(s: str):
    """
    Parse 'POLYGON ((lon lat, lon lat, ...))' into list of (lon, lat) tuples.
    Returns [] on failure.
    """
    if not isinstance(s, str):
        return []

    txt = s.strip()
    if not txt:
        return []

    # Remove leading POLYGON, surrounding parens
    txt = txt.replace("POLYGON", "").strip()
    # remove outer parens
    txt = txt.lstrip("(").rstrip(")")
    # If still nested "(...)", strip again
    if txt.startswith("(") and txt.endswith(")"):
        txt = txt[1:-1]

    coords = []
    for pair in txt.split(","):
        parts = pair.strip().split()
        if len(parts) >= 2:
            try:
                lon = float(parts[0])
                lat = float(parts[1])
                coords.append((lon, lat))
            except ValueError:
                continue
    return coords


@st.cache_data
def fetch_data(city: str, poi_type: str, grid_size: str, output_type: str) -> pd.DataFrame:
    """Fetch data for a given city/grid/poi/output combination, including polygon info."""

    key = (city, grid_size, poi_type)
    worksheet = WORKSHEET_MAP.get(key)

    if worksheet is None:
        st.error(
            f"No worksheet configured for {city} – {grid_size} – {poi_type}. "
            f"Add it to WORKSHEET_MAP in google_sheets_client.py."
        )
        return pd.DataFrame()

    # Uses the connection configured in .streamlit/secrets.toml
    conn: GSheetsConnection = st.connection("gsheets", type=GSheetsConnection)

    # spreadsheet parameter is taken from secrets, so we only pass worksheet
    df = conn.read(
        worksheet=worksheet,
        ttl="10m",
    )

    # Drop completely empty rows
    df = df.dropna(how="all")
    if df.empty:
        return df

    # --- POINT GEOMETRY -> lon / lat for st.map ---
    if "geometry" in df.columns:
        lon, lat = _parse_wkt_point(df["geometry"])
        df["lon"] = lon
        df["lat"] = lat

    # --- POLYGON -> list of (lon, lat) + simple centroid ---
    if "polygon_points" in df.columns:
        poly_coords = df["polygon_points"].astype(str).apply(_parse_wkt_polygon)
        df["polygon_coords"] = poly_coords

        # simple centroid = mean of polygon coordinates
        def centroid(coords):
            if not coords:
                return (None, None)
            xs = [c[0] for c in coords]
            ys = [c[1] for c in coords]
            return (sum(xs) / len(xs), sum(ys) / len(ys))

        centroids = poly_coords.apply(centroid)
        df["poly_lon_centroid"] = centroids.apply(lambda c: c[0])
        df["poly_lat_centroid"] = centroids.apply(lambda c: c[1])

    # --- metric column based on output_type ---
    metric_col = METRIC_COL_MAP.get(output_type)
    if metric_col and metric_col in df.columns:
        df["metric"] = pd.to_numeric(df[metric_col], errors="coerce")
    else:
        st.warning(
            f"Metric column for '{output_type}' not found. "
            f"Check METRIC_COL_MAP or sheet columns."
        )
        df["metric"] = None

    return df
