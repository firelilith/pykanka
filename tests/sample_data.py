# Sample data for Kanka testing from the documentation at https://kanka.io/en-US/docs/1.0/
# All keys dealing with images have been removed
# All keys dealing with id have been removed (these can't be preserved in debugging)

sample_data = {
    # https://kanka.io/en-US/docs/1.0/locations
    "location":{
            "name": "Mordor",
            "entry": "<p>Lorem Ipsum.</p>",
            "has_custom_image": False,
            "is_private": True,
            "tags": [],
            "is_map_private": 0,
            "type": "Kingdom"
        },
    # https://kanka.io/en-US/docs/1.0/characters
    "character": {
        "name": "Jonathan Green",
        "entry": "<p>Lorem Ipsum.</p>",
        "has_custom_image": False,
        "is_private": True,
        "is_personality_visible": True,
        "is_template": False,
        "tags": [],
        "title": None,
        "age": "39",
        "sex": "Male",
        "pronouns": None,
        "race_id": 3,
        "type": None,
        "is_dead": True,
    },
    # https://kanka.io/en-US/docs/1.0/organisations
    "organisation":{
            "name": "Tiamat Cultists",
            "entry": "<p>Lorem Ipsum.</p>",
            "has_custom_image": False,
            "is_private": True,
            "tags": [],
            "type": "Kingdom",
            "members": []
        },
    #https://kanka.io/en-US/docs/1.0/timelines
    #Note: There is a "links" and "meta" return from this endpoint
    #It has been removed from this sample data
    "timeline":{
            "name": "Thaelian Timeline",
            "entry": "<p>Lorem Ipsum</p>",
            "has_custom_image": False,
            "is_private": False,
            "tags": [],
            "type": "Primary",
            "revert_order": False,
            # "eras": [
            #   {
            #     "name": "Anno Domani",
            #     "abbreviation": "AD",
            #     "start_year": 0,
            #     "end_year": None,
            #     "elements": []
            #   },
            #   {
            #     "name": "Before Christ",
            #     "abbreviation": "BC",
            #     "start_year": None,
            #     "end_year": 0,
            #     "elements": []
            #   }
            # ]
        },
    # https://kanka.io/en-US/docs/1.0/races
    "race":{
        "name": "Goblin",
        "entry": "<p>Lorem Ipsum.</p>",
        "has_custom_image": False,
        "is_private": True,
        "tags": [],
        "type": None
    },
    # https://kanka.io/en-US/docs/1.0/families
    "family":{
            "name": "Adams",
            "entry": "<p>Lorem Ipsum.</p>",
            "has_custom_image": False,
            "is_private": True,
            "tags": [],
            "location_id": 4,
            "type": "",
            "family_id": 2,
            "members": [
              "3"
            ]
        },
    # https://kanka.io/en-US/docs/1.0/notes
    "note": {
        "name": "Legends of the World",
        "entry": "<p>Lorem Ipsum.</p>",
        "has_custom_image": False,
        "is_private": True,
        "tags": [],
        "type": "Lore",
        "is_pinned": 0
    },
    #https://kanka.io/en-US/docs/1.0/maps
    "map":{
            "name": "Pelor's Map",
            "entry": "<p>Lorem Ipsum.</p>",
            "entry_parsed": "<p>Lorem Ipsum.</p>",
            "image": "{path}",
            "image_full": "{url}",
            "image_thumb": "{url}",
            "has_custom_image": False,
            "is_private": True,
            "entity_id": 164,
            "tags": [],
            "location_id": 4,
            "type": "Continent",
            "height": 1080,
            "width": 1920,
            "grid": 0,
            "min_zoom": -1,
            "max_zoom": 10,
            "initial_zoom": -1,
            "center_marker_id": None,
            "center_x": None,
            "center_y": None,
        },
    # https://kanka.io/en-US/docs/1.0/tags
    "tag":{
            "name": "Religion",
            "entry": "<p>Lorem Ipsum.</p>",
            "has_custom_image": False,
            "is_private": True,
            "tags": [],
            "type": "Lore",
            "colour": "green",
        },
    # https://kanka.io/en-US/docs/1.0/quests
    "quest":{
            "name": "Pelor's Quest",
            "entry": "<p>Lorem Ipsum.</p>",
            "has_custom_image": False,
            "is_private": True,
            "tags": [],
            # "date": "2020-04-20", # Not working, returns None
            "type": "Main",
            "is_completed": False,
        },
    # https://kanka.io/en-US/docs/1.0/journals
    "journal": {
        "name": "Session 2 - Descent into the Abyss",
        "entry": "<p>Lorem Ipsum</p>",
        "has_custom_image": False,
        "is_private": True,
        "tags": [],
        "date": "2017-11-02",
        "type": "Session"
    },
    # https://kanka.io/en-US/docs/1.0/items
    "item": {
        "name": "Spear",
        "entry": "<p>Lorem Ipsum.</p>",
        "has_custom_image": False,
        "is_private": True,
        "tags": [],
        "type": "Weapon",
        "price": "25 gp",
        "size": "1 lb."
    },
    # https://kanka.io/en-US/docs/1.0/events
    "event": {
        "name": "Battle of Hadish",
        "entry": "<p>Lorem Ipsum.</p>",
        "has_custom_image": False,
        "is_private": True,
        "tags": [],
        "date": "44-3-16",
        "type": "Battle"
    },
    # https://kanka.io/en-US/docs/1.0/abilities
    "ability":{
            "name": "Fireball",
            "entry": "<p>Lorem Ipsum.</p>",
            "has_custom_image": False,
            "is_private": True,
            "tags": [],
            "type": "3rd level",
            "charges": '3',
            "abilities": []
        },
    # https://kanka.io/en-US/docs/1.0/calendars
    # Note: There is a "links" and "meta" return from this endpoint
    # It has been removed from this sample data
    "calendar":{
            "name": "Georgian Calendar",
            "entry": "<p>Lorem Ipsum</p>",
            "has_custom_image": False,
            "is_private": False,
            "tags": [],
            "type": "Primary",
            "date": "311-2-3",
            "parameters": None,
            "months": [
              {
                "name": "January",
                "length": 31,
                "type": "standard"
              },
              {
                "name": "February",
                "length": 5,
                "type": "intercalary"
              }
            ],
            "start_offset": 0,
            "weekdays": [
                "Sul",
                "Mol",
                "Zol",
                "Wir",
                "Zor",
                "Far",
                "Sar"
            ],
            "years": {
                "299": "Year of Blood and Fire",
                "300": "Year of Water and Bone"
            },
            "seasons": [
              {
                  "name": "Spring",
                  "month": 1,
                  "day": 1
              },
              {
                  "name": "Summer",
                  "month": 4,
                  "day": 1
              }
            ],
            "moons": [
              {
                  "name": "Zarantyr",
                  "fullmoon": "13",
                  "offset": 0,
                  "colour": "aqua"
              },
              {
                  "name": "Olarune",
                  "fullmoon": "17",
                  "offset": 0,
                  "colour": "brown"
              }
            ],
            "suffix": "BC",
            "has_leap_year": True,
            "leap_year_amount": 4,
            "leap_year_month": 2,
            "leap_year_offset": 3,
            "leap_year_start": 233
        },
    # https://kanka.io/en-US/docs/1.0/entities
    "entity":{
        "name": "Redkeep",
        "type": "location",
        "tags": [],
        "is_private": False,
        "campaign_id": 1,
        "is_attributes_private": False,
        "tooltip": None,
    }
 }