import typing
import json

import requests

import pykanka
import pykanka.child_subentries as st
from pykanka.exceptions import *


class GenericChildType:
    """Generic class for child types. Shouldn't be used directly, it is used as a base class for specialized child types."""
    _possible_keys = list()  # Overridden by inheritors
    _key_replacer = list()  # Overridden by inheritors
    _file_keys = list()  # Overridden by inheritors

    class GenericChildData:
        """Container class for a GenericChildType. Gets overridden by specialized child type data containers."""
        def __init__(self, val: dict = None):
            self.id = None
            self.type = None
            self.entity_id = None
            self.name = None

            self.entry = None
            self.entry_parsed = None

            self.image = None
            self.image_full = None
            self.image_thumb = None

            self.tags = None

            self.focus_x = None
            self.focus_y = None

            self.has_custom_image = None
            self.is_template = None
            self.is_private = None

            self.created_by = None
            self.created_at = None
            self.updated_by = None
            self.updated_at = None

            if val:
                for key in val.keys():
                    if f"{key}" in self.__dict__:
                        self.__dict__[f"{key}"] = val[key]
                    else:
                        raise WrongParametersPassedToEntity(f"{key} has been passed to child class, but is not a valid parameter")

    def __init__(self, client: "pykanka.KankaClient", parent: "pykanka.entities.Entity" = None):

        self.client = client

        self._parent = parent

        self.data = self.GenericChildData()

        self.base_url = str()           # Overridden by inheritors

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

    @classmethod
    def from_id(cls, client: "pykanka.KankaClient", child_id: int, parent: "pykanka.entities.Entity" = None) -> "GenericChildType":
        obj = cls(client, parent=parent)

        response = client.request_get(f"{obj.base_url}{child_id}")

        if not response.ok:
            raise ResponseNotOkError(f"Response from {obj.base_url}{child_id} not OK, code {response.status_code}: {response.reason}")

        obj.data = obj.data.__class__(response.json()["data"])

        return obj

    @classmethod
    def from_json(cls, client: "pykanka.KankaClient", content: typing.Union[str, dict], parent: "pykanka.entities.Entity" = None) -> "GenericChildType":

        if type(content) == str:
            content = json.loads(content)

        obj = cls(client, parent=parent)

        obj.data = obj.data.__class__(val=content)

        return obj

    def post(self, json_data: str = None, name: str = "", **kwargs):
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

        payload, files = self._prepare_post(json_data, name=name, **kwargs)

        return self.client.request_post(f"{self.base_url}", json=payload)

    def patch(self, json_data: str = None, name: str = "", **kwargs):
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

        payload, files = self._prepare_post(json_data, name=name, **kwargs)

        return self.client.request_patch(f"{self.base_url}{self.data.id}", json=payload)

    def delete(self):
        return self.client.request_delete(f"{self.base_url}{self.data.id}")

    def _prepare_post(self, json_data: str, **kwargs):  # implement support for image files (keys: image and map) when the API allows it
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


class Location(GenericChildType):
    """A class representing a location child contained within an Entity."""

    # keys accepted by POST and also delivered by GET as per API documentation
    _possible_keys = ["name", "type", "parent_location_id", "tags", "is_private", "image_full", "map", "is_map_private"]
    # keys called differently in GET compared to POST as per API documentation, format: (get_version, post_version)
    _key_replacer = [("image_full", "image_url"), ("map", "map_url")]
    # fields that accept stream object, not yet supported in API 1.0
    _file_keys = ["image", "map"]

    class LocationData(GenericChildType.GenericChildData):
        def __init__(self, val: dict = None):
            self.parent_location_id = None
            self.is_map_private = None
            self.map = None

            super().__init__(val=val)

    def __init__(self, client: "pykanka.KankaClient", parent: "pykanka.entities.Entity" = None):
        """
        Creates an empty Location. Consider using Location.from_id() or Location.from_json() instead.

        :param client: KankaClient
        :param parent: Entity
        """
        super().__init__(client, parent=parent)

        self.data = self.LocationData()
        self.child_id = None

        self.base_url = f"{self.client.campaign_base_url}locations/"

    def get_map_image(self) -> "requests.Response.raw":
        """Returns file-like object of the entity's map image"""
        return self.client.request_get(self.data.map, stream=True).raw


class Character(GenericChildType):
    """A class representing a Character child contained within an Entity."""

    # keys accepted by POST and also delivered by GET as per API documentation
    _possible_keys = ["name", "entry", "title", "age", "sex", "pronouns", "type", "family_id", "location_id", "race_id", "tags", "is_dead", "is_private", "image_full", "is_personality_visible"]
    # keys called differently in GET compared to POST as per API documentation, format: (get_version, post_version)
    _key_replacer = [("image_full", "image_url")]
    # fields that accept stream object, not yet supported in API 1.0
    _file_keys = ["image"]

    class CharacterData(GenericChildType.GenericChildData):
        def __init__(self, val: dict = None):
            self.location_id = None
            self.family_id = None
            self.race_id = None
            self.age = None
            self.sex = None
            self.pronouns = None
            self.title = None
            self.traits = None
            self.is_dead = None
            self.is_personality_visible = None

            super().__init__(val=val)

    def __init__(self, client: "pykanka.KankaClient", parent: "pykanka.entities.Entity" = None):
        """
        Creates an empty Character. Consider using Character.from_id() or Character.from_json() instead.

        :param client: KankaClient
        :param parent: Entity
        """
        super().__init__(client, parent=parent)

        self.data = self.CharacterData()

        self.base_url = f"{self.client.campaign_base_url}characters/"


class Organisation(GenericChildType):
    """A class representing a Organisation child contained within an Entity."""

    # keys accepted by POST and also delivered by GET as per API documentation
    _possible_keys = ["name", "entry", "type", "organization_id", "location_id", "tags", "is_private", "image_full"]
    # keys called differently in GET compared to POST as per API documentation, format: (get_version, post_version)
    _key_replacer = [("image_full", "image_url")]
    # fields that accept stream object, not yet supported in API 1.0
    _file_keys = ["image"]

    class OrganisationData(GenericChildType.GenericChildData):
        def __init__(self, val: dict = None):
            self.organisation_id = None
            self.location_id = None
            self.members = None

            super().__init__(val=val)

    def __init__(self, client: "pykanka.KankaClient", parent: "pykanka.entities.Entity" = None):
        """
        Creates an empty Organisation. Consider using Organisation.from_id() or Organisation.from_json() instead.

        :param client: KankaClient
        :param parent: Entity
        """
        super().__init__(client, parent=parent)

        self.data = self.OrganisationData()

        self.base_url = f"{self.client.campaign_base_url}organisations/"


class Timeline(GenericChildType):
    """A class representing a Timeline child contained within an Entity."""

    # keys accepted by POST and also delivered by GET as per API documentation
    _possible_keys = ["name", "entry", "type", "revert_order", "tags", "is_private", "image_full"]
    # keys called differently in GET compared to POST as per API documentation, format: (get_version, post_version)
    _key_replacer = [("image_full", "image_url")]
    # fields that accept stream object, not yet supported in API 1.0
    _file_keys = ["image"]

    class TimelineData(GenericChildType.GenericChildData):
        def __init__(self, val: dict = None):
            self.eras = None
            self.timeline_id = None
            self.revert_order = None

            super().__init__(val=val)

    def __init__(self, client: "pykanka.KankaClient", parent: "pykanka.entities.Entity" = None):
        """
        Creates an empty Timeline. Consider using Timeline.from_id() or Timeline.from_json() instead.

        :param client: KankaClient
        :param parent: Entity
        """
        super().__init__(client, parent=parent)

        self.data = self.TimelineData()

        self.base_url = f"{self.client.campaign_base_url}timelines/"


class Race(GenericChildType):
    """A class representing a Race child contained within an Entity."""

    # keys accepted by POST and also delivered by GET as per API documentation
    _possible_keys = ["name", "entry", "type", "race_id", "tags", "is_private", "image_full"]
    # keys called differently in GET compared to POST as per API documentation, format: (get_version, post_version)
    _key_replacer = [("image_full", "image_url")]
    # fields that accept stream object, not yet supported in API 1.0
    _file_keys = ["image"]

    class RaceData(GenericChildType.GenericChildData):
        def __init__(self, val: dict = None):
            self.race_id = None

            super().__init__(val=val)

    def __init__(self, client: "pykanka.KankaClient", parent: "pykanka.entities.Entity" = None):
        """
        Creates an empty Race. Consider using Race.from_id() or Race.from_json() instead.

        :param client: KankaClient
        :param parent: Entity
        """
        super().__init__(client, parent=parent)

        self.data = self.RaceData()

        self.base_url = f"{self.client.campaign_base_url}races/"


class Family(GenericChildType):
    """A class representing a Family child contained within an Entity."""

    # keys accepted by POST and also delivered by GET as per API documentation
    _possible_keys = ["name", "entry", "type", "location_id", "family_id", "tags", "is_private", "image_full"]
    # keys called differently in GET compared to POST as per API documentation, format: (get_version, post_version)
    _key_replacer = [("image_full", "image_url")]
    # fields that accept stream object, not yet supported in API 1.0
    _file_keys = ["image"]

    class FamilyData(GenericChildType.GenericChildData):
        def __init__(self, val: dict = None):
            self.members = None
            self.location_id = None
            self.family_id = None

            super().__init__(val=val)

    def __init__(self, client: "pykanka.KankaClient", parent: "pykanka.entities.Entity" = None):
        """
        Creates an empty Family. Consider using Location.from_id() or Family.from_json() instead.

        :param client: KankaClient
        :param parent: Entity
        """
        super().__init__(client, parent=parent)

        self.data = self.FamilyData()

        self.base_url = f"{self.client.campaign_base_url}families/"


class Note(GenericChildType):
    """A class representing a Note child contained within an Entity."""

    # keys accepted by POST and also delivered by GET as per API documentation
    _possible_keys = ["name", "entry", "type", "note_id", "tags", "is_private", "image_full"]
    # keys called differently in GET compared to POST as per API documentation, format: (get_version, post_version)
    _key_replacer = [("image_full", "image_url")]
    # fields that accept stream object, not yet supported in API 1.0
    _file_keys = ["image"]

    class NoteData(GenericChildType.GenericChildData):
        def __init__(self, val: dict = None):
            self.is_pinned = None
            self.note_id = None

            super().__init__(val=val)

    def __init__(self, client: "pykanka.KankaClient", parent: "pykanka.entities.Entity" = None):
        """
        Creates an empty Note. Consider using Note.from_id() or Note.from_json() instead.

        :param client: KankaClient
        :param parent: Entity
        """
        super().__init__(client, parent=parent)

        self.data = self.NoteData()

        self.base_url = f"{self.client.campaign_base_url}notes/"


class Map(GenericChildType):
    """A class representing a Map child contained within an Entity."""

    # keys accepted by POST and also delivered by GET as per API documentation
    _possible_keys = ["name", "entry", "type", "map_id", "location_id", "center_marker_id", "center_x", "center_y", "tags", "is_private", "image_full"]
    # keys called differently in GET compared to POST as per API documentation, format: (get_version, post_version)
    _key_replacer = [("image_full", "image_url")]
    # fields that accept stream object, not yet supported in API 1.0
    _file_keys = ["image"]

    class MapData(GenericChildType.GenericChildData):
        def __init__(self, val: dict = None):
            self.location_id = None
            self.map_id = None
            self.width = None
            self.height = None
            self.initial_zoom = None
            self.center_x = None
            self.center_y = None
            self.max_zoom = None
            self.min_zoom = None
            self.layers = None
            self.groups = None
            self.grid = None
            self.center_marker_id = None

            super().__init__(val=val)

    def __init__(self, client: "pykanka.KankaClient", parent: "pykanka.entities.Entity" = None):
        """
        Creates an empty Map. Consider using Map.from_id() or Map.from_json() instead.

        :param client: KankaClient
        :param parent: Entity
        """
        super().__init__(client, parent=parent)

        self.data = self.MapData()

        self.base_url = f"{self.client.campaign_base_url}maps/"

    def all_markers(self) -> list["st.MapMarker"]:
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


class Tag(GenericChildType):
    """A class representing a Tag child contained within an Entity."""

    # keys accepted by POST and also delivered by GET as per API documentation
    _possible_keys = ["name", "entry", "type", "colour", "tag_id", "is_private", "image_full"]
    # keys called differently in GET compared to POST as per API documentation, format: (get_version, post_version)
    _key_replacer = [("image_full", "image_url")]
    # fields that accept stream object, not yet supported in API 1.0
    _file_keys = ["image"]

    class TagData(GenericChildType.GenericChildData):
        def __init__(self, val: dict = None):
            self.entities = None
            self.tag_id = None
            self.colour = None

            super().__init__(val=val)

    def __init__(self, client: "pykanka.KankaClient", parent: "pykanka.entities.Entity" = None):
        """
        Creates an empty Tag. Consider using Tag.from_id() or Tag.from_json() instead.

        :param client: KankaClient
        :param parent: Entity
        """
        super().__init__(client, parent=parent)

        self.data = self.TagData()

        self.base_url = f"{self.client.campaign_base_url}tags/"


class Quest(GenericChildType):
    """A class representing a Quest child contained within an Entity."""

    # keys accepted by POST and also delivered by GET as per API documentation
    _possible_keys = ["name", "entry", "type", "quest_id", "character_id", "tags", "is_private", "image_full"]
    # keys called differently in GET compared to POST as per API documentation, format: (get_version, post_version)
    _key_replacer = [("image_full", "image_url")]
    # fields that accept stream object, not yet supported in API 1.0
    _file_keys = ["image"]

    class QuestData(GenericChildType.GenericChildData):
        def __init__(self, val: dict = None):
            self.quest_id = None
            self.character_id = None
            self.calendar_id = None
            self.calendar_year = None
            self.calendar_month = None
            self.calendar_day = None
            self.date = None
            self.elements_count = None
            self.elements = None
            self.is_completed = None

            super().__init__(val=val)

    def __init__(self, client: "pykanka.KankaClient", parent: "pykanka.entities.Entity" = None):
        """
        Creates an empty Quest. Consider using Quest.from_id() or Quest.from_json() instead.

        :param client: KankaClient
        :param parent: Entity
        """
        super().__init__(client, parent=parent)

        self.data = self.QuestData()

        self.base_url = f"{self.client.campaign_base_url}quests/"


class Journal(GenericChildType):
    """A class representing a Journal child contained within an Entity."""

    # keys accepted by POST and also delivered by GET as per API documentation
    _possible_keys = ["name", "entry", "type", "date", "character_id", "tags", "is_private", "image_full"]
    # keys called differently in GET compared to POST as per API documentation, format: (get_version, post_version)
    _key_replacer = [("image_full", "image_url")]
    # fields that accept stream object, not yet supported in API 1.0
    _file_keys = ["image"]

    class JournalData(GenericChildType.GenericChildData):
        def __init__(self, val: dict = None):
            self.journal_id = None
            self.location_id = None
            self.character_id = None
            self.calendar_id = None
            self.calendar_year = None
            self.calendar_month = None
            self.calendar_day = None
            self.date = None

            super().__init__(val=val)

    def __init__(self, client: "pykanka.KankaClient", parent: "pykanka.entities.Entity" = None):
        """
        Creates an empty Journal. Consider using Journal.from_id() or Journal.from_json() instead.

        :param client: KankaClient
        :param parent: Entity
        """
        super().__init__(client, parent=parent)

        self.data = self.JournalData()

        self.base_url = f"{self.client.campaign_base_url}journals/"


class Item(GenericChildType):
    """A class representing a Item child contained within an Entity."""

    # keys accepted by POST and also delivered by GET as per API documentation
    _possible_keys = ["name", "entry", "type", "location_id", "character_id", "price", "size", "tags", "is_private", "image_full"]
    # keys called differently in GET compared to POST as per API documentation, format: (get_version, post_version)
    _key_replacer = [("image_full", "image_url")]
    # fields that accept stream object, not yet supported in API 1.0
    _file_keys = ["image"]

    class ItemData(GenericChildType.GenericChildData):
        def __init__(self, val: dict = None):
            self.location_id = None
            self.character_id = None
            self.size = None
            self.price = None

            super().__init__(val=val)

    def __init__(self, client: "pykanka.KankaClient", parent: "pykanka.entities.Entity" = None):
        """
        Creates an empty Item. Consider using Item.from_id() or Item.from_json() instead.

        :param client: KankaClient
        :param parent: Entity
        """
        super().__init__(client, parent=parent)

        self.data = self.ItemData()

        self.base_url = f"{self.client.campaign_base_url}items/"


class Event(GenericChildType):
    """A class representing a Event child contained within an Entity."""

    # keys accepted by POST and also delivered by GET as per API documentation
    _possible_keys = ["name", "entry", "type", "date", "location_id", "tags", "is_private", "image_full"]
    # keys called differently in GET compared to POST as per API documentation, format: (get_version, post_version)
    _key_replacer = [("image_full", "image_url")]
    # fields that accept stream object, not yet supported in API 1.0
    _file_keys = ["image"]

    class EventData(GenericChildType.GenericChildData):
        def __init__(self, val: dict = None):
            self.event_id = None
            self.location_id = None
            self.date = None

            super().__init__(val=val)

    def __init__(self, client: "pykanka.KankaClient", parent: "pykanka.entities.Entity" = None):
        """
        Creates an empty Event. Consider using Event.from_id() or Event.from_json() instead.

        :param client: KankaClient
        :param parent: Entity
        """
        super().__init__(client, parent=parent)

        self.data = self.EventData()

        self.base_url = f"{self.client.campaign_base_url}events/"


class Ability(GenericChildType):
    """A class representing a Ability child contained within an Entity."""

    # keys accepted by POST and also delivered by GET as per API documentation
    _possible_keys = ["name", "entry", "type", "ability_id", "charges", "tags", "is_private", "image_full"]
    # keys called differently in GET compared to POST as per API documentation, format: (get_version, post_version)
    _key_replacer = [("image_full", "image_url")]
    # fields that accept stream object, not yet supported in API 1.0
    _file_keys = ["image"]

    class AbilityData(GenericChildType.GenericChildData):
        def __init__(self, val: dict = None):
            self.ability_id = None
            self.abilities = None
            self.charges = None

            super().__init__(val=val)

    def __init__(self, client: "pykanka.KankaClient", parent: "pykanka.entities.Entity" = None):
        """
        Creates an empty Ability. Consider using Ability.from_id() or Ability.from_json() instead.

        :param client: KankaClient
        :param parent: Entity
        """
        super().__init__(client, parent=parent)

        self.data = self.AbilityData()

        self.base_url = f"{self.client.campaign_base_url}abilities/"


class Calendar(GenericChildType):
    """A class representing a Calendar child contained within an Entity"""

    # keys accepted by POST and also delivered by GET as per API documentation
    _possible_keys = ["name", "entry", "type", "current_year", "current_month", "current_day", "tags", "month_name", "month_length", "month_type", "weekday", "year_name", "year_number",
                      "moon_name", "moon_fullmoon", "epoch_name", "season_name", "season_month", "season_day", "has_leap_year", "leap_year_amount", "leap_year_offset", "leap_year_start",
                      "tags", "is_private", "image_full"]
    # keys called differently in GET compared to POST as per API documentation, format: (get_version, post_version)
    _key_replacer = [("image_full", "image_url")]
    # fields that accept stream object, not yet supported in API 1.0
    _file_keys = ["image"]

    class CalendarData(GenericChildType.GenericChildData):
        def __init__(self, val: dict = None):
            self.suffix = None
            self.parameters = None
            self.weekdays = None
            self.leap_year_offset = None
            self.seasons = None
            self.moons = None
            self.leap_year_amount = None
            self.leap_year_month = None
            self.date = None
            self.years = None
            self.has_leap_year = None
            self.leap_year_start = None
            self.start_offset = None
            self.months = None

            super().__init__(val=val)

    def __init__(self, client: "pykanka.KankaClient", parent: "pykanka.entities.Entity" = None):
        """
        Creates an empty Calendar. Consider using Ability.from_id() or Ability.from_json() instead.

        :param client: KankaClient
        :param parent: Entity
        """
        super().__init__(client, parent=parent)

        self.data = self.CalendarData()

        self.base_url = f"{self.client.campaign_base_url}calendars/"
