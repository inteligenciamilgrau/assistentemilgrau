from pyfirmata import Arduino # pip install pyfirmata
import pyttsx3 # pip install pyttsx3
import time

def main():
    print("Iniciando Assistente")

    assistente_falante = True
    com_arduino = True

    if com_arduino:
        porta = "COM10"
        try:
            board = Arduino(porta)
        except Exception as e:
            print("Sem Arduino na porta", porta)
            return "Saindo"
    voz = 1
    pino = 8
    contar = 0

    # falar
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('rate', 180) # velocidade 120 = lento
    for indice, vozes in enumerate(voices): # listar vozes
        print(indice, vozes.name)
    print("Voz escolhida", voz, voices[voz].name)
    print("")

    def falar(texto, voz_escolhida = 1):
        engine.setProperty('voice', voices[voz_escolhida].id)
        # falando
        engine.say(texto)
        engine.runAndWait()
        engine.stop()

    falar("Assistente Mil Grau Ligando", voz)

    while contar < 4:
        print(contar)
        if(assistente_falante):
            falar("Vai ligar")
        if com_arduino:
            board.digital[pino].write(1)
        time.sleep(1)

        if (assistente_falante):
            falar("Vai Desligar")
        if com_arduino:
            board.digital[pino].write(0)
        time.sleep(1)

        contar += 1

    return "Funcionou"

if __name__ == '__main__':
    texto = main()
    print(texto)