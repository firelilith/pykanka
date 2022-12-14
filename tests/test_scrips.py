import logging
from pykanka import *

logging.basicConfig(level=logging.DEBUG)
logging.getLogger(__name__)

with open("secrets", "r") as f:
    token = f.readline()

client = CampaignClient(campaign_id=86924, token=token)
client.create_entity("character", name="Frederik", image_url="https://picsum.photos/512")

