import tkinter as tk

from secrets import openai_key
import requests, json, time, os, sys

if openai_key == 'get your own key.':
    print('You need to get your own openai key.')
    sys.exit()

def make_json(dic, filename):
    with open(filename, 'w', encoding="utf-8") as f:
        json.dump(dic, f, indent=2)
        f.close()

def open_json(filename):
    with open(filename, 'r', encoding="utf-8") as f:
        dic = json.load(f)
        f.close()
    return dic

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

def craft_messages(full_text, paragraph):
    messages = [
        {
            'role':'system',
            'content':"Roleplay with the user. Listen to their instructions and desires and respond in character."
        },
        {
            'role':'user',
            'content':"hey",
        },
        {
            'role':'assistant',
            'content':"Hey there! What's up? I'm a chatbot that can talk to you about anything."
        },
        {
            'role':'user',
            'content':"can you pretend to the author of an article im reading?",
        },
        {
            'role':'assistant',
            'content':"Sure. Send me the article, and then the paragraph you want me to comment on."
        },
        {
            'role':'user',
            'content':f'article:\n{full_text}\n---\nparagraph:\n{paragraph}'
        }
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
    # get context
    idx = event.widget.index('insert')
    charpos = tk_idx_to_idx(event.widget, idx)
    input_text = event.widget.get('1.0', 'end')
    paragraph = idx_to_paragraph(input_text, charpos)
    messages = craft_messages(input_text, paragraph)
    # clear output widget and insert new text
    output_widget.delete('1.0', 'end')
    output_widget.insert('1.0', json.dumps(messages, indent=4))
    # scroll to end
    output_widget.see('end')

    # count tokens of context
    token_count = token_guesser('\n\n'.join('\n'.join([f'{k}:{v}' for k,v in mess.items()]) for mess in messages))
    misc_widget.delete('1.0', 'end')
    misc_widget.insert('1.0', f'token count: {token_count}')

# if f5 is pressed, generate response
def on_keypress(event):
    if event.keysym == 'F5':
        # get full text and paragraph, then messages
        full_text = input_widget.get('1.0', 'end')
        idx = input_widget.index('insert')
        charpos = tk_idx_to_idx(input_widget, idx)
        paragraph = idx_to_paragraph(full_text, charpos)
        messages = craft_messages(full_text, paragraph)

        assert type(messages) == list
        for item in messages:
            assert type(item) is dict

        # put in output widget to check, scroll to end
        output_widget.delete('1.0', 'end')
        output_widget.insert('1.0', json.dumps(messages, indent=4))
        output_widget.see('end')

        # check if in cache
        response = chatgpt_cacher.get(messages)
        if response == None:
            # if not in cache, generate response
            response = use_chatgpt(messages)
            # add to cache
            chatgpt_cacher.add(messages, response)
        
        # put response in misc widget
        misc_widget.delete('1.0', 'end')
        misc_widget.insert('1.0', response)


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

with open('default_text.txt', 'r') as f:
    default_text = f.read()

# start cache
chatgpt_cacher = Cache('chatgpt_cache.json')

root = tk.Tk()
root.config(bg='black')
root.geometry('1200x800+0+0')

input_widget = tk.Text(root)
input_widget.insert('end', default_text)

output_frame = tk.Frame(root)
output_widget = tk.Text(output_frame)
misc_widget = tk.Text(output_frame)

# set black bg and grey fg
style_settings = {
    'bg': 'black',
    'fg': 'grey',
    'font': ('comic sans', 14),
    'insertbackground': 'white',
    'width': 50,
    'height': 15,
}
for w in [input_widget, output_widget, misc_widget]:
    w.config(**style_settings)
input_widget.config(width=50, height=30)

trigger = 'ButtonRelease-1'
input_widget.bind(f'<{trigger}>', on_trigger)
root.bind('<Key>', on_keypress)

frame_layout = [
    [output_widget],
    [misc_widget],
]
layout = [
    [input_widget, output_frame],
]
apply_layout(layout)
apply_layout(frame_layout)

root.mainloop()
