import logging
import requests
from pykanka import *

logging.basicConfig(level=logging.DEBUG)
logging.getLogger(__name__)

with open("secrets", "r") as f:
    token = f.readline()

image = requests.get(url="https://picsum.photos/512", stream=True).raw
print(image)

client = CampaignClient(campaign_id=86924, token=token)
ent = client.create_entity("character", name="Frederik")
client.upload_image(ent, image_file=image)

