import json
import os
from pathlib import Path

from fire import Fire
from loguru import logger

from osm_ai_helper.utils.tiles import download_tile, group_elements_by_tile


@logger.catch(reraise=True)
def create_tile_dataset(input_annotation_file: str, output_dir: str, zoom: int = 18):
    """
    Create dataset of satellite images and annotations from the given OSM elements.

    Groups the elements by tile and downloads the satellite image
    corresponding to the tile.

    Args:
        input_annotation_file (str): Path to the input annotation file.
            The file should be a JSON file containing a list of OSM elements.
            See [download_osm](osm_ai_helper.download_osm.download_osm).
        output_dir (str): Output directory.
            The images and annotations will be saved in this directory.
            The images will be saved as JPEG files and the annotations as JSON files.
            The names of the files will be in the format `{zoom}_{tile_col}_{tile_row}`.

        zoom (int, optional): Zoom level of the tiles to download.
            See https://docs.mapbox.com/help/glossary/zoom-level/.
            Defaults to 18.
    """
    annotation_path = Path(input_annotation_file)
    area = annotation_path.stem
    output_path = Path(output_dir)

    (output_path / area).mkdir(exist_ok=True, parents=True)

    elements = json.loads(annotation_path.read_text())

    logger.info("Grouping elements by tile")
    grouped = group_elements_by_tile(elements, zoom)

    total = len(grouped)
    n = 0
    logger.info("Downloading tiles and writing annotation")
    for (tile_col, tile_row), group in grouped.items():
        if n % 50 == 0:
            logger.info(f"Processed {n}/{total} tiles")
        n += 1
        logger.info(f"Downloading tile {tile_col}, {tile_row}")
        output_name = f"{zoom}_{tile_col}_{tile_row}"
        image_name = f"{output_path / area / output_name}.jpg"
        annotation_name = f"{output_path / area / output_name}.json"
        if not Path(image_name).exists():
            image = download_tile(zoom, tile_col, tile_row, os.environ["MAPBOX_TOKEN"])
            image.save(image_name)
        if not Path(annotation_name).exists():
            Path(annotation_name).write_text(
                json.dumps(
                    {
                        "elements": group,
                    }
                )
            )


if __name__ == "__main__":
    Fire(create_tile_dataset)
