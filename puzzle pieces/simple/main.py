import tkinter as tk

def token_guesser(text):
    """Given text, will guess the token count"""
    factor = 1.5  # on the safe side
    words = text.split(' ')
    return int(len(words) * factor)

with open('main.txt', 'r') as f:
    text = f.read()
token_limit = 3000  # chatgpt context is 4096 tokens
token_count = token_guesser(text)
if token_count > token_limit:
    print(f'Text is too long. It has {token_count} tokens, but the limit is {token_limit} tokens.')
    exit()

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
    
    # form a question for the AI
    lines = []
    for line in [
        'hey AI, im going to send you a full article, followed by a paragraph from it, and want you to explain it.',
        '',
        'full article:',
        full_text,
        '',
        'the paragraph in question:',
        p,
        '',
        'could you explain it please?',
    ]:
        lines.append(line)
    return '\n'.join(lines)

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
    # scroll to end
    output_widget.see('end')

    # count tokens of context
    token_count = token_guesser(context)
    misc_widget.delete('1.0', 'end')
    misc_widget.insert('1.0', f'token count: {token_count}')

root = tk.Tk()
root.config(bg='black')

input_widget = tk.Text(root)
input_widget.insert('1.0', text)

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
    'height': 20,
}
for w in [input_widget, output_widget, misc_widget]:
    w.config(**style_settings)
input_widget.config(width=50, height=30)

trigger = 'ButtonRelease-1'
input_widget.bind(f'<{trigger}>', on_trigger)

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
