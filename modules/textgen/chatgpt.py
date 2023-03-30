from secrets import openai_key
import requests, json, time, os, sys

def make_json(dic, filename):
    with open(filename, 'w', encoding="utf-8") as f:
        json.dump(dic, f, indent=2)
        f.close()

def use_chatgpt(messages, folder_to_dump=None):
    """Use the OpenAI chat API to get a response."""

    assert type(messages) is list
    for i in messages:
        assert type(i) is dict
        assert 'role' in i
        assert 'content' in i
        assert i['role'] in ['user', 'system', 'assistant']

    # create the request
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai_key}"
    }
    data = {
        "model":"gpt-3.5-turbo",
        'messages':messages,
        'n':1,
        'temperature':0,
    }
    response = requests.post(url, headers=headers, data=json.dumps(data)).json()

    if folder_to_dump != None:
        # store the data and response for debugging
        make_json({'data':data, 'response':response}, f'{folder_to_dump}/{time.time()}.json')

    # parse and return ai response
    prompt_tokens = response['usage']['prompt_tokens']
    completion_tokens = response['usage']['completion_tokens']
    total_tokens = response['usage']['total_tokens']
    ai_response = response['choices'][0]['message']['content']
    return ai_response




