import pytest

from osm_ai_helper.utils.osm import get_area_id


@pytest.mark.parametrize(
    "area_name, area_id",
    [
        ("Ponteareas", 3600345984),
        ("Galicia", 3600349036),
        ("Spain", 3601311341),
    ],
)
def test_get_area_id(area_name, area_id):
    assert get_area_id(area_name) == area_id
