import datetime

from pykanka import KankaClient
from pykanka.entities import Entity
from pykanka.exceptions import *

from datetime import datetime
from dataclasses import dataclass
from typing import Optional, ClassVar, Set, Union, IO


@dataclass
class GenericSubentry:
    _required: ClassVar[Set[str]]
    _possible: ClassVar[Set[str]]
    _endpoint: ClassVar[str] = ""

    _client: KankaClient

    id: int = None

    def __post_init__(self):
        self._base_url: str = f"{self._client.campaign_base_url}entities/"

    def post(self, **kwargs):
        data, url = self._prepare_post(kwargs)
        return self._client.request_post(url=url, data=data)

    def patch(self, **kwargs):
        data, url = self._prepare_post(kwargs)
        return self._client.request_patch(url=url, data=data)

    def _prepare_post(self, manual_parameters):
        data = {}

        for key, val in self.__dict__.items():
            if key in self._possible and val is not None:
                data[key] = val

        for key, val in manual_parameters.items():
            if key in self._possible:
                data[key] = val
            else:
                raise WrongParametersPassedToEntity(key)

        if not self._required.issubset(data.keys()):
            raise ParameterMissingError(self._required - data.keys())

        self._extra_validation(data)

        if "entity_id" in data:
            url = f"{self._base_url}{data['entity_id']}/{self._endpoint}"
        else:                                                                                   # Relations behave differently
            url = f"{self._base_url}{data['owner_id']}/{self._endpoint}"

        return data, url

    def _extra_validation(self, data):
        pass

    def delete(self):
        if "entity_id" in self.__dict__:
            url = f"{self._base_url}{self.__dict__['entity_id']}/{self._endpoint}/{self.id}"
        elif "owner_id" in self.__dict__:                                                       # Relations behave differently
            url = f"{self._base_url}{self.__dict__['owner_id']}/{self._endpoint}/{self.id}"
        else:
            raise DeletingNonExistentError("no entity id present")

        return self._client.request_delete(url=url)


@dataclass
class Attribute(GenericSubentry):                                           # Working
    _required: ClassVar[Set[str]] = {"name", "entity_id"}
    _possible: ClassVar[Set[str]] = {"name", "value", "default_order", "type", "entity_id", "is_private", "is_star", "api_key"}
    _endpoint: ClassVar[str] = "attributes"

    api_key:            Optional[str] = None
    created_at:         Optional[Union[datetime, str]] = None
    created_by:         Optional[int] = None
    default_order:      Optional[int] = None
    entity_id:          Optional[int] = None
    is_private:         Optional[bool] = None
    is_star:            Optional[bool] = None
    name:               Optional[str] = None
    parsed:             Optional[str] = None
    type:               Optional[str] = None
    updated_at:         Optional[Union[datetime, str]] = None
    updated_by:         Optional[int] = None
    value:              Optional[str] = None


@dataclass
class EntityEvent(GenericSubentry):                                         # Working
    _required: ClassVar[Set[str]] = {"calendar_id", "name", "day", "month", "year", "length", "entity_id"}
    _possible: ClassVar[Set[str]] = {"calendar_id", "name", "day", "month", "year", "length", "recurring_periodicity", "recurring_until", "colour", "comment", "entity_id", "is_private", "type_id", "visibility"}
    _endpoint: ClassVar[str] = "entity_events"

    calendar_id:            Optional[int] = None
    comment:                Optional[str] = None
    created_at:             Optional[Union[datetime, str]] = None
    created_by:             Optional[int] = None
    date:                   Optional[str] = None
    entity_id:              Optional[int] = None
    id:                     Optional[int] = None
    is_private:             Optional[bool] = None
    is_recurring:           Optional[bool] = None
    recurring_periodicity:  Optional[str] = None
    length:                 Optional[int] = None
    recurring_until:        Optional[int] = None
    type_id:                Optional[int] = None
    updated_at:             Optional[Union[datetime, str]] = None
    updated_by:             Optional[int] = None
    visibility:             Optional[str] = None
    year:                   Optional[int] = None


@dataclass
class EntityFile(GenericSubentry):                                              # Currently broken, code 500
    _required: ClassVar[Set[str]] = {}
    _possible: ClassVar[Set[str]] = {"file", "visibility"}
    _endpoint: ClassVar[str] = "entity_files"

    created_at:             Optional[Union[datetime, str]] = None
    created_by:             Optional[int] = None
    entity_id:              Optional[int] = None
    entry:                  Optional[str] = None
    id:                     Optional[int] = None
    visibility:             Optional[str] = None
    name:                   Optional[str] = None
    path:                   Optional[str] = None
    size:                   Optional[str] = None
    type:                   Optional[str] = None
    updated_at:             Optional[Union[datetime, str]] = None
    updated_by:             Optional[int] = None

    def post(self, file: IO = None, **kwargs):
        if "entity_id" in kwargs:
            ent_id = kwargs["entity_id"]
            kwargs.pop("entity_id")
        elif self.entity_id:
            ent_id = self.entity_id
        else:
            raise ParameterMissingError("no entity id present")

        url = f"{self._base_url}{ent_id}/{self._endpoint}"

        files = [(
            "file", file
        )]

        return self._client.request_post(url=url, files=files, data=kwargs)

    def patch(self, **kwargs):
        print("patch not supported on this endpoint")

    def get_file(self):
        return self._client.request_get(self.path, stream=True).raw.data


@dataclass
class Inventory(GenericSubentry):                                           # Warning! In the documentation sidebar this is called "Entity Inventory"
    _required: ClassVar[Set[str]] = {"item_id", "entity_id"}
    _possible: ClassVar[Set[str]] = {"item_id", "amount", "position", "entity_id", "visibility"}
    _endpoint: ClassVar[str] = "inventories"

    created_at:             Optional[Union[datetime, str]] = None
    created_by:             Optional[int] = None
    entity_id:              Optional[int] = None
    id:                     Optional[int] = None
    item_id:                Optional[int] = None
    visibility:             Optional[str] = None
    amount:                 Optional[int] = None
    position:               Optional[int] = None
    updated_at:             Optional[Union[datetime, str]] = None
    updated_by:             Optional[int] = None


@dataclass
class EntityNotes(GenericSubentry):                                         # Working
    _required: ClassVar[Set[str]] = {"name", "entity_id", "visibility", "entry"}
    _possible: ClassVar[Set[str]] = {"name", "entry", "entity_id", "visibility", "position", "settings"}
    _endpoint: ClassVar[str] = "entity_notes"

    created_at:             Optional[Union[datetime, str]] = None
    created_by:             Optional[int] = None
    entity_id:              Optional[int] = None
    entry:                  Optional[str] = None
    entry_parsed:           Optional[str] = None
    id:                     Optional[int] = None
    position:               Optional[int] = None
    visibility:             Optional[str] = None
    name:                   Optional[str] = None
    settings:               Optional[list] = None
    updated_at:             Optional[Union[datetime, str]] = None
    updated_by:             Optional[int] = None


@dataclass
class EntityTags(GenericSubentry):                                        # Working
    _required: ClassVar[Set[str]] = {"entity_id", "tag_id"}
    _possible: ClassVar[Set[str]] = {"entity_id", "tag_id"}
    _endpoint: ClassVar[str] = "entity_tags"

    id:                     Optional[int] = None
    entity_id:              Optional[int] = None
    tag_id:                 Optional[int] = None


@dataclass
class Relation(GenericSubentry):                                           # Working, but two_way not effective
    _required: ClassVar[Set[str]] = {"relation", "owner_id", "target_id", "visibility"}
    _possible: ClassVar[Set[str]] = {"relation", "owner_id", "target_id", "attitude", "colour", "two_way", "is_star", "visibility"}
    _endpoint: ClassVar[str] = "relations"

    owner_id:               Optional[int] = None
    target_id:              Optional[int] = None
    relation:               Optional[str] = None
    attitude:               Optional[int] = None
    visibility:             Optional[str] = None
    is_star:                Optional[bool] = None
    colour:                 Optional[str] = None
    created_at:             Optional[Union[datetime, str]] = None
    created_by:             Optional[int] = None
    updated_at:             Optional[Union[datetime, str]] = None
    updated_by:             Optional[int] = None


@dataclass                                                                      # Warning! In the documentation sidebar this is called "Inventory"
class EntityInventory(GenericSubentry):                                         # Working
    _required: ClassVar[Set[str]] = {"entity_id", "amount"}
    _possible: ClassVar[Set[str]] = {"entity_id", "item_id", "name", "amount", "position", "visibility", "is_equipped"}
    _endpoint: ClassVar[str] = "inventory"

    id:                     Optional[int] = None
    entity_id:              Optional[int] = None
    item_id:                Optional[int] = None
    amount:                 Optional[int] = None
    is_equipped:            Optional[bool] = None
    is_private:             Optional[bool] = None
    item:                   Optional[dict] = None
    name:                   Optional[str] = None
    position:               Optional[str] = None
    visibility:             Optional[str] = None

    def _extra_validation(self, data):
        if not ("item_id" in data or "name" in data):
            raise ParameterMissingError("either item_id or name must be present")


@dataclass
class EntityAbility(GenericSubentry):                               # Working
    _required: ClassVar[Set[str]] = {"entity_id", "ability_id"}
    _possible: ClassVar[Set[str]] = {"entity_id", "ability_id", "visibility", "charges", "note", "position"}
    _endpoint: ClassVar[str] = "entity_abilities"

    ability_id:             Optional[int] = None
    created_at:             Optional[Union[datetime, str]] = None
    created_by:             Optional[int] = None
    entity_id:              Optional[int] = None
    id:                     Optional[int] = None
    visibility:             Optional[str] = None
    updated_at:             Optional[Union[datetime, str]] = None
    updated_by:             Optional[int] = None
    charges:                Optional[int] = None
    position:               Optional[int] = None
    note:                   Optional[str] = None


@dataclass
class EntityLink(GenericSubentry):                                  # Working
    _required: ClassVar[Set[str]] = {"entity_id", "name", "url", "visibility"}
    _possible: ClassVar[Set[str]] = {"entity_id", "name", "icon", "url", "position", "visibility"}
    _endpoint: ClassVar[str] = "entity_links"

    created_at:             Optional[Union[datetime, str]] = None
    created_by:             Optional[int] = None
    entity_id:              Optional[int] = None
    id:                     Optional[int] = None
    visibility:             Optional[str] = None
    name:                   Optional[str] = None
    url:                    Optional[str] = None
    icon:                   Optional[str] = None
    position:               Optional[int] = None
    updated_at:             Optional[Union[datetime, str]] = None
    updated_by:             Optional[int] = None

    def patch(self, **kwargs):
        print("patch not supported on this endpoint")
