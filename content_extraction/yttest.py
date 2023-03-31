from pytube import YouTube
# YouTube('https://youtu.be/2lAe1cqCOXo').streams.first().download()

#basically for getting all the text between 2 given strings, in a big mess of a string, and putting them in a list
#plus an option to only get items with the strings in strings_list in it
def between2(mess,start,end,strings_list=None):
    mess = mess.split(start)
    for i in range(len(mess)):
        mess[i] = mess[i].partition(end)[0]
    if strings_list == None:
        return mess[1:]
    else:
        filtered_mess = []
        for i in mess[1:]:
            for string in strings_list:
                if string in i:
                    filtered_mess.append(i)
        return filtered_mess
    mess = mess.split(start)
    for i in range(len(mess)):
        mess[i] = mess[i].partition(end)[0]
    return mess[1:]

def get_captions(url):
    yt = YouTube(url)
    captions = yt.captions

    if 'en' in captions:
        caption = captions['en']
        lang = 'en'
    else:
        return 'no english captions found'
        """caption = captions['a.en']
        lang = 'a.en'"""

    xml_captions = caption.xml_captions

    extractions = []
    text = ''
    if lang == 'en':
        for line in xml_captions.splitlines():
            if line.startswith('<p t'):
                t = line.partition('t="')[2].partition('"')[0]
                d = line.partition('d="')[2].partition('"')[0]
                text = line.partition('>')[2].partition('<')[0]
                text = text.replace('&#39;',"'")
                extractions.append([t,d,text])
            elif line.endswith('</p>'):
                text = line.partition('>')[2].partition('<')[0]
                text = text.replace('&#39;',"'")
                extractions[-1][-1] += text
            if '&#39;' in text:
                print(text)
                raise Exception('found &#39;')

    result = '\n'.join([i[-1] for i in extractions])
    assert '&#39;' not in result
    return result

