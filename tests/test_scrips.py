import logging
from pykanka import *

logging.basicConfig(level=logging.DEBUG)
logging.getLogger(__name__)

with open("secrets", "r") as f:
    token = f.readline()

client = CampaignClient(token=token, campaign_id=86924)

a = client._request("get", f"{client.campaign_api_url}entities/{2174620}?related=0").json()

b = client._request("get", f"{client.campaign_api_url}entities/{2174620}?related=1").json()

a_ent = Entity(a["data"])
b_ent = Entity(b["data"])

print(b_ent.child.__dict__)


