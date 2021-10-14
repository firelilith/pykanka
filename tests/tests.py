import unittest
from typing import Callable, List, Type
from pykanka import KankaClient
from pykanka.entities import Entity
from pykanka.child_types import *
from pykanka.childdata_types import *
import vcr
from kanka_credentials import KANKA_TOKEN, CAMPAIGN_ID
CASSETTE_DIR = "fixtures/vcr_cassettes"

def remove_campaign_id_from_request(request):
    """A callback to manipulate the HTTP request before adding it to the cassette. This one removes references to
    the actual Kanka ID used to generate the cassette and replaces it with "1", which is the sample campaign ID.

    :param request: HTTP response received during cassette generation
    """
    if f"campaigns/{CAMPAIGN_ID}" in request.path:
        request.uri = request.uri.replace(f"campaigns/{CAMPAIGN_ID}", f"campaigns/1")
    if request.body and bytes(f'"campaign_id":{CAMPAIGN_ID}',"utf-8") in request.body:
        request.body = request.path.replace(bytes(f'"campaign_id":{CAMPAIGN_ID}',"utf-8"), '"campaign_id":1')
    return request

def remove_campaign_id_from_response(response):
    """A callback to manipulate the HTTP response before adding it to the cassette. This one removes references to
    the actually Kanka ID used to generate the cassette and replaces it with "1", which is the sample campaign ID.

    :param response: HTTP response received during cassette generation
    """
    # Remove Kanka campaign references in HTTP response body
    if response.get('body').get('string') and bytes(f'"campaign_id":{CAMPAIGN_ID}',"utf-8") in response['body']['string']:
        response['body']['string'] = response['body']['string'].replace(bytes(f'"campaign_id":{CAMPAIGN_ID}',"utf-8"), b'"campaign_id":1')
    # Remove Kanka campaign references in 'x-req-url' in HTTP response header
    if response.get('headers').get('x-req-url') and f"{CAMPAIGN_ID}" in response['headers']['x-req-url'][0]:
        response['headers']['x-req-url'][0] = response['headers']['x-req-url'][0].replace(f"{CAMPAIGN_ID}","1")
    return response

cassette_kwargs = dict(
    filter_headers=[
        'authorization', # Filters out Kanka Token in HTTP header
        'x-req-url' # Should filter out 'x-req-url' which contains the campaign ID. Broken...
    ],
    decode_compressed_response=True, # Output decoded strings rather than binary data in cassette
    before_record_request=remove_campaign_id_from_request, # Filter refs to campaign ID in request
    before_record_response=remove_campaign_id_from_response # Filter refs to campaign ID in response
)
class TestPykanka(unittest.TestCase):
    """Tests for pykanka module"""

    def setUp(self) -> None:
        """Set up the clients
        If using cassettes, there is no need for a working token, as the authorization header is filtered out.
        To generate new cassettes, a working token and writable campaign ID is required.
        Campaign ID 1 is the sample campaign on Kanka. It can be read, but not edited. There is much pre-generated public
        data here, so it makes sense to include this as part of the tests.
        """
        self.read_campaign = KankaClient(KANKA_TOKEN, 1)
        self.write_campaign = KankaClient(KANKA_TOKEN, CAMPAIGN_ID, cache_duration=0)
        pass

    def _get_and_test_all_of_childtype(self,
                       all_child: Callable[[], List[GenericChildType]],
                       ChildType: Type[GenericChildType],
                       ChildDataType: Type[GenericChildData]) -> None:
        """Helper function that tests the client.all_{child} method and the children returned
        The test gets all of each child type, then surveys the first ten objects.
        For each sampled child the test verifies that:
            The child is of the expected type (a character should be of Character type)
            The child's parent is of Entity type
            The child's data is the expected type (a character's data should be of CharacterData type)
        """
        children = [e for e in all_child()]
        for child in children[:10]:
            with self.subTest("ChildType"):
                self.assertIsInstance(child, ChildType)
            with self.subTest("Entity"):
                self.assertIsInstance(child.parent, Entity)
            with self.subTest("ChildDataType"):
                self.assertIsInstance(child.data, ChildDataType)
        pass

    def _create_and_test_new_of_childtype(self, client: KankaClient, ChildType: Type[GenericChildType], data: dict) -> GenericChildType:
        """Tests the {child}.post() method and the data returned from the server
                The test takes provided data and attempts to post them to the provided client
                The test then verifies that all the returned data is the same as the sample data
                """
        new = ChildType.from_json(client, content=data)
        response = new.post()
        new_data = response.json()['data']
        retrieved_entity = client.get_entity(new_data['entity_id'])
        retrieved_child = retrieved_entity.child.from_id(client, retrieved_entity.data.child_id)
        for key, value in data.items():
            with self.subTest(key=key):
                self.assertEqual(retrieved_child.data.__dict__[key], value, f"Result: {retrieved_child.data.__dict__[key]}, Expected: {value}")
        pass

        return retrieved_child

    def _update_and_test_existing_of_childtype(self, client, existing_child: GenericChildType, update_data: dict) -> GenericChildType:
        """Tests the {child}.patch() method and the data returned from the server
                        The test takes provided data and attempts to patch them to the existing child
                        The test then verifies that all the returned data is the same as the sample data
                        """
        response = existing_child.patch(json_data=json.dumps(update_data))
        new_data = response.json()['data']
        self.write_campaign._cache={} #TODO Cache should not have to be reset like this.
        retrieved_entity = client.get_entity(new_data['entity_id'])
        retrieved_child = retrieved_entity.child.from_id(client, retrieved_entity.data.child_id)
        for key, value in update_data.items():
            with self.subTest(key=key):
                self.assertEqual(retrieved_child.data.__dict__[key], value, f"Result: {retrieved_child.data.__dict__[key]}, Expected: {value}")
        pass

        return retrieved_child

    def _delete_and_test_existing_of_childtype(self, client, existing_child: GenericChildType) -> None:
        """Tests the {child}.delete() method"""
        existing_entity_id = existing_child.data.entity_id
        response = existing_child.delete()
        self.assertEqual(response.status_code, 204, f"Expected {204}, response code {response.status_code} returned. {response.text}")

    @vcr.use_cassette(f'{CASSETTE_DIR}/location.yaml', **cassette_kwargs)
    def test_location(self):
        with self.subTest(functionality=f"get all"):
            self._get_and_test_all_of_childtype(self.read_campaign.all_locations,
                                                Location,
                                                LocationData)
        with self.subTest(functionality=f"create"):
            # Sample data from Kanka API documentation, with some keys removed.
            # https://kanka.io/en-US/docs/1.0/locations
            data = {
                "name": "Mordor",
                "entry": "<p>Lorem Ipsum.</p>",
                "has_custom_image": False,
                "is_private": True,
                "tags": [],
                "is_map_private": 0,
                "type": "Kingdom"
            }
            new_child = self._create_and_test_new_of_childtype(self.write_campaign, Location, data)
        with self.subTest(functionality=f"update"):
            update_data = {
                "name": f"{data['name']} (revised)",
                "entry": f"{data['entry']}<p>Dolor Sit Amet.</p>"
            }
            updated_child = self._update_and_test_existing_of_childtype(self.write_campaign, new_child, update_data)

        # with self.subTest(functionality=f"delete"):
        #     self._delete_and_test_existing_of_childtype(self.write_campaign, new_child)
        pass

    @vcr.use_cassette(f'{CASSETTE_DIR}/character.yaml', **cassette_kwargs)
    def test_character(self):
        with self.subTest(functionality=f"get all"):
            self._get_and_test_all_of_childtype(self.read_campaign.all_characters,
                                                Character,
                                                CharacterData)
        with self.subTest():
            with self.subTest(functionality=f"create"):
                # Sample data from Kanka API documentation, with some keys removed.
                # https://kanka.io/en-US/docs/1.0/characters
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
                new_child = self._create_and_test_new_of_childtype(self.write_campaign, Character, data)
            with self.subTest(functionality=f"update"):
                update_data = {
                    "name": f"{data['name']} (revised)",
                    "entry": f"{data['entry']}<p>Dolor Sit Amet.</p>"
                }
                updated_child = self._update_and_test_existing_of_childtype(self.write_campaign, new_child,update_data)

            with self.subTest(functionality=f"delete"):
                self._delete_and_test_existing_of_childtype(self.write_campaign, new_child)

    @vcr.use_cassette(f'{CASSETTE_DIR}/organisation.yaml', **cassette_kwargs)
    def test_organisation(self):
        with self.subTest(functionality=f"get all"):
            self._get_and_test_all_of_childtype(self.read_campaign.all_organisations,
                                                Organisation,
                                                OrganisationData)
        with self.subTest(functionality=f"create"):
            # Sample data from Kanka API documentation, with some keys removed.
            # https://kanka.io/en-US/docs/1.0/organisations
            data = {
                "name": "Tiamat Cultists",
                "entry": "<p>Lorem Ipsum.</p>",
                "has_custom_image": False,
                "is_private": True,
                "tags": [],
                "type": "Kingdom",
                "members": []
            }
            new_child = self._create_and_test_new_of_childtype(self.write_campaign, Organisation, data)
        with self.subTest(functionality=f"update"):
            update_data = {
                "name": f"{data['name']} (revised)",
                "entry": f"{data['entry']}<p>Dolor Sit Amet.</p>"
            }
            updated_child = self._update_and_test_existing_of_childtype(self.write_campaign, new_child, update_data)

        with self.subTest(functionality=f"delete"):
            self._delete_and_test_existing_of_childtype(self.write_campaign, new_child)

    @vcr.use_cassette(f'{CASSETTE_DIR}/timeline.yaml', **cassette_kwargs)
    def test_timeline(self):
        with self.subTest(functionality=f"get all"):
            self._get_and_test_all_of_childtype(self.read_campaign.all_timelines,
                                                Timeline,
                                                TimelineData)
        with self.subTest(functionality=f"create"):
            # Sample data from Kanka API documentation, with some keys removed.
            # https://kanka.io/en-US/docs/1.0/timelines
            # Note: There is a "links" and "meta" return from this endpoint
            # It has been removed from this sample data
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
            new_child = self._create_and_test_new_of_childtype(self.write_campaign, Timeline, data)
        with self.subTest(functionality=f"update"):
            update_data = {
                "name": f"{data['name']} (revised)",
                "entry": f"{data['entry']}<p>Dolor Sit Amet.</p>"
            }
            updated_child = self._update_and_test_existing_of_childtype(self.write_campaign, new_child, update_data)

        with self.subTest(functionality=f"delete"):
            self._delete_and_test_existing_of_childtype(self.write_campaign, new_child)

    @vcr.use_cassette(f'{CASSETTE_DIR}/race.yaml', **cassette_kwargs)
    def test_race(self):
        with self.subTest(functionality=f"get all"):
            self._get_and_test_all_of_childtype(self.read_campaign.all_races,
                                                Race,
                                                RaceData)
        with self.subTest(functionality=f"create"):
            # Sample data from Kanka API documentation, with some keys removed.
            # https://kanka.io/en-US/docs/1.0/races
            data = {
                "name": "Goblin",
                "entry": "<p>Lorem Ipsum.</p>",
                "has_custom_image": False,
                "is_private": True,
                "tags": [],
                "type": None
            }
            new_child = self._create_and_test_new_of_childtype(self.write_campaign, Race, data)
        with self.subTest(functionality=f"update"):
            update_data = {
                "name": f"{data['name']} (revised)",
                "entry": f"{data['entry']}<p>Dolor Sit Amet.</p>"
            }
            updated_child = self._update_and_test_existing_of_childtype(self.write_campaign, new_child, update_data)

        with self.subTest(functionality=f"delete"):
            self._delete_and_test_existing_of_childtype(self.write_campaign, new_child)

    @vcr.use_cassette(f'{CASSETTE_DIR}/family.yaml', **cassette_kwargs)
    def test_family(self):
        with self.subTest(functionality=f"get all"):
            self._get_and_test_all_of_childtype(self.read_campaign.all_families,
                                                Family,
                                                FamilyData)
        with self.subTest(functionality=f"create"):
            # Sample data from Kanka API documentation, with some keys removed.
            # https://kanka.io/en-US/docs/1.0/families
            data = {
                "name": "Adams",
                "entry": "<p>Lorem Ipsum.</p>",
                "has_custom_image": False,
                "is_private": True,
                "tags": [],
                "type": None,
            }
            new_child = self._create_and_test_new_of_childtype(self.write_campaign, Family, data)
        with self.subTest(functionality=f"update"):
            update_data = {
                "name": f"{data['name']} (revised)",
                "entry": f"{data['entry']}<p>Dolor Sit Amet.</p>"
            }
            updated_child = self._update_and_test_existing_of_childtype(self.write_campaign, new_child, update_data)

        with self.subTest(functionality=f"delete"):
            self._delete_and_test_existing_of_childtype(self.write_campaign, new_child)

    @vcr.use_cassette(f'{CASSETTE_DIR}/note.yaml', **cassette_kwargs)
    def test_note(self):
        with self.subTest(functionality=f"get all"):
            self._get_and_test_all_of_childtype(self.read_campaign.all_notes,
                                                Note,
                                                NoteData)
        with self.subTest(functionality=f"create"):
            # Sample data from Kanka API documentation, with some keys removed.
            # https://kanka.io/en-US/docs/1.0/notes
            data = {
                "name": "Legends of the World",
                "entry": "<p>Lorem Ipsum.</p>",
                "has_custom_image": False,
                "is_private": True,
                "tags": [],
                "type": "Lore",
                "is_pinned": 0
            }
            new_child = self._create_and_test_new_of_childtype(self.write_campaign, Note, data)
        with self.subTest(functionality=f"update"):
            update_data = {
                "name": f"{data['name']} (revised)",
                "entry": f"{data['entry']}<p>Dolor Sit Amet.</p>"
            }
            updated_child = self._update_and_test_existing_of_childtype(self.write_campaign, new_child, update_data)

        with self.subTest(functionality=f"delete"):
            self._delete_and_test_existing_of_childtype(self.write_campaign, new_child)

    @vcr.use_cassette(f'{CASSETTE_DIR}/tag.yaml', **cassette_kwargs)
    def test_tag(self):
        with self.subTest(functionality=f"get all"):
            self._get_and_test_all_of_childtype(self.read_campaign.all_tags,
                                                Tag,
                                                TagData)
        with self.subTest(functionality=f"create"):
            # Sample data from Kanka API documentation, with some keys removed.
            # https://kanka.io/en-US/docs/1.0/tags
            data = {
                "name": "Religion",
                "entry": "<p>Lorem Ipsum.</p>",
                "has_custom_image": False,
                "is_private": True,
                "tags": [],
                "type": "Lore",
                "colour": "green",
            }
            new_child = self._create_and_test_new_of_childtype(self.write_campaign, Tag, data)
        with self.subTest(functionality=f"update"):
            update_data = {
                "name": f"{data['name']} (revised)",
                "entry": f"{data['entry']}<p>Dolor Sit Amet.</p>"
            }
            updated_child = self._update_and_test_existing_of_childtype(self.write_campaign, new_child, update_data)

        with self.subTest(functionality=f"delete"):
            self._delete_and_test_existing_of_childtype(self.write_campaign, new_child)

    @vcr.use_cassette(f'{CASSETTE_DIR}/quest.yaml', **cassette_kwargs)
    def test_quest(self):
        with self.subTest(functionality=f"get all"):
            self._get_and_test_all_of_childtype(self.read_campaign.all_quests,
                                                Quest,
                                                QuestData)
        with self.subTest(functionality=f"create"):
            # Sample data from Kanka API documentation, with some keys removed.
            # https://kanka.io/en-US/docs/1.0/quests
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
            new_child = self._create_and_test_new_of_childtype(self.write_campaign, Quest, data)
        with self.subTest(functionality=f"update"):
            update_data = {
                "name": f"{data['name']} (revised)",
                "entry": f"{data['entry']}<p>Dolor Sit Amet.</p>"
            }
            updated_child = self._update_and_test_existing_of_childtype(self.write_campaign, new_child, update_data)

        with self.subTest(functionality=f"delete"):
            self._delete_and_test_existing_of_childtype(self.write_campaign, new_child)

    @vcr.use_cassette(f'{CASSETTE_DIR}/journal.yaml', **cassette_kwargs)
    def test_journal(self):
        with self.subTest(functionality=f"get all"):
            self._get_and_test_all_of_childtype(self.read_campaign.all_journals,
                                                Journal,
                                                JournalData)
        with self.subTest(functionality=f"create"):
            # Sample data from Kanka API documentation, with some keys removed.
            # https://kanka.io/en-US/docs/1.0/journals
            data = {
                "name": "Session 2 - Descent into the Abyss",
                "entry": "<p>Lorem Ipsum</p>",
                "has_custom_image": False,
                "is_private": True,
                "tags": [],
                "date": "2017-11-02",
                "type": "Session"
            }
            new_child = self._create_and_test_new_of_childtype(self.write_campaign, Journal, data)
        with self.subTest(functionality=f"update"):
            update_data = {
                "name": f"{data['name']} (revised)",
                "entry": f"{data['entry']}<p>Dolor Sit Amet.</p>"
            }
            updated_child = self._update_and_test_existing_of_childtype(self.write_campaign, new_child, update_data)

        with self.subTest(functionality=f"delete"):
            self._delete_and_test_existing_of_childtype(self.write_campaign, new_child)

    @vcr.use_cassette(f'{CASSETTE_DIR}/item.yaml', **cassette_kwargs)
    def test_item(self):
        with self.subTest(functionality=f"get all"):
            self._get_and_test_all_of_childtype(self.read_campaign.all_items,
                                                Item,
                                                ItemData)
        with self.subTest(functionality=f"create"):
            # Sample data from Kanka API documentation, with some keys removed.
            # https://kanka.io/en-US/docs/1.0/items
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
            new_child = self._create_and_test_new_of_childtype(self.write_campaign, Item, data)
        with self.subTest(functionality=f"update"):
            update_data = {
                "name": f"{data['name']} (revised)",
                "entry": f"{data['entry']}<p>Dolor Sit Amet.</p>"
            }
            updated_child = self._update_and_test_existing_of_childtype(self.write_campaign, new_child, update_data)

        with self.subTest(functionality=f"delete"):
            self._delete_and_test_existing_of_childtype(self.write_campaign, new_child)

    @vcr.use_cassette(f'{CASSETTE_DIR}/event.yaml', **cassette_kwargs)
    def test_event(self):
        with self.subTest(functionality=f"get all"):
            self._get_and_test_all_of_childtype(self.read_campaign.all_events,
                                                Event,
                                                EventData)
        with self.subTest(functionality=f"create"):
            # Sample data from Kanka API documentation, with some keys removed.
            # https://kanka.io/en-US/docs/1.0/events
            data = {
                "name": "Battle of Hadish",
                "entry": "<p>Lorem Ipsum.</p>",
                "has_custom_image": False,
                "is_private": True,
                "tags": [],
                "date": "44-3-16",
                "type": "Battle"
            }
            new_child = self._create_and_test_new_of_childtype(self.write_campaign, Event, data)
        with self.subTest(functionality=f"update"):
            update_data = {
                "name": f"{data['name']} (revised)",
                "entry": f"{data['entry']}<p>Dolor Sit Amet.</p>"
            }
            updated_child = self._update_and_test_existing_of_childtype(self.write_campaign, new_child, update_data)

        with self.subTest(functionality=f"delete"):
            self._delete_and_test_existing_of_childtype(self.write_campaign, new_child)

    @vcr.use_cassette(f'{CASSETTE_DIR}/ability.yaml', **cassette_kwargs)
    def test_ability(self):
        with self.subTest(functionality=f"get all"):
            self._get_and_test_all_of_childtype(self.read_campaign.all_abilities,
                                                Ability,
                                                AbilityData)
        with self.subTest(functionality=f"create"):
            # Sample data from Kanka API documentation, with some keys removed.
            # https://kanka.io/en-US/docs/1.0/abilities
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
            new_child = self._create_and_test_new_of_childtype(self.write_campaign, Ability, data)
        with self.subTest(functionality=f"update"):
            update_data = {
                "name": f"{data['name']} (revised)",
                "entry": f"{data['entry']}<p>Dolor Sit Amet.</p>"
            }
            updated_child = self._update_and_test_existing_of_childtype(self.write_campaign, new_child, update_data)

        with self.subTest(functionality=f"delete"):
            self._delete_and_test_existing_of_childtype(self.write_campaign, new_child)

    @vcr.use_cassette(f'{CASSETTE_DIR}/calendar.yaml', **cassette_kwargs)
    def test_calendar(self):
        #TODO Incomplete
        with self.subTest(functionality=f"get all"):
            self._get_and_test_all_of_childtype(self.read_campaign.all_abilities,
                                                Ability,
                                                AbilityData)
        # https://kanka.io/en-US/docs/1.0/calendars
        # Note: There is a "links" and "meta" return from this endpoint
        # It has been removed from this sample data
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
        pass

    @vcr.use_cassette(f'{CASSETTE_DIR}/menulink.yaml', **cassette_kwargs)
    def test_menulink(self):
        with self.subTest(functionality=f"get all"):
            self._get_and_test_all_of_childtype(self.read_campaign.all_menulinks,
                                                MenuLink,
                                                MenuLinkData)
        with self.subTest(functionality=f"create"):
            # Sample data from Kanka API documentation, with some keys removed.
            # https://kanka.io/en-US/docs/1.0/menu-links
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
            new_child = self._create_and_test_new_of_childtype(self.write_campaign, MenuLink, data)
        with self.subTest(functionality=f"update"):
            update_data = {
                "name": f"{data['name']} (revised)"
            }
            updated_child = self._update_and_test_existing_of_childtype(self.write_campaign, new_child, update_data)

        with self.subTest(functionality=f"delete"):
            self._delete_and_test_existing_of_childtype(self.write_campaign, new_child)

    @vcr.use_cassette(f'{CASSETTE_DIR}/dashboardwidget.yaml', **cassette_kwargs)
    def test_dashboardwidget(self):
        with self.subTest(functionality=f"get all"):
            self._get_and_test_all_of_childtype(self.read_campaign.all_dashboardwidgets,
                                                DashboardWidget,
                                                DashboardWidgetData)
        with self.subTest(functionality=f"create"):
            # Sample data from Kanka API documentation, with some keys removed.
            # https://kanka.io/en-US/docs/1.0/dashboard-widgets
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
            new_child = self._create_and_test_new_of_childtype(self.write_campaign, DashboardWidget, data)
        with self.subTest(functionality=f"update"):
            update_data = {
                "position": 1
            }
            updated_child = self._update_and_test_existing_of_childtype(self.write_campaign, new_child, update_data)

        with self.subTest(functionality=f"delete"):
            self._delete_and_test_existing_of_childtype(self.write_campaign, new_child)