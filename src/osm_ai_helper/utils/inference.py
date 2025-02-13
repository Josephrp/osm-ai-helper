import cv2
import numpy as np
from shapely import Polygon, box

from osm_ai_helper.utils.coordinates import (
    TILE_SIZE,
    lat_lon_to_tile_col_row,
    lat_lon_to_pixel_col_row,
)
from osm_ai_helper.utils.tiles import download_tile


def grouped_elements_to_mask(group, zoom, tile_col, tile_row):
    left_pixel = tile_col * TILE_SIZE
    top_pixel = tile_row * TILE_SIZE
    mask = np.zeros((TILE_SIZE, TILE_SIZE), dtype=np.uint8)
    bbox = box(left_pixel, top_pixel, left_pixel + TILE_SIZE, top_pixel + TILE_SIZE)
    for element in group:
        pixel_polygon = [
            lat_lon_to_pixel_col_row(point["lat"], point["lon"], zoom)
            for point in element["geometry"]
        ]
        bounded_polygon = Polygon(pixel_polygon).intersection(bbox).exterior.coords

        local_polygon = []
        for col, row in bounded_polygon:
            local_polygon.append((col - left_pixel, row - top_pixel))

        mask = cv2.fillPoly(
            mask, [np.array(local_polygon, dtype=np.int32)], color=(255, 0, 0)
        )
    return mask


def download_stacked_image_and_mask(bbox, grouped_elements, zoom, token):
    south, west, north, east = bbox
    left, top = lat_lon_to_tile_col_row(north, west, zoom)
    right, bottom = lat_lon_to_tile_col_row(south, east, zoom)

    stacked_image = np.zeros(
        ((right - left) * TILE_SIZE, (bottom - top) * TILE_SIZE, 3), dtype=np.uint8
    )
    stacked_mask = np.zeros(
        ((right - left) * TILE_SIZE, (bottom - top) * TILE_SIZE), dtype=np.uint8
    )

    for n_col, tile_col in enumerate(range(left, right)):
        for n_row, tile_row in enumerate(range(top, bottom)):
            group = grouped_elements[(tile_col, tile_row)]

            img = download_tile(zoom, tile_col, tile_row, token)

            mask = grouped_elements_to_mask(group, zoom, tile_col, tile_row)

            stacked_image[
                n_row * TILE_SIZE : (n_row + 1) * TILE_SIZE,
                n_col * TILE_SIZE : (n_col + 1) * TILE_SIZE,
            ] = np.array(img)

            stacked_mask[
                n_row * TILE_SIZE : (n_row + 1) * TILE_SIZE,
                n_col * TILE_SIZE : (n_col + 1) * TILE_SIZE,
            ] = mask

    return stacked_image, stacked_mask


def yield_tile_corners(stacked_image: np.ndarray, tile_size: int, overlap: float):
    for top in range(0, stacked_image.shape[1], int(tile_size * (1 - overlap))):
        bottom = top + tile_size
        if bottom > stacked_image.shape[1]:
            bottom = stacked_image.shape[1]
            top = stacked_image.shape[1] - tile_size

        for left in range(0, stacked_image.shape[0], int(tile_size * (1 - overlap))):
            right = left + tile_size
            if right > stacked_image.shape[0]:
                right = stacked_image.shape[0]
                left = stacked_image.shape[0] - tile_size

            yield top, left, bottom, right


def tile_prediction(
    bbox_predictor, sam_predictor, image: np.ndarray, overlap: float = 0.125
):
    stacked_output = np.zeros((image.shape[0], image.shape[1]), dtype=np.uint8)
    for top, left, bottom, right in yield_tile_corners(image, TILE_SIZE, overlap):
        tile_image = image[left:right, top:bottom].copy()
        sam_predictor.set_image(tile_image)

        bbox_result = bbox_predictor.predict(tile_image)

        for bbox in bbox_result:
            if len(bbox.boxes.xyxy) == 0:
                continue

            masks, *_ = sam_predictor.predict(
                point_coords=None,
                point_labels=None,
                box=[list(int(x) for x in bbox.boxes.xyxy[0])],
                multimask_output=False,
            )

            stacked_output[left:right, top:bottom] += masks[0].astype(np.uint8)

    stacked_output[stacked_output != 0] = 255

    return stacked_output
