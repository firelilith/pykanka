import typing
import json
from typing import List, Optional

import requests

import pykanka
import pykanka.child_subentries as st
from pykanka.exceptions import *
from dataclasses import dataclass, InitVar


@dataclass
class GenericChildData:
    name: str = None
    id: Optional[int] = None
    type: Optional[str] = None
    entity_id: Optional[int] = None

    entry: Optional[str] = None
    entry_parsed: Optional[str] = None

    image: Optional[str] = None
    image_full: Optional[str] = None
    image_thumb: Optional[str] = None

    tags: Optional[List[int]] = None

    focus_x: Optional[float] = None
    focus_y: Optional[float] = None

    has_custom_image: Optional[str] = None
    is_template: Optional[bool] = None
    is_private: Optional[bool] = None

    # Should be datetimes, but will require some type conversions, likely
    created_by: Optional[str] = None
    created_at: Optional[str] = None
    updated_by: Optional[str] = None
    updated_at: Optional[str] = None

    header_full: Optional[str] = None
    has_custom_header: Optional[bool] = None


@dataclass
class LocationData(GenericChildData):
    parent_location_id: Optional[int] = None
    is_map_private: Optional[bool] = None
    map: Optional[str] = None


@dataclass
class CharacterData(GenericChildData):
    location_id: Optional[int] = None
    family_id: Optional[int] = None
    race_id: Optional[int] = None
    age: Optional[int] = None
    sex: Optional[str] = None
    pronouns: Optional[str] = None
    title: Optional[str] = None
    traits: Optional[List[int]] = None
    is_dead: Optional[bool] = None
    is_personality_visible: Optional[bool] = None


@dataclass
class OrganisationData(GenericChildData):
    organisation_id: Optional[int] = None
    location_id: Optional[int] = None
    members: Optional[List[int]] = None


@dataclass
class TimelineData(GenericChildData):
    eras: Optional[str] = None
    timeline_id: Optional[int] = None
    revert_order: Optional[bool] = None


@dataclass
class RaceData(GenericChildData):
    race_id: Optional[int] = None


@dataclass
class FamilyData(GenericChildData):
    members: Optional[List[int]] = None
    location_id: Optional[int] = None
    family_id: Optional[int] = None


@dataclass()
class NoteData(GenericChildData):
    is_pinned: Optional[bool] = None
    note_id: Optional[int] = None


@dataclass
class MapData(GenericChildData):
    location_id: Optional[int] = None
    map_id: Optional[int] = None
    width: Optional[float] = None
    height: Optional[float] = None
    initial_zoom: Optional[float] = None
    center_x: Optional[float] = None
    center_y: Optional[float] = None
    max_zoom: Optional[float] = None
    min_zoom: Optional[float] = None
    layers: Optional[str] = None
    groups: Optional[str] = None
    grid: Optional[str] = None
    center_marker_id: Optional[id] = None


@dataclass
class TagData(GenericChildData):
    entities: Optional[List[int]] = None
    tag_id: Optional[int] = None
    colour: Optional[str] = None


@dataclass
class QuestData(GenericChildData):
    quest_id: Optional[str] = None
    character_id: Optional[str] = None
    calendar_id: Optional[str] = None
    calendar_year: Optional[str] = None
    calendar_month: Optional[str] = None
    calendar_day: Optional[str] = None
    date: Optional[str] = None
    elements_count: Optional[str] = None
    elements: Optional[str] = None
    is_completed: Optional[str] = None


@dataclass
class JournalData(GenericChildData):
    journal_id: Optional[int] = None
    location_id: Optional[int] = None
    character_id: Optional[int] = None
    calendar_id: Optional[int] = None
    calendar_year: Optional[str] = None
    calendar_month: Optional[str] = None
    calendar_day: Optional[str] = None
    date: Optional[str] = None


@dataclass
class ItemData(GenericChildData):
    location_id: Optional[int] = None
    character_id: Optional[int] = None
    size: Optional[float] = None
    price: Optional[float] = None


@dataclass
class EventData(GenericChildData):
    event_id: Optional[int] = None
    location_id: Optional[int] = None
    date: Optional[str] = None


@dataclass
class AbilityData(GenericChildData):
    ability_id: Optional[int] = None
    abilities: Optional[str] = None
    charges: Optional[str] = None


@dataclass
class CalendarData(GenericChildData):
    suffix: Optional[str] = None
    parameters: Optional[str] = None
    weekdays: Optional[str] = None
    leap_year_offset: Optional[str] = None
    seasons: Optional[str] = None
    moons: Optional[str] = None
    leap_year_amount: Optional[str] = None
    leap_year_month: Optional[str] = None
    date: Optional[str] = None
    years: Optional[str] = None
    has_leap_year: Optional[str] = None
    leap_year_start: Optional[str] = None
    start_offset: Optional[str] = None
    months: Optional[str] = None