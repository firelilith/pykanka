import requests
import typing
import tenacity

import pykanka.entities as ent
from pykanka.exceptions import *


class KankaClient:
    """Main client for interacting with the Kanka.io API"""

    def __init__(self, token: str, campaign: typing.Union[str, int], **kwargs):
        """Create a client associated with a specific campaign.

        :param token: str
        :param campaign: Union[str, int]
        :param cache: bool
        :param cache_name: str
        :param cache_duration: int
        :param kwargs:
        """

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
    def _request(self, method, url, **kwargs):
        response = requests.request(method=method, url=url, headers=self.headers, **kwargs)

        if response.status_code == 429:
            print("API request limit reached. Retrying in 5 seconds.")
            raise ApiThrottlingError()

        return response

    def request_get(self, url, **kwargs):
        """get request with proper headers. usually shouldn't be accessed directly."""
        return self._request("get", url, **kwargs)

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

    def get_entity(self, entity_id: int = None) -> "ent.Entity":
        """returns specified entity or empty entity if no ID given"""
        if entity_id:
            return ent.Entity.from_id(self, entity_id)
        else:
            return ent.Entity(self)

    def get_location(self, location_id: int = None) -> "ent.Location":
        """returns specified location or empty location if no ID given"""
        if location_id:
            return ent.Location.from_id(self, location_id)
        else:
            return ent.Location(self)

    def get_organisation(self, organisation_id: int = None) -> "ent.Organisation":
        """returns specified organisation or empty organisation if no ID given"""
        if organisation_id:
            return ent.Organisation.from_id(self, organisation_id)
        else:
            return ent.Organisation(self)

    def get_timeline(self, timeline_id: int = None) -> "ent.Timeline":
        """returns specified timeline or empty timeline if no ID given"""
        if timeline_id:
            return ent.Timeline.from_id(self, timeline_id)
        else:
            return ent.Timeline(self)

    def get_race(self, race_id: int = None) -> "ent.Race":
        """returns specified race or empty race if no ID given"""
        if race_id:
            return ent.Race.from_id(self, race_id)
        else:
            return ent.Race(self)

    def get_family(self, family_id: int = None) -> "ent.Family":
        """returns specified family or empty family if no ID given"""
        if family_id:
            return ent.Family.from_id(self, family_id)
        else:
            return ent.Family(self)

    def get_note(self, note_id: int = None) -> "ent.Note":
        """returns specified note or empty note if no ID given"""
        if note_id:
            return ent.Note.from_id(self, note_id)
        else:
            return ent.Note(self)

    def get_character(self, character_id: int = None) -> "ent.Character":
        """returns specified character or empty character if no ID given"""
        if character_id:
            return ent.Character.from_id(self, character_id)
        else:
            return ent.Character(self)

    def get_map(self, map_id: int = None) -> "ent.Map":
        """returns specified map or empty map if no ID given"""
        if map_id:
            return ent.Map.from_id(self, map_id)
        else:
            return ent.Map(self)

    def get_tag(self, tag_id: int = None) -> "ent.Tag":
        """returns specified tag or empty tag if no ID given"""
        if tag_id:
            return ent.Tag.from_id(self, tag_id)
        else:
            return ent.Tag(self)

    def get_quest(self, quest_id: int = None) -> "ent.Quest":
        """returns specified quest or empty quest if no ID given"""
        if quest_id:
            return ent.Quest.from_id(self, quest_id)
        else:
            return ent.Quest(self)

    def get_journal(self, journal_id: int = None) -> "ent.Journal":
        """returns specified journal or empty journal if no ID given"""
        if journal_id:
            return ent.Journal.from_id(self, journal_id)
        else:
            return ent.Journal(self)

    def get_item(self, item_id: int = None) -> "ent.Item":
        """returns specified item or empty item if no ID given"""
        if item_id:
            return ent.Item.from_id(self, item_id)
        else:
            return ent.Item(self)

    def get_event(self, event_id: int = None) -> "ent.Event":
        """returns specified event or empty event if no ID given"""
        if event_id:
            return ent.Event.from_id(self, event_id)
        else:
            return ent.Event(self)

    def get_ability(self, ability_id: int = None) -> "ent.Ability":
        """returns specified ability or empty ability if no ID given"""
        if ability_id:
            return ent.Ability.from_id(self, ability_id)
        else:
            return ent.Ability(self)

    def getall_entities(self) -> typing.Dict[typing.Tuple[str, int], "ent.Entity"]:

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
                entity = ent.Entity.from_json(self, entry)
                members[(entity.data.name, entity.data.id)] = entity

        return members

    def getall_locations(self) -> typing.Dict[typing.Tuple[str, int], "ent.Location"]:

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
                location = ent.Location.from_json(self, entry)
                members[(location.data.name, location.data.id)] = location

        return members


