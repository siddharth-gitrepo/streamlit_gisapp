# app.py
import streamlit as st
import pandas as pd
import pydeck as pdk
from google_sheets_client import fetch_data

st.set_page_config(page_title="Pedestrian GIS App", layout="wide")

st.markdown("""
<div style="background-color:#111;padding:12px 24px;color:white;font-size:22px;font-weight:600;border-radius:4px;">
    Gis App
</div>
""", unsafe_allow_html=True)

st.write("")

# TOP FILTERS
with st.container():
    col1, col2, col3, col4, col5 = st.columns([1.2, 1.2, 1.2, 1.2, 0.7])

    with col1:
        city = st.selectbox("City", ["Delhi", "Mumbai", "Jaipur", "Chandigarh", "Faridabad"])
    with col2:
        poi_type = st.selectbox("POI Type", ["Google Pois", "OSM Pois"])
    with col3:
        grid_size = st.selectbox("Grid Size", ["200m", "400m", "800m", "1km", "1.2km", "1.5km", "2km"])
    with col4:
        output_type = st.selectbox("Output", ["Exposure", "Volume", "Crash"])
    with col5:
        st.write(" ")
        st.write(" ")
        run = st.button("Run")

st.write("")


def show_default_map():
    default_df = pd.DataFrame({"lat": [20.5937], "lon": [78.9629]})
    st.map(default_df, zoom=4, use_container_width=True)


# MAIN BEHAVIOR
if run:
    with st.spinner("Fetching data..."):
        df = fetch_data(city, poi_type, grid_size, output_type)

    if df.empty:
        st.warning("No rows found for these filters.")
        show_default_map()
    else:
        st.success(f"Showing {len(df)} rows.")

        # If we have lat/lon, build a pydeck map with points + polygons
        if {"lat", "lon"}.issubset(df.columns):
            center_lat = df["lat"].astype(float).mean()
            center_lon = df["lon"].astype(float).mean()

            layers = []
            m_min = None
            m_max = None

            # Polygon layer (if polygon_coords exists)
            if "polygon_coords" in df.columns:
                poly_df = df[df["polygon_coords"].notna()].copy()

                # ---- Color scale based on metric ----
                # assumes df has a 'metric' column
                m_min = poly_df["metric"].min()
                m_max = poly_df["metric"].max()
                span = (m_max - m_min) or 1  # avoid division by zero

                def metric_to_color(v):
                    # normalize 0–1
                    t = (v - m_min) / span
                    # purple -> yellow style gradient
                    # start = (68, 1, 84), end = (253, 231, 37)
                    r = int(68 + t * (253 - 68))
                    g = int(1 + t * (231 - 1))
                    b = int(84 + t * (37 - 84))
                    return [r, g, b, 200]  # RGBA, alpha 200

                poly_df["fill_color"] = poly_df["metric"].apply(metric_to_color)

                polygon_layer = pdk.Layer(
                    "PolygonLayer",
                    data=poly_df,
                    get_polygon="polygon_coords",   # list of [lon, lat] pairs
                    filled=True,
                    get_fill_color="fill_color",
                    stroked=True,
                    get_line_color=[255, 255, 255],
                    line_width_min_pixels=0.5,
                    pickable=True,
                )
                layers.append(polygon_layer)

            # Point layer (centroids)
            point_layer = pdk.Layer(
                "ScatterplotLayer",
                data=df,
                get_position="[lon, lat]",
                get_radius=25,
                get_fill_color=[0, 0, 0, 255],  # black points
                pickable=True,
            )
            layers.append(point_layer)

            view_state = pdk.ViewState(
                latitude=center_lat,
                longitude=center_lon,
                zoom=11,
                pitch=0,
            )

            r = pdk.Deck(
                layers=layers,
                initial_view_state=view_state,
                tooltip={"text": "grid_id: {grid_id}\nvalue: {metric}"},
            )

            # ---- Map + Legend side by side ----
            map_col, legend_col = st.columns([5, 1])

            with map_col:
                st.pydeck_chart(r)

            with legend_col:
                if m_min is not None and m_max is not None:
                    st.markdown(f"""
                    <div style="
                        height: 320px;
                        display: flex;
                        flex-direction: column;
                        align-items: center;
                        justify-content: space-between;
                        padding-top: 10px;
                        padding-bottom: 10px;
                    ">
                        <div style="font-size:12px; font-weight:500;">{m_max:,.2f}</div>
                        <div style="
                            flex-grow: 1;
                            width: 40px;
                            background: linear-gradient(to bottom,
                                rgba(253,231,37,1),
                                rgba(68,1,84,1)
                            );
                            border-radius:4px;
                            border: 1px solid #ccc;
                        ">
                        </div>
                        <div style="font-size:12px; font-weight:500;">{m_min:,.2f}</div>
                        <div style="font-size:11px; margin-top:4px; text-align:center;">
                            {output_type}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.write("")

        else:
            # Fallback: simple map if lat/lon missing
            st.map(df[["lat", "lon"]], use_container_width=True)

        # Show full table below
        st.markdown("### Data")
        st.dataframe(df, use_container_width=True)

else:
    show_default_map()

