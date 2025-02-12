import json
from pathlib import Path

from PIL import Image
from shapely import Polygon

from osm_ai_helper.utils.coordinates import (
    TILE_SIZE,
    lat_lon_to_meters_col_row,
    meters_col_row_to_pixel_col_row,
)


def get_pixel_centroid(element, zoom) -> tuple[float, float]:
    pixel_polygon = Polygon(
        [
            meters_col_row_to_pixel_col_row(
                *lat_lon_to_meters_col_row(point["lat"], point["lon"]), zoom
            )
            for point in element["geometry"]
        ]
    )
    return pixel_polygon.centroid.x, pixel_polygon.centroid.y


def grouped_elements_to_points(
    group: list[dict], zoom: int, tile_col: int, tile_row: int
) -> str:
    points = []
    left_pixel = tile_col * TILE_SIZE
    top_pixel = tile_row * TILE_SIZE
    for element in group:
        col, row = get_pixel_centroid(element, zoom)
        local_col = (col - left_pixel) / TILE_SIZE
        local_row = (row - top_pixel) / TILE_SIZE
        points.append((round(local_col, 2), round(local_row, 2)))
    return points


def convert_to_vlm_dataset(input_dir: str, instruction: str):
    """
    Converts the grouped elements and tiles to a Visual Language Model dataset.

    Args:
        input_dir (str): Path to the directory containing the grouped elements and tiles.
            The grouped elements are in JSON files and the tiles are in JPEG files.
            The names of the files are in the format `{zoom}_{tile_col}_{tile_row}`.
        instruction (str): Instruction to use as prompt for the model.

    Returns:
        list: List of conversations.
    """
    vlm_dataset = []
    for grouped_elements_file in Path(input_dir).glob("**/*.json"):
        grouped_elements = json.loads(grouped_elements_file.read_text())["elements"]
        zoom, tile_col, tile_row = map(int, grouped_elements_file.stem.split("_"))
        points = grouped_elements_to_points(grouped_elements, zoom, tile_col, tile_row)
        image = Image.open(grouped_elements_file.with_suffix(".jpg"))

        conversation = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": instruction},
                    {"type": "image", "image": image},
                ],
            },
            {"role": "assistant", "content": [{"type": "text", "text": str(points)}]},
        ]
        vlm_dataset.append({"messages": conversation})

    return vlm_dataset
