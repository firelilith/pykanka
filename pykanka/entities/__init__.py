import json
import typing

import pykanka
from pykanka.exceptions import *


class Entity:
    """Base class from which specific entity classes like locations and characters are inherited. Should usually not be interacted with directly."""

    class EntityData:
        def __init__(self, val: dict = None):
            self.id = None
            self.name = None
            self.type = None
            self.child_id = None
            self.campaign_id = None

            self.is_private = None
            self.is_attributes_private = None
            self.is_template = None
            self.tags = None
            self.tooltip = None

            self.updated_at = None
            self.updated_by = None
            self.created_at = None
            self.created_by = None

            self.header_image = None
            self.image_uuid = None

            if val:
                for key in val.keys():
                    if f"{key}" in self.__dict__:
                        self.__dict__[f"{key}"] = val[key]
                    else:
                        raise WrongParametersPassedToEntity(f"{key} has been passed to Entity class, but is not a valid parameter")

    def __init__(self, client: "pykanka.KankaClient"):
        """
        Generates empty Entity. Consider using Entity.from_id() or Entity.from_json() instead.

        :param client: KankaClient object
        """

        self.client = client
        self.data = self.EntityData()
        self.entity_id = None

        self._child = None

    @property
    def child(self):
        if self._child:
            return self._child
        else:
            self._child = self._get_child_class(self.data.type).from_id(self.client, self.data.child_id, parent=self)
            return self._child

    @classmethod
    def from_id(cls, client: "pykanka.KankaClient", entity_id: int) -> "Entity":
        obj = Entity(client)

        response = client.request_get(f"{client.campaign_base_url}entities/{entity_id}")

        if not response.ok:
            raise ResponseNotOkError(f"Response not OK, code {response.status_code}:\n{response.text}")

        response_data = response.json()["data"]

        child_data = response_data["child"]
        response_data.pop("child")

        obj.data = obj.EntityData(response_data)
        obj.entity_id = obj.data.id

        obj._child = obj._build_child_from_json(child_json=child_data, child_type=obj.data.type,)

        return obj

    @classmethod
    def from_json(cls, client: "pykanka.KankaClient", content: typing.Union[str, dict]) -> "Entity":

        if type(content) == str:
            content = json.loads(content)

        if "data" in content.keys():
            content = content["data"]

        if "child" in content.keys():
            child_data = content["child"]
            content.pop("child")
        else:
            child_data = dict()

        obj = Entity(client)

        obj.data = cls.EntityData(val=content)
        obj.entity_id = obj.data.id

        if child_data:
            obj._child = obj._build_child_from_json(child_json=child_data, child_type=obj.data.type)

        return obj

    def _request_data(self):
        response = self.client.request_get(f"{self.client.campaign_base_url}entities/{self.entity_id}")

        if not response.ok:
            raise ResponseNotOkError(f"Response not OK, code {response.status_code}:\n{response.text}")

    def _build_child_from_json(self, child_json: dict, child_type: str):
        return self._get_child_class(child_type).from_json(self.client, child_json, parent=self)

    @classmethod
    def _get_child_class(cls, child_type: str):
        type_dictionary = dict(location=pykanka.entities.Location,
                               character=pykanka.entities.Character)
        """,
                               family=pykanka.entities.Family,
                               organisation=pykanka.entities.Organization,
                               timeline=pykanka.entities.Timeline,
                               race=pykanka.entities.Race,
                               note=pykanka.entities.Note,
                               map=pykanka.entities.Map,
                               tag=pykanka.entities.Tag,
                               quest=pykanka.entities.Quest,
                               journal=pykanka.entities.Journal,
                               item=pykanka.entities.Item,
                               event=pykanka.entities.Event,
                               ability=pykanka.entities.Ability
                               )"""
        return type_dictionary[child_type]


class GenericChildType:
    class GenericChildData:
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

            # for upload only
            self.image_file = None

            if val:
                for key in val.keys():
                    if f"{key}" in self.__dict__:
                        self.__dict__[f"{key}"] = val[key]
                    else:
                        raise WrongParametersPassedToEntity(f"{key} has been passed to child class, but is not a valid parameter")

    def __init__(self, client: "pykanka.KankaClient", parent: "Entity" = None):

        self.client = client
        self.parent = parent

        self.data = self.GenericChildData()

        self.base_url = str()           # Overridden by inheritors
        self.child_id = int()           # Overridden by inheritors

        self._possible_keys = list()    # Overridden by inheritors
        self._key_replacer = list()     # Overridden by inheritors
        self._file_keys = list()        # Overridden by inheritors

    @classmethod
    def from_id(cls, client: "pykanka.KankaClient", location_id: int, parent: "Entity" = None) -> "GenericChildType":
        obj = cls(client, parent=parent)

        response = client.request_get(f"{obj.base_url}{location_id}")

        if not response.ok:
            raise ResponseNotOkError(f"Response not OK, code {response.status_code}:\n{response.text}")

        obj.data = obj.data.__class__(response.json()["data"])
        obj.entity_id = obj.data.id

        return obj

    @classmethod
    def from_json(cls, client: "pykanka.KankaClient", content: typing.Union[str, dict], parent: "Entity" = None) -> "GenericChildType":

        if type(content) == str:
            content = json.loads(content)

        obj = cls(client, parent=parent)

        obj.data = obj.data.__init__(val=content)
        obj.child_id = obj.data.id

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

        return self.client.request_patch(f"{self.base_url}{self.child_id}", json=payload)

    def delete(self):
        return self.client.request_delete(f"{self.base_url}{self.child_id}")

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
                print(f"API doesn't support direct file uploads yet parameter {key} omitted. use url instead")

        existing_values = self._get_post_values()
        existing_values.update(values)

        if "name" not in existing_values.keys():
            raise ValueError("'name' is a required field, but is missing")

        return existing_values, files

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


class Location(GenericChildType):
    """A class representing a location child contained within an Entity."""

    class LocationData(GenericChildType.GenericChildData):
        def __init__(self, val: dict = None):
            self.parent_location_id = None
            self.is_map_private = None
            self.map = None

            super().__init__(val=val)

    def __init__(self, client: "pykanka.KankaClient", parent: "Entity" = None):
        """
        Creates an empty Location. Consider using Location.from_id() or Location.from_json() instead.

        :param client: KankaClient
        :param parent: Entity
        """
        super().__init__(client, parent=parent)

        self.data = self.LocationData()
        self.child_id = None

        self.base_url = f"{self.client.campaign_base_url}locations/"

        # keys accepted by POST and also delivered by GET as per API documentation
        self._possible_keys = ["name", "type", "parent_location_id", "tags", "is_private", "image", "map", "is_map_private"]
        # keys called differently in GET compared to POST as per API documentation, format: (get_version, post_version)
        self._key_replacer = [("image", "image_url"), ("map", "map_url")]
        # fields that accept stream object, currently not in API 1.0 yet
        self._file_keys = ["image", "map"]


class Character:
    pass
