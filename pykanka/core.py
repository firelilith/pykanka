import requests
import tenacity
import logging

from typing import Optional, List
from dataclasses import dataclass

from .exceptions import *

logger = logging.getLogger(__name__)


class CampaignList:
    pass


class CampaignClient:
    """Client to interact with the kanka.io API"""

    _map_name_to_id = {
        "character": 1,
        "family": 2,
        "location": 3,
        "organisation": 4,
        "item": 5,
        "note": 6,
        "event": 7,
        "calendar": 8,
        "race": 9,
        "quest": 10,
        "journal": 11,
        "tag": 12,
        "dice_roll": 13,
        "conversation": 14,
        "attribute_template": 15,
        "ability": 16,
        "map": 17,
        "timeline": 18,
        "menu_link": 19,
        "creature": 20}
    _map_id_to_endpoint = {
        1: "characters",
        2: "families",
        3: "locations",
        4: "organisations",
        5: "items",
        6: "notes",
        7: "events",
        8: "calendars",
        9: "races",
        10: "quests",
        11: "journals",
        12: "tags",
        13: "dice_rolls",
        14: "conversations",
        15: "attribute_templates",
        16: "abilities",
        17: "maps",
        18: "timelines",
        19: "menu_links",
        20: "creatures"
    }
    _map_name_to_endpoint = {
        "character": "characters",
        "family": "families",
        "location": "locations",
        "organisation": "organisations",
        "item": "items",
        "note": "notes",
        "event": "events",
        "calendar": "calendars",
        "race": "races",
        "quest": "quests",
        "journal": "journals",
        "tag": "tags",
        "dice_roll": "dice_rolls",
        "conversation": "conversations",
        "attribute_template": "attribute_templates",
        "ability": "abilities",
        "map": "maps",
        "timeline": "timelines",
        "menu_link": "menu_links",
        "creature": "creatures"
    }

    api_base_url = "https://kanka.io/api/1.0/campaigns/"

    def __init__(self, *, token: str, campaign_id: id, locale: str = "en_US"):
        self._api_token = token
        self._headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "kanka-locale": locale
        }

        self._campaign_id = campaign_id
        self._campaign_api_url = f"{self.api_base_url}{campaign_id}/"
        self._campaign_web_url = f"https://kanka.io/en/campaign/{campaign_id}/"

    @property
    def campaign_id(self):
        return self._campaign_id

    @property
    def campaign_api_url(self):
        return self._campaign_api_url

    @property
    def campaign_web_url(self):
        return self._campaign_web_url

    @classmethod
    def from_name(cls, *, token: str, campaign_name: str, locale: str = "en_US"):
        pass

    # @tenacity.retry(retry=tenacity.retry_if_exception_type(ResponseNotOkayException), stop=tenacity.stop_after_attempt(5))
    @tenacity.retry(retry=tenacity.retry_if_exception_type(APIThrottlingException), wait=tenacity.wait_fixed(5))
    def _request(self, method, url, stream=False, **kwargs):
        logger.debug(f"API call: {method.upper()} {url}" + (f" with kwargs {kwargs.items()}" if kwargs else ""))

        response = requests.request(method=method, url=url, headers=self._headers, **kwargs, stream=stream)

        logger.debug(f"API response: Status {response.status_code}")

        if response.status_code == 429:
            logger.warning(f"API throttling in effect. Retrying in 5 seconds.")
            raise APIThrottlingException()

        if not response.ok:
            logger.exception(f"API response not ok: Status {response.status_code}, Reason {response.reason}")
            logger.exception(f"Response content   : {response.text}")
            if response.status_code == 422:
                raise InvalidRequest(response.text)
            raise ResponseNotOkayException(response.status_code, response.reason)

        return response

    @tenacity.retry(retry=tenacity.retry_if_exception_type(APIThrottlingException), wait=tenacity.wait_fixed(5))
    def _file_patch_request(self, url, headers, name, img):
        logger.debug(f"API call: PATCH {url} with image file")

        response = requests.patch(url, params={"name": name}, files={"image": img}, headers=headers)

        logger.debug(f"API response: Status {response.status_code}")

        if not response.ok:
            logger.exception(f"API response not ok: Status {response.status_code}, Reason {response.reason}")
            logger.exception(f"Response content   : {response.text}")

        if response.status_code == 429:
            logger.warning(f"API throttling in effect. Retrying in 5 seconds.")
            raise APIThrottlingException()

    def search(self, entity_name: str):
        url = f"{self.campaign_api_url}search/{entity_name}"
        response_data = self._request(method="get", url=url).json()["data"]

        for ent in response_data:
            yield self.get_entity_by_id(ent["entity_id"])

    def get_entity_by_id(self, entity_id: int):
        url = f"{self.campaign_api_url}entities/{entity_id}"
        response = self._request(method="get", url=url)

        return Entity(response.json()["data"])

    def get_entity_by_child_id(self, entity_type: str, child_id: int):
        endpoint = self._map_name_to_endpoint[entity_type]
        child_url = f"{self.campaign_api_url}{endpoint}/{child_id}"

        child_response = self._request(method="get", url=child_url)
        entity_id = child_response.json()["data"]["entity_id"]

        return self.get_entity_by_id(entity_id=entity_id)

    def delete_entity_by_id(self, entity_id: int):
        url = f"{self.campaign_api_url}entities/{entity_id}"
        response_data = self._request(method="get", url=url).json()["data"]

        return self.delete_entity_by_child_id(response_data["type"], response_data["entity_id"])

    def delete_entity_by_child_id(self, entity_type: str, child_id: int):
        endpoint = self._map_name_to_endpoint[entity_type]
        child_url = f"{self.campaign_api_url}{endpoint}/{child_id}"

        response = self._request(method="delete", url=child_url)

        return response.ok

    def all_entities(self, *, types: Optional[List[str]] = None,
                              name=None,
                              is_private=None,
                              is_template=None,
                              created_by=None,
                              updated_by=None,
                              tags=None):
        all_filters = {"types": ",".join(types) if types is not None else None,
                       "name": name,
                       "is_private": is_private,
                       "is_template": is_template,
                       "created_by": created_by,
                       "updated_by": updated_by,
                       "tags": tags}
        filters = {i: j for i, j in all_filters.items() if j is not None}

        url = f"{self.campaign_api_url}entities/"
        response = self._request(method="get", url=url, params=filters).json()

        while True:
            for entity in response["data"]:
                yield Entity(entity)

            if response["links"]["next"] is None:
                return

            logging.debug("Page finished, getting new page of Entities")
            response = self._request("get", response["links"]["next"]).json()

    def create_entity(self, entity_type: str, **kwargs):
        image = None
        if "image" in kwargs:
            image = kwargs["image"]
            kwargs.pop("image")

        url = f"{self.campaign_api_url}{self._map_name_to_endpoint[entity_type]}"
        response = self._request("post", url=url, params=kwargs).json()["data"]

        if image is not None:
            ent = self.get_entity_by_id(response["entity_id"])
            self.upload_image(entity=ent, image_file=image)

        return self.get_entity_by_id(response["entity_id"])

    def update_entity(self, entity: "Entity", **kwargs):
        entity_type = entity.type
        child_id = entity.child_id
        url = f"{self.campaign_api_url}{self._map_name_to_endpoint[entity_type]}/{child_id}"
        self._request("patch", url=url, params=kwargs)
        entity = self.get_entity_by_id(entity_id=entity.id)
        return entity

    def upload_image(self, entity: "Entity", image_file):
        headers = {
            "Authorization": f"Bearer {self._api_token}",
            "Content-Type": "multipart/form-data",
            "Accept": "application/json"
        }
        self._file_patch_request(entity.urls.api, headers=headers, name=entity.name, img=image_file)



@dataclass
class Entity:
    name: str
    type: str
    tooltip: Optional[str]

    campaign_id: int
    id: int
    child_id: int
    type_id: int

    created_at: str
    created_by: int
    updated_at: str
    updated_by: int

    header_image: Optional[str]
    image_uuid: Optional[int]

    is_attributes_private: bool
    is_private: bool
    is_template: bool

    tags: list
    urls: "Urls"

    child: Optional["Child"] = None

    # only returned if related tag is set in request

    attributes:         Optional[list] = None
    entity_abilities:   Optional[list] = None
    entity_events:      Optional[list] = None
    entity_notes:       Optional[list] = None       # deprecated, remove in future release
    posts:              Optional[list] = None
    inventory:          Optional[list] = None
    relations:          Optional[list] = None

    def __init__(self, values):
        allowed_keys = {'attributes', 'campaign_id', 'child', 'child_id', 'created_at', 'created_by',
                        'entity_abilities', 'entity_events', 'entity_notes', 'header_image', 'id', 'image_uuid',
                        'inventory', 'is_attributes_private', 'is_private', 'is_template', 'name', 'posts', 'relations',
                        'tags', 'tooltip', 'type', 'type_id', 'updated_at', 'updated_by', 'urls'}
        if values.keys() - allowed_keys:
            raise InvalidValueError()
        self.__dict__.update(values)

        if values.get("child"):
            self.child = Child(values["child"])

        if values.get("urls"):
            self.urls = Urls(**values["urls"])


@dataclass(frozen=True)
class Urls:
    view: str
    api: str


@dataclass
class Child:
    def __init__(self, values: dict):
        self.__dict__.update(values)

        if values.get("urls"):
            self.urls = Urls(**values["urls"])

    def __repr__(self):
        return f"Child({', '.join(f'{key}={val}' for key, val in sorted(self.__dict__.items()))})"
