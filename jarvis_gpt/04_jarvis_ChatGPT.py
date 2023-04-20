from pyfirmata import Arduino # pip install pyfirmata
import pyttsx3 # pip install pyttsx3
import speech_recognition as sr  # pip install SpeechRecognition
import openai # pip instal openai
import json

config_assistente = {
    "porta_arduino" : "COM10",
    "pino": 8,
    "assistente_falante": True,
    "com_arduino": True,
    "entrada_por_texto": False,
    "lingua": "pt-BR",
    "voz":1,
    # caso nao queira falar "assistente" ou "Chat GPT"
    "sem_palavra_ativadora": False,
    "sem_palavra_ativadora_chatgpt": False,
    # ajusta ruido do ambiente
    "ajustar_ambiente_noise": True
}

def falar(texto, engine, voices, voz_escolhida = 1):
    engine.setProperty('voice', voices[voz_escolhida].id)
    # falando
    engine.say(texto)
    engine.runAndWait()
    engine.stop()


def generate_answer(messages):
    try:
        response = openai.ChatCompletion.create(
            #model="gpt-4",
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=1000,
            temperature=0.9,
            top_p=0.5,
            frequency_penalty=0.25,
            presence_penalty=0.25
        )
        return [response.choices[0].message.content, response.usage]
    except Exception as e:
        print("Deu ruim", e)
        return ["", ""]


def zerarMensagens():
    return [{"role": "system", "content": "Seu nome é Assistente Mil Grau"}]


def main():
    if config_assistente["com_arduino"]:
        try:
            board = Arduino(config_assistente["porta_arduino"])
        except:
            print("Nao encontrei arduino na porta", config_assistente["porta_arduino"])
            return "Encerrando"

    # Initialize the API key
    f = open('chat_key.json')
    chave = json.load(f)
    openai.api_key = chave['api_key']

    # falar
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('rate', 180)  # velocidade 120 = lento
    for indice, vozes in enumerate(voices):  # listar vozes
        print(indice, vozes.name)
    print("Voz escolhida", config_assistente["voz"], voices[config_assistente["voz"]].name)
    print("")

    # ouvir
    r = sr.Recognizer()
    mic = sr.Microphone()

    sair = {"sair"}
    chamar_assistente = {"assistente"}
    chamar_assistente_ChatGPT = {"gpt", "chatgpt", "chat gpt"}
    cancelar = ("cancela", "cancelar")

    comando1 = {"ligar luz"}
    comando2 = {"desligar luz"}
    comandos = [comando1, comando2]

    comecar = set()
    comecar.update(sair)
    comecar.update(chamar_assistente)
    comecar.update(chamar_assistente_ChatGPT)

    falar("Assistente Mil Grau Ligando", engine, voices, config_assistente["voz"])

    while True:
        print("")
        print("Chamadas", comecar)
        print("Comandos", comandos)
        print("")
        if config_assistente["entrada_por_texto"]:
            comando_recebido = input("Perguntar pro ChatGPT (\"sair\"): ")
        else:
            # Ask a question
            with mic as fonte:
                if config_assistente["ajustar_ambiente_noise"]:
                    r.adjust_for_ambient_noise(fonte)
                    ajustar_ambiente_noise = False
                print("Fale alguma coisa")
                audio = r.listen(fonte)
                print("Enviando para reconhecimento")

                try:
                    comando_recebido = r.recognize_google(audio, language=config_assistente["lingua"])
                except:
                    print("Problemas com o reconhecimento")
                    comando_recebido = ""
                print("############ Ouvi:", comando_recebido)

        comecodafrase = ""
        for espressao in comecar:
            if comando_recebido.lower().startswith(espressao):
                comecodafrase = espressao.lower()

        if comecodafrase in sair:
            print(comando_recebido, "Saindo.")
            if config_assistente["assistente_falante"]:
                falar("Desligando", engine, voices, config_assistente["voz"])
            break
        elif comando_recebido == "" or comando_recebido.lower().endswith(cancelar):
            print("!!! Sem som, texto ou cancelou !!!", comando_recebido)
            continue
        elif comecodafrase in chamar_assistente or config_assistente["sem_palavra_ativadora"]:
            if len(comecodafrase) > 0:
                comando_recebido = comando_recebido[len(comecodafrase) + 1:].lower()
            elif config_assistente["sem_palavra_ativadora"]:
                mensagem = comando_recebido
            print("comando_recebido", comando_recebido)
            if comando_recebido in comando1:
                if (config_assistente["assistente_falante"]):
                    falar("Vai ligar", engine, voices, config_assistente["voz"])
                if config_assistente["com_arduino"]:
                    board.digital[config_assistente["pino"]].write(1)
            elif comando_recebido in comando2:
                if (config_assistente["assistente_falante"]):
                    falar("Vai Desligar", engine, voices, config_assistente["voz"])
                if config_assistente["com_arduino"]:
                    board.digital[config_assistente["pino"]].write(0)
        elif comecodafrase in chamar_assistente_ChatGPT or config_assistente["sem_palavra_ativadora_chatgpt"]:
            if len(comecodafrase) > 0:
                mensagem = comando_recebido[len(comecodafrase) + 1:]
            elif config_assistente["sem_palavra_ativadora_chatgpt"]:
                mensagem = comando_recebido
            print("comando_recebido", mensagem)
            mensagens = zerarMensagens()
            mensagens.append({"role": "user", "content": str(mensagem)})
            answer = generate_answer(mensagens)

            resposta = answer[0]
            preco = answer[1]

            print("ChatGPT:", resposta)
            if (config_assistente["assistente_falante"]):
                falar(resposta, engine, voices, config_assistente["voz"])
    return "Fim"

if __name__ == '__main__':
    texto = main()
    print(texto)
