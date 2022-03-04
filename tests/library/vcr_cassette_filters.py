from .kanka_credentials import CAMPAIGN_ID, KANKA_TOKEN

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