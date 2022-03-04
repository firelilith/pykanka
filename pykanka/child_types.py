import typing
import json
from typing import List, Optional

import requests

import pykanka
import pykanka.child_subentries as st
from pykanka.exceptions import *
from dataclasses import dataclass, InitVar
from pykanka.childdata_types import *


@dataclass
class GenericChildType:
    client: Optional["pykanka.KankaClient"]
    _parent: Optional["pykanka.entities.Entity"] = None
    base_url: Optional[str] = str()
    endpoint: Optional[str] = str()  # Overidden by inheritors
    data: Optional[GenericChildData] = GenericChildData() # Overidden by inheritors

    """Generic class for child types. 
    Shouldn't be used directly, it is used as a base class for specialized child types."""
    _possible_keys = list()  # Overridden by inheritors
    _key_replacer = list()  # Overridden by inheritors
    _file_keys = list()  # Overridden by inheritors

    def __post_init__(self):
        self.base_url = f"{self.client.campaign_base_url}{self.endpoint}/"

    @property
    def parent(self):
        """Lazily gets the Entity object belonging to this instance"""
        if self._parent:
            return self._parent
        elif self.data.entity_id:
            self._parent = pykanka.entities.Entity.from_id(self.client, self.data.entity_id, child=self)
            return self._parent
        else:
            self._parent = pykanka.entities.Entity(self.client, child=self)
            return self._parent

    @parent.setter
    def parent(self, v: "pykanka.entities.Entity"):
        self._parent = v

    @classmethod
    def from_id(cls, client: "pykanka.KankaClient", child_id: int, parent: "pykanka.entities.Entity" = None,
                refresh=False) -> "GenericChildType":
        obj = cls(client=client, _parent=parent)

        response = client.request_get(f"{obj.base_url}{child_id}", refresh=refresh)

        if not response.ok:
            raise ResponseNotOkError(
                f"Response from {obj.base_url}{child_id} not OK, code {response.status_code}: {response.reason}")

        obj.data = obj.data.__class__(**response.json()["data"])

        return obj

    @classmethod
    def from_json(cls, client: "pykanka.KankaClient", content: typing.Union[str, dict],
                  parent: "pykanka.entities.Entity" = None) -> "GenericChildType":

        if type(content) == str:
            content = json.loads(content)

        obj = cls(client, _parent=parent)

        obj.data = obj.data.__class__(**content)

        return obj

    def post(self, json_data: str = None, **kwargs):
        """
        Posts Location to Campaign. Possible parameters are outlined in the documentation, here:
        https://kanka.io/en/docs/1.0/
        Parameters are taken from existing object, a json string or keywords.
        Here, keywords override json override existing.

        Currently, the kanka API does not support the parameters 'image' and 'map'.

        :param json_data: str
        :param name: str
        :return: requests.response
        """

        payload, files = self._prepare_post(json_data, **kwargs)

        return self.client.request_post(f"{self.base_url}", json=payload)

    def patch(self, json_data: str = None, **kwargs):
        """
        Updates Location to Campaign. Possible parameters are outlined in the documentation, here:
        https://kanka.io/en/docs/1.0/
        Parameters are taken from existing object, a json string or keywords.
        Here, keywords override json override existing.

        Currently, the kanka API does not support the parameters 'image' and 'map'.

        :param json_data: str
        :param name: str
        :return: requests.response
        """

        payload, files = self._prepare_post(json_data, **kwargs)

        return self.client.request_patch(f"{self.base_url}{self.data.id}", json=payload)

    def delete(self):
        return self.client.request_delete(f"{self.base_url}{self.data.id}")

    def _prepare_post(self, json_data: str,
                      **kwargs):  # implement support for image files (keys: image and map) when the API allows it
        if json_data:
            values = json.loads(json_data)
            values.update(kwargs)
        else:
            values = kwargs

        # The API doesn't support file uploads as of now, placeholder to when it will become relevant.
        files = dict()

        for key in self._file_keys:
            if key in values.keys():
                files[key] = open(values[key], "rb")
                values.pop(key)
                print(f"API doesn't support direct file uploads yet, parameter {key} omitted. use url instead")

        existing_values = self._get_post_values()
        existing_values.update(values)

        self._validate_parameters(existing_values, files)

        return existing_values, files

    @staticmethod
    def _validate_parameters(values, files):
        if "name" not in values.keys():
            raise ValueError("'name' is a required field, but is missing")

    def _get_post_values(self):
        values = dict()

        for key in self._possible_keys:
            if self.data.__dict__[key] is not None:
                values[key] = self.data.__dict__[key]

        for key, replacement in self._key_replacer:
            if key in values.keys():
                values[replacement] = values[key]
                values.pop(key)

        return values

    def get_image(self) -> "requests.Response.raw":
        """Returns file-like object of the child's image"""
        return self.client.request_get(self.data.image_full, stream=True).raw


@dataclass
class Location(GenericChildType):
    """A class representing a location child contained within an Entity."""

    # keys accepted by POST and also delivered by GET as per API documentation
    _possible_keys = ["name", "entry", "type", "parent_location_id", "tags", "is_private", "image_full", "map",
                      "is_map_private", "header_full", "has_custom_header"]
    # keys called differently in GET compared to POST as per API documentation, format: (get_version, post_version)
    _key_replacer = [("image_full", "image_url"), ("map", "map_url")]
    # fields that accept stream object, not yet supported in API 1.0
    _file_keys = ["image", "map"]

    child_id: Optional[int] = None
    data: LocationData = LocationData()
    endpoint: str = "locations"


    def get_map_image(self) -> "requests.Response.raw":
        """Returns file-like object of the entity's map image"""
        return self.client.request_get(self.data.map, stream=True).raw


@dataclass
class Character(GenericChildType):
    """A class representing a Character child contained within an Entity."""
    # keys accepted by POST and also delivered by GET as per API documentation
    _possible_keys = ["name", "entry", "title", "age", "sex", "pronouns", "type", "family_id", "location_id", "race_id",
                      "tags", "is_dead", "is_private", "image_full", "is_personality_visible", "header_full",
                      "has_custom_header"]
    # keys called differently in GET compared to POST as per API documentation, format: (get_version, post_version)
    _key_replacer = [("image_full", "image_url")]
    # fields that accept stream object, not yet supported in API 1.0
    _file_keys = ["image"]

    data: CharacterData = CharacterData()
    endpoint: str = "characters"


@dataclass
class Organisation(GenericChildType):
    """A class representing a Organisation child contained within an Entity."""

    # keys accepted by POST and also delivered by GET as per API documentation
    _possible_keys = ["name", "entry", "type", "organisation_id", "location_id", "tags", "is_private", "image_full",
                      "header_full",
                      "has_custom_header"]
    # keys called differently in GET compared to POST as per API documentation, format: (get_version, post_version)
    _key_replacer = [("image_full", "image_url")]
    # fields that accept stream object, not yet supported in API 1.0
    _file_keys = ["image"]

    data: OrganisationData = OrganisationData()
    endpoint: str = "organisations"


@dataclass
class Timeline(GenericChildType):
    """A class representing a Timeline child contained within an Entity."""

    # keys accepted by POST and also delivered by GET as per API documentation
    _possible_keys = ["name", "entry", "type", "revert_order", "tags", "is_private", "image_full", "header_full",
                      "has_custom_header"]
    # keys called differently in GET compared to POST as per API documentation, format: (get_version, post_version)
    _key_replacer = [("image_full", "image_url")]
    # fields that accept stream object, not yet supported in API 1.0
    _file_keys = ["image"]

    data: TimelineData = TimelineData()
    endpoint: str = "timelines"


@dataclass
class Race(GenericChildType):
    """A class representing a Race child contained within an Entity."""

    # keys accepted by POST and also delivered by GET as per API documentation
    _possible_keys = ["name", "entry", "type", "race_id", "tags", "is_private", "image_full", "header_full",
                      "has_custom_header"]
    # keys called differently in GET compared to POST as per API documentation, format: (get_version, post_version)
    _key_replacer = [("image_full", "image_url")]
    # fields that accept stream object, not yet supported in API 1.0
    _file_keys = ["image"]

    data: RaceData = RaceData()
    endpoint: str = "races"


@dataclass
class Family(GenericChildType):
    """A class representing a Family child contained within an Entity."""

    # keys accepted by POST and also delivered by GET as per API documentation
    _possible_keys = ["name", "entry", "type", "location_id", "family_id", "tags", "is_private", "image_full",
                      "header_full",
                      "has_custom_header"]
    # keys called differently in GET compared to POST as per API documentation, format: (get_version, post_version)
    _key_replacer = [("image_full", "image_url")]
    # fields that accept stream object, not yet supported in API 1.0
    _file_keys = ["image"]

    data: FamilyData = FamilyData()
    endpoint: str = "families"


@dataclass
class Note(GenericChildType):
    """A class representing a Note child contained within an Entity."""

    # keys accepted by POST and also delivered by GET as per API documentation
    _possible_keys = ["name", "entry", "type", "note_id", "tags", "is_private", "image_full", "header_full",
                      "has_custom_header"]
    # keys called differently in GET compared to POST as per API documentation, format: (get_version, post_version)
    _key_replacer = [("image_full", "image_url")]
    # fields that accept stream object, not yet supported in API 1.0
    _file_keys = ["image"]

    data: NoteData = NoteData()
    endpoint: str = "notes"


@dataclass
class Map(GenericChildType):
    """A class representing a Map child contained within an Entity."""

    # keys accepted by POST and also delivered by GET as per API documentation
    _possible_keys = ["name", "entry", "type", "map_id", "location_id", "center_marker_id", "center_x", "center_y",
                      "tags", "is_private", "image_full", "header_full",
                      "has_custom_header"]
    # keys called differently in GET compared to POST as per API documentation, format: (get_version, post_version)
    _key_replacer = [("image_full", "image_url")]
    # fields that accept stream object, not yet supported in API 1.0
    _file_keys = ["image"]

    data: MapData = MapData()
    endpoint: str = "maps"

    def all_markers(self) -> List["st.MapMarker"]:
        """Returns a list of all existing map markers"""
        markers = []
        url = f"{self.base_url}{self.data.id}/map_markers"
        done = False

        while not done:
            response = self.client.request_get(url).json()
            for entry in response["data"]:
                markers.append(st.MapMarker(self, values=entry))
                if response["links"]["next"]:
                    url = response["links"]["next"]
                else:
                    done = True

        return markers

    def get_marker(self, marker_id: int = None) -> "st.MapMarker":
        """
        Returns either the map marker with the specified ID, or, if none is given, an empty map marker.

        :param marker_id: Map marker id.
        :return: MapMarker object
        """
        if marker_id:
            response = self.client.request_get(f"{self.base_url}{self.data.id}/map_markers/{marker_id}")
            if not response.ok:
                raise ResponseNotOkError(f"Response not OK, code {response.status_code}: {response.text}")
            marker = st.MapMarker(parent_map=self, values=response.json()["data"])
        else:
            marker = st.MapMarker(parent_map=self)
        return marker

    @staticmethod
    def _validate_parameters(values: set, files: set):
        if "name" not in values:
            raise ValueError("'name' is a required field, but is missing")
        if "image" not in files and "image_url" not in values:
            raise ValueError("either 'image' or 'image_url' is required, but both are missing")


@dataclass
class Tag(GenericChildType):
    """A class representing a Tag child contained within an Entity."""

    # keys accepted by POST and also delivered by GET as per API documentation
    _possible_keys = ["name", "entry", "type", "colour", "tag_id", "is_private", "image_full", "header_full",
                      "has_custom_header"]
    # keys called differently in GET compared to POST as per API documentation, format: (get_version, post_version)
    _key_replacer = [("image_full", "image_url")]
    # fields that accept stream object, not yet supported in API 1.0
    _file_keys = ["image"]

    data: TagData = TagData()
    endpoint: str = "tags"


@dataclass
class Quest(GenericChildType):
    """A class representing a Quest child contained within an Entity."""

    # keys accepted by POST and also delivered by GET as per API documentation
    _possible_keys = ["name", "entry", "type", "quest_id", "character_id", "tags", "is_private", "image_full" , "header_full",
                      "has_custom_header", "date"]
    # keys called differently in GET compared to POST as per API documentation, format: (get_version, post_version)
    _key_replacer = [("image_full", "image_url")]
    # fields that accept stream object, not yet supported in API 1.0
    _file_keys = ["image"]

    data: QuestData = QuestData()
    endpoint: str = "quests"


@dataclass
class Journal(GenericChildType):
    """A class representing a Journal child contained within an Entity."""

    # keys accepted by POST and also delivered by GET as per API documentation
    _possible_keys = ["name", "entry", "type", "date", "character_id", "tags", "is_private", "image_full",
                      "header_full"]
    # keys called differently in GET compared to POST as per API documentation, format: (get_version, post_version)
    _key_replacer = [("image_full", "image_url")]
    # fields that accept stream object, not yet supported in API 1.0
    _file_keys = ["image"]

    data: JournalData = JournalData()
    endpoint: str = "journals"


@dataclass
class Item(GenericChildType):
    """A class representing a Item child contained within an Entity."""

    # keys accepted by POST and also delivered by GET as per API documentation
    _possible_keys = ["name", "entry", "type", "location_id", "character_id", "price", "size", "tags", "is_private",
                      "image_full", "header_full",
                      "has_custom_header"]
    # keys called differently in GET compared to POST as per API documentation, format: (get_version, post_version)
    _key_replacer = [("image_full", "image_url")]
    # fields that accept stream object, not yet supported in API 1.0
    _file_keys = ["image"]

    data: ItemData = ItemData()
    endpoint: str = "items"


@dataclass
class Event(GenericChildType):
    """A class representing a Event child contained within an Entity."""

    # keys accepted by POST and also delivered by GET as per API documentation
    _possible_keys = ["name", "entry", "type", "date", "location_id", "tags", "is_private", "image_full", "header_full",
                      "has_custom_header"]
    # keys called differently in GET compared to POST as per API documentation, format: (get_version, post_version)
    _key_replacer = [("image_full", "image_url")]
    # fields that accept stream object, not yet supported in API 1.0
    _file_keys = ["image"]

    data: EventData = EventData()
    endpoint: str = "events"


@dataclass
class Ability(GenericChildType):
    """A class representing a Ability child contained within an Entity."""

    # keys accepted by POST and also delivered by GET as per API documentation
    _possible_keys = ["name", "entry", "type", "ability_id", "charges", "tags", "is_private", "image_full",
                      "header_full",
                      "has_custom_header"]
    # keys called differently in GET compared to POST as per API documentation, format: (get_version, post_version)
    _key_replacer = [("image_full", "image_url")]
    # fields that accept stream object, not yet supported in API 1.0
    _file_keys = ["image"]

    data: AbilityData = AbilityData()
    endpoint: str = "abilities"


@dataclass
class Calendar(GenericChildType):
    """A class representing a Calendar child contained within an Entity"""

    # keys accepted by POST and also delivered by GET as per API documentation
    _possible_keys = ["name", "entry", "type", "current_year", "current_month", "current_day", "tags", "month_name",
                      "month_length", "month_type", "weekday", "year_name", "year_number",
                      "moon_name", "moon_fullmoon", "epoch_name", "season_name", "season_month", "season_day",
                      "has_leap_year", "leap_year_amount", "leap_year_offset", "leap_year_start",
                      "tags", "is_private", "image_full", "header_full",
                      "has_custom_header"]
    # keys called differently in GET compared to POST as per API documentation, format: (get_version, post_version)
    _key_replacer = [("image_full", "image_url")]
    # fields that accept stream object, not yet supported in API 1.0
    _file_keys = ["image"]

    data: CalendarData = CalendarData()
    endpoint: str = "calendars"

    @staticmethod
    def _validate_parameters(values, files):
        if "name" not in values.keys():
            raise ValueError("'name' is a required field, but is missing")
        if "month_name" not in values.keys():
            raise ValueError("'month_name' is a required field, but is missing")
        if "month_length" not in values.keys():
            raise ValueError("'month_length' is a required field, but is missing")
        if "weekday" not in values.keys():
            raise ValueError("'weekday' is a required field, but is missing")
        if len(values["month_day"]) < 2:
            raise ValueError("'month_name' needs at least two entries, but has fewer")
        if len(values["month_length"]) < 2:
            raise ValueError("'month_length' needs at least two entries, but has fewer")
        if len(values["weekday"]) < 2:
            raise ValueError("'weekday' needs at least two entries, but has fewer")


child_type_dictionary = dict(location=Location,
                             character=Character,
                             family=Family,
                             organisation=Organisation,
                             timeline=Timeline,
                             race=Race,
                             note=Note,
                             map=Map,
                             tag=Tag,
                             quest=Quest,
                             journal=Journal,
                             item=Item,
                             event=Event,
                             ability=Ability,
                             calendar=Calendar
                             )
