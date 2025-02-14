import pytest

from osm_ai_helper.convert_to_yolo_dataset import grouped_elements_to_annotation


@pytest.mark.parametrize(
    "tile_col, tile_row, expected_annotation",
    [
        (
            0,
            0,
            ("0 0.83 0.79 0.33 0.42\n" "0 0.67 0.59 0.01 0.01\n"),
        ),
        (
            0,
            1,
            ("0 0.83 0.21 0.33 0.42\n"),
        ),
        (
            1,
            0,
            ("0 0.17 0.79 0.33 0.42\n"),
        ),
        (
            1,
            1,
            ("0 0.17 0.21 0.33 0.42\n"),
        ),
    ],
)
def test_grouped_elements_to_annotation(
    square_across_the_4_tiles,
    square_inside_the_top_lef_tile,
    tile_col,
    tile_row,
    expected_annotation,
):
    if (tile_col, tile_row) == (0, 0):
        group = [square_across_the_4_tiles, square_inside_the_top_lef_tile]
    else:
        group = [square_across_the_4_tiles]
    annotation = grouped_elements_to_annotation(
        group, zoom=1, tile_col=tile_col, tile_row=tile_row
    )
    assert annotation == expected_annotation
