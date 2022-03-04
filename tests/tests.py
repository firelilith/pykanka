import unittest
from pykanka.child_types import *
from library.child_base_test import ChildBaseTest

class TestLocation(ChildBaseTest):
    ChildType = Location
    ChildDataType = Location.LocationData
    data = {
                "name": "Mordor",
                "entry": "<p>Lorem Ipsum.</p>",
                "has_custom_image": False,
                "is_private": True,
                "tags": [],
                "is_map_private": 0,
                "type": "Kingdom"
            }

    def setUp(self) -> None:
        super().setUp()
        self.get_all = self.read_campaign.all_locations
    pass

class TestCharacter(ChildBaseTest):
    ChildType = Character
    ChildDataType = Character.CharacterData
    data = {
        "name": "Jonathan Green",
        "entry": "<p>Lorem Ipsum.</p>",
        "has_custom_image": False,
        "is_private": True,
        "is_personality_visible": True,
        "is_template": False,
        "tags": [],
        "title": None,
        "age": "39",
        "sex": "Male",
        "pronouns": None,
        "race_id": 3,
        "type": None,
        "is_dead": True,
    }

    def setUp(self) -> None:
        super().setUp()
        self.get_all = self.read_campaign.all_characters
    pass

class TestOrganisation(ChildBaseTest):
    ChildType = Organisation
    ChildDataType = Organisation.OrganisationData
    data = {
                "name": "Tiamat Cultists",
                "entry": "<p>Lorem Ipsum.</p>",
                "has_custom_image": False,
                "is_private": True,
                "tags": [],
                "type": "Kingdom",
                "members": []
            }

    def setUp(self) -> None:
        super().setUp()
        self.get_all = self.read_campaign.all_organisations
    pass

class TestTimeline(ChildBaseTest):
    ChildType = Timeline
    ChildDataType = Timeline.TimelineData
    data = {
                "name": "Thaelian Timeline",
                "entry": "<p>Lorem Ipsum</p>",
                "has_custom_image": False,
                "is_private": False,
                "tags": [],
                "type": "Primary",
                "revert_order": False,
                # "eras": [
                #   {
                #     "name": "Anno Domani",
                #     "abbreviation": "AD",
                #     "start_year": 0,
                #     "end_year": None,
                #     "elements": []
                #   },
                #   {
                #     "name": "Before Christ",
                #     "abbreviation": "BC",
                #     "start_year": None,
                #     "end_year": 0,
                #     "elements": []
                #   }
                # ]
            }

    def setUp(self) -> None:
        super().setUp()
        self.get_all = self.read_campaign.all_timelines
    pass

class TestRace(ChildBaseTest):
    ChildType = Race
    ChildDataType = Race.RaceData
    data = {
                "name": "Goblin",
                "entry": "<p>Lorem Ipsum.</p>",
                "has_custom_image": False,
                "is_private": True,
                "tags": [],
                "type": None
            }

    def setUp(self) -> None:
        super().setUp()
        self.get_all = self.read_campaign.all_races
    pass

class TestFamily(ChildBaseTest):
    ChildType = Family
    ChildDataType = Family.FamilyData
    data = {
                "name": "Adams",
                "entry": "<p>Lorem Ipsum.</p>",
                "has_custom_image": False,
                "is_private": True,
                "tags": [],
                "type": None,
            }

    def setUp(self) -> None:
        super().setUp()
        self.get_all = self.read_campaign.all_families
    pass

class TestNote(ChildBaseTest):
    ChildType = Note
    ChildDataType = Note.NoteData
    data = {
                "name": "Legends of the World",
                "entry": "<p>Lorem Ipsum.</p>",
                "has_custom_image": False,
                "is_private": True,
                "tags": [],
                "type": "Lore",
                "is_pinned": 0
            }

    def setUp(self) -> None:
        super().setUp()
        self.get_all = self.read_campaign.all_notes
    pass

class TestTag(ChildBaseTest):
    ChildType = Tag
    ChildDataType = Tag.TagData
    data = {
                "name": "Religion",
                "entry": "<p>Lorem Ipsum.</p>",
                "has_custom_image": False,
                "is_private": True,
                "tags": [],
                "type": "Lore",
                "colour": "green",
            }

    def setUp(self) -> None:
        super().setUp()
        self.get_all = self.read_campaign.all_tags
    pass

class TestQuest(ChildBaseTest):
    ChildType = Quest
    ChildDataType = Quest.QuestData
    data = {
                "name": "Pelor's Quest",
                "entry": "<p>Lorem Ipsum.</p>",
                "has_custom_image": False,
                "is_private": True,
                "tags": [],
                "date": "2020-04-20",
                "type": "Main",
                "is_completed": False,
            }

    def setUp(self) -> None:
        super().setUp()
        self.get_all = self.read_campaign.all_quests
    pass

class TestJournal(ChildBaseTest):
    ChildType = Journal
    ChildDataType = Journal.JournalData
    data = {
                "name": "Session 2 - Descent into the Abyss",
                "entry": "<p>Lorem Ipsum</p>",
                "has_custom_image": False,
                "is_private": True,
                "tags": [],
                "date": "2017-11-02",
                "type": "Session"
            }

    def setUp(self) -> None:
        super().setUp()
        self.get_all = self.read_campaign.all_journals
    pass

class TestItem(ChildBaseTest):
    ChildType = Item
    ChildDataType = Item.ItemData
    data = {
                "name": "Spear",
                "entry": "<p>Lorem Ipsum.</p>",
                "has_custom_image": False,
                "is_private": True,
                "tags": [],
                "type": "Weapon",
                "price": "25 gp",
                "size": "1 lb."
            }

    def setUp(self) -> None:
        super().setUp()
        self.get_all = self.read_campaign.all_items
    pass

class TestEvent(ChildBaseTest):
    ChildType = Event
    ChildDataType = Event.EventData
    data = {
                "name": "Battle of Hadish",
                "entry": "<p>Lorem Ipsum.</p>",
                "has_custom_image": False,
                "is_private": True,
                "tags": [],
                "date": "44-3-16",
                "type": "Battle"
            }

    def setUp(self) -> None:
        super().setUp()
        self.get_all = self.read_campaign.all_events
    pass

class TestAbility(ChildBaseTest):
    ChildType = Ability
    ChildDataType = Ability.AbilityData
    data = {
                "name": "Fireball",
                "entry": "<p>Lorem Ipsum.</p>",
                "has_custom_image": False,
                "is_private": True,
                "tags": [],
                "type": "3rd level",
                "charges": '3',
                "abilities": []
            }

    def setUp(self) -> None:
        super().setUp()
        self.get_all = self.read_campaign.all_abilities
    pass

class TestCalendar(ChildBaseTest):
    ChildType = Calendar
    ChildDataType = Calendar.CalendarData
    data = {
            "name": "Georgian Calendar",
            "entry": "<p>Lorem Ipsum</p>",
            "has_custom_image": False,
            "is_private": False,
            "tags": [],
            "type": "Primary",
            "date": "311-2-3",
            "parameters": None,
            "months": [
                {
                    "name": "January",
                    "length": 31,
                    "type": "standard"
                },
                {
                    "name": "February",
                    "length": 5,
                    "type": "intercalary"
                }
            ],
            "start_offset": 0,
            "weekdays": [
                "Sul",
                "Mol",
                "Zol",
                "Wir",
                "Zor",
                "Far",
                "Sar"
            ],
            "years": {
                "299": "Year of Blood and Fire",
                "300": "Year of Water and Bone"
            },
            "seasons": [
                {
                    "name": "Spring",
                    "month": 1,
                    "day": 1
                },
                {
                    "name": "Summer",
                    "month": 4,
                    "day": 1
                }
            ],
            "moons": [
                {
                    "name": "Zarantyr",
                    "fullmoon": "13",
                    "offset": 0,
                    "colour": "aqua"
                },
                {
                    "name": "Olarune",
                    "fullmoon": "17",
                    "offset": 0,
                    "colour": "brown"
                }
            ],
            "suffix": "BC",
            "has_leap_year": True,
            "leap_year_amount": 4,
            "leap_year_month": 2,
            "leap_year_offset": 3,
            "leap_year_start": 233
        }

    def setUp(self) -> None:
        super().setUp()
        self.get_all = self.read_campaign.all_locations
    pass

class TestMenuLink(ChildBaseTest):
    # ChildType = MenuLink
    # ChildDataType = MenuLinkData
    data = {
                "name": "Random Chara",
                "filters": None,
                "icon": None,
                "is_private": 0,
                "menu": None,
                "random_entity_type": "character",
                "type": None,
                "tab": "",
                "target": None,
                "dashboard_id": None,
                "options": {"is_nested": "1"}
            }

    def setUp(self) -> None:
        super().setUp()
        self.get_all = self.read_campaign.all_menulinks
    pass

class TestDashboardWidget(ChildBaseTest):
    # ChildType = DashboardWidget
    # ChildDataType = TestDashboardWidgetData
    data = {
                "entity_id": 6,
                "widget": "preview",
                "config": {
                    "full": "1"
                },
                "width": 6,
                "position": 2,
                "tags": [],
            }

    def setUp(self) -> None:
        super().setUp()
        self.get_all = self.read_campaign.all_dashboardwidgets()
    pass

class TestPykanka(unittest.TestCase):
    """Tests for pykanka module"""

if __name__ == '__main__':
    unittest.main()