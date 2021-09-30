import json
import typing
from typing import Dict

from pykanka.exceptions import *


class MapMarker:
    class _PolygonStyle:
        def __init__(self, values: dict = None):
            self.stroke = None
            self.stroke_width = None
            self.stroke_opacity = None

            # Inconsistency in Kanka API, stroke_width and stroke_opacity use '-' instead of '_'

            if values:
                for key in values.keys():
                    if f"{key}".replace("-", "_") in self.__dict__:
                        self.__dict__[f"{key}".replace("-", "_")] = values[key]
                    else:
                        raise WrongParametersPassedToEntity(f"{key} has been passed to PolygonStyle class, but is not a valid parameter")

        def to_json(self) -> Dict[str, typing.Any]:
            """Returns the object in dict form in preparation for json export"""
            self_dict = {"stroke": self.stroke,
                         "stroke-width": self.stroke_width,
                         "stroke-opacity": self.stroke_opacity}
            return self_dict

    def __init__(self, parent_map: "pykanka.child_types.Map", values: dict = None):
        """Creates a new map marker from given values. Probably shouldn't be done directly, try Map.get_marker() and Map.get_marker().post() instead."""
        self.circle_radius = None
        self.colour = None
        self.created_at = None
        self.created_by = None
        self.custom_icon = None
        self.custom_shape = None
        self.entity_id = None
        self.font_colour = None
        self.icon = None
        self.id = None
        self.is_draggable = None
        self.is_private = None
        self.latitude = None
        self.longitude = None
        self.name = None
        self.map_id = parent_map.data.id
        self.opacity = None
        self.pin_size = None
        self.polygon_style = None
        self.shape_id = None
        self.size_id = None
        self.updated_at = None
        self.updated_by = None
        self.visibility = None

        if values:
            for key in values.keys():
                if f"{key}" in self.__dict__:
                    self.__dict__[f"{key}"] = values[key]
                else:
                    raise WrongParametersPassedToEntity(f"{key} has been passed to MapMarker class, but is not a valid parameter")

        self.polygon_style = self._PolygonStyle(self.polygon_style)

        self._parent_map = parent_map

    def to_json(self) -> Dict[str, typing.Any]:
        """Returns the object in dict form in preparation for json export"""
        data = self.__dict__
        data["polygon_style"] = self.polygon_style.to_json()
        data.pop("_parent_map")

        return data

    def _prepare_post(self, json_data: str = None, **kwargs):
        possible_keys = ["name", "entity_id", "map_id", "latitude", "longitude", "shape_id", "icon", "group_id", "is_draggable", "custom_shape",
                         "custom_icon", "size_id", "opacity", "visibility", "colour", "font_colour", "circle_radius", "polygon_style"]

        if json_data:
            json_data = json.loads(json_data)
        else:
            json_data = dict()

        values = dict()

        for key in possible_keys:
            if key in self.__dict__:
                if self.__dict__[key] is not None:
                    values[key] = self.__dict__[key]
            if key in json_data:
                values[key] = json_data[key]
                json_data.pop(key)
            if key in kwargs:
                values[key] = kwargs[key]
                kwargs.pop(key)

        if type(values["polygon_style"]) == self._PolygonStyle:
            values["polygon_style"] = self.polygon_style.to_json()

        if json_data or kwargs:
            raise WrongParametersPassedToEntity()

        missing = {"map_id", "latitude", "longitude", "shape_id", "icon"} - values.keys()
        if missing:
            raise ValueError(f"{missing} are required fields, but are missing")
        if not (values["name"] or values["entity_id"]):
            raise ValueError("either 'name' or 'entity_id' is required, but both are missing")

        return values

    def post(self, json_data: str = None, **kwargs):
        """
        Create this map point on kanka.io. Takes any values outlined in the documentation.
        Required are either name or entity_id, map_id, latitude, longitude, shape_id and icon.
        Takes object parameter if no new one is specified.

        :param json_data: json string of the data. Parameters can be overwritten by kwargs.
        :param kwargs: Individual parameters
        :return: https response
        """
        payload = self._prepare_post(json_data=json_data, **kwargs)
        return self._parent_map.client.request_post(f"{self._parent_map.base_url}{self._parent_map.data.id}/map_markers", json=payload)

    def patch(self, json_data: str = None, **kwargs):
        """
        Update this map point on kanka.io. Takes any values outlined in the documentation.
        Required are either name or entity_id, map_id, latitude, longitude, shape_id and icon.
        Takes object parameter if no new one is specified.

        :param json_data: json string of the data. Parameters can be overwritten by kwargs.
        :param kwargs: Individual parameters
        :return: https response
        """
        payload = self._prepare_post(json_data=json_data, **kwargs)
        return self._parent_map.client.request_patch(f"{self._parent_map.base_url}{self._parent_map.data.id}/map_markers/{self.id}", json=payload)

    def delete(self):
        """
        Delete this map point on kanka.io

        :return: https response
        """
        return self._parent_map.client.request_delete(f"{self._parent_map.base_url}{self._parent_map.data.id}/map_markers/{self.id}")
