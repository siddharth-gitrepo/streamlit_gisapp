# app.py
import streamlit as st
import pandas as pd

st.set_page_config(page_title="GIS App", layout="wide")

# ---------- Top bar ----------
st.markdown(
    """
    <div style="
        background-color:#111;
        padding: 12px 24px;
        color: white;
        font-size: 22px;
        font-weight: 600;
        border-radius: 4px;
        ">
        Gis App
    </div>
    """,
    unsafe_allow_html=True,
)
st.write("")

# ---------- TOP ROW: DROPDOWNS + RUN BUTTON ----------
with st.container():
    col1, col2, col3, col4, col5 = st.columns([1.2, 1.2, 1.2, 1.2, 0.7])

    with col1:
        city = st.selectbox(
            "City",
            ["Delhi", "Mumbai", "Jaipur", "Chandigarh", "Faridabad"],
        )

    with col2:
        poi_type = st.selectbox(
            "POI Type",
            ["Google Pois", "OSM Pois"],
        )

    with col3:
        grid_size = st.selectbox(
            "Grid Size",
            ["200m", "400m", "800m", "1km", "1.2km", "1.5km", "2km"],
        )

    with col4:
        output_type = st.selectbox(
            "Output",
            ["Exposure", "Volume", "Crash"],
        )

    with col5:
        st.write(" ")
        st.write(" ")
        run = st.button("Run")

st.write("")  

# ---------- FULL-WIDTH MAP ----------
st.markdown("#### OSM Map")
st.info("Map placeholder — integrate your real OSM/folium/pydeck map here.")

# Full-width map placeholder (center = India)
map_df = pd.DataFrame({"lat": [20.5937], "lon": [78.9629]})
st.map(map_df, zoom=4, use_container_width=True)

# Optional success message after clicking Run
if run:
    st.success(f"Analysis Triggered for → {city} | {poi_type} | {grid_size} | {output_type}")
