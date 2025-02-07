from collections import defaultdict
from io import BytesIO
from typing import Dict, List

import numpy as np
import requests

from PIL import Image

from osm_ai_helper.utils.coordinates import TILE_SIZE, lat_lon_to_pixel_col_row


def group_elements_by_tile(elements: List[Dict], zoom: int):
    grouped: dict[tuple, list[dict]] = defaultdict(list)

    for element in elements:
        pixel_polygon = []
        for point in element["geometry"]:
            pixel_point = lat_lon_to_pixel_col_row(point["lat"], point["lon"], zoom)
            pixel_polygon.append(pixel_point)

        pixel_polygon = np.array(pixel_polygon, dtype=np.int32)

        tiles = map(tuple, np.unique(pixel_polygon // TILE_SIZE, axis=0))
        for group in tiles:
            grouped[group].append(element)

    return grouped


def download_tile(zoom, tile_col, tile_row, token):
    MAPBOX = "https://api.mapbox.com/styles/v1/mapbox/satellite-v9/tiles"
    response = requests.get(
        f"{MAPBOX}/{zoom}/{tile_col}/{tile_row}?access_token={token}"
    )
    return Image.open(BytesIO(response.content))
