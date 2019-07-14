import pyttsx3 # pip install pyttsx3

engine = pyttsx3.init()

engine.say("Hello World!")

engine.runAndWait()

engine.stop()
