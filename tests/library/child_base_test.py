from pykanka import KankaClient
from pykanka.entities import Entity
from pykanka.child_types import *
from .vcr_cassette_filters import remove_campaign_id_from_request, remove_campaign_id_from_response
from .kanka_credentials import KANKA_TOKEN, CAMPAIGN_ID
from vcr_unittest import VCRTestCase
import unittest

class ChildBaseTest(VCRTestCase):
    def _get_vcr(self, **kwargs):
        myvcr = super(ChildBaseTest, self)._get_vcr(**kwargs)
        myvcr.before_record_request = remove_campaign_id_from_request # Filter refs to campaign ID in request
        myvcr.before_record_response = remove_campaign_id_from_response # Filter refs to campaign ID in response
        myvcr.decode_compressed_response = True # Output decoded strings rather than binary data in cassette
        myvcr.filter_headers = [
            'authorization', # Filters out Kanka Token in HTTP header
            'x-req-url' # Should filter out 'x-req-url' which contains the campaign ID. Broken...
        ]
        return myvcr

    @classmethod
    def setUpClass(cls):
        if cls.__name__ == ChildBaseTest.__name__:
            raise unittest.SkipTest("Base class")
        super().setUpClass()

    def setUp(self) -> None:
        """Set up the clients
        If using cassettes, there is no need for a working token, as the authorization header is filtered out.
        To generate new cassettes, a working token and writable campaign ID is required.
        Campaign ID 1 is the sample campaign on Kanka. It can be read, but not edited. There is much pre-generated public
        data here, so it makes sense to include this as part of the tests.
        """
        super().setUp()
        self.read_campaign = KankaClient(KANKA_TOKEN, 1)
        self.write_campaign = KankaClient(KANKA_TOKEN, CAMPAIGN_ID, cache_duration=0)
        self.update_data = {
            "name": f"{self.data['name']} (revised)",
            "entry": f"{self.data['entry']}<p>Dolor Sit Amet.</p>"
        }
        pass

    def test_get_all_of_type(self):
        """Tests the client.all_{child} method and the children returned
        The test gets all of each child type, then surveys the first ten objects.
        For each sampled child the test verifies that:
            The child is of the expected type (a character should be of Character type)
            The child's parent is of Entity type
            The child's data is the expected type (a character's data should be of CharacterData type)"""
        children = [e for e in self.get_all()[0]]
        for child in children[:10]:
            with self.subTest("ChildType"):
                self.assertIsInstance(child, self.ChildType)
            with self.subTest("Entity"):
                self.assertIsInstance(child.parent, Entity)
            with self.subTest("ChildDataType"):
                self.assertIsInstance(child.data, self.ChildDataType)
        pass

    def test_create_update_delete(self):
        """Tests the {child}.post(), {child}.patch(), and {child}.delete() methods and the data returned from the server
            The test takes provided data and attempts to post them to the provided client
            The test then verifies that all the returned data is the same as the sample data
                    """
        with self.subTest(functionality=f"create"):
            """Tests the {child}.post() method and the data returned from the server
            The test takes provided data and attempts to post them to the provided client
            The test then verifies that all the returned data is the same as the sample data
            """
            new = self.ChildType.from_json(self.write_campaign, content=self.data)
            response = new.post()
            self.assertEqual(response.status_code, 201,
                             f"Expected {201}, response code {response.status_code} returned. {response.reason}")
            new_data = response.json()['data']
            retrieved_entity = self.write_campaign.get_entity(new_data['entity_id'])
            retrieved_child = retrieved_entity.child.from_id(self.write_campaign, retrieved_entity.data.child_id)
            for key, value in self.data.items():
                with self.subTest(key=key):
                    self.assertEqual(retrieved_child.data.__dict__[key], value,
                                     f"Result: {retrieved_child.data.__dict__[key]}, Expected: {value}")

        with self.subTest(functionality=f"update"):
            """Tests the {child}.patch() method and the data returned from the server
            The test takes provided data and attempts to patch them to the existing child
            The test then verifies that all the returned data is the same as the sample data
            """

            response = retrieved_child.patch(json_data=json.dumps(self.update_data))
            self.assertEqual(response.status_code, 200,
                             f"Expected {200}, response code {response.status_code} returned. {response.reason}")
            new_data = response.json()['data']
            self.write_campaign._cache = {}  # TODO Cache should not have to be reset like this.
            retrieved_entity = self.write_campaign.get_entity(new_data['entity_id'])
            retrieved_child = retrieved_entity.child.from_id(self.write_campaign, retrieved_entity.data.child_id)
            for key, value in self.update_data.items():
                with self.subTest(key=key):
                    self.assertEqual(retrieved_child.data.__dict__[key], value,
                                     f"Result: {retrieved_child.data.__dict__[key]}, Expected: {value}")
            pass

        with self.subTest(functionality=f"delete"):
            """Tests the {child}.delete() method"""
            existing_entity_id = retrieved_child.data.entity_id
            response = retrieved_child.delete()
            self.assertEqual(response.status_code, 204,
                             f"Expected {204}, response code {response.status_code} returned. {response.text}")