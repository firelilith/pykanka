import json
from pykanka import KankaClient
from pykanka.exceptions import *


class _Entity:
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
        def name(self):
            return self._name

        @property
        def id(self):
            return self._id

        @property
        def type(self):
            return self._type

        @property
        def child_id(self):
            return self._child_id

        @property
        def campaign_id(self):
            return self._campaign_id

        @property
        def is_private(self):
            return self._is_private

        @property
        def is_attributes_private(self):
            return self._is_attributes_private

        @property
        def is_template(self):
            return self._is_template

        @property
        def tags(self):
            return self._tags

        @property
        def tooltip(self):
            return self._tooltip

        @property
        def updated_at(self):
            return self._updated_at

        @property
        def updated_by(self):
            return self._updated_by

        @property
        def created_at(self):
            return self._created_at

        @property
        def created_by(self):
            return self._created_by

        @property
        def header_image(self):
            return self._header_image

        @property
        def image_uuid(self):
            return self._image_uuid

        # End of property declarations

    def __init__(self, client: "KankaClient", entity_id: int):
        self.client = client

        response = client.get(f"{client.campaign_base_url}entities/{entity_id}")

        if not response.ok:
            raise ResponseNotOkError(f"Response not OK, code {response.status_code}:\n{response.text}")

        self.entity = self._EntityData(response.json())


class Location(_Entity):
    """A class representing a location entity."""

    class _EntityData(_Entity.EntityData):
        pass

    def __init__(self, client: "KankaClient", entity_id: int = None, location_id: int = None):
        super().__init__(client)


class Character(_Entity):
    pass
