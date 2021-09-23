import random
import unittest
from pykanka import KankaClient
from pykanka.entities import Entity
from pykanka.child_types import *
# from pykanka.childdata_types import *
# from pykanka.child_types.Character import Character.Character.CharacterData as CharacterData
from sample_data import sample_data
import vcr

class TestPykanka(unittest.TestCase):
    def setUp(self) -> None:
        self.campaign = KankaClient("API_TOKEN", 1)

    def test_get_all(self):
        all_children = [
            (self.campaign.all_abilities, Ability),
            (self.campaign.all_calendars, Calendar),
            (self.campaign.all_characters, Character),
            (self.campaign.all_events, Event),
            (self.campaign.all_families, Family),
            (self.campaign.all_items, Item),
            (self.campaign.all_journals, Journal),
            (self.campaign.all_locations, Location),
            (self.campaign.all_maps, Map),
            (self.campaign.all_notes, Note),
            # (self.campaign.all_organisations, Organisation),
            (self.campaign.all_quests, Quest),
            (self.campaign.all_races, Race),
            (self.campaign.all_tags, Tag),
            (self.campaign.all_timelines, Timeline)
        ]

        for all_child, ChildType in all_children:
            # print(f'fixtures/vcr_cassettes/get_all/{ChildType.__name__}.yaml')
            with self.subTest(msg=f"get_all_{ChildType.__name__}'".lower()):
                with vcr.use_cassette((f'fixtures/vcr_cassettes/get_all/{ChildType.__name__}.yaml'), filter_headers=['authorization'],
                                      decode_compressed_response=True):
                    children = [e for e in all_child()[0]]
                    for child in children[:10]:
                        self.assertIsInstance(child, ChildType)
                        self.assertIsInstance(child.parent, Entity)
                        # self.assertIsInstance(timeline.data, TimelineData)
                    pass

    def test_create(self):
        children = [
            (sample_data["event"], Event),
            (sample_data["character"], Character),
            (sample_data["item"], Item),
            (sample_data["note"], Note),
            (sample_data["race"], Race),
            (sample_data["journal"], Journal)
        ]

        for data, ChildType in children:
            with self.subTest(msg=f"get_all_{ChildType.__name__}'".lower()):
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