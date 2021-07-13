import requests
import typing
import tenacity

import pykanka.entities as ent
import pykanka.child_types as ct

from pykanka.exceptions import *


class KankaClient:
    """Main client for interacting with the Kanka.io API"""

    def __init__(self, token: str, campaign: typing.Union[str, int]):
        """Create a client associated with a specific campaign.

        :param token: User API token from kanka.io
        :param campaign: Campaign name or ID
        """

        self._api_token = token
        self._headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        self._api_base_url = "https://kanka.io/api/1.0/campaigns/"

        if type(campaign) == int:
            self.campaign_id = campaign
        elif type(campaign) == str:
            self.campaign_id = self._get_campaign_id(campaign)
        else:
            raise ValueError("Campaign not valid, provide either a valid name or id")

        self.campaign_base_url = f"{self._api_base_url}{self.campaign_id}/"

    #  Utility functions to locate campaign from its name

    def _get_campaigns(self):
        campaigns = requests.get("https://kanka.io/api/1.0/campaigns/", headers=self._headers)

        if not campaigns.ok:
            raise ResponseNotOkError(f"Response not OK, code {campaigns.status_code}:\n{campaigns.text}")

        return campaigns.json()

    def _get_campaign_id(self, name: str):
        campaigns = self._get_campaigns()

        for campaign in campaigns["data"]:
            if campaign["name"].lower() == name.lower():
                campaign_id = campaign["id"]
                return campaign_id

        raise CampaignError(f"No campaign of the name '{name}' found")

    @tenacity.retry(retry=tenacity.retry_if_exception_type(ApiThrottlingError), wait=tenacity.wait_fixed(5))
    def _request(self, method, url, **kwargs):
        response = requests.request(method=method, url=url, headers=self._headers, **kwargs)

        if response.status_code == 429:
            print("API request limit reached. Retrying in 5 seconds.")
            raise ApiThrottlingError()

        return response

    def request_get(self, url: str, **kwargs):
        """get request with proper headers. usually shouldn't be accessed directly."""
        return self._request("get", url, **kwargs)

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

    def get_entity(self, entity_id: int = None) -> "ent.Entity":
        """Returns specified entity or empty entity if no ID given"""
        if entity_id:
            return ent.Entity.from_id(self, entity_id)
        else:
            return ent.Entity(self)

    def get_location(self, location_id: int = None) -> "ct.Location":
        """returns specified location or empty location if no ID given"""
        if location_id:
            return ct.Location.from_id(self, location_id)
        else:
            return ct.Location(self)

    def get_organisation(self, organisation_id: int = None) -> "ct.Organisation":
        """returns specified organisation or empty organisation if no ID given"""
        if organisation_id:
            return ct.Organisation.from_id(self, organisation_id)
        else:
            return ct.Organisation(self)

    def get_timeline(self, timeline_id: int = None) -> "ct.Timeline":
        """returns specified timeline or empty timeline if no ID given"""
        if timeline_id:
            return ct.Timeline.from_id(self, timeline_id)
        else:
            return ct.Timeline(self)

    def get_race(self, race_id: int = None) -> "ct.Race":
        """returns specified race or empty race if no ID given"""
        if race_id:
            return ct.Race.from_id(self, race_id)
        else:
            return ct.Race(self)

    def get_family(self, family_id: int = None) -> "ct.Family":
        """returns specified family or empty family if no ID given"""
        if family_id:
            return ct.Family.from_id(self, family_id)
        else:
            return ct.Family(self)

    def get_note(self, note_id: int = None) -> "ct.Note":
        """returns specified note or empty note if no ID given"""
        if note_id:
            return ct.Note.from_id(self, note_id)
        else:
            return ct.Note(self)

    def get_character(self, character_id: int = None) -> "ct.Character":
        """returns specified character or empty character if no ID given"""
        if character_id:
            return ct.Character.from_id(self, character_id)
        else:
            return ct.Character(self)

    def get_map(self, map_id: int = None) -> "ct.Map":
        """returns specified map or empty map if no ID given"""
        if map_id:
            return ct.Map.from_id(self, map_id)
        else:
            return ct.Map(self)

    def get_tag(self, tag_id: int = None) -> "ct.Tag":
        """returns specified tag or empty tag if no ID given"""
        if tag_id:
            return ct.Tag.from_id(self, tag_id)
        else:
            return ct.Tag(self)

    def get_quest(self, quest_id: int = None) -> "ct.Quest":
        """returns specified quest or empty quest if no ID given"""
        if quest_id:
            return ct.Quest.from_id(self, quest_id)
        else:
            return ct.Quest(self)

    def get_journal(self, journal_id: int = None) -> "ct.Journal":
        """returns specified journal or empty journal if no ID given"""
        if journal_id:
            return ct.Journal.from_id(self, journal_id)
        else:
            return ct.Journal(self)

    def get_item(self, item_id: int = None) -> "ct.Item":
        """returns specified item or empty item if no ID given"""
        if item_id:
            return ct.Item.from_id(self, item_id)
        else:
            return ct.Item(self)

    def get_event(self, event_id: int = None) -> "ct.Event":
        """returns specified event or empty event if no ID given"""
        if event_id:
            return ct.Event.from_id(self, event_id)
        else:
            return ct.Event(self)

    def get_ability(self, ability_id: int = None) -> "ct.Ability":
        """returns specified ability or empty ability if no ID given"""
        if ability_id:
            return ct.Ability.from_id(self, ability_id)
        else:
            return ct.Ability(self)

    def get_calendar(self, calendar_id: int = None) -> "ct.Calendar":
        """returns specified calendar or empty calendar if no ID given"""
        if calendar_id:
            return ct.Calendar.from_id(self, calendar_id)
        else:
            return ct.Calendar(self)

    def _get_all_of_type(self, url, type_class) -> typing.Generator[typing.Any, None, None]:
        done = False

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
                entity = type_class.from_json(self, entry)
                yield entity
        return

    def all_entities(self) -> typing.Generator["ent.Entity", None, None]:
        return self._get_all_of_type(f"{self.campaign_base_url}entities", ent.Entity)

    def all_locations(self) -> typing.Generator["ct.Location", None, None]:
        return self._get_all_of_type(f"{self.campaign_base_url}locations", ct.Location)

    def all_organisations(self) -> typing.Generator["ct.Organisation", None, None]:
        return self._get_all_of_type(f"{self.campaign_base_url}organisations", ct.Organisation)

    def all_timelines(self) -> typing.Generator["ct.Timeline", None, None]:
        return self._get_all_of_type(f"{self.campaign_base_url}timelines", ct.Timeline)

    def all_races(self) -> typing.Generator["ct.Race", None, None]:
        return self._get_all_of_type(f"{self.campaign_base_url}races", ct.Race)

    def all_families(self) -> typing.Generator["ct.Family", None, None]:
        return self._get_all_of_type(f"{self.campaign_base_url}families", ct.Family)

    def all_notes(self) -> typing.Generator["ct.Note", None, None]:
        return self._get_all_of_type(f"{self.campaign_base_url}notes", ct.Note)

    def all_characters(self) -> typing.Generator["ct.Character", None, None]:
        return self._get_all_of_type(f"{self.campaign_base_url}characters", ct.Character)

    def all_maps(self) -> typing.Generator["ct.Map", None, None]:
        return self._get_all_of_type(f"{self.campaign_base_url}maps", ct.Map)

    def all_tags(self) -> typing.Generator["ct.Tag", None, None]:
        return self._get_all_of_type(f"{self.campaign_base_url}tags", ct.Tag)

    def all_quests(self) -> typing.Generator["ct.Quest", None, None]:
        return self._get_all_of_type(f"{self.campaign_base_url}quests", ct.Quest)

    def all_journals(self) -> typing.Generator["ct.Journal", None, None]:
        return self._get_all_of_type(f"{self.campaign_base_url}journals", ct.Journal)

    def all_items(self) -> typing.Generator["ct.Item", None, None]:
        return self._get_all_of_type(f"{self.campaign_base_url}items", ct.Item)

    def all_events(self) -> typing.Generator["ct.Event", None, None]:
        return self._get_all_of_type(f"{self.campaign_base_url}events", ct.Event)

    def all_abilities(self) -> typing.Generator["ct.Ability", None, None]:
        return self._get_all_of_type(f"{self.campaign_base_url}abilities", ct.Ability)

    def all_calendars(self) -> typing.Generator["ct.Calendar", None, None]:
        return self._get_all_of_type(f"{self.campaign_base_url}calenders", ct.Calendar)

    def search(self, name: str, results: int = 1) -> list["ent.Entity"]:
        """
        Search for entities with a given name.

        :param name: Name to be searched
        :param results: Maximum number of results to be fetched. Each result requires its own API call, so be careful!
        :return: List of Entities that match the name given.
        """
        response = self.request_get(f"{self.campaign_base_url}search/{name}").json()["data"]

        res = []
        for entry, _ in zip(response, range(results)):
            res.append(self.get_entity(entry["entity_id"]))

        return res
