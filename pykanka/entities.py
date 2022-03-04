import json
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Union, Callable

import pykanka.entity_subentries
import pykanka.child_types
from pykanka.exceptions import *

import logging

logger = logging.getLogger(__name__)


# from pykanka.child_types import child_type_dictionary

@dataclass
class EntityData:
    id:                     Optional[int] = None
    name:                   Optional[str] = None
    type:                   Optional[str] = None
    type_id:                Optional[int] = None
    child_id:               Optional[int] = None
    campaign_id:            Optional[int] = None

    is_private:             Optional[bool] = None
    is_attributes_private:  Optional[bool] = None
    is_template:            Optional[bool] = None
    tags:                   Optional[List[int]] = None
    tooltip:                Optional[str] = None

    updated_at:             Optional[Union[datetime, str]] = None
    updated_by:             Optional[str] = None
    created_at:             Optional[Union[datetime, str]] = None
    created_by:             Optional[str] = None

    header_image:           Optional[str] = None
    image_uuid:             Optional[str] = None

    def __post_init__(self):
        if type(self.created_at) == str:
            self.created_at = datetime.fromisoformat(self.created_at.replace("Z", "+00:00"))
        if type(self.updated_at) == str:
            self.updated_at = datetime.fromisoformat(self.updated_at.replace("Z", "+00:00"))


@dataclass
class Entity:
    """Base class from which specific entity classes like locations and characters are inherited. Should usually not be interacted with directly."""

    client:                 "pykanka.KankaClient"

    data:       Optional[EntityData] = EntityData()
    base_url:   Optional[str] = str()
    endpoint:   Optional[str] = "entities"
    _child:     "pykanka.child_types.GenericChildType" = None


    def __post_init__(self):
        """
        Generates empty Entity. Consider using Entity.from_id() or Entity.from_json() instead.
        """

        self.base_url = f"{self.client.campaign_base_url}{self.endpoint}/"

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

    @child.setter
    def child(self, v: "pykanka.child_types.GenericChildType"):
        self._child = v

    @classmethod
    def from_id(cls, client: "pykanka.KankaClient", entity_id: int, child=None, refresh=False) -> "Entity":
        """
        Requests and constructs Entity from its ID. Requires one API call.

        :param client: KankaClient object
        :param entity_id: Entity ID to request from Kanka
        :param child: Existing child object, e.g. Location, Character. If none is given, new child is constructed from response.
        :return: Entity instance
        """
        obj = Entity(client, _child=child)

        response = client.request_get(f"{client.campaign_base_url}{cls.endpoint}/{entity_id}", refresh=refresh)

        if not response.ok:
            raise ResponseNotOkError(f"Response from {client.campaign_base_url}{cls.endpoint}/{entity_id} not OK, code {response.status_code}:\n{response.reason}")

        response_data = response.json()["data"]

        child_data = response_data["child"]
        response_data.pop("child")

        obj.data = EntityData(**response_data)

        if not obj.child:
            obj._child = obj._build_child_from_json(child_json=child_data, child_type=obj.data.type,)

        return obj

    @classmethod
    def from_json(cls, client: "pykanka.KankaClient", content: Union[str, dict]) -> "Entity":
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

        obj.data = EntityData(**content)

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
        response = self.client.request_get(f"{self.base_url}/{self.data.id}")

        if not response.ok:
            raise ResponseNotOkError(f"Response not OK, code {response.status_code}: {response.text}")

    def _build_child_from_json(self, child_json: dict, child_type: str):
        return self._get_child_class(child_type).from_json(self.client, child_json, parent=self)

    @classmethod
    def _get_child_class(cls, child_type: str):
        type_dictionary = pykanka.child_types.child_type_dictionary

        return type_dictionary[child_type]

    def _check_that_i_exist(self):              # if this Entity instance was locally created, it won't exist on the server yet and not have an entity_id
        if not self.data.id:
            raise AccessingNonExistentError("this entity doesn't have an id yet, does it exist on the server?")

    def get_attribute(self, attribute_id: int = None):
        self._check_that_i_exist()
        if attribute_id:
            return pykanka.entity_subentries.Attribute.from_id(client=self.client, entity_id=self.data.id, subentry_id=attribute_id)
        else:
            return pykanka.entity_subentries.Attribute(_client=self.client, entity_id=self.data.id)

    def get_event(self, attribute_id: int = None):
        self._check_that_i_exist()
        if attribute_id:
            return pykanka.entity_subentries.EntityEvent.from_id(client=self.client, entity_id=self.data.id, subentry_id=attribute_id)
        else:
            return pykanka.entity_subentries.EntityEvent(_client=self.client, entity_id=self.data.id)

    def get_file(self, attribute_id: int = None):
        self._check_that_i_exist()
        if attribute_id:
            return pykanka.entity_subentries.EntityFile.from_id(client=self.client, entity_id=self.data.id, subentry_id=attribute_id)
        else:
            return pykanka.entity_subentries.EntityFile(_client=self.client, entity_id=self.data.id)

    def get_note(self, attribute_id: int = None):
        self._check_that_i_exist()
        if attribute_id:
            return pykanka.entity_subentries.EntityNote.from_id(client=self.client, entity_id=self.data.id, subentry_id=attribute_id)
        else:
            return pykanka.entity_subentries.EntityNote(_client=self.client, entity_id=self.data.id)

    def get_tag(self, attribute_id: int = None):
        self._check_that_i_exist()
        if attribute_id:
            return pykanka.entity_subentries.EntityTag.from_id(client=self.client, entity_id=self.data.id, subentry_id=attribute_id)
        else:
            return pykanka.entity_subentries.EntityTag(_client=self.client, entity_id=self.data.id)

    def get_relation(self, attribute_id: int = None):
        self._check_that_i_exist()
        if attribute_id:
            return pykanka.entity_subentries.Relation.from_id(client=self.client, entity_id=self.data.id, subentry_id=attribute_id)
        else:
            return pykanka.entity_subentries.Relation(_client=self.client, owner_id=self.data.id)

    def get_inventory(self, attribute_id: int = None):
        self._check_that_i_exist()
        if attribute_id:
            return pykanka.entity_subentries.EntityInventory.from_id(client=self.client, entity_id=self.data.id, subentry_id=attribute_id)
        else:
            return pykanka.entity_subentries.EntityInventory(_client=self.client, entity_id=self.data.id)

    def get_ability(self, attribute_id: int = None):
        self._check_that_i_exist()
        if attribute_id:
            return pykanka.entity_subentries.EntityAbility.from_id(client=self.client, entity_id=self.data.id, subentry_id=attribute_id)
        else:
            return pykanka.entity_subentries.EntityAbility(_client=self.client, entity_id=self.data.id)

    def get_link(self, attribute_id: int = None):
        self._check_that_i_exist()
        if attribute_id:
            return pykanka.entity_subentries.EntityLink.from_id(client=self.client, entity_id=self.data.id, subentry_id=attribute_id)
        else:
            return pykanka.entity_subentries.EntityLink(_client=self.client, entity_id=self.data.id)

    def _get_all_of_type(self, endpoint, cls):
        self._check_that_i_exist()
        url = f"{self.base_url}{self.data.id}/{endpoint}"

        response = self.client.request_get(url)

        objects = []

        for entry in response.json()["data"]:
            objects.append(cls(_client=self.client, **entry))

        return objects

    def all_attributes(self):
        return self._get_all_of_type("attributes", pykanka.entity_subentries.Attribute)

    def all_events(self):
        return self._get_all_of_type("entity_events", pykanka.entity_subentries.EntityEvent)

    def all_files(self):
        return self._get_all_of_type("entity_files", pykanka.entity_subentries.EntityFile)

    def all_notes(self):
        return self._get_all_of_type("entity_notes", pykanka.entity_subentries.EntityNote)

    def all_tags(self):
        return self._get_all_of_type("entity_tags", pykanka.entity_subentries.EntityTag)

    def all_relations(self):
        return self._get_all_of_type("relations", pykanka.entity_subentries.Relation)

    def all_inventories(self):
        return self._get_all_of_type("inventory", pykanka.entity_subentries.EntityInventory)

    def all_abilities(self):
        return self._get_all_of_type("entity_abilities", pykanka.entity_subentries.EntityAbility)

    def all_links(self):
        return self._get_all_of_type("entity_links", pykanka.entity_subentries.EntityLink)
