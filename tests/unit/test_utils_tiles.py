from osm_ai_helper.utils.tiles import group_elements_by_tile


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
