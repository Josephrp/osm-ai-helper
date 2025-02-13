import json
from pathlib import Path
from typing import Tuple

from fire import Fire
from loguru import logger

from PIL import Image
from ultralytics import FastSAM, YOLO

from osm_ai_helper.utils.coordinates import (
    TILE_SIZE,
    lat_lon_to_tile_col_row,
    lat_lon_to_bbox,
)
from osm_ai_helper.utils.inference import (
    download_stacked_image_and_mask,
    tile_prediction,
)
from osm_ai_helper.utils.osm import get_elements
from osm_ai_helper.utils.polygons import (
    crop_polygon,
    polygon_evaluation,
    paint_polygon_evaluation,
    pixel_polygon_to_lat_lon_polygon,
)
from osm_ai_helper.utils.tiles import group_elements_by_tile


@logger.catch(reraise=True)
def run_inference(
    model_file: str,
    output_dir: str,
    lat_lon: Tuple[float, float],
    token: str,
    margin: int = 5,
    selector: str = "leisure=swimming_pool",
    zoom: int = 18,
):
    bbox_predictor = YOLO(model_file)
    sam_predictor = FastSAM("FastSAM-s.pt")
    bbox = lat_lon_to_bbox(*lat_lon, zoom, margin)

    output_path = Path(output_dir) / f"{zoom}_{'_'.join(map(str, bbox))}"
    output_path.mkdir(exist_ok=True, parents=True)

    logger.info(f"Downloading elements for {selector} in {bbox}")
    grouped_elements, _ = group_elements_by_tile(
        get_elements(selector, bbox=bbox), zoom
    )

    logger.info(f"Downloading stacked image and mask for {bbox}")
    stacked_image, stacked_mask = download_stacked_image_and_mask(
        bbox, grouped_elements, zoom, token
    )
    Image.fromarray(stacked_image).save(output_path / "full_image.png")
    Image.fromarray(stacked_mask).save(output_path / "full_mask.png")

    logger.info("Predicting on stacked image")
    # Change to BGR for inference
    stacked_output = tile_prediction(
        bbox_predictor, sam_predictor, stacked_image[:, :, ::-1]
    )

    logger.info("Finding existing, new and missed polygons")
    existing, new, missed = polygon_evaluation(stacked_mask, stacked_output)

    logger.info("Painting evaluation")
    stacked_image_pil = Image.fromarray(stacked_image)
    painted_img = paint_polygon_evaluation(stacked_image_pil, existing, new, missed)
    painted_img.save(output_path / "full_image_painted.png")

    _, west, north, _ = bbox
    left_col, top_row = lat_lon_to_tile_col_row(north, west, zoom)
    top_pixel = top_row * TILE_SIZE
    left_pixel = left_col * TILE_SIZE

    logger.info("Saving new polygons")
    for n, polygon in enumerate(new):
        lon_lat_polygon = pixel_polygon_to_lat_lon_polygon(
            polygon, top_pixel, left_pixel, zoom
        )

        with open(f"{output_path}/{n}.json", "w") as f:
            json.dump(lon_lat_polygon, f)

        painted_image_crop = crop_polygon(polygon, painted_img, margin=50)
        painted_image_crop.save(f"{output_path}/{n}_painted.png")

    return painted_img, existing, new, missed


if __name__ == "__main__":
    Fire(run_inference)
