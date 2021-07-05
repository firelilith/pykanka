import json
import typing

from pykanka import KankaClient
from pykanka.exceptions import *


class Entity:
    """Base class from which specific entity classes like locations and characters are inherited. Should usually not be interacted with directly."""

    class EntityData:
        def __init__(self, val: dict = None):
            self._id = None
            self._name = None
            self._type = None
            self._child_id = None
            self._campaign_id = None

            self._is_private = None
            self._is_attributes_private = None
            self._is_template = None
            self._tags = None
            self._tooltip = None

            self._updated_at = None
            self._updated_by = None
            self._created_at = None
            self._created_by = None

            self._header_image = None
            self._image_uuid = None

            if val:
                for key in val.keys():
                    if f"_{key}" in self.__dict__:
                        self.__dict__[f"_{key}"] = val[key]
                    else:
                        raise WrongParametersPassedToEntity(f"{key} has been passed to Entity class, but is not a valid parameter")

        # Property declarations, entity data is read-only

        @property
        def name(self) -> typing.Optional[str]:
            return self._name

        @property
        def entity_id(self) -> typing.Optional[int]:
            return self._id

        @property
        def type(self) -> typing.Optional[str]:
            return self._type

        @property
        def child_id(self) -> typing.Optional[int]:
            return self._child_id

        @property
        def campaign_id(self) -> typing.Optional[int]:
            return self._campaign_id

        @property
        def is_private(self) -> typing.Optional[bool]:
            return self._is_private

        @property
        def is_attributes_private(self) -> typing.Optional[bool]:
            return self._is_attributes_private

        @property
        def is_template(self) -> typing.Optional[bool]:
            return self._is_template

        @property
        def tags(self) -> typing.Optional[list]:
            return self._tags

        @property
        def tooltip(self) -> typing.Optional[str]:
            return self._tooltip

        @property
        def updated_at(self) -> typing.Optional[str]:
            return self._updated_at

        @property
        def updated_by(self) -> typing.Optional[int]:
            return self._updated_by

        @property
        def created_at(self) -> typing.Optional[str]:
            return self._created_at

        @property
        def created_by(self) -> typing.Optional[int]:
            return self._created_by

        @property
        def header_image(self) -> typing.Optional[str]:
            return self._header_image

        @property
        def image_uuid(self):
            return self._image_uuid

        # End of property declarations

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
        """
        readonly variable

        :var type_id
        """
        def __init__(self, val: dict = None):
            self._id = None
            self._type = None
            self._entity_id = None
            self._name = None

            self._entry = None
            self._entry_parsed = None

            self._image = None
            self._image_full = None
            self._image_thumb = None

            self._tags = None

            self._focus_x = None
            self._focus_y = None

            self._has_custom_image = None
            self._is_template = None
            self._is_private = None

            self._created_by = None
            self._created_at = None
            self._updated_by = None
            self._updated_at = None

            # for upload only
            self._image_file = None

            if val:
                for key in val.keys():
                    if f"_{key}" in self.__dict__:
                        self.__dict__[f"_{key}"] = val[key]
                    else:
                        raise WrongParametersPassedToEntity(f"{key} has been passed to child class, but is not a valid parameter")

        # Property declarations

        @property
        def local_id(self) -> typing.Optional[int]:
            return self._id

        @property
        def type(self) -> typing.Optional[str]:
            return self._type

        @type.setter
        def type(self, value: str) -> None:
            if type(value) == str:
                self._type = value
            else:
                raise ValueError(f"Expected type str, received {type(value)}")

        @property
        def entity_id(self) -> typing.Optional[int]:
            return self._entity_id

        @property
        def name(self) -> typing.Optional[str]:
            return self._name

        @type.setter
        def type(self, value: str) -> None:
            if type(value) == str:
                self._type = value
            else:
                raise ValueError(f"Expected type str, received {type(value)}")

        @property
        def entry(self) -> typing.Optional[str]:
            return self._entry

        @type.setter
        def type(self, value: str) -> None:
            if type(value) == str:
                self._type = value
            else:
                raise ValueError(f"Expected type str, received {type(value)}")

        @property
        def entry_parsed(self) -> typing.Optional[str]:
            return self._entry_parsed

        @property
        def image(self) -> typing.Optional[str]:
            return self._image

        @property
        def image_full(self) -> typing.Optional[str]:
            return self._image_full

        @property
        def image_thumb(self) -> typing.Optional[str]:
            return self._image_thumb

        @property
        def tags(self) -> typing.Optional[list[int]]:
            return self._tags

        @tags.setter
        def tags(self, value: list[int]) -> None:
            if type(value) == list:
                if all(map(lambda x: type(x) == int, value)):
                    self._tags = value
            else:
                raise ValueError(f"Expected list of int, received {type(value)}")

        @property
        def focus_x(self) -> typing.Optional[int]:
            return self._focus_x

        @focus_x.setter
        def focus_x(self, value: int) -> None:
            if type(value) == int:
                self._focus_x = value
            else:
                raise ValueError(f"Expected type int, received {type(value)}")

        @property
        def focus_y(self) -> typing.Optional[int]:
            return self._focus_y

        @focus_y.setter
        def focus_y(self, value: int) -> None:
            if type(value) == int:
                self._focus_y = value
            else:
                raise ValueError(f"Expected type int, received {type(value)}")

        @property
        def has_custom_image(self) -> typing.Optional[bool]:
            return self._has_custom_image

        @property
        def is_template(self) -> typing.Optional[bool]:
            return self._is_template

        @property
        def is_private(self) -> typing.Optional[bool]:
            return self._is_private

        @is_private.setter
        def is_private(self, value: bool) -> None:
            if type(value) == bool:
                self._is_private = value
            else:
                raise ValueError(f"Expected type bool, received {type(value)}")

        @property
        def created_by(self) -> typing.Optional[int]:
            return self._created_by

        @property
        def created_at(self) -> typing.Optional[str]:
            return self._created_at

        @property
        def updated_by(self) -> typing.Optional[int]:
            return self._updated_by

        @property
        def updated_at(self) -> typing.Optional[str]:
            return self._updated_at

        # End of property declarations

    def __init__(self, client: "KankaClient", parent: "Entity" = None):

        self.client = client
        self.parent = parent


class Location(EntityType):
    """A class representing a location child contained within an Entity."""

    class LocationData(EntityType.GenericData):
        def __init__(self, val: dict = None):
            self._parent_location_id = None
            self._is_map_private = None
            self._map = None

            super().__init__(val=val)

        @property
        def parent_location_id(self) -> typing.Optional[int]:
            return self._parent_location_id

        @property
        def is_map_private(self) -> typing.Optional[bool]:
            return self._is_map_private

        @property
        def map(self) -> typing.Optional[int]:
            return self._map

        @parent_location_id.setter
        def parent_location_id(self, value: int) -> None:
            if type(value) == int:
                self._parent_location_id = value
            else:
                raise ValueError(f"Expected type int, received {type(value)}")


    def __init__(self, client: "KankaClient", entity: "Entity"):
        super().__init__()


class Character:
    pass
