# -*- coding: utf-8 -*-
import speech_recognition as sr # pip install SpeechRecognition
import pyttsx3 # pip install pyttsx3

#chatbot
from chatterbot.trainers import ListTrainer # pip install chatterbot
# caso de erro: No module named 'chatterbot_corpus'
# python -m pip install chatterbot-corpus

from chatterbot import ChatBot

AMGbot = ChatBot("Assistente Mil Grau")

# texto inicial, com as conversas o bot vai ficando mais inteligente
conversa1 = ['oi','olá','olá bom dia', 'bom dia', 'como vai?','estou bem']
conversa2 = ['e aí?','fala mano','vai lá na parada?', 'nem vou', 'e as criança?','dormindo']

treinar = ListTrainer(AMGbot)
treinar.train(conversa1)
treinar.train(conversa2)

#import socket

#voz jarvis
#import win32com.client as comclt
#wsh= comclt.Dispatch("WScript.Shell")
#wsh.AppActivate("MiniSpeech") # select another application

engine = pyttsx3.init()

voices = engine.getProperty('voices')
engine.setProperty('rate', 150) # velocidade 120 = lento
contar = 0;
for vozes in voices: # listar vozes
    print(contar, vozes.name)
    contar+=1

voz = 1
engine.setProperty('voice', voices[voz].id)

#IVONA VOICE: RICARDO
#https://harposoftware.com/en/portuguese-brasil/166-ricardo-portuguese-brasilian-voice.html
#https://kripytonianojarvis.com/site/pre-instalacao/

r = sr.Recognizer()

mic = sr.Microphone(0) # 0 = microfone embutido

falarTexto = False;
textoFalado = ""


while (True):
    if falarTexto:
        if textoFalado != "":
            resposta = AMGbot.get_response(textoFalado)
            engine.say(resposta)
            engine.runAndWait()
            textoFalado = ""
        
        #voz jarvis
        #wsh.AppActivate("MiniSpeech") # select another application
        #wsh.SendKeys("^a")
        #wsh.SendKeys(textoRecebido)
        #wsh.SendKeys("%{ENTER}")
        
        falarTexto = False
        #time.sleep(3)
    try:
        with mic as fonte:
            r.adjust_for_ambient_noise(fonte)
            print("Fale alguma coisa")
            audio = r.listen(fonte)
            print("Enviando para reconhecimento")
        try:
            text = r.recognize_google(audio, language= "pt-BR").lower()
            print("Você disse: {}".format(text))

            if text != "":
                textoFalado = text
                falarTexto = True
            
            print("Dado enviado")
            if(text == "desativar"):
                print("Saindo")
                
                desativando = "Assistente mil grau desativando."
                
                engine.say(desativando)
                engine.runAndWait()
                
                #voz jarvis
                #wsh.AppActivate("MiniSpeech") # select another application
                #wsh.SendKeys("^a")
                #wsh.SendKeys(desativando)
                #wsh.SendKeys("%{ENTER}")
                
                engine.stop()
                break
        except:
            print("Não entendi o que você disse\n")
            engine.say("que que cê disse?")
            engine.runAndWait()
        
        #time.sleep(0.5) # aguarda resposta do arduino
    except (KeyboardInterrupt, SystemExit):
        print("Apertou Ctrl+C")
        engine.stop()
        break
