import pyttsx3

def convert_text_to_speech (text):
    # Need to specify the language 
    engine = pyttsx3.init()
    engine.setProperty('voice', engine.getProperty('voices')[1].id)
    engine.say(text)
    engine.runAndWait()
