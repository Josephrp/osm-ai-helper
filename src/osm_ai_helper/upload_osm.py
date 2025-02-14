import json
import os
import xml.etree.ElementTree as ET
from contextlib import contextmanager
from pathlib import Path

from fire import Fire
from loguru import logger
from requests_oauthlib import OAuth2Session

API = "https://api.openstreetmap.org/api/0.6"

# Get from OSM Application registration
CLIENT_ID = os.environ["OSM_CLIENT_ID"]
CLIENT_SECRET = os.environ["OSM_CLIENT_SECRET"]
REDIRECT_URI = "https://127.0.0.1:8000"

AUTHORIZATION_BASE_URL = "https://www.openstreetmap.org/oauth2/authorize"
TOKEN_URL = "https://www.openstreetmap.org/oauth2/token"
TOKEN_FILE = "/tmp/osm_token.json"


def get_oauth_session(token=None):
    return OAuth2Session(CLIENT_ID, redirect_uri=REDIRECT_URI, token=token, scope=["write_api"])


def fetch_token(session, authorization_response):
    return session.fetch_token(
        TOKEN_URL,
        authorization_response=authorization_response,
        client_secret=CLIENT_SECRET,
    )


def load_token():
    try:
        with open(TOKEN_FILE, 'r') as f:
            token = json.load(f)
            logger.info(f"Token loaded from {TOKEN_FILE}")
            return token
    except FileNotFoundError:
        logger.info(f"Token file {TOKEN_FILE} not found.")
        return None
    except json.JSONDecodeError:
        logger.warning(f"Invalid JSON in token file {TOKEN_FILE}. Ignoring.")
        return None

def authorize():
    osm_session = get_oauth_session()

    authorization_url, state = osm_session.authorization_url(
        AUTHORIZATION_BASE_URL)

    print(f"Please go to this URL and authorize the application: {authorization_url}")
    authorization_response = input("Enter the full callback URL you were redirected to: ")

    token = fetch_token(osm_session, authorization_response)
    logger.info(f"Token fetched successfully: {token}")
    with open(TOKEN_FILE, 'w') as f:
        json.dump(token, f)
    logger.info(f"Token saved to {TOKEN_FILE}")
    return token


def ensure_authorized_session():
    token_data = load_token()

    osm_session = get_oauth_session(token=token_data)

    if not token_data:
        logger.info("No valid token found, starting authorization flow.")
        token = authorize()
        osm_session.token = token
    else:
        if 'access_token' in osm_session.token and osm_session.token['access_token']:
            logger.info("Token exists, attempting to use it.")
        else:
             logger.warning("Stored token might be invalid or incomplete. Re-authorizing.")
             token = authorize()
             osm_session.token = token

    return osm_session


@contextmanager
def open_changeset(
    osm_session,
    url: str = "https://github.com/mozilla-ai/osm-ai-helper",
    created_by: str= "https://github.com/mozilla-ai/osm-ai-helper",
    comment: str = "Add Swimming Pools",
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
        response = osm_session.put( # Use the session for requests
            f"{API}/changeset/create",
            data=body,
            headers={
                "Content-type": "text/xml",
            },
        )
        logger.info(f"CREATE: {response}, {response.content}")
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        changeset = int(response.content.decode().strip())
        yield changeset
    finally:
        if changeset:
            response = osm_session.put( # Use the session for requests
                f"{API}/changeset/{changeset}/close",
            )
            logger.info(f"CLOSE: {response}, {response.content}")
            response.raise_for_status()


def upload_polygon(osm_session, lon_lat_polygon, changeset): # Pass the OAuth session
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

    response = osm_session.post( # Use the session for requests
        f"{API}/changeset/{changeset}/upload",
        data=ET.tostring(osmchange, "utf-8"),
        headers={
            "Content-type": "text/xml",
        },
    )
    logger.info(f"UPLOAD: {response}, {response.content}")
    response.raise_for_status()


def upload(results_folder: str):

    osm_session = ensure_authorized_session()

    lon_lat_polygons = [
        json.loads(result.read_text()) for result in Path(results_folder).glob("*.json")
    ]

    with open_changeset(osm_session) as changeset:
        for lon_lat_polygon in lon_lat_polygons:
            upload_polygon(osm_session, lon_lat_polygon, changeset)


if __name__ == "__main__":
    Fire(upload)
