import json
import typing

import pykanka
from pykanka.exceptions import *
import pykanka.child_types as ct


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

    def __init__(self, client: "pykanka.KankaClient", child: "pykanka.child_types.GenericChildType" = None):
        """
        Generates empty Entity. Consider using Entity.from_id() or Entity.from_json() instead.

        :param client: KankaClient object
        :param child: Subclass inherited from GenericChildType
        """

        self.client = client
        self.data = self.EntityData()

        self._child = child

    @property
    def child(self):
        if self._child:
            return self._child
        elif self.data.child_id:
            self._child = self._get_child_class(self.data.type).from_id(self.client, self.data.child_id, parent=self)
            return self._child
        else:
            self._child = self._get_child_class(self.data.type)(self.client, parent=self)
            return self._child

    @classmethod
    def from_id(cls, client: "pykanka.KankaClient", entity_id: int, child=None) -> "Entity":
        """
        Requests and constructs Entity from its ID. Requires one API call.

        :param client: KankaClient object
        :param entity_id: Entity ID to request from Kanka
        :param child: Existing child object, e.g. Location, Character. If none is given, new child is constructed from response.
        :return: Entity instance
        """
        obj = Entity(client, child=child)

        response = client.request_get(f"{client.campaign_base_url}entities/{entity_id}")

        if not response.ok:
            raise ResponseNotOkError(f"Response from {client.campaign_base_url}entities/{entity_id} not OK, code {response.status_code}:\n{response.reason}")

        response_data = response.json()["data"]

        child_data = response_data["child"]
        response_data.pop("child")

        obj.data = obj.EntityData(response_data)

        if not obj.child:
            obj._child = obj._build_child_from_json(child_json=child_data, child_type=obj.data.type,)

        return obj

    @classmethod
    def from_json(cls, client: "pykanka.KankaClient", content: typing.Union[str, dict]) -> "Entity":
        """
        Constructs Entity from json string or dictionary. Requires no API calls.

        :param client: KankaClient object
        :param content: Either a json string or a dict containing the entity data.
        :return: Entity instance
        """
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

        if child_data:
            obj._child = obj._build_child_from_json(child_json=child_data, child_type=obj.data.type)

        return obj

    def to_json(self) -> str:
        """
        Dumps the Entity object as json string.

        :return: json string representation of the Entity object.
        """
        ent_data = self.data.__dict__
        if self._child:
            child_data = self._child.data.__dict__
            ent_data["child"] = child_data
        return json.dumps(ent_data)

    def _request_data(self):
        response = self.client.request_get(f"{self.client.campaign_base_url}entities/{self.data.id}")

        if not response.ok:
            raise ResponseNotOkError(f"Response not OK, code {response.status_code}: {response.text}")

    def _build_child_from_json(self, child_json: dict, child_type: str):
        return self._get_child_class(child_type).from_json(self.client, child_json, parent=self)

    @classmethod
    def _get_child_class(cls, child_type: str):
        type_dictionary = dict(location=ct.Location,
                               character=ct.Character,
                               family=ct.Family,
                               organisation=ct.Organisation,
                               timeline=ct.Timeline,
                               race=ct.Race,
                               note=ct.Note,
                               map=ct.Map,
                               tag=ct.Tag,
                               quest=ct.Quest,
                               journal=ct.Journal,
                               item=ct.Item,
                               event=ct.Event,
                               ability=ct.Ability,
                               calendar=ct.Calendar
                               )

        return type_dictionary[child_type]
