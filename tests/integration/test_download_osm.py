import json

from osm_ai_helper.download_osm import download_osm


def test_download_osm(tmp_path):
    output_dir = tmp_path / "output"

    download_osm(
        area="Ponteareas",
        output_dir=output_dir,
        selector="leisure=swimming_pool",
    )

    assert (output_dir / "Ponteareas.json").exists()

    elements = json.loads((output_dir / "Ponteareas.json").read_text())
    assert len(elements) > 0
    assert all(element["tags"]["leisure"] == "swimming_pool" for element in elements)


def test_download_osm_discard(tmp_path):
    output_dir = tmp_path / "output"

    download_osm(
        area="Ponteareas",
        output_dir=output_dir,
        selector="leisure=swimming_pool",
    )

    assert (output_dir / "Ponteareas.json").exists()

    unfiltered = json.loads((output_dir / "Ponteareas.json").read_text())
    assert any(element["tags"].get("location") == "indoor" for element in unfiltered)

    download_osm(
        area="Ponteareas",
        output_dir=output_dir,
        selector="leisure=swimming_pool",
        discard={"location": "indoor"},
    )

    filtered = json.loads((output_dir / "Ponteareas.json").read_text())
    assert all(element["tags"].get("location") != "indoor" for element in filtered)
