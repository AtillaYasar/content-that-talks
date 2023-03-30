# currently refactoring this module to be more modular and easier to use, and improving docs.

import os, sys

## make root available for import
with open('root_path.txt', 'r') as f:
    root_path = f.read()
sys.path.append(root_path)

from secrets import elevenlabs_key
import requests, json, time, base64

def generate_and_save(voice_id, string, output_path):
    """Uses the elevenlabs tts api to convert a string to an audio file. Returns the path to the audio file."""

    # payload and headers for api request
    data = {
      "text": string,
      "voice_settings": {
        "stability": 0.50,
        "similarity_boost": 0.10,
      }
    }
    headers = {
        "Content-Type": "application/json",
        'xi-api-key': elevenlabs_key,
        }
    # call api
    url = f'https://api.elevenlabs.io/v1/text-to-speech/{voice_id}'
    r = requests.request(url=url, data=json.dumps(data), method='post', headers=headers)
    # handle response
    if r.status_code == 200:
        with open(output_path, mode='bx') as f:
            f.write(r.content)
        return output_path
    else:
        print(vars(r))
        raise Exception('elevenlabs tts failed')

def get_name_ID_mapping():
    """Returns a dictionary mapping voice names to voice ids."""

    # get and parse response
    headers = {
        "Content-Type": "application/json",
        'xi-api-key': elevenlabs_key,
        }
    url = 'https://api.elevenlabs.io/v1/voices'
    r = requests.request(url=url, method='get', headers=headers)
    c = r.content
    d = json.loads(c)

    # d is a list of dicts. example dict:
    ## (substituted None for null, and False for false to prevent errors when running this.)
    {
        "voice_id": "ofKgYdqLcAQu3Z53STPl",
        "name": "emma",
        "samples": None,
        "category": "generated",
        "fine_tuning": {
            "model_id": None,
            "is_allowed_to_fine_tune": False,
            "fine_tuning_requested": False,
            "finetuning_state": "not_started",
            "verification_attempts": None,
            "verification_failures": [],
            "verification_attempts_count": 0,
            "slice_ids": None
        },
        "labels": {
            "accent": "british",
            "age": "young",
            "gender": "female"
        },
        "preview_url": "https://storage.googleapis.com/eleven-public-prod/WMn7xNzYZcbqzQvkWhHQjaDW2wV2/voices/ofKgYdqLcAQu3Z53STPl/74972b58-bbe8-48b9-b79e-d0eb4aa5bcd0.mp3",
        "available_for_tiers": [],
        "settings": None
    }

    # extract the names and ids
    mapping = {}
    for item in d['voices']:
        mapping[item['name']] = item['voice_id']
    return mapping

def get_settings(ID):
    """Returns settings for a single voice.
    
    i forgot why i made this."""

    headers = {
        "Content-Type": "application/json",
        'xi-api-key': elevenlabs_key,
        }
    url = f'https://api.elevenlabs.io/v1/voices/{ID}?with_settings=true'
    r = requests.request(url=url, method='get', headers=headers)
    return r.json()

def serialize(d):
    """Helper for the edit_voice function, which uses the f'https://api.elevenlabs.io/v1/voices/{ID}/edit' endpoint."""

    def make_pair(tup):
        return f'"{tup[0]}":"{tup[1]}"'
    return '{' + ', '.join(list(map(make_pair,d.items()))) + '}'

def edit_voice(name, new_settings):
    """Edits the settings of a single voice.
    note: is currently useless because the labels dont change the way the voice sounds.
    """

    ID = mapping[name]
    url = f'https://api.elevenlabs.io/v1/voices/{ID}/edit'
    headers = {
        'accept': 'application/json',
        'xi-api-key': elevenlabs_key,
    }
    data = {
        'name':name,
        'labels': serialize(new_settings),
    }
    response = requests.post(url, headers=headers, data=data)
    # print('edit_voice response:', response.json())
