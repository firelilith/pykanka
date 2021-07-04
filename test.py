from pykanka.api import KankaClient
import requests
import json
from pykanka import endpoints

token = "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIxIiwianRpIjoiOWMwYjU0YzIyYjUzOGM1OTg4N2YwYzY3OGMwMDQ3ZjBiNDhhYzgxY2Q3OGQyNzFjMThiODhkZDE3NDU5YmI3YWFkOGYwZGFkNWRhZWNlMjgiLCJpYXQiOjE2MjIzMDM0MTguNjM1ODc5LCJuYmYiOjE2MjIzMDM0MTguNjM1ODg4LCJleHAiOjE2NTM4Mzk0MTguNjI4NjA3LCJzdWIiOiI3OTgzMyIsInNjb3BlcyI6W119.BQ1MsqVC3dmRNRV3EIm-U_NCLSK-d999VmTcGNz9EBTThP7u7mOMo_gfYF99WyQqSYXgKfOn28MAXwKHmdElh9iVgcZrGuOJwWnEyjnoOg9c-qu99IAxsSm9oLN1ZjpYfnN_-g5O8cMgpGc6xQIm2f7orwWBqlSGvLJwMTjFOzC43OFxy-beJXWPDt39zXxocy3ZmVeML5rSd4dap24svPHq8JrtOGV6Sm2YIQzAEXxw4qrDEQjYY8wyIKthjuy7k_cQkUkWMPTuhkqyTnOkCdNYICvrkmj2SZ6MceYsgzj_5Asun9Qv1m9hcPYHQEdjdwKxinLcU3aXSOIRbXA3q0wFfh2L22NFJCKyKg8uT2Nf5s41rGOKgBq3wvIQspYqr6NX0TUmRuZ0OhKrEf77TZXMFYU7wD3-Htf8HYwWItznnmdvfv9VWtd-ug5Dmyybqp-vwMj9syXhm2uWj7ZHlSv-IH1GxSNemumQzwAbRZWxnH2E4W1t8ciFvawyGkjkcOpaNnANXHUabz-A_Cfmu4MMwlaAqzfA_frLb0Nq9R9RwSyTMOsxe9IzHiTUyZQTe8ZH7O-GFZCvxRLzxiyoYY8vfLT7vHhu-ZnTL5NPu4QLZ6YLZgWn83StO1Ox99Ms4rNAzaxnv-PIn7909WsAzXn4ip2l2UAiByK24QAn888"


headers = {
    "Authorization": token,
    "Accept": "application/json",
    "Content-Type": "application/json"
}

# a = KankaClient(token, campaign_id=70188)


def post_test():

    data = requests.get("https://kanka.io/api/1.0/campaigns/70188/locations/429848", headers=headers).json()["data"]
    print(data)

    new_data = {}

    for key in data:
        if key in ["name", "type", "parent_location_id", "tags", "is_private", "image", "image_url", "map_url", "is_map_private"]:
            if data[key]:
                new_data[key] = data[key]

    new_data["name"] = "New Imeron"
    print(new_data)

    print(a := requests.post("https://kanka.io/api/1.0/campaigns/70188/locations", headers=headers, data=json.dumps(new_data)))

    print(a.text)


def post_entity_test():

    a = requests.patch("https://kanka.io/api/1.0/campaigns/70188/entities/1797792", headers=headers, data=json.dumps({"name": "test"}))
    print(a)
    print(a.text)


#post_entity_test()

a = KankaClient(token, campaign="Alath")

b = endpoints.Entity.build_from_json(client=a, json_dict={"name": "test"})

print(b.entity.name)

#kanka = KankaClient(token, campaign="Alath")
#print(kanka.location.entity.name)


with open("entity.json", "w") as f:
    json.dump(requests.get("https://kanka.io/api/1.0/campaigns/70188/entities/1797792", headers=headers).json(), f, indent="    ")
