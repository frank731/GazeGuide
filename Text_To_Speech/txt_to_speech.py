from gtts import gTTS
import os

def convert_text_to_speech (text, slow_speed, language="en"):
    # Need to specify the language 
    myobj = gTTS(text=text, lang=language, slow=slow_speed)
    myobj.save("welcome.mp3")
    os.system("start welcome.mp3")
    