import folium
import streamlit as st

from huggingface_hub import hf_hub_download
from streamlit_folium import st_folium

from osm_ai_helper.run_inference import run_inference


@st.fragment
def download_model():
    hf_hub_download(
        "daavoo/yolo-osm-pool-detector",
        filename="model.pt",
        repo_type="model",
        local_dir="models",
    )


@st.fragment
def inference(lat_lon):
    run_inference("models/model.pt", "results", lat_lon)


st.title("Open Street Map AI Helper")
download_model()
st.markdown("Click on the map to select a latitude and longitude")

m = folium.Map(location=[42.2489, -8.5117], zoom_start=11, tiles="OpenStreetMap")

st_data = st_folium(m, width=725)

if st_data.get("last_clicked"):
    lat = st_data["last_clicked"]["lat"]
    lon = st_data["last_clicked"]["lng"]
    st.write(f"Last Clicked: {lat}, {lon}")

    if st.button("Run Inference"):
        inference((lat, lon))
