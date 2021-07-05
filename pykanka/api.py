from pykanka.exceptions import *
from pykanka.endpoints import *
import requests


class KankaClientOld:
    def __init__(self, api_token, campaign=None, campaign_id=None):

        if not (campaign or campaign_id):
            raise Exception("no campaign supplied")

        self.headers = {
            "Authorization": api_token,
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        if campaign_id:
            self.campaign_id = campaign_id
        else:
            self.campaign_id = self._get_campaign_id(campaign)

        self.base_url = f"https://kanka.io/api/1.0/campaigns/{campaign_id}"

        self.location = Location(self)

    def _get_campaigns(self):
        campaigns = requests.get("https://kanka.io/api/1.0/campaigns/", headers=self.headers)
        return campaigns.json()

    def _get_campaign_id(self, name):
        campaigns = self._get_campaigns()

        for campaign in campaigns["data"]:
            if campaign["name"].lower() == name.lower():
                campaign_id = campaign["id"]
                return campaign_id

        raise CampaignError(f"No campaign of the name '{name}' found")

