# chatgpt-generated summary of my repo readme.
"""
The text discusses the idea of creating an AI system that can generate text and turn it into speech, allowing users to ask for the system's thoughts on a particular moment in a video or article. The system would consist of two types of AI: a language model to generate text and analyze content, and a text-to-speech generator to turn the text into speech. The author explores various resources and services for these AI components, including NovelAI, ElevenLabs, and ChatGPT. The author also discusses implementation details such as caching and on-the-spot generation, and outlines a plan of action for building the system in a modular and importable way.
"""

# will later write this mapper with more generality.. this is kinda to practice the idea
def idx_to_context(full_text, idx):
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
    
    context = 'You are in paragraph ' + str(p_idx) + '. \n' + p
    return context

"""
will test with tkinter, because its hard to visually know what idx something is in a text file
"""
with open('main.txt', 'r') as f:
    text = f.read()

import tkinter as tk

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
    context = idx_to_context(text, charpos)
    # clear output widget and insert new text
    output_widget.delete('1.0', 'end')
    output_widget.insert('1.0', context)
    print(context)

root = tk.Tk()

input_widget = tk.Text(root)
input_widget.insert('1.0', text)

output_widget = tk.Text(root)

# set black bg and grey fg
style_settings = {
    'bg': 'black',
    'fg': 'grey',
    'font': ('comic sans', 15),
    'width': 50,
}
for w in [input_widget, output_widget]:
    w.config(**style_settings)

trigger = 'ButtonRelease-1'
input_widget.bind(f'<{trigger}>', on_trigger)

layout = [
    [input_widget, output_widget],
]
apply_layout(layout)   

root.mainloop()
