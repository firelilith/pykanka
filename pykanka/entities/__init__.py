import json
import typing

from pykanka import KankaClient
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

    def __init__(self, client: "KankaClient", child: "EntityType" = None):
        """
        Generates empty Entity. Consider using Entity.from_id() or Entity.from_json() instead.

        :param client: KankaClient object
        """

        self.client = client
        self.data = self.EntityData()

    @classmethod
    def from_id(cls, client: "KankaClient", entity_id: int) -> "Entity":
        obj = Entity(client)

        response = client.get(f"{client.campaign_base_url}entities/{entity_id}")

        if not response.ok:
            raise ResponseNotOkError(f"Response not OK, code {response.status_code}:\n{response.text}")

        obj.data = obj.EntityData(response.json())

        return obj

    @classmethod
    def from_json(cls, client: "KankaClient", content: typing.Union[str, dict]) -> "Entity":

        if type(content) == str:
            content = json.loads(content)

        obj = Entity(client)

        obj.data = cls.EntityData(val=content)

        return obj


class EntityType:
    class GenericData:
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


    def __init__(self, client: "KankaClient", parent: "Entity" = None):

        self.client = client
        self.parent = parent


class Location(EntityType):
    """A class representing a location child contained within an Entity."""

    class LocationData(EntityType.GenericData):
        def __init__(self, val: dict = None):
            self.parent_location_id = None
            self.is_map_private = None
            self.map = None

            super().__init__(val=val)

    def __init__(self, client: "KankaClient", entity: "Entity"):
        super().__init__(client)


class Character:
    pass
