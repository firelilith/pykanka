import json
import typing

from PIL import Image
from io import BytesIO

import pykanka
from pykanka.exceptions import *


class Entity:
    """Base class from which specific entity classes like locations and characters are inherited. Should usually not be interacted with directly."""

    type_dictionary = dict(location=pykanka.entities.Location,
                           character=pykanka.entities.Character,
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
                           )

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

    def __init__(self, client: "KankaClient"):
        """
        Generates empty Entity. Consider using Entity.from_id() or Entity.from_json() instead.

        :param client: KankaClient object
        """

        self.client = client
        self.data = self.EntityData()
        self.entity_id = None

    @classmethod
    def from_id(cls, client: "pykanka.KankaClient", entity_id: int) -> "Entity":
        obj = Entity(client)

        response = client.request_get(f"{client.campaign_base_url}entities/{entity_id}")

        if not response.ok:
            raise ResponseNotOkError(f"Response not OK, code {response.status_code}:\n{response.text}")

        obj.data = obj.EntityData(response.json())
        obj.entity_id = obj.data.id

        return obj

    @classmethod
    def from_json(cls, client: "pykanka.KankaClient", content: typing.Union[str, dict]) -> "Entity":

        if type(content) == str:
            content = json.loads(content)

        obj = Entity(client)

        obj.data = cls.EntityData(val=content)
        obj.entity_id = obj.data.id

        return obj

    def _request_data(self):
        response = self.client.request_get(f"{self.client.campaign_base_url}entities/{self.entity_id}")

        if not response.ok:
            raise ResponseNotOkError(f"Response not OK, code {response.status_code}:\n{response.text}")


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

    def refresh(self):
        pass

    def _request_values(self):
        pass

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
        self.location_id = None

        self.base_url = f"{self.client.campaign_base_url}locations/"

    @classmethod
    def from_id(cls, client: "pykanka.KankaClient", location_id: int) -> "Location":
        obj = Location(client)

        response = client.request_get(f"{client.campaign_base_url}entities/{location_id}")

        if not response.ok:
            raise ResponseNotOkError(f"Response not OK, code {response.status_code}:\n{response.text}")

        obj.data = obj.L(response.json())
        obj.entity_id = obj.data.id

        return obj

    @classmethod
    def from_json(cls, client: "pykanka.KankaClient", content: typing.Union[str, dict]) -> "Location":

        if type(content) == str:
            content = json.loads(content)

        obj = Location(client)

        obj.data = cls.LocationData(val=content)
        obj.location_id = obj.data.id

        return obj

    def _get_post_values(self):
        possible_keys = ["name", "type", "parent_location_id", "tags", "is_private", "image", "map", "is_map_private"]

        values = dict()

        for key in possible_keys:
            if self.data.__dict__[key] is not None:
                values[key] = self.data.__dict__[key]

        if "image" in values.keys():
            values["image_url"] = values["image"]
            values.pop("image")
        if "map" in values.keys():
            values["map_url"] = values["map"]
            values.pop("map")

        return values

    def post(self, json_data: str = None, name: str = "", **kwargs):
        """
        Posts Location to Campaign. Possible parameters are outlined in the documentation, here:
        https://kanka.io/en/docs/1.0/locations#create-location
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
        https://kanka.io/en/docs/1.0/locations#create-location
        Parameters are taken from existing object, a json string or keywords.
        Here, keywords override json override existing.

        Currently, the kanka API does not support the parameters 'image' and 'map'.

        :param json_data: str
        :param name: str
        :return: requests.response
        """

        payload, files = self._prepare_post(json_data, name=name, **kwargs)

        return self.client.request_patch(f"{self.base_url}{self.location_id}", json=payload)

    def delete(self):
        return self.client.request_delete(f"{self.base_url}{self.location_id}")

    def _prepare_post(self, json_data: str, **kwargs):  # implement support for image files (keys: image and map) when the API allows it
        if json_data:
            values = json.loads(json_data)
            values.update(kwargs)
        else:
            values = kwargs

        # The API doesn't support file uploads as of now, placeholder to when it will become relevant.

        files = dict()

        if "image" in values:
            files["image"] = open(values["image"], "rb")
            values.pop("image")
            print("API doesn't support direct file uploads yet, use url instead")
        if "map" in values:
            files["map"] = open(values["map"], "rb")
            values.pop("map")
            print("API doesn't support direct file uploads yet, use url instead")

        existing_values = self._get_post_values()
        existing_values.update(values)

        if "name" not in existing_values.keys():
            raise ValueError("'name' is a required field, but is missing")

        return existing_values, files


class Character:
    pass
