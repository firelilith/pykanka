import pykanka.child_types
from pykanka import KankaClient
from pykanka.entities import Entity
from pykanka.child_types import GenericChildType, Character, Event, Item, Journal, Note, Race
import vcr
from kanka_credentials import KANKA_TOKEN, CAMPAIGN_ID
from sample_data import sample_data

def before_record_request(request):
    """A callback to manipulate the HTTP request before adding it to the cassette. This one removes references to
    the actual Kanka ID used to generate the cassette and replaces it with "1", which is the sample campaign ID.

    :param request: HTTP response received during cassette generation
    """
    if f"campaigns/{CAMPAIGN_ID}" in request.path:
        request.uri = request.uri.replace(f"campaigns/{CAMPAIGN_ID}", f"campaigns/1")
    if request.body and bytes(f'"campaign_id":{CAMPAIGN_ID}',"utf-8") in request.body:
        request.body = request.path.replace(bytes(f'"campaign_id":{CAMPAIGN_ID}',"utf-8"), '"campaign_id":1')
    return request

def before_record_response(response):
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

def create_child(data: dict, ChildType, cassette_dir: str = "fixtures/vcr_cassettes/create" ):
    """Generate cassette files for creating Kanka children objects.

      :param data: Dictionary data for the object
      :param ChildType: Class for the child time
      """
    with vcr.use_cassette((f'{cassette_dir}/create_{ChildType.__name__}.yaml'.lower()),
                          filter_headers=[
                              'authorization', # Filters out Kanka Token in HTTP header
                              'x-req-url' # Should filter out 'x-req-url' which contains the campaign ID. Broken...
                          ],
                          decode_compressed_response=True, # Output decoded strings rather than binary data in cassette
                            before_record_request=before_record_request, # Filter refs to campaign ID in request
                            before_record_response=before_record_response # Filter refs to campaign ID in response
                          ):
        # Create new child object
        new = ChildType.from_json(campaign, content=data)
        # Post the new child object
        response = new.post()
        # Get the data from the post response
        new_data = response.json()['data']
        # Retrieve entity for what is now in the server
        retrieved_entity = campaign.get_entity(new_data['entity_id'])
        # Retrieve child from entity.
        retrieved_child = retrieved_entity.child.from_id(campaign, retrieved_entity.data.child_id)
        # Assert what we inputted is what came back from the server
        for key, value in data.items():
            assert retrieved_child.data.__dict__[key] == value
        pass

if __name__ == '__main__':
    # Use this script to generate VCR.py "cassettes" for use in unit testing. More info at https://vcrpy.readthedocs.io
    # To run, you will have to provide a valid Kanka token (https://kanka.io/en-US/docs/1.0/setup) and campaign id.
    # These values should be stored in  kanka_credentials.py as variables KANKA_TOKEN and CAMPAIGN_ID
    # The script will strip the token and id from the cassettes.

    campaign = KankaClient(KANKA_TOKEN, CAMPAIGN_ID)
    children = [
        (sample_data["event"], Event),
        (sample_data["character"], Character),
        (sample_data["item"], Item),
        (sample_data["note"], Note),
        (sample_data["race"], Race),
        (sample_data["journal"], Journal)
    ]
    entities = [
        (sample_data['entity'], Entity)
    ]
    # Generate cassettes for posting Kanka children objects.
    for child_data, child_class in children:
        create_child(child_data, child_class)
        pass

    # Generate cassettes for posting entities objects.
    for entity_data, entity_class in entities:
        # Commented out for now, because it doesn't work. There is an error for unexpected keyword 'parent'
        # and error that there is no method 'post'. This doesn't seem right.
        # create_child(entity_data, entity_class)
        pass
