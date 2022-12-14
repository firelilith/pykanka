import logging
from pykanka import *

logging.basicConfig(level=logging.DEBUG)
logging.getLogger(__name__)

with open("secrets", "r") as f:
    token = f.readline()

client = CampaignClient(token=token, campaign_id=86924)

a = client.create_entity("character", name="sam the destroyer")
print(a)
