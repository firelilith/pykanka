from pykanka import KankaClient
from pykanka.entities import Entity
from pykanka.child_types import Character, Event, Item, Journal, Note, Race
import vcr
from kanka_credentials import KANKA_TOKEN, CAMPAIGN_ID
from sample_data import sample_data

campaign = KankaClient(KANKA_TOKEN, CAMPAIGN_ID)

def before_record_request(request):
    if f"campaigns/{CAMPAIGN_ID}" in request.path:
        request.uri = request.uri.replace(f"campaigns/{CAMPAIGN_ID}", f"campaigns/1")
    if request.body and bytes(f'"campaign_id":{CAMPAIGN_ID}',"utf-8") in request.body:
        request.body = request.path.replace(bytes(f'"campaign_id":{CAMPAIGN_ID}',"utf-8"), '"campaign_id":1')
    return request

def before_record_response(response):
    if response.get('body').get('string') and bytes(f'"campaign_id":{CAMPAIGN_ID}',"utf-8") in response['body']['string']:
        response['body']['string'] = response['body']['string'].replace(bytes(f'"campaign_id":{CAMPAIGN_ID}',"utf-8"), b'"campaign_id":1')
    if response.get('headers').get('x-req-url') and f"{CAMPAIGN_ID}" in response['headers']['x-req-url'][0]:
        response['headers']['x-req-url'][0] = response['headers']['x-req-url'][0].replace(f"{CAMPAIGN_ID}","1")
        response['headers']['x-req-url'][0] = response['headers']['x-req-url'][0].replace(f"{CAMPAIGN_ID}","1")
    return response

def create_child(data, ChildType):
    with vcr.use_cassette((f'fixtures/vcr_cassettes/create/create_{ChildType.__name__}.yaml'.lower()),
                          filter_headers=['authorization', 'x-req-url'],
                          decode_compressed_response=True,
                            before_record_request=before_record_request,
                            before_record_response=before_record_response
                          ):
        new = ChildType.from_json(campaign, content=data)
        response = new.post()
        new_data = response.json()['data']
        retrieved_entity = campaign.get_entity(new_data['entity_id'])
        retrieved_child = retrieved_entity.child.from_id(campaign, retrieved_entity.data.child_id)
        for key, value in data.items():
            assert retrieved_child.data.__dict__[key] == value
        pass

children = [
    (sample_data["event"], Event),
    (sample_data["character"], Character),
    (sample_data["item"], Item),
    (sample_data["note"], Note),
    (sample_data["race"], Race),
    (sample_data["journal"], Journal)
]

for child_data, child_class in children:
    create_child(child_data, child_class)

pass