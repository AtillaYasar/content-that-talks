import os
from chatgpt import use_chatgpt

folder_to_dump = 'dumps'
if folder_to_dump not in os.listdir():
    os.mkdir(folder_to_dump)

print(use_chatgpt([{'role':'user', 'content':'tell me what would happen if one built a tool that could generate analysis of content and then could speak it using tts'}]))