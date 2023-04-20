from pyfirmata import Arduino # pip install pyfirmata
import pyttsx3 # pip install pyttsx3
import speech_recognition as sr  # pip install SpeechRecognition

def main():
    print("Iniciando Assistente")

    pino = 8
    assistente_falante = True
    com_arduino = True
    entrada_por_texto = False
    lingua = "pt-BR"
    voz = 1
    # caso nao queira falar "assistente" ou "Chat GPT"
    sem_palavra_ativadora = False
    # ajusta ruido do ambiente
    ajustar_ambiente_noise = False

    if com_arduino:
        porta = "COM10"
        try:
            board = Arduino(porta)
        except Exception as e:
            print("Sem Arduino na porta", porta)
            return "Saindo"

    # falar
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('rate', 180) # velocidade 120 = lento
    for indice, vozes in enumerate(voices): # listar vozes
        print(indice, vozes.name)
    print("Voz escolhida", voz, voices[voz].name)
    print("")

    # ouvir
    r = sr.Recognizer()
    mic = sr.Microphone()

    def falar(texto, voz_escolhida = 1):
        engine.setProperty('voice', voices[voz_escolhida].id)
        # falando
        engine.say(texto)
        engine.runAndWait()
        engine.stop()

    sair = {"sair", "desligar"}
    chamar_assistente = {"assistente"}
    cancelar = ("cancela", "cancelar")

    comando1 = {"ligar luz"}
    comando2 = {"desligar luz"}
    comandos = [comando1, comando2]

    comecar = set()
    comecar.update(chamar_assistente)
    comecar.update(sair)

    falar("Assistente Mil Grau Ligando", voz)

    while True:
        print("")
        print("Chamadas", comecar)
        print("Comandos", comandos)
        print("")
        if entrada_por_texto:
            comando_recebido = input("Perguntar pro ChatGPT (\"sair\"): ")
        else:
            # Ask a question
            with mic as fonte:
                if ajustar_ambiente_noise:
                    r.adjust_for_ambient_noise(fonte)
                    ajustar_ambiente_noise = False
                print("Fale alguma coisa")
                audio = r.listen(fonte)
                print("Enviando para reconhecimento")

                try:
                    comando_recebido = r.recognize_google(audio, language=lingua)
                except:
                    print("Problemas com o reconhecimento")
                    comando_recebido = ""
                print("Ouvi:", comando_recebido)

        comecodafrase = ""
        for espressao in comecar:
            if comando_recebido.startswith(espressao):
                comecodafrase = espressao.lower()

        if comecodafrase in sair:
            print(comando_recebido, "Saindo.")
            if assistente_falante:
                falar("Desligando", voz)
            break
        elif comando_recebido == "" or comando_recebido.lower().endswith(cancelar):
            print("!!! Sem som, texto ou cancelou !!!", comando_recebido)
            continue
        elif comecodafrase in chamar_assistente or sem_palavra_ativadora:
            if len(comecodafrase) > 0:
                comando_recebido = comando_recebido[len(comecodafrase) + 1:].lower()
            print("comando_recebido", comando_recebido)
            if comando_recebido in comando1:
                if (assistente_falante):
                    falar("Vai ligar", voz)
                if com_arduino:
                    board.digital[pino].write(1)
            elif comando_recebido in comando2:
                if (assistente_falante):
                    falar("Vai Desligar", voz)
                if com_arduino:
                    board.digital[pino].write(0)


if __name__ == '__main__':
    texto = main()
    print(texto)
