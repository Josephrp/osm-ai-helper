from PIL import ImageDraw


def show_vlm_entry(entry):
    """
    Extracts image and points from entry and draws the points.

    Args:
        entry (dict): Dataset entry generated by
            [convert_to_vlm_dataset](osm_ai_helper.convert_to_vlm_dataset.convert_to_vlm_dataset).
            Expected format:

            ```py
            entry = [
                { "role": "user",
                "content" : [
                    {"type" : "text",  "text"  : instruction},
                    {"type" : "image", "image" : image} ]
                },
                { "role" : "assistant",
                "content" : [
                    {"type" : "text",  "text"  : str(points)} ]
                },
            ]
            ```

    Returns:
        Image: Image with points drawn.
    """
    image = entry[0]["content"][1]["image"]
    width, height = image.size
    points = eval(entry[1]["content"][0]["text"])
    draw = ImageDraw.Draw(image)

    for point in points:
        draw.circle((point[0] * width, point[1] * height), 5, fill="red")

    return image
