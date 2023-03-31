import tkinter as tk

from secrets import openai_key
import requests, json, time, os, sys
import pygame

from abc import ABC, abstractmethod

from modules.tts.elevenlabs_endpoints import *

from content_extraction.yttest import get_captions

def make_json(dic, filename):
    with open(filename, 'w', encoding="utf-8") as f:
        json.dump(dic, f, indent=2)
        f.close()

def open_json(filename):
    with open(filename, 'r', encoding="utf-8") as f:
        dic = json.load(f)
        f.close()
    return dic

def use_chatgpt(messages):
    """Use the OpenAI chat API to get a response."""

    folder_to_dump = 'chatgpt_responses'

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

def craft_messages(full_text, paragraph):
    """Given full text and paragraph, will craft messages for use with OpenAI chat API."""

    messages = [
        {
            'role': 'system',
            'content': f'You are a roleplayer, acting as a human.'
        },
        {
            'role': 'assistant',
            'content': 'I can do that. Any personality traits you want me to have?'
        },
        {
            'role': 'system',
            'content': f'Become the personification of this piece of text:\n\n{full_text}\n\nRemember, you are a roleplayer, acting as a human. Never break character, speak about the article as though *you* wrote it, and be as human as possible.\n Your session with the user starts now.',
        },
        {
            'role': 'assistant',
            'content': 'Hey, thanks for reading my article. You like it?',
        },
        {
            'role': 'user',
            'content': f'why did you write it?',
        },
    ]
    return messages

def token_guesser(text):
    """Given text, will guess the token count"""
    factor = 1.5  # on the safe side
    words = text.split(' ')
    return int(len(words) * factor)

# chatgpt-generated summary of my repo readme.
"""
The text discusses the idea of creating an AI system that can generate text and turn it into speech, allowing users to ask for the system's thoughts on a particular moment in a video or article. The system would consist of two types of AI: a language model to generate text and analyze content, and a text-to-speech generator to turn the text into speech. The author explores various resources and services for these AI components, including NovelAI, ElevenLabs, and ChatGPT. The author also discusses implementation details such as caching and on-the-spot generation, and outlines a plan of action for building the system in a modular and importable way.
"""

# will later write this mapper with more generality.. this is kinda to practice the idea
def idx_to_context(full_text, idx):
    raise NotImplementedError

    """Given text and idx, will return context that you can feed an AI model to generate a response."""

    assert idx < len(full_text), "idx must be less than length of full_text"

    # store paragraph boundaries
    paragraphs = full_text.split('\n\n')
    paragraph_starts = [0]
    for paragraph in paragraphs:
        paragraph_starts.append(paragraph_starts[-1] + len(paragraph) + 2)

    # turn starts into ranges
    paragraph_ranges = []
    for i in range(len(paragraph_starts) - 1):
        paragraph_ranges.append((paragraph_starts[i], paragraph_starts[i + 1]))
    
    # find paragraph that idx is in
    for paragraph_range in paragraph_ranges:
        if paragraph_range[0] <= idx <= paragraph_range[1]:
            p_idx = paragraph_ranges.index(paragraph_range)
            p = paragraphs[p_idx]
            break
    
    # form a question for the AI
    lines = []
    for line in [
        'hey, i want you to roleplay as the author of this text.',
        'ill send you the full text, then a paragraph, and then i want you to give commentary on the paragraph, or explain its relationship to the previous one, or the next one, or whatever you want.',
        'here is the full text:',
        full_text,
        'here is the paragraph:',
        p,
    ]:
        lines.append(line)
    return '\n'.join(lines)

def idx_to_paragraph(full_text, idx):
    """Given text and idx, will return paragraph that idx is in."""

    assert idx < len(full_text), "idx must be less than length of full_text"

    # store paragraph boundaries
    paragraphs = full_text.split('\n\n')
    paragraph_starts = [0]
    for paragraph in paragraphs:
        paragraph_starts.append(paragraph_starts[-1] + len(paragraph) + 2)

    # turn starts into ranges
    paragraph_ranges = []
    for i in range(len(paragraph_starts) - 1):
        paragraph_ranges.append((paragraph_starts[i], paragraph_starts[i + 1]))
    
    # find paragraph that idx is in
    for paragraph_range in paragraph_ranges:
        if paragraph_range[0] <= idx <= paragraph_range[1]:
            p_idx = paragraph_ranges.index(paragraph_range)
            p = paragraphs[p_idx]
            break
    
    return p

def apply_layout(layout):
    """Places things in a grid. Takes in a list of lists of widgets."""
    for i in range(len(layout)):
        for j in range(len(layout[i])):
            w = layout[i][j]
            if w == None:
                continue
            w.grid(row=i,column=j)

# function to map tkinter index to normal string index
def tk_idx_to_idx(w, tk_idx):
    # first sum length of lines before tk_idx
    row_idx = int(tk_idx.split('.')[0]) - 1
    
    current_idx = 0
    prior_count = 0
    while True:
        if current_idx == row_idx:
            break
        else:
            line = w.get(f'{current_idx+1}.0', f'{current_idx+1}.end')
            prior_count += len(line) + 1
            current_idx += 1
    
    # now add the column index
    col_idx = int(tk_idx.split('.')[1])
    return prior_count + col_idx

def on_trigger(event):
    """This is the trigger for generating the context (messages for chatgpt) and updating the context widget.
    
    The context will later be read as a json string, when you want to generate a response from the AI."""

    # collect info to use in generating messages
    idx = event.widget.index('insert')
    charpos = tk_idx_to_idx(event.widget, idx)
    full_text = event.widget.get('1.0', 'end')
    paragraph = idx_to_paragraph(full_text, charpos)

    # get messages generator, then generate messages
    settings_string = settings_widget.get('1.0', 'end')[:-1]
    if settings_string == 'default':
        message_generator = craft_messages
    else:
        # just write an error message to context widget
        context_widget.delete('1.0', 'end')
        context_widget.insert('1.0', 'settings string not recognized')
        return 0
    
    args = (full_text, paragraph)
    messages = message_generator(*args)

    # clear output widget and insert new text
    context_widget.delete('1.0', 'end')
    context_widget.insert('1.0', json.dumps(messages, indent=4))
    # scroll to end
    context_widget.see('end')

    # count tokens of context
    token_count = token_guesser('\n\n'.join('\n'.join([f'{k}:{v}' for k,v in mess.items()]) for mess in messages))
    misc_widget.delete('1.0', 'end')
    misc_widget.insert('1.0', f'token count: {token_count}')

# if f5 is pressed, generate response
# need to refactor to parse context from context widget
def on_keypress(event):
    if event.keysym == 'F5':
        # get context from context widget
        context = context_widget.get('1.0', 'end')
        messages = json.loads(context)

        assert type(messages) == list
        for item in messages:
            assert type(item) is dict

        # check if in cache
        response = cacher.get(messages)
        if response == None:
            # if not in cache, generate response
            response = use_chatgpt(messages)
            # add to cache
            cacher.add(messages, response)
        
        # put response in misc widget
        misc_widget.delete('1.0', 'end')
        misc_widget.insert('1.0', response)
    elif event.keysym == 'F6':
        # play tts of response
        response = misc_widget.get('1.0', 'end')
        tts(response)


# set up caching for chatgpt calls
class Cache:
    def __init__(self, filename):
        self.filename = filename
        if not os.path.exists(self.filename):
            with open(self.filename, 'w') as f:
                json.dump([], f)
        self.cache = self.load_cache()
    
    def load_cache(self):
        cache = open_json(self.filename)
        return cache
    
    def save_cache(self):
        with open(self.filename, 'w') as f:
            json.dump(self.cache, f)

    def get(self, inp):
        for item in self.cache:
            if item['input'] == inp:
                return item['output']
        return None

    def add(self, inp, outp):
        self.cache.append({'input':inp, 'output':outp})
        self.save_cache()

class CacheABC(ABC):
    """I'm making this to kinda practice the caching concept.
    
    In general, the point of a cache is to store data that is expensive to generate.
    So it needs a function that searches for the output corresponding to the input, and a function that adds the input and output to the cache.

    ill start by making just everything an abstract method, then try to figure out what is general, and what is specific to the chatgpt cache.
    """

    def __init__(self, filename):
        self.filename = filename
        if not os.path.exists(self.filename):
            with open(self.filename, 'w') as f:
                json.dump([], f)
        self.cache = self.load_cache()
    
    @abstractmethod
    def load_cache(self):
        # called on initialization
        pass
    
    @abstractmethod
    def save_cache(self):
        # should be called after adding to cache
        pass
    
    @abstractmethod
    def get(self, inp):
        # called to find an input in the cache
        pass
    
    @abstractmethod
    def add(self, inp, outp):
        # add to cache
        pass

## wrapper around generate_and_save
def tts(text):
    # prepare request
    name = 'jemma'
    timestamp = time.time()
    out_path = f'./tts_output/{timestamp}.mp3'

    # check with cacher, call api if necessary
    args = {
        'text': text,
        'name': name,
    }
    cached = cacher.get(args)
    if cached == None:
        voice_id = name_id_mapping[name]
        generate_and_save(voice_id, text, out_path)
        cacher.add(args, out_path)
    else:
        out_path = cached
    
    # play audio
    play_tts(out_path)

def play_tts(path):
    pygame.mixer.music.load(path)
    pygame.mixer.music.play()

# will write captions to the input widget
def on_command(event):
    url = command_widget.get()
    captions = get_captions(url)
    initial_text_widget.delete('1.0', 'end')
    initial_text_widget.insert('1.0', captions)

# for tts
pygame.mixer.init()
name_id_mapping = get_name_ID_mapping()

with open('default_text.txt', 'r') as f:
    default_text = f.read()

# start cache
cacher = Cache('chatgpt_cache.json')

root = tk.Tk()
root.config(bg='black')
root.geometry('1200x800+0+0')

# need to put initial text widget in a frame so i have more freedom over layout.
inputs_frame = tk.Frame(root)
initial_text_widget = tk.Text(inputs_frame)
initial_text_widget.insert('end', default_text)
settings_widget = tk.Text(inputs_frame)
default_settings_text = '''
default
'''[1:-1]
settings_widget.insert('1.0', default_settings_text)

output_frame = tk.Frame(root)
context_widget = tk.Text(output_frame)
misc_widget = tk.Text(output_frame)

# add an entry widget for commands.
command_widget = tk.Entry(root)


# set black bg and grey fg
style_settings = {
    'bg': 'black',
    'fg': 'grey',
    'font': ('comic sans', 14),
    'insertbackground': 'white',
    'width': 50,
    'height': 15,
}
for w in [initial_text_widget, settings_widget, context_widget, misc_widget]:
    w.config(**style_settings)

trigger = 'ButtonRelease-1'
initial_text_widget.bind(f'<{trigger}>', on_trigger)
root.bind('<Key>', on_keypress)
command_widget.bind('<Return>', on_command)

inputs_frame_layout = [
    [initial_text_widget],
    [settings_widget]
]
output_frame_layout = [
    [context_widget],
    [misc_widget],
    [command_widget]
]
overall_layout = [
    [inputs_frame, output_frame],
]
apply_layout(inputs_frame_layout)
apply_layout(output_frame_layout)
apply_layout(overall_layout)

root.mainloop()
