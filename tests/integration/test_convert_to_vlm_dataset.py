import json

from PIL import Image


from osm_ai_helper.convert_to_vlm_dataset import convert_to_vlm_dataset


def test_convert_to_vlm_dataset(tmp_path):
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    grouped_elements_file = input_dir / "18_124853_97162.json"
    grouped_elements_file.write_text(
        json.dumps(
            {
                "elements": [
                    {
                        "type": "way",
                        "id": 1118870723,
                        "geometry": [
                            {"lat": 42.1527456, "lon": -8.5395705},
                            {"lat": 42.1527426, "lon": -8.5396184},
                            {"lat": 42.1527336, "lon": -8.5396306},
                            {"lat": 42.1527203, "lon": -8.5396306},
                            {"lat": 42.1527095, "lon": -8.539616},
                            {"lat": 42.1527119, "lon": -8.5395689},
                            {"lat": 42.1527215, "lon": -8.5395543},
                            {"lat": 42.1527408, "lon": -8.5395559},
                            {"lat": 42.1527456, "lon": -8.5395705},
                        ],
                        "tags": {"access": "private", "leisure": "swimming_pool"},
                    }
                ]
            }
        )
    )
    Image.new("RGB", (256, 256)).save(input_dir / "18_124853_97162.jpg")

    instruction = "Point to the swimming pools in the image."

    vlm_dataset = convert_to_vlm_dataset(input_dir, instruction)

    assert vlm_dataset == [
        {
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": instruction},
                        {
                            "type": "image",
                            "image": Image.open(input_dir / "18_124853_97162.jpg"),
                        },
                    ],
                },
                {
                    "role": "assistant",
                    "content": [{"type": "text", "text": "[(0.66, 0.49)]"}],
                },
            ]
        }
    ]
