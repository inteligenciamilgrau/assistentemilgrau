import time
import socket

def enviarMensagem(comandar,tempo):

        message = (comandar).encode()
                            
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_address = ('192.168.4.1', 1234)
        sock.connect(server_address)
        sock.sendall(message)
        sock.close()
        
        time.sleep(tempo)

enviarMensagem("ligar", 0)
enviarMensagem("garra20", 2)
enviarMensagem("base70", 2)
enviarMensagem("base120", 2)
enviarMensagem("base90", 2)
enviarMensagem("frente50", 2)
enviarMensagem("frente20", 2)
enviarMensagem("garra90", 2)
enviarMensagem("garra20", 2)
enviarMensagem("desligar", 0)
