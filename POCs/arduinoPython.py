import serial
import threading
import time

conectado = False
porta = 'COM3' # linux ou mac em geral -> '/dev/ttyS0'
velocidadeBaud = 115200

mensagensRecebidas = 1;
desligarArduinoThread = False

try:
    SerialArduino = serial.Serial(porta,velocidadeBaud, timeout = 0.2)
except:
    print("Verificar porta serial ou religar arduino")

def handle_data(data):
    global mensagensRecebidas
    print("Recebi " + str(mensagensRecebidas) + ": " + data)
    mensagensRecebidas += 1

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
    try:
        print("Enviando")
        SerialArduino.write('ligar luzes\n'.encode())
        time.sleep(2)
    except KeyboardInterrupt:
        print("Apertou Ctrl+C")
        desligarArduinoThread = True
        SerialArduino.close()
        lerSerialThread.join()
        break
