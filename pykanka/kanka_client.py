import time
import types
from typing import Generator, Union, Callable, Dict, Any

import requests
import tenacity

import pykanka.child_types
import pykanka.entities
from pykanka.exceptions import *

import logging

logger = logging.getLogger(__name__)


class KankaClient:
    """Main client for interacting with the Kanka.io API"""

    _type_dictionary = dict(
        location=pykanka.child_types.Location,
        character=pykanka.child_types.Character,
        family=pykanka.child_types.Family,
        organisation=pykanka.child_types.Organisation,
        timeline=pykanka.child_types.Timeline,
        race=pykanka.child_types.Race,
        note=pykanka.child_types.Note,
        map=pykanka.child_types.Map,
        tag=pykanka.child_types.Tag,
        quest=pykanka.child_types.Quest,
        journal=pykanka.child_types.Journal,
        item=pykanka.child_types.Item,
        event=pykanka.child_types.Event,
        ability=pykanka.child_types.Ability,
        calendar=pykanka.child_types.Calendar,

        entity=pykanka.entities.Entity
    )

    def __init__(self,
                 token: str,
                 campaign: Union[str, int] = None,
                 cache_duration: int = 600,
                 on_request: Callable = None,
                 kanka_locale: str = None):
        """Create a client associated with a specific campaign.

        :param token: User API token from kanka.io
        :param campaign: Campaign name or ID
        """

        logger.debug(f"creating client for campaign: {campaign}")

        self.test = types.SimpleNamespace(a="a", b="b")

        self._api_token = token
        self._headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        }
        if kanka_locale:
            self._headers["kanka-locale"] = kanka_locale

        self._api_base_url = "https://kanka.io/api/1.0/campaigns/"

        self._cache = dict()
        self._cache_duration = max(cache_duration, 0)

        self._campaign_id = None
        self._campaign_base_url = None

        if campaign:
            self.set_campaign(campaign)

        logger.info(f"client for campaign with id: {self._campaign_id} was created")

        self._on_request = on_request

    @property
    def cache(self):
        t = time.time()
        for entry in self._cache.keys():
            if t - self._cache[entry][1].time() > self._cache_duration:
                self._cache.pop(entry)
        return self._cache

    @property
    def campaign_id(self):
        return self._campaign_id

    @property
    def campaign_base_url(self):
        return self._campaign_base_url

    def view_campaigns(self):
        return requests.get("https://kanka.io/api/1.0/campaigns/", headers=self._headers).json()

    def set_campaign(self, campaign: Union[int, str]):
        if type(campaign) == int:
            self._campaign_id = campaign
            self._campaign_base_url = f"{self._api_base_url}{self.campaign_id}/"
        elif type(campaign) == str:
            self._campaign_id = self._get_campaign_id(campaign)
            self._campaign_base_url = f"{self._api_base_url}{self.campaign_id}/"

    def _get_campaign_id(self, name: str):
        campaigns = requests.get("https://kanka.io/api/1.0/campaigns/", headers=self._headers).json()
        done = False

        while not done:
            for campaign in campaigns["data"]:
                if campaign["name"].lower() == name.lower():
                    campaign_id = campaign["id"]
                    return campaign_id

            if not campaigns["links"]["next"]:
                done = True
            else:
                campaigns = requests.get(campaigns["links"]["next"], headers=self._headers).json()

        raise CampaignError(f"No campaign of the name '{name}' found")

    @tenacity.retry(retry=tenacity.retry_if_exception_type(ApiThrottlingError), wait=tenacity.wait_fixed(5))
    def _request(self, method, url, **kwargs):
        logger.info(f"requesting '{method.upper()}' on {url}")
        response = requests.request(method=method, url=url, headers=self._headers, **kwargs)

        if self._on_request:
            self._on_request(method=method, url=url, response=response, **kwargs)

        if response.status_code == 429:
            logger.info(f"API request limit reached. retrying in 5 seconds.")
            raise ApiThrottlingError()
        elif not response.ok:
            logger.warning(f"response not okay (code {response.status_code}): {response.reason}")

        return response

    def request_get(self, url: str, refresh=False, **kwargs):
        """get request with proper headers. usually shouldn't be accessed directly."""
        if not refresh and self._cache_duration:
            if url in self.cache:
                logger.debug(f"found request for {url} in cache.")
                return self._cache[url][0]  # return the reponse portion of the cache

        response = self._request("get", url, **kwargs)

        if self._cache_duration:
            self._cache[url] = (response, time)

        return response

    def request_post(self, url: str, **kwargs):
        """post request with proper headers. usually shouldn't be accessed directly."""
        return self._request("post", url, **kwargs)

    def request_put(self, url: str, **kwargs):
        """put request with proper headers. usually shouldn't be accessed directly."""
        return self._request("put", url, **kwargs)

    def request_patch(self, url: str, **kwargs):
        """patch request with proper headers. usually shouldn't be accessed directly."""
        return self._request("patch", url, **kwargs)

    def request_delete(self, url: str, **kwargs):
        """delete request with proper headers. usually shouldn't be accessed directly."""
        return self._request("delete", url, **kwargs)

    def search(self, name: str, refresh: bool = True):
        url = f"{self.campaign_base_url}search/{name}"
        response = self.request_get(url=url, refresh=refresh)
        for entry in response.json()["data"]:
            yield self.get_entity(entity_id=entry["entity_id"], refresh=refresh)

    def get_entity_of_type(self, type_name: str, type_specific_id: int = None, refresh: bool = False) -> Any:
        if type_specific_id:
            return self._type_dictionary[type_name].from_id(self, type_specific_id, refresh=refresh)

        return self._type_dictionary[type_name](client=self)

    def get_type_metadata(self, type_name: str, refresh: bool = True) -> Dict[str, Any]:
        data = self.request_get(self.get_entity_of_type(type_name=type_name, refresh=refresh).base_url).json()["meta"]
        data.pop("current_page")
        data.pop("per_page")
        data.pop("last_page")
        data.pop("from")
        data.pop("to")
        return data

    def get_all_of_type(self, type_name: str, refresh: bool = True):
        url = self.get_entity_of_type(type_name=type_name).base_url
        cls = self.get_entity_of_type(type_name=type_name).__class__

        while url:
            data = self.request_get(url, refresh=refresh).json()

            url = data["links"]["next"]

            for entry in data["data"]:
                entity = cls.from_json(self, entry)
                yield entity

    def get_entity(self, entity_id: int = None, refresh: bool = False) -> pykanka.entities.Entity:
        return self.get_entity_of_type(type_name="entity", type_specific_id=entity_id, refresh=refresh)

    def get_ability(self, ability_id: int = None, refresh: bool = False) -> pykanka.child_types.Ability:
        return self.get_entity_of_type(type_name="ability", type_specific_id=ability_id, refresh=refresh)

    def get_calendar(self, calendar_id: int = None, refresh: bool = False) -> pykanka.child_types.Calendar:
        return self.get_entity_of_type(type_name="calendar", type_specific_id=calendar_id, refresh=refresh)

    def get_character(self, character_id: int = None, refresh: bool = False) -> pykanka.child_types.Character:
        return self.get_entity_of_type(type_name="character", type_specific_id=character_id, refresh=refresh)

    def get_event(self, event_id: int = None, refresh: bool = False) -> pykanka.child_types.Event:
        return self.get_entity_of_type(type_name="event", type_specific_id=event_id, refresh=refresh)

    def get_family(self, family_id: int = None, refresh: bool = False) -> pykanka.child_types.Family:
        return self.get_entity_of_type(type_name="family", type_specific_id=family_id, refresh=refresh)

    def get_item(self, item_id: int = None, refresh: bool = False) -> pykanka.child_types.Item:
        return self.get_entity_of_type(type_name="item", type_specific_id=item_id, refresh=refresh)

    def get_journal(self, journal_id: int = None, refresh: bool = False) -> pykanka.child_types.Journal:
        return self.get_entity_of_type(type_name="journal", type_specific_id=journal_id, refresh=refresh)

    def get_location(self, location_id: int = None, refresh: bool = False) -> pykanka.child_types.Location:
        return self.get_entity_of_type(type_name="location", type_specific_id=location_id, refresh=refresh)

    def get_map(self, map_id: int = None, refresh: bool = False) -> pykanka.child_types.Map:
        return self.get_entity_of_type(type_name="map", type_specific_id=map_id, refresh=refresh)

    def get_note(self, note_id: int = None, refresh: bool = False) -> pykanka.child_types.Note:
        return self.get_entity_of_type(type_name="note", type_specific_id=note_id, refresh=refresh)

    def get_organisation(self, organisation_id: int = None, refresh: bool = False) -> pykanka.child_types.Organisation:
        return self.get_entity_of_type(type_name="organisation", type_specific_id=organisation_id, refresh=refresh)

    def get_quest(self, quest_id: int = None, refresh: bool = False) -> pykanka.child_types.Quest:
        return self.get_entity_of_type(type_name="quest", type_specific_id=quest_id, refresh=refresh)

    def get_race(self, race_id: int = None, refresh: bool = False) -> pykanka.child_types.Race:
        return self.get_entity_of_type(type_name="race", type_specific_id=race_id, refresh=refresh)

    def get_tag(self, tag_id: int = None, refresh: bool = False) -> pykanka.child_types.Tag:
        return self.get_entity_of_type(type_name="tag", type_specific_id=tag_id, refresh=refresh)

    def get_timeline(self, timeline_id: int = None, refresh: bool = False) -> pykanka.child_types.Timeline:
        return self.get_entity_of_type(type_name="timeline", type_specific_id=timeline_id, refresh=refresh)

    def all_entities(self, refresh: bool = False) -> Generator[pykanka.entities.Entity, None, None]:
        return self.get_all_of_type(type_name="entity", refresh=refresh)

    def all_abilities(self, refresh: bool = False) -> Generator[pykanka.child_types.Ability, None, None]:
        return self.get_all_of_type(type_name="ability", refresh=refresh)

    def all_calendars(self, refresh: bool = False) -> Generator[pykanka.child_types.Calendar, None, None]:
        return self.get_all_of_type(type_name="calendar", refresh=refresh)

    def all_characters(self, refresh: bool = False) -> Generator[pykanka.child_types.Character, None, None]:
        return self.get_all_of_type(type_name="character", refresh=refresh)

    def all_events(self, refresh: bool = False) -> Generator[pykanka.child_types.Event, None, None]:
        return self.get_all_of_type(type_name="event", refresh=refresh)

    def all_families(self, refresh: bool = False) -> Generator[pykanka.child_types.Family, None, None]:
        return self.get_all_of_type(type_name="family", refresh=refresh)

    def all_items(self, refresh: bool = False) -> Generator[pykanka.child_types.Item, None, None]:
        return self.get_all_of_type(type_name="item", refresh=refresh)

    def all_journals(self, refresh: bool = False) -> Generator[pykanka.child_types.Journal, None, None]:
        return self.get_all_of_type(type_name="journal", refresh=refresh)

    def all_locations(self, refresh: bool = False) -> Generator[pykanka.child_types.Location, None, None]:
        return self.get_all_of_type(type_name="location", refresh=refresh)

    def all_maps(self, refresh: bool = False) -> Generator[pykanka.child_types.Map, None, None]:
        return self.get_all_of_type(type_name="map", refresh=refresh)

    def all_notes(self, refresh: bool = False) -> Generator[pykanka.child_types.Note, None, None]:
        return self.get_all_of_type(type_name="note", refresh=refresh)

    def all_organisations(self, refresh: bool = False) -> Generator[pykanka.child_types.Organisation, None, None]:
        return self.get_all_of_type(type_name="organisation", refresh=refresh)

    def all_quests(self, refresh: bool = False) -> Generator[pykanka.child_types.Quest, None, None]:
        return self.get_all_of_type(type_name="quest", refresh=refresh)

    def all_races(self, refresh: bool = False) -> Generator[pykanka.child_types.Race, None, None]:
        return self.get_all_of_type(type_name="race", refresh=refresh)

    def all_tags(self, refresh: bool = False) -> Generator[pykanka.child_types.Tag, None, None]:
        return self.get_all_of_type(type_name="tag", refresh=refresh)

    def all_timelines(self, refresh: bool = False) -> Generator[pykanka.child_types.Timeline, None, None]:
        return self.get_all_of_type(type_name="timeline", refresh=refresh)
