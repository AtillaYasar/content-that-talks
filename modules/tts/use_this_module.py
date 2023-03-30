import json, os, time, sys, random

from elevenlabs_endpoints import generate_and_save, get_name_ID_mapping

mapping = get_name_ID_mapping()

out_folder = 'dump'
if not os.path.isdir(out_folder):
    os.mkdir(out_folder)
out_path = f'{out_folder}/' + str(time.time()).replace('.','_') + '.mp3'
voice = mapping['jemma']
generate_and_save(voice, 'Hello sir. I am Jemma, a text to speech voice named after Jemma Simmons from Agents of Shield. Do you like my soft spoken British accent?', out_path)
