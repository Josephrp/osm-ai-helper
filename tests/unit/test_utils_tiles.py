import pytest

from osm_ai_helper.utils.tiles import group_elements_by_tile


@pytest.fixture
def square_across_the_4_tiles():
    return {
        "id": "Square across the 4 tiles",
        "geometry": [
            # Top-Left
            {"lat": 60, "lon": -60},
            # Bottom-Left
            {"lat": -60, "lon": -60},
            # Botton-Right
            {"lat": -60, "lon": 60},
            # Top-Right
            {"lat": 60, "lon": 60},
            # Top-Left
            {"lat": 60, "lon": -60},
        ],
    }


@pytest.fixture
def square_inside_the_top_lef_tile():
    return {
        "id": "Square inside the Top-Left tile",
        "geometry": [
            {"lat": 60, "lon": -60},
            {"lat": 59, "lon": -60},
            {"lat": 59, "lon": -59},
            {"lat": 60, "lon": -59},
            {"lat": 60, "lon": -60},
        ],
    }


def test_group_elements_by_tile(
    square_across_the_4_tiles, square_inside_the_top_lef_tile
):
    """
    At zoom=1, the world is divided in just 4 tiles.
    """
    elements = [square_across_the_4_tiles, square_inside_the_top_lef_tile]
    grouped = group_elements_by_tile(elements, zoom=1)
    assert grouped == {
        (0, 0): [square_across_the_4_tiles, square_inside_the_top_lef_tile],
        (0, 1): [square_across_the_4_tiles],
        (1, 0): [square_across_the_4_tiles],
        (1, 1): [square_across_the_4_tiles],
    }
