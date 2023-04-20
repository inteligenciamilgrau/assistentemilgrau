from pyfirmata import Arduino # pip install pyfirmata
import time

def main():
    print("Iniciando Assistente")

    porta = "COM10"
    try:
        board = Arduino(porta)
    except Exception as e:
        print("Sem Arduino na porta", porta)
        return "Saindo"

    pino = 8
    contar = 0

    while contar < 4:
        print(contar)
        board.digital[pino].write(1)
        time.sleep(1)
        board.digital[pino].write(0)
        time.sleep(1)

        contar += 1

    return "Funcionou"

if __name__ == '__main__':
    texto = main()
    print(texto)