import json
import os
import xml.etree.ElementTree as ET
from contextlib import contextmanager
from pathlib import Path

import requests
from fire import Fire
from loguru import logger
from requests.auth import HTTPBasicAuth

API = "https://api.openstreetmap.org/api/0.6"


@contextmanager
def open_changeset(
    username: str,
    password: str,
    url: str = "https://github.com/mozilla-ai/osm-ai-helper",
    created_by: str= "https://github.com/mozilla-ai/osm-ai-helper",
    comment: str = "",
    source: str = "aerial imagery",
):
    root = ET.Element("osm")
    element = ET.SubElement(root, "changeset")
    ET.SubElement(element, "tag", {"k": "url", "v": url})
    ET.SubElement(element, "tag", {"k": "import", "v": "yes"})
    ET.SubElement(element, "tag", {"k": "created_by", "v": created_by})
    ET.SubElement(element, "tag", {"k": "comment", "v": comment})
    ET.SubElement(element, "tag", {"k": "source", "v": source})
    body = ET.tostring(root, "utf-8")

    changeset = None
    try:
        response = requests.put(
            f"{API}/changeset/create",
            data=body,
            auth=HTTPBasicAuth(username, password),
            headers={
                "Content-type": "text/xml",
            },
        )
        logger.info(f"CREATE: {response}, {response.content}")
        changeset = int(response.content.decode().strip())
        yield changeset
    finally:
        if changeset:
            response = requests.put(
                f"{API}/changeset/{changeset}/close",
                auth=HTTPBasicAuth(username, password),
            )
            logger.info(f"CLOSE: {response}, {response.content}")


def upload_polygon(username, password, lon_lat_polygon, changeset):
    osmchange = ET.Element("osmChange", version="0.6", generator="iD")
    create = ET.SubElement(osmchange, "create")

    way = ET.Element("way", id="-1", version="0")
    tags = {
        "leisure": "swimming_pool",
        "access": "private",
        "location": "outdoor"
    }
    for k, v in tags.items():
        ET.SubElement(way, "tag", k=k, v=v)

    # Polygon contains a duplicate of the first point
    lon_lat_polygon.pop()

    n = 1
    for lon, lat in lon_lat_polygon:
        ET.SubElement(
            create, "node", id=f"-{n}", lon=f"{lon}", lat=f"{lat}", version="0"
        )
        ET.SubElement(way, "nd", ref=f"-{n}")
        n += 1
    # OSM requires to duplicate first point to close the polygon
    ET.SubElement(way, "nd", ref="-1")
    create.append(way)

    ET.SubElement(osmchange, "modify")
    delete = ET.SubElement(osmchange, "delete")
    delete.set("if-unused", "true")
    for element in create:
        element.attrib["changeset"] = str(changeset)

    response = requests.post(
        f"{API}/changeset/{changeset}/upload",
        data=ET.tostring(osmchange, "utf-8"),
        auth=HTTPBasicAuth(username, password),
        headers={
            "Content-type": "text/xml",
        },
    )
    logger.info(f"UPLOAD: {response}, {response.content}")


def upload(results_folder: str):
    username = os.environ["OSM_USERNAME"]
    password = os.environ["OSM_PASSWORD"]

    lon_lat_polygons = [
        json.loads(result.read_text()) for result in Path(results_folder).glob("*.json")
    ]

    with open_changeset(username, password) as changeset:
        for lon_lat_polygon in lon_lat_polygons:
            upload_polygon(username, password, lon_lat_polygon, changeset)


if __name__ == "__main__":
    Fire(upload)
