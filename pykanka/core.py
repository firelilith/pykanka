import requests
import tenacity
import logging

from typing import Optional
from dataclasses import dataclass, field

from .exceptions import *

logger = logging.getLogger(__name__)


class CampaignList:
    pass


class CampaignClient:
    """Client to interact with the kanka.io API"""

    api_base_url = "https://kanka.io/api/1.0/campaigns/"

    def __init__(self, *, token: str, campaign_id: id, locale: str = "en_US"):
        self._api_token = token
        print(token)
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
    def _request(self, method, url, **kwargs):
        logger.debug(f"API call: {method.upper()} {url}" + (f" with kwargs {kwargs.items()}" if kwargs else ""))

        response = requests.request(method=method, url=url, headers=self._headers, **kwargs)

        logger.debug(f"API response: Status {response.status_code}")

        if response.status_code == 429:
            logger.warning(f"API throttling in effect. Retrying in 5 seconds.")
            raise APIThrottlingException()

        if not response.ok:
            logger.exception(f"API response not ok: Status {response.status_code}, Reason {response.reason}")
            raise ResponseNotOkayException()

        return response

    def search(self, entity_name: str):
        url = f"{self.campaign_api_url}search/{entity_name}"
        response = self._request(method="get", url=url)

        # TODO

    def get_entity_by_id(self):
        pass

    def get_entity_by_type_id(self):
        pass

    def all_entities(self):
        pass

    def all_of_type(self):
        pass


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

    child: "Child"

    header_image: Optional[str]
    image_uuid: Optional[int]

    is_attributes_private: bool
    is_private: bool
    is_template: bool

    tags: list
    urls: dict

    # only returned if related tag is set in request

    attributes:         Optional[list] = None
    entity_abilities:   Optional[list] = None
    entity_events:      Optional[list] = None
    entity_notes:       Optional[list] = None
    inventory:          Optional[list] = None
    posts:              Optional[list] = None
    relations:          Optional[list] = None

    def __init__(self, values):
        allowed_keys = {'attributes', 'campaign_id', 'child', 'child_id', 'created_at', 'created_by', 'entity_abilities', 'entity_events', 'entity_notes', 'header_image', 'id', 'image_uuid',
                        'inventory', 'is_attributes_private', 'is_private', 'is_template', 'name', 'posts', 'relations', 'tags', 'tooltip', 'type', 'type_id', 'updated_at', 'updated_by', 'urls'}
        if values.keys() - allowed_keys:
            raise InvalidValueError()
        self.__dict__.update(values)

        if values.get("child"):
            self.child = Child(values["child"])


@dataclass
class Child:
    def __init__(self, values):
        self.__dict__.update(values)
