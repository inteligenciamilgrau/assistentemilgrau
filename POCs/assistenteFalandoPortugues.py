import pyttsx3 # pip install pyttsx3

engine = pyttsx3.init()

voices = engine.getProperty('voices')
engine.setProperty('rate', 150) # velocidade 120 = lento

for indice, vozes in enumerate(voices): # listar vozes
    print(indice, vozes.name)

voz = 1
engine.setProperty('voice', voices[voz].id)

engine.say("Olá pessoal! Eba!")

engine.runAndWait()

engine.stop()
