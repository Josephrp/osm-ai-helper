from pathlib import Path
from shutil import move

import folium
import streamlit as st
from loguru import logger
from huggingface_hub import hf_hub_download
from PIL import Image
from streamlit_folium import st_folium

from osm_ai_helper.run_inference import run_inference
from osm_ai_helper.upload_osm import upload


class StreamlitHandler:
    def __init__(self):
        self.text_widget = st.empty()
        self.log_messages = ""

    def write(self, message):
        self.log_messages += message
        self.text_widget.code(self.log_messages)
        return


@st.fragment
def inference(lat_lon, margin):
    hf_hub_download(
        "daavoo/yolo-osm-pool-detector",
        filename="model.pt",
        repo_type="model",
        local_dir="models",
    )
    output_path, *_ = run_inference(
        model_file="models/model.pt",
        output_dir="results",
        lat_lon=lat_lon,
        margin=margin,
    )
    return output_path


@st.fragment
def handle_polygon(polygon):
    raw_image = Image.open(polygon.with_suffix(".png"))
    painted_image = Image.open(f"{polygon.parent}/{polygon.stem}_painted.png")

    st.subheader(f"Reviewing: {polygon.name}")

    col1, col2 = st.columns(2)

    with col1:
        st.image(raw_image, caption="Raw Image", use_column_width=True)
    with col2:
        st.image(painted_image, caption="Painted Image", use_column_width=True)

    if st.button("Keep Polygon", key=f"keep_{polygon}"):
        keep_folder = polygon.parent / "keep"
        keep_folder.mkdir(parents=True, exist_ok=True)
        move(polygon, keep_folder / polygon.name)
        st.success(f"Polygon moved to {keep_folder}")
    elif st.button("Discard Polygon", key=f"discard_{polygon.stem}"):
        discard_folder = polygon.parent / "discard"
        discard_folder.mkdir(parents=True, exist_ok=True)
        move(polygon, discard_folder / polygon.name)
        st.success(f"Polygon moved to {discard_folder}")


@st.fragment
def upload_results(output_path):
    st.divider()
    st.header("Upload all polygons in `keep`")

    st.markdown(
        "Check the docs on [How to Authorize OSM Uploads](https://mozilla-ai.github.io/osm-ai-helper/authorization)"
    )
    osm_client_id = st.text_input("OSM_CLIENT_ID")
    osm_client_secret = st.text_input("OSM_CLIENT_SECRET")
    if (
        st.button("Upload all polygons in `keep`")
        and osm_client_id
        and osm_client_secret
    ):
        upload(output_path / "keep", osm_client_id, osm_client_secret)


st.title("Open Street Map AI Helper")

st.divider()

st.subheader("Click on the map to select a latitude and longitude")

m = folium.Map(location=[42.2489, -8.5117], zoom_start=11, tiles="OpenStreetMap")

st_data = st_folium(m, width=725)

if st_data.get("last_clicked"):
    lat = st_data["last_clicked"]["lat"]
    lon = st_data["last_clicked"]["lng"]
    st.write(f"Last Clicked: {lat}, {lon}")

    if st.button("Run Inference"):
        streamlit_handler = StreamlitHandler()
        logger.add(streamlit_handler, format="<level>{message}</level>")

        output_path = inference(lat_lon=(lat, lon), margin=1)

        for new in Path(output_path).glob("*.json"):
            handle_polygon(new)

        upload_results(output_path)
