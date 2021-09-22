import typing
import json
from typing import List, Optional

import requests

import pykanka
import pykanka.child_subentries as st
from pykanka.exceptions import *
from dataclasses import dataclass


@dataclass
class GenericChildType:
    client: Optional["pykanka.KankaClient"]
    _parent: Optional["pykanka.entities.Entity"] = None
    base_url: Optional[str] = str()  # Overridden by inheritors

    """Generic class for child types. 
    Shouldn't be used directly, it is used as a base class for specialized child types."""
    _possible_keys = list()  # Overridden by inheritors
    _key_replacer = list()  # Overridden by inheritors
    _file_keys = list()  # Overridden by inheritors

    @dataclass
    class GenericChildData:
        name: str = None
        id:         Optional[int] = None
        type:       Optional[str] = None
        entity_id:  Optional[int] = None

        entry:          Optional[str] = None
        entry_parsed:   Optional[str] = None

        image:          Optional[str] = None
        image_full:     Optional[str] = None
        image_thumb:    Optional[str] = None

        tags:           Optional[List[int]] = None

        focus_x:        Optional[float] = None
        focus_y:        Optional[float] = None

        has_custom_image:   Optional[str] = None
        is_template:        Optional[bool] = None
        is_private:         Optional[bool] = None

        # Should be datetimes, but will require some type conversions, likely
        created_by:     Optional[str] = None
        created_at:         Optional[str] = None
        updated_by:         Optional[str] = None
        updated_at:         Optional[str] = None

        header_full:        Optional[str] = None
        has_custom_header:  Optional[bool] = None

    def __post_init__(self):
        self.data = self.GenericChildData()

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

        payload, files = self.client._prepare_post(json_data, **kwargs)

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


@dataclass()
class Location(GenericChildType):
    """A class representing a location child contained within an Entity."""

    # keys accepted by POST and also delivered by GET as per API documentation
    _possible_keys = ["name", "type", "parent_location_id", "tags", "is_private", "image_full", "map", "is_map_private",
                      "header_full",
                      "has_custom_header"]
    # keys called differently in GET compared to POST as per API documentation, format: (get_version, post_version)
    _key_replacer = [("image_full", "image_url"), ("map", "map_url")]
    # fields that accept stream object, not yet supported in API 1.0
    _file_keys = ["image", "map"]

    child_id: Optional[int] = None

    @dataclass
    class LocationData(GenericChildType.GenericChildData):
        parent_location_id: Optional[int] = None
        is_map_private: Optional[bool] = None
        map: Optional[str] = None

    def __post_init__(self):
        """
        Creates an empty Location. Consider using Location.from_id() or Location.from_json() instead.
        """
        self.data = self.LocationData()
        self.base_url = f"{self.client.campaign_base_url}locations/"

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

    @dataclass
    class CharacterData(GenericChildType.GenericChildData):
        location_id: Optional[int] = None
        family_id: Optional[int] = None
        race_id: Optional[int] = None
        age: Optional[int] = None
        sex: Optional[str] = None
        pronouns: Optional[str] = None
        title: Optional[str] = None
        traits: Optional[List[int]] = None
        is_dead: Optional[bool] = None
        is_personality_visible: Optional[bool] = None

    def __post_init__(self):
        """
        Creates an empty Character. Consider using Character.from_id() or Character.from_json() instead.
        """

        self.data = self.CharacterData()
        self.base_url = f"{self.client.campaign_base_url}characters/"


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

    @dataclass
    class OrganisationData(GenericChildType.GenericChildData):
        organisation_id: Optional[int] = None
        location_id: Optional[int] = None
        members: Optional[List[int]] = None

    def __post_init__(self):
        """
        Creates an empty Organisation. Consider using Organisation.from_id() or Organisation.from_json() instead.
        """
        self.data = self.OrganisationData()
        self.base_url = f"{self.client.campaign_base_url}organisations/"


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

    @dataclass
    class TimelineData(GenericChildType.GenericChildData):
        eras: Optional[str] = None
        timeline_id: Optional[int] = None
        revert_order: Optional[bool] = None

    def __post_init__(self):
        """
        Creates an empty Timeline. Consider using Timeline.from_id() or Timeline.from_json() instead.
        """
        self.data = self.TimelineData()
        self.base_url = f"{self.client.campaign_base_url}timelines/"


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

    @dataclass
    class RaceData(GenericChildType.GenericChildData):
        race_id: Optional[int] = None

    def __post_init__(self):
        """
        Creates an empty Race. Consider using Race.from_id() or Race.from_json() instead.
        """
        self.data = self.RaceData()
        self.base_url = f"{self.client.campaign_base_url}races/"


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

    @dataclass
    class FamilyData(GenericChildType.GenericChildData):
        members: Optional[List[int]] = None
        location_id: Optional[int] = None
        family_id: Optional[int] = None

    def __post_init__(self):
        """
        Creates an empty Family. Consider using Location.from_id() or Family.from_json() instead.
        """
        self.data = self.FamilyData()
        self.base_url = f"{self.client.campaign_base_url}families/"


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

    @dataclass()
    class NoteData(GenericChildType.GenericChildData):
        is_pinned: Optional[bool] = None
        note_id: Optional[int] = None

    def __post_init__(self):
        """
        Creates an empty Note. Consider using Note.from_id() or Note.from_json() instead.
        """
        self.data = self.NoteData()
        self.base_url = f"{self.client.campaign_base_url}notes/"


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

    @dataclass
    class MapData(GenericChildType.GenericChildData):
        location_id: Optional[int] = None
        map_id: Optional[int] = None
        width: Optional[float] = None
        height: Optional[float] = None
        initial_zoom: Optional[float] = None
        center_x: Optional[float] = None
        center_y: Optional[float] = None
        max_zoom: Optional[float] = None
        min_zoom: Optional[float] = None
        layers: Optional[str] = None
        groups: Optional[str] = None
        grid: Optional[str] = None
        center_marker_id: Optional[id] = None

    def __post_init__(self):
        """
        Creates an empty Map. Consider using Map.from_id() or Map.from_json() instead.
        """
        self.data = self.MapData()
        self.base_url = f"{self.client.campaign_base_url}maps/"

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

    @dataclass
    class TagData(GenericChildType.GenericChildData):
        entities: Optional[List[int]] = None
        tag_id: Optional[int] = None
        colour: Optional[str] = None

    def __post_init__(self):
        """
        Creates an empty Tag. Consider using Tag.from_id() or Tag.from_json() instead.
        """
        self.data = self.TagData()
        self.base_url = f"{self.client.campaign_base_url}tags/"


@dataclass
class Quest(GenericChildType):
    """A class representing a Quest child contained within an Entity."""

    # keys accepted by POST and also delivered by GET as per API documentation
    _possible_keys = ["name", "entry", "type", "quest_id", "character_id", "tags", "is_private", "image_full",
                      "header_full",
                      "has_custom_header"]
    # keys called differently in GET compared to POST as per API documentation, format: (get_version, post_version)
    _key_replacer = [("image_full", "image_url")]
    # fields that accept stream object, not yet supported in API 1.0
    _file_keys = ["image"]

    @dataclass
    class QuestData(GenericChildType.GenericChildData):
        quest_id: Optional[str] = None
        character_id: Optional[str] = None
        calendar_id: Optional[str] = None
        calendar_year: Optional[str] = None
        calendar_month: Optional[str] = None
        calendar_day: Optional[str] = None
        date: Optional[str] = None
        elements_count: Optional[str] = None
        elements: Optional[str] = None
        is_completed: Optional[str] = None

    def __post_init__(self):
        """
        Creates an empty Quest. Consider using Quest.from_id() or Quest.from_json() instead.
        """
        self.data = self.QuestData()
        self.base_url = f"{self.client.campaign_base_url}quests/"


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

    @dataclass
    class JournalData(GenericChildType.GenericChildData):
        journal_id: Optional[int] = None
        location_id: Optional[int] = None
        character_id: Optional[int] = None
        calendar_id: Optional[int] = None
        calendar_year: Optional[str] = None
        calendar_month: Optional[str] = None
        calendar_day: Optional[str] = None
        date: Optional[str] = None

    def __post_init__(self):
        """
        Creates an empty Journal. Consider using Journal.from_id() or Journal.from_json() instead.
        """
        self.data = self.JournalData()
        self.base_url = f"{self.client.campaign_base_url}journals/"


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

    @dataclass
    class ItemData(GenericChildType.GenericChildData):
        location_id: Optional[int] = None
        character_id: Optional[int] = None
        size: Optional[float] = None
        price: Optional[float] = None

    def __post_init__(self):
        """
        Creates an empty Item. Consider using Item.from_id() or Item.from_json() instead.
        """
        self.data = self.ItemData()
        self.base_url = f"{self.client.campaign_base_url}items/"


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

    @dataclass
    class EventData(GenericChildType.GenericChildData):
        event_id: Optional[int] = None
        location_id: Optional[int] = None
        date: Optional[str] = None

    def __post_init__(self):
        """
        Creates an empty Event. Consider using Event.from_id() or Event.from_json() instead.
        """
        self.data = self.EventData()
        self.base_url = f"{self.client.campaign_base_url}events/"


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

    @dataclass
    class AbilityData(GenericChildType.GenericChildData):
        ability_id: Optional[int] = None
        abilities: Optional[str] = None
        charges: Optional[str] = None

    def __post_init__(self):
        """
        Creates an empty Ability. Consider using Ability.from_id() or Ability.from_json() instead.

        """
        self.data = self.AbilityData()
        self.base_url = f"{self.client.campaign_base_url}abilities/"


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

    @dataclass
    class CalendarData(GenericChildType.GenericChildData):
        current_year:       Optional[int] = None
        current_month:      Optional[int] = None
        current_day:        Optional[int] = None

        month_name:         Optional[List[str]] = None
        month_length:       Optional[List[int]] = None
        month_type:         Optional[List[str]] = None

        year_name:          Optional[List[str]] = None
        year_number:        Optional[List[int]] = None

        moon_name:          Optional[List[str]] = None
        moon_fullmoon:      Optional[List[int]] = None

        weekday:            Optional[List[str]] = None

        epoch_name:         Optional[List[str]] = None

        season_name:        Optional[List[str]] = None
        season_month:       Optional[List[int]] = None
        season_day:         Optional[List[int]] = None

        has_leap_year:      Optional[bool] = None
        leap_year_amount:   Optional[int] = None
        leap_year_start:    Optional[int] = None
        leap_year_offset:   Optional[int] = None

        header_full:        Optional[str] = None
        has_custom_header:  Optional[bool] = None

        # the following fields get returned by GET, but can't be passed to POST.

        suffix:             Optional[str] = None
        start_offset:       Optional[int] = None
        leap_year_month:    Optional[int] = None
        parameters:         Optional[None] = None
        date:               Optional[str] = None

        years:              Optional[dict] = None
        seasons:            Optional[List[dict]] = None
        months:             Optional[List[dict]] = None
        moons:              Optional[List[dict]] = None
        weekdays:           Optional[list] = None

        def __post_init__(self):
            # The API's naming scheme is very different between GET and POST, so workarounds like this are needed

            if self.months:
                month_name = []
                month_length = []
                for m in self.months:
                    month_name.append(m["name"])
                    month_length.append(m["length"])

                self.month_name = month_name
                self.month_length = month_length

            if self.weekdays:
                self.weekday = self.weekdays

    def __post_init__(self):
        """
        Creates an empty Calendar. Consider using Ability.from_id() or Ability.from_json() instead.
        """
        self.data = self.CalendarData()
        self.base_url = f"{self.client.campaign_base_url}calendars/"

    @staticmethod
    def _validate_parameters(values, files):
        if "name" not in values.keys():
            raise ValueError("'name' is a required field, but is missing")
        if "month_name" not in values.keys():
            raise ValueError("'month_name' is a required field, but is missing")
        if "weekday" not in values.keys():
            raise ValueError("'weekday' is a required field, but is missing")
        if "month_length" not in values.keys():
            raise ValueError("'month_length' is a required field, but is missing")
        if len(values["month_name"]) < 2:
            raise ValueError("'month_name' needs at least two entries, but has fewer")
        if len(values["weekday"]) < 2:
            raise ValueError("'weekday' needs at least two entries, but has fewer")
        if len(values["month_length"]) < 2:
            raise ValueError("'month_length' needs at least two entries, but has fewer")
        if len(values["month_name"]) != len(values["month_length"]):
            raise ValueError("lengths of month_name and month_length don't match")
