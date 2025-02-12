import pytest


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
