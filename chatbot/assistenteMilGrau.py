import serial # pip install pyserial
import threading
import time
import speech_recognition as sr # pip install SpeechRecognition
import pyttsx3 # pip install pyttsx3

#se estiver tendo problemas rodando a voz do Ricardo feito pela Ivona, abra o MiniSpeech que vem junto com a instalação
#descomente as linhas apõs o #voz jarvis
#estas linhas de código irão colocar o foco na janela do MiniSpeech, colar o texto recebido pelo arduino e dar play

#voz jarvis
#import win32com.client as comclt
#wsh= comclt.Dispatch("WScript.Shell")
#wsh.AppActivate("MiniSpeech") # select another application

engine = pyttsx3.init()

voices = engine.getProperty('voices')
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

mic = sr.Microphone()

conectado = False
porta = 'COM3' # linux ou mac em geral -> '/dev/ttyS0'
velocidadeBaud = 115200

mensagensRecebidas = 1;
desligarArduinoThread = False

falarTexto = False;
textoRecebido = ""

try:
    SerialArduino = serial.Serial(porta,velocidadeBaud, timeout = 0.2)
except:
    print("Verificar porta serial ou religar arduino")

def handle_data(data):
    global mensagensRecebidas, engine, falarTexto, textoRecebido
    print("Recebi " + str(mensagensRecebidas) + ": " + data)
    
    mensagensRecebidas += 1
    textoRecebido = data
    falarTexto = True

def read_from_port(ser):
    global conectado, desligarArduinoThread
    
    while not conectado:
        conectado = True

        while True:
           reading = ser.readline().decode()
           if reading != "":
               handle_data(reading)
           if desligarArduinoThread:
               print("Desligando Arduino")
               break

lerSerialThread = threading.Thread(target=read_from_port, args=(SerialArduino,))
lerSerialThread.start()

print("Preparando Arduino")
time.sleep(2)
print("Arduino Pronto")

while (True):
    if falarTexto:
        engine.say(textoRecebido)
        engine.runAndWait()
        
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

            SerialArduino.write((text + '\n').encode())
            
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
                desligarArduinoThread = True
                SerialArduino.close()
                lerSerialThread.join()
                break
        except:
            print("Não entendi o que você disse\n")
        
        time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        print("Apertou Ctrl+C")
        engine.stop()
        desligarArduinoThread = True
        SerialArduino.close()
        lerSerialThread.join()
        break
