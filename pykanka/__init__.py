import requests
import typing
import tenacity
from time import time

from requests_cache import CachedSession

import pykanka.entities
from pykanka.exceptions import *


class KankaClient:
    """Main client for interacting with the Kanka.io API"""

    def __init__(self, token: str, campaign: typing.Union[str, int], cache: bool = True, cache_name: str = "kanka_cache", cache_duration: int = 600, **kwargs):
        """Create a client associated with a specific campaign.

        :param token: str
        :param campaign: Union[str, int]
        :param cache: bool
        :param cache_name: str
        :param cache_duration: int
        :param kwargs:
        """

        if cache:
            self.cache = CachedSession(cache_name, backend="sqlite", expire_after=cache_duration)

        self.api_token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        self.api_base_url = "https://kanka.io/api/1.0/campaigns/"

        if type(campaign) == int:
            self.campaign_id = campaign
        elif type(campaign) == str:
            self.campaign_id = self._get_campaign_id(campaign)
        else:
            raise ValueError("Campaign not valid, provide either a valid name or id")

        self.campaign_base_url = f"{self.api_base_url}{self.campaign_id}/"

    #  Utility functions to locate campaign from its name

    def _get_campaigns(self):
        campaigns = requests.get("https://kanka.io/api/1.0/campaigns/", headers=self.headers)

        if not campaigns.ok:
            raise ResponseNotOkError(f"Response not OK, code {campaigns.status_code}:\n{campaigns.text}")

        return campaigns.json()

    def _get_campaign_id(self, name):
        campaigns = self._get_campaigns()

        for campaign in campaigns["data"]:
            if campaign["name"].lower() == name.lower():
                campaign_id = campaign["id"]
                return campaign_id

        raise CampaignError(f"No campaign of the name '{name}' found")

    @tenacity.retry(retry=tenacity.retry_if_exception_type(ApiThrottlingError), wait=tenacity.wait_fixed(5))
    def _request(self, method, url, refresh=False, **kwargs):
        if refresh:
            with self.cache.cache_disabled():
                response = self.cache.request(method=method, url=url, headers=self.headers, **kwargs)
        else:
            response = self.cache.request(method=method, url=url, headers=self.headers, **kwargs)

        if response.status_code == 429:
            print("API request limit reached. Retrying in 5 seconds.")
            raise ApiThrottlingError()

        return response

    def request_get(self, url, refresh=False, **kwargs):
        """get request with proper headers. usually shouldn't be accessed directly."""
        return self._request("get", url, refresh=refresh, **kwargs)

    def request_post(self, url, **kwargs):
        """post request with proper headers. usually shouldn't be accessed directly."""
        return self._request("post", url, **kwargs)

    def request_put(self, url, **kwargs):
        """put request with proper headers. usually shouldn't be accessed directly."""
        return self._request("put", url, **kwargs)

    def request_patch(self, url, **kwargs):
        """patch request with proper headers. usually shouldn't be accessed directly."""
        return self._request("patch", url, **kwargs)

    def request_delete(self, url, **kwargs):
        """delete request with proper headers. usually shouldn't be accessed directly."""
        return self._request("delete", url, **kwargs)

    def entity(self, entity_id: int) -> "pykanka.entities.Entity":
        return pykanka.entities.Entity.from_id(self, entity_id)

    def location(self, location_id: int) -> "pykanka.entities.Location":
        return pykanka.entities.Location.from_id(self, location_id)

    def get_all_entities(self) -> typing.Dict[typing.Tuple[str, int], "pykanka.entities.Entity"]:

        url = f"{self.campaign_base_url}entities"
        done = False
        members = dict()

        while not done:
            response = self.request_get(url)

            if not response.ok:
                raise ResponseNotOkError(f"Code {response.status_code}: {response.text}")

            content = response.json()

            if not content["links"]["next"]:
                done = True
            else:
                url = content["links"]["next"]

            for entry in content["data"]:
                entity = pykanka.entities.Entity.from_json(self, entry)
                members[(entity.data.name, entity.data.id)] = entity

        return members

    def get_all_locations(self) -> typing.Dict[typing.Tuple[str, int], "pykanka.entities.Location"]:

        url = f"{self.campaign_base_url}locations"
        done = False
        members = dict()

        while not done:
            response = self.request_get(url)

            if not response.ok:
                raise ResponseNotOkError(f"Code {response.status_code}: {response.text}")

            content = response.json()

            if not content["links"]["next"]:
                done = True
            else:
                url = content["links"]["next"]

            for entry in content["data"]:
                location = pykanka.entities.Location.from_json(self, entry)
                members[(location.data.name, location.data.id)] = location

        return members


