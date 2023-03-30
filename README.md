# content-that-talks
"yo what if you can just pause a yt video or like an article and you can just ask its thoughts at a particular moment"

## ALPHA
alpha as fuck. more alpha than andrew tate.  
i created this repo as kind of the central hub for code around this idea.  

## two kinds of AI
The Beast  (language model):  will generate text, and analyze content, and answer questions etc  
The Beauty  (tts generator):  will turn ugly booh eww text into woah poggers monkey brain happy hehe nice sounds  

## resources, services

### TTS and Text gen
- ElevenLabs for fast and high quality TTS + cloning, is expensive
- ChatGPT for decent-speed and high quality text gen, is somewhat expensive
- NovelAI for both textgen and TTS that is fast and not-the-worst-quality.
  - private
    - NovelAI has full privacy, and is reliable
      - this makes NAI the ONLY option for some people, for whom privacy is important
    - I also really like the NAI community and the devs, which would make working closely with them, more fun
  - pricing makes this the best option for some use cases  (maybe a lot)
- custom options
  - tortoise, tortoisefast, llama, alpaca, gpt4all, gpt5yomother, sheep, goat, whatever the heck open source stuff people made
  - this path requires way more programming skill  :p
  - basically, I'd build my own API for text and/or speech, instead of using one of the above. should only be relevant if pricing becomes a big problem.
    - (but then, it's kind of insane to think I can build a better API than those guys... especially the NAI guys)
      - but good to at least know it's an option

### repositories/code
- my own? idk. i havent looked around that much. will link to what i have later.

## steps
1) get content
2) show content to smart AI
3) turn AI response into speech

## puzzle pieces, "implementation details"
- caching vs on the spot generation
  - hard problem, both figuring out the balance, and implementing aspects around this programmatically
  - depends on what services you are using, how much youre willing to pay, what kind of analysis youre trying to get, and just how any given user feels, at that particular moment, about waiting for tts and/or text gen
  - TIME is really what makes this difficult. it complicates everything. functionally, there is not really a difference between wanting to know x about y in time t of content c, but since it takes time to generate such analysis, you have to do some caching tricks
    - this probably describes like 99% of software engineering, lol.
  - this problem seems to permeate every part of this project, and many others. experienced devs will probably tell me, "yeah duh. lmao."
- functions
  - get tts
    - options for the generator service, and which voice+settings youre using
  - get textgen
    - huge amount of variables regarding what kinds of analysis to get, how to craft context, how many things to ask at any given point, etc etc

## proof of concept, and exploration of this idea
- youtube video i made: https://www.youtube.com/watch?v=-7rV2Eiulpc

## the heart, `location --> string`
### how so?
  At the heart of all this, is a function where you feed a location in a video or article, and receive text.  
  `Text --> speech` is trivial (conceptually)  
  For videos, the timestamp basically turns into a location (on a linear plane, so it's just a single number).  
    (and a video itself is represented as a bunch of text anyway, where each bit of text is mappepd to a timestamp)
  For articles, the location is maybe a string index.
### details
  - once you have the text, you just need a "play sound" function. that either grabs a cached tts, or generates it on the spot  
  - the mapping function (conceptually speaking) is kind of like an assert, that says "if you have this, your code works"  
  - then connected to the heart (whatever the biological analogy is) you have code that takes that mapping function and uses it to play a sound when a "user" (another piece of code or a literal human user (probably the former)) feeds it an index

## plan of action
"enough talk, show me the code"  <-- i think from George Hotz, but dont remember :p  

### reduce complexity (by a lot)
#### frozen parameters
- TTS:
  + I have an ElevenLabs voice that I really like and is easy to generate.
  + "young british female" generated with the Voice Synthesis option and with 0.2 stability and 0.3 "clarity + similarity enhancement"
- text generation:
  + ChatGPT api
  + limit context to some character or word count, raise error when it goes above it. (dont know how much yet)
    - as opposed to doing some summarization/retrieval tricks to let ChatGPT comment on things larger than its total context
- limit "frontend" to cached files and cached text.
#### dynamic variables
- chatgpt prompt engineering. has too much unexplored space, and no "just do this and itll be fine" thing.



