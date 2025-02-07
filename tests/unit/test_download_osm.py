import pytest

from osm_ai_helper.download_osm import get_elements


@pytest.mark.parametrize(
    "filter_args",
    [
        {"area": "Ponteareas"},
        # south, west, north, east
        {"bbox": (42.1094, -8.5824, 42.2514, -8.432)},
    ],
)
def test_get_elements(filter_args):
    elements = get_elements(selector="leisure=swimming_pool", **filter_args)
    assert len(elements) > 0
    assert all(isinstance(element["geometry"], list) for element in elements)
