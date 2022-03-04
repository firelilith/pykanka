from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Union

import pykanka
from pykanka.exceptions import *


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
    created_by: Optional[int] = None
    created_at: Optional[Union[datetime, str]] = None
    updated_by: Optional[int] = None
    updated_at: Optional[Union[datetime, str]] = None

    header_full: Optional[str] = None
    has_custom_header: Optional[bool] = None

    def __post_init__(self):
        if type(self.created_at) == str:
            self.created_at = datetime.fromisoformat(self.created_at.replace("Z", "+00:00"))
        if type(self.updated_at) == str:
            self.updated_at = datetime.fromisoformat(self.updated_at.replace("Z", "+00:00"))


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
    eras: Optional[List[dict]] = None
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
    elements: Optional[List[int]] = None
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
    abilities: Optional[List[int]] = None
    charges: Optional[str] = None


@dataclass
class CalendarData(GenericChildData):
    """The /calendars/ endpoint of the Kanka API is hopelessly broken. Don't expect this to be stable or make sense"""
    current_year: Optional[int] = None
    current_month: Optional[int] = None
    current_day: Optional[int] = None

    month_name: Optional[List[str]] = None
    month_length: Optional[List[int]] = None
    month_type: Optional[List[str]] = None

    year_name: Optional[List[str]] = None
    year_number: Optional[int] = None

    moon_name: Optional[List[str]] = None
    moon_fullmoon: Optional[List[int]] = None

    weekday: Optional[List[str]] = None

    epoch_name: Optional[List[str]] = None

    season_name: Optional[List[str]] = None
    season_month: Optional[List[int]] = None
    season_day: Optional[List[int]] = None

    has_leap_year: Optional[bool] = None
    leap_year_amount: Optional[int] = None
    leap_year_start: Optional[int] = None
    leap_year_offset: Optional[int] = None

    # the following fields get returned by GET, but aren't used by POST

    leap_year_month: Optional[int] = None

    suffix: Optional[str] = None
    parameters: Optional[None] = None

    weekdays: Optional[List[str]] = None

    seasons: Optional[List[dict]] = None
    moons: Optional[List[dict]] = None
    years: Optional[dict] = None
    months: Optional[List[dict]] = None

    start_offset: Optional[int] = None
    date: Optional[str] = None
