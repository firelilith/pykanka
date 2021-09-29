import unittest
from pykanka import KankaClient
from pykanka.entities import Entity
from pykanka.child_types import *
# from pykanka.childdata_types import *
from sample_data import sample_data
import vcr

class TestPykanka(unittest.TestCase):
    """Test Classes for pykanka module"""

    def setUp(self) -> None:
        """Set up the client
        API_TOKEN is a placeholder. Since we are using cassettes that filter out the authorization header,
        there is no need for a working token. Use "generate_cassettes.py" to generate cassettes for this test.
        The cassettes set up the response for campaign_id 1. This is the sample campaign on Kanka."""
        self.campaign = KankaClient("API_TOKEN", 1)

    def test_get_all(self):
        """Tests the client.all_{child} method and the children returned
        The test gets all of each child type, then surveys the first ten objects.
        For each sampled child the test verifies that:
            The child is of the expected type (a character should be of Character type)
            The child's parent is of Entity type
            The child's data is the expected type (a character's data should be of CharacterData type)
        """
        all_children = [
            (self.campaign.all_abilities, Ability, AbilityData),
            (self.campaign.all_calendars, Calendar, CalendarData),
            (self.campaign.all_characters, Character, CharacterData),
            (self.campaign.all_events, Event, EventData),
            (self.campaign.all_families, Family, FamilyData),
            (self.campaign.all_items, Item, ItemData),
            (self.campaign.all_journals, Journal, JournalData),
            (self.campaign.all_locations, Location, LocationData),
            (self.campaign.all_maps, Map, MapData),
            (self.campaign.all_notes, Note, NoteData),
            # (self.campaign.all_organisations, Organisation, OrganisationData), # Not working
            (self.campaign.all_quests, Quest, QuestData),
            (self.campaign.all_races, Race, RaceData),
            (self.campaign.all_tags, Tag, TagData),
            (self.campaign.all_timelines, Timeline, TimelineData)
        ]

        for all_child, ChildType, ChildDataType in all_children:
            with self.subTest(msg=f"get_all_{ChildType.__name__}'".lower()):
                with vcr.use_cassette((f'fixtures/vcr_cassettes/get_all/{ChildType.__name__}.yaml'), filter_headers=['authorization'],
                                      decode_compressed_response=True):
                    children = [e for e in all_child()[0]]
                    for child in children[:10]:
                        self.assertIsInstance(child, ChildType)
                        self.assertIsInstance(child.parent, Entity)
                        self.assertIsInstance(child.data, ChildDataType)
                    pass

    def test_create(self):
        """Tests the {child}.post() method and the data returned from the server
        The test takes sample data (provided by sample_data.py) for a set of children and attempts to post them
        to the server. The test then verifies that all the returned data is the same as the sample data
        NOTE: Not all child types are implemented yet.
        """
        children = [
            # (sample_data["location"], Location), # "entry" is not being returned correctly, it's always None.
            (sample_data["character"], Character),
            (sample_data["organisation"], Organisation),
            (sample_data["timeline"], Timeline),
            (sample_data["race"], Race),
            # (sample_data["family"], Family),  # Not working, getting a 404
            (sample_data["note"], Note),
            (sample_data["tag"], Tag),
            (sample_data["quest"], Quest),
            (sample_data["journal"], Journal),
            (sample_data["item"], Item),
            (sample_data["event"], Event),
            (sample_data["ability"], Ability),
            # (sample_data["calendar"], Calendar), # Skipping for now
        ]

        for data, ChildType in children:
            with self.subTest(msg=f"get_all_{ChildType.__name__}".lower()):
                with vcr.use_cassette((f'fixtures/vcr_cassettes/create/create_{ChildType.__name__}.yaml'.lower()),
                                      filter_headers=['authorization', 'x-req-url'],
                                      decode_compressed_response=True,
                                      ):
                    new = ChildType.from_json(self.campaign, content=data)
                    response = new.post()
                    new_data = response.json()['data']
                    retrieved_entity = self.campaign.get_entity(new_data['entity_id'])
                    retrieved_child = retrieved_entity.child.from_id(self.campaign, retrieved_entity.data.child_id)
                    for key, value in data.items():
                        self.assertEqual(retrieved_child.data.__dict__[key], value)
                    pass