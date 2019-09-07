# -*- coding: utf-8 -*-
import serial # pip install pyserial
import threading
import time
import speech_recognition as sr # pip install SpeechRecognition
import pyttsx3 # pip install pyttsx3
import cv2

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

r = sr.Recognizer()

mic = sr.Microphone(0) # 0 = microfone embutido

conectado = False
porta = 'COM3' # linux ou mac em geral -> '/dev/ttyS0'
velocidadeBaud = 115200

mensagensRecebidas = 1;
desligarArduinoThread = False
desligarCameraThread = False
desligarVozThread = False

falarTexto = False;
textoRecebido = ""
textoFalado = ""

arduinoFuncionando = True
nuncaTeVi = True;
jaTeVi = False;

try:
    SerialArduino = serial.Serial(porta,velocidadeBaud, timeout = 0.2)
except:
    print("Verificar porta serial ou religar arduino")
    arduinoFuncionando = False

def handle_data(data):
    global mensagensRecebidas, falarTexto, textoRecebido
    print("Recebi " + str(mensagensRecebidas) + ": " + data)
    
    mensagensRecebidas += 1
    textoRecebido = data
    
    falarTexto = True

def read_from_port(ser):
    global conectado, desligarArduinoThread
    
    while not conectado:
        conectado = True

        while True:
           try:
               reading = ser.readline().decode()
           except:
               print("Serial desligada")
           if reading != "":
               handle_data(reading)
           if desligarArduinoThread:
               print("Desligando Arduino")
               break

def conectaCamera():
    global desligarCameraThread, arduinoFuncionando, SerialArduino,\
        nuncaTeVi, jaTeVi
    classificador = cv2.CascadeClassifier(
        "cascades/haarcascade_frontalface_default.xml")
    webCam = cv2.VideoCapture(1)
    while(True):
        conectou, imagem = webCam.read()
        
        imagem = cv2.flip(imagem, 1) # inverte imagem (opcional)
        alturaImagem, larguraImagem = imagem.shape[:2]
        
        converteuCinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
        
        encontrarFaces = classificador.detectMultiScale(converteuCinza,
                                                        scaleFactor=1.5,
                                                        minSize=(150,150),
                                                        maxSize=(200,200))
        cor = (0,0,255)
        for(origemX, origemY, largura, altura) in encontrarFaces:
            cv2.rectangle(imagem,(origemX,origemY),
                          (origemX + largura, origemY + altura),
                          cor,2)
            
            if nuncaTeVi: # quando a camera te ver pela primeira vez
                time.sleep(0.5)
                nuncaTeVi = False
                jaTeVi = True
            
            raio = 4
            centroRosto = (origemX + int(largura/2),origemY + int(altura/2))
            cv2.circle(imagem, centroRosto, raio, cor)
            
            # Normalizar = deixa valores entre zero até um
            normalizarZeroAteUm = int(larguraImagem/2)
            # Correção = transforma valores para 1 até 10
            fatorDeCorrecao = 10
            
            erroCentro = (((centroRosto[0] - (larguraImagem/2))
            /normalizarZeroAteUm) * fatorDeCorrecao)
            
            try:
                if arduinoFuncionando:
                    pass
                # arduino desativado porque o som do motor interfere na voz
                    #SerialArduino.write(('servo' + str(erroCentro) + '\n').encode())
            except:
                print("não enviou")
    
        cv2.imshow("Rosto", imagem)
        
        teclou = cv2.waitKey(1) & 0xFF
        if desligarCameraThread:
            webCam.release()
            cv2.destroyAllWindows()
            print("Desligando camera")
            break
        

    
def falar():
    global jaTeVi, falarTexto, textoRecebido, textoFalado
    
    engine = pyttsx3.init()
    
    voices = engine.getProperty('voices')
    engine.setProperty('rate', 150) # velocidade 120 = lento
    contar = 0;
    for vozes in voices: # listar vozes
        print(contar, vozes.name)
        contar+=1
    
    voz = 3#1
    engine.setProperty('voice', voices[voz].id)
    
    #IVONA VOICE: RICARDO
    #https://harposoftware.com/en/portuguese-brasil/166-ricardo-portuguese-brasilian-voice.html
    #https://kripytonianojarvis.com/site/pre-instalacao/

    while True:
        if desligarVozThread:
            engine.stop()
            break
        if jaTeVi:
            engine.say("Olá Robert")
            engine.runAndWait()
            jaTeVi = False
        if falarTexto:
            if textoRecebido != "":
                engine.say(textoRecebido)
                engine.runAndWait()
                textoRecebido = ""
            elif textoFalado != "":
                resposta = AMGbot.get_response(textoFalado)
                print("Assistente: " + str(resposta))
                engine.say(resposta)
                engine.runAndWait()
                textoFalado = ""
            
            falarTexto = False

def desligando():
    global desligarArduinoThread, arduinoFuncionando, \
        SerialArduino, lerSerialThread,  \
        desligarCameraThread, desligarVozThread
    
    desligarArduinoThread = True
    desligarCameraThread = True
    desligarVozThread = True
    if arduinoFuncionando:
        SerialArduino.close()
        lerSerialThread.join()
    falarVozThread.join()
    
    print("Tudo desligado")

if arduinoFuncionando:
    try:
        lerSerialThread = threading.Thread(target=read_from_port, args=(SerialArduino,))
        lerSerialThread.start()
    except:
        print("Verificar porta serial ou religar arduino")
        arduinoFuncionando = False
    print("Preparando Arduino")
    time.sleep(2)
    print("Arduino Pronto")
else:
    time.sleep(2)
    print("Arduino não conectou")

ligaCamera = True
if ligaCamera:
    try:
        cameraLigadaThread = threading.Thread(target=conectaCamera)
        cameraLigadaThread.start()
    except:
        print("sem câmera")
        
falarVozes = True
if falarVozes:
    try:
        falarVozThread = threading.Thread(target=falar)
        falarVozThread.start()
    except:
        print("sem mic")

while(nuncaTeVi): # só conversa depois de ver a pessoa
        pass

while (True):
    
    try:
        with mic as fonte:
            r.adjust_for_ambient_noise(fonte)
            print("Fale alguma coisa")
            audio = r.listen(fonte)
            print("Enviando para reconhecimento")
        try:
            text = r.recognize_google(audio, language= "pt-BR").lower()
            print("Você disse: {}".format(text))

            if arduinoFuncionando:
                SerialArduino.write((text + '\n').encode())

            print("Dado enviado")
            if(text.startswith("desativar")):
                print("Saindo")
                
                desativando = "Assistente mil grau desativando."
                textoRecebido = desativando
                textoFalado = desativando

                desligando()
                break
            
            # retirar os textos que são comandos especiais
            if text != "" and not text.startswith("ligar") and \
            not text.startswith("desligar") \
            and not text.startswith("desativar"):
                textoFalado = text
                falarTexto = True
        except:
            print("Não entendi o que você disse\n")

    except (KeyboardInterrupt, SystemExit):
        print("Apertou Ctrl+C")
        desligando()
        break
