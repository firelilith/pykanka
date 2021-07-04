import requests
import typing
import json
from exceptions import *


class Entity:
    class _EntityData:
        def __init__(self, val: dict = None):
            self._id = None
            self._name = None
            self._entry = None
            self._entry_parsed = None
            self._image = None
            self._image_full = None
            self._image_thumb = None
            self._image_uuid = None
            self._is_private = None
            self._entity_id = None
            self._tags = None
            self._created_at = None
            self._created_by = None
            self._updated_by = None

            if val:
                for key in val.keys():
                    if f"_{key}" in self.__dict__:
                        self.__dict__[f"_{key}"] = val[key]

        @property
        def id(self):
            return self._id

        @property
        def name(self):
            return self._name

        @property
        def entry(self):
            return self._entry

        @property
        def entry_parsed(self):
            return self._entry_parsed

        @property
        def image(self):
            return self._image

        @property
        def image_full(self):
            return self._image_full

        @property
        def image_thumb(self):
            return self._image_thumb

        @property
        def image_uuid(self):
            return self._image_uuid

        @property
        def is_private(self):
            return self._is_private

        @property
        def entity_id(self):
            return self._entity_id

        @property
        def tags(self):
            return self._tags

        @property
        def created_at(self):
            return self._created_at

        @property
        def created_by(self):
            return self._created_by

        @property
        def updated_by(self):
            return self._updated_by

    def __init__(self, client):
        self.client = client
        self.entity = self._EntityData()

    @classmethod
    def build_from_json(cls, client, json_dict: dict = None, json_str: str = None, **kwargs) -> "Entity":
        obj = Entity(client)

        val = {}

        if json_str:
            json_str=json.loads(json_str)
            val.update(json_str)

        if json_dict:
            val.update(json_dict)

        val.update(kwargs)

        if not val.keys() <= cls._EntityData.__dict__.keys():
            raise WrongParametersPassedToEntity((val.keys() - cls._EntityData.__dict__.keys()))

        obj.entity = cls._EntityData(val)

        return obj

    #deprecated
    def _request(self, ent_id, **kwargs):
        if "return_error" in kwargs:
            return_error = kwargs["return_error"]
            del kwargs["return_error"]
        else:
            return_error = False

        response = requests.get(f"{self.client.base_url}/entities/{ent_id}", params=kwargs, headers=self.client.headers)

        if response.ok:
            return response.json()
        else:
            if return_error:
                return {"status": response.status_code, "error": response.reason}
            else:
                return None

    def _request_by_id(self, local_id, ent_type, **kwargs):
        if "return_error" in kwargs:
            return_error = kwargs["return_error"]
            del kwargs["return_error"]
        else:
            return_error = False

        response = requests.get(f"{self.client.base_url}/{ent_type}/{local_id}", params=kwargs, headers=self.client.headers)

        if response.ok:
            ent_id = response.json()["data"]["entity_id"]

            return self._request(ent_id, **kwargs)

        if return_error:
            return {"status": response.status_code, "error": response.reason}
        else:
            return None


class Location(Entity):

    def __init__(self, client):
        super().__init__(client)

    def request_by_id(self, local_id, **kwargs):
        return super()._request_by_id(local_id, "locations", **kwargs)

    def request_by_entity(self, entity_id, **kwargs):
        return super()._request(entity_id, kwargs)


class Character(Entity):
    pass
