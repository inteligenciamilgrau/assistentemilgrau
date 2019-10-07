import time
import socket
import cv2

H_MIN = 0
H_MAX = 255
S_MIN = 0
S_MAX = 255
V_MIN = 0
V_MAX = 255

#default capture width and height
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
#max number of objects to be detected in frame
MAX_NUM_OBJECTS=50
#minimum and maximum object area
MIN_OBJECT_AREA = 20*20
MAX_OBJECT_AREA = FRAME_HEIGHT*FRAME_WIDTH/1.5
#names that will appear at the top of each window
windowName = "Original Image"
windowName1 = "HSV Image"
windowName2 = "Thresholded Image"
windowName3 = "After Morphological Operations"
trackbarWindowName = "Trackbars"
testando = 0

## integração com arduino
def enviarMensagem(comandar,tempo):

        #print(comandar)  #para fins de debug
        message = (comandar).encode()
                            
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_address = ('192.168.4.1', 1234)
        sock.connect(server_address)
        sock.sendall(message)
        sock.close()
        
        time.sleep(tempo)
        
def explorar():
    global posicaoBase, voltar, limiteIda, limiteVoltar, configuraTreshHold
      
    if posicaoBase >= 0 and not configuraTreshHold:
        enviarMensagem("base" + str(posicaoBase), 0.1)
        
        if posicaoBase == limiteVoltar:
            voltar = True
        elif posicaoBase == limiteIda:
            voltar = False
            
        if voltar:
            posicaoBase = posicaoBase - 1
        else:
            posicaoBase = posicaoBase + 1

#iniciando braço robótico
alturaSobe = 178
posicaoFrente = 30
posicaoBase = 90
voltar = False
limiteVoltar = 130
limiteIda = 40
configuraTreshHold = True

enviarMensagem("ligar", 0)
enviarMensagem("base" + str(posicaoBase), 0.4)
enviarMensagem("sobe" + str(alturaSobe), 0.4)
enviarMensagem("frente" + str(posicaoFrente), 0.4)
enviarMensagem("garra90", 0.4)

# arduino integrado

def nothing(val):
    pass 

def createTrackbars():
    cv2.namedWindow(trackbarWindowName,cv2.WINDOW_NORMAL)
    
    cv2.resizeWindow(trackbarWindowName, 600, 400) # caso a trackbar fique muito grande

    cv2.createTrackbar("H_MIN",trackbarWindowName,H_MIN, H_MAX, nothing)
    cv2.createTrackbar("H_MAX",trackbarWindowName,H_MAX, H_MAX, nothing)
    cv2.createTrackbar("S_MIN",trackbarWindowName,S_MIN, S_MAX, nothing)
    cv2.createTrackbar("S_MAX",trackbarWindowName,S_MAX, S_MAX, nothing)
    cv2.createTrackbar("V_MIN",trackbarWindowName,V_MIN, V_MAX, nothing)
    cv2.createTrackbar("V_MAX",trackbarWindowName,V_MAX, V_MAX, nothing)

def drawObject(x,y,frame):

    x = int(x)
    y = int(y)
    cv2.circle(frame,(x,y),20,(0,255,0),2);
    if(y-25>0):
        cv2.line(frame,(x,y),(x,y-25),\
                 (0,255,0),2)
    else:
        cv2.line(frame,(x,y),(x,0)\
                 ,(0,255,0),2)
    if(y+25<FRAME_HEIGHT):
        cv2.line(frame,(x,y),(x,y+25),\
                 (0,255,0),2)
    else:
        cv2.line(frame,(x,y),(x,FRAME_HEIGHT),\
                 (0,255,0),2)
    if(x-25>0):
        cv2.line(frame,(x,y),(x-25,y),\
                 (0,255,0),2)
    else:
        cv2.line(frame,(x,y),(0,y),\
                 (0,255,0),2)
    if(x+25<FRAME_WIDTH):
        cv2.line(frame,(x,y),(x+25,y),\
                 (0,255,0),2)
    else:
        cv2.line(frame,(x,y),(FRAME_WIDTH,y),\
                 (0,255,0),2)

    cv2.putText(frame,str(x)+","+str(y),\
                (x,y+30),1,1,(0,255,0),2)


def morphOps(thresh):

    erodeElement = cv2.getStructuringElement(cv2.MORPH_RECT,(3,3))
    dilateElement = cv2.getStructuringElement(cv2.MORPH_RECT,(8,8))

    thresh = cv2.erode(thresh,erodeElement)
    thresh = cv2.erode(thresh,erodeElement)

    thresh = cv2.dilate(thresh,dilateElement)
    thresh = cv2.dilate(thresh,dilateElement)
    
    return thresh

def trackFilteredObject(x, y, threshold, cameraFeed):
    global testando 
    
    temp = threshold

    (_,contours,hierarchy) = cv2.findContours(temp,cv2.RETR_CCOMP,cv2.CHAIN_APPROX_SIMPLE)
    refArea = 0
    objectFound = False
    try:
        if (hierarchy.size > 0):
            numObjects = hierarchy.size/4
            if(numObjects<MAX_NUM_OBJECTS):
                index = 0
                while index >= 0:
                    moment = cv2.moments(contours[index])
                    area = moment['m00']
                    if(area>MIN_OBJECT_AREA and area<MAX_OBJECT_AREA and \
                       area>refArea):
                        x = moment['m10']/area
                        y = moment['m01']/area
                        objectFound = True
                        refArea = area
                    else:
                        objectFound = False
                    index = hierarchy[0][index][0]
                    testando = hierarchy
                        
            if(objectFound == True):
                cv2.putText(cameraFeed,"Tracking Object",(0,50),2,1,(0,255,0),2);
                drawObject(x,y,cameraFeed)
            return x # Alteração # variavel que envia o X calculado
        else:
            cv2.putText(cameraFeed,"TOO MUCH NOISE! ADJUST FILTER",(0,50),1,2,(0,0,255),2);
    
    except:
        pass
    
def main():
    global configuraTreshHold, voltar
    
    trackObjects = True
    useMorphOps = True
    
    x = 0
    y = 0

    createTrackbars();

    capture = cv2.VideoCapture(1)

    capture.set(cv2.CAP_PROP_FRAME_WIDTH,FRAME_WIDTH)
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT,FRAME_HEIGHT)

    while(1):
        ret, cameraFeed = capture.read()
        cameraFeed = cv2.flip(cameraFeed, -1)
        HSV = cv2.cvtColor(cameraFeed,cv2.COLOR_BGR2HSV)
        threshold = cv2.inRange(HSV,\
                (cv2.getTrackbarPos("H_MIN",trackbarWindowName),\
                 cv2.getTrackbarPos("S_MIN",trackbarWindowName),\
                 cv2.getTrackbarPos("V_MIN",trackbarWindowName)),\
                 (cv2.getTrackbarPos("H_MAX",trackbarWindowName),\
                 cv2.getTrackbarPos("S_MAX",trackbarWindowName),\
                 cv2.getTrackbarPos("V_MAX",trackbarWindowName)))

        if(useMorphOps):
            threshold = morphOps(threshold)

        if(trackObjects):
            # recebe o X da mira
            posicaoAtualX = trackFilteredObject(x,y,threshold,cameraFeed);

        # adiciona um circulo na tela para referencia para o robo
        cv2.circle(cameraFeed,(int(FRAME_WIDTH/2),
                               int(FRAME_HEIGHT*(1/6))),5,(255,255,0),2);
        cv2.imshow(windowName2,threshold)
        cv2.imshow(windowName,cameraFeed)
        cv2.imshow(windowName1,HSV)
        
        # integra com o rastreamento
        if posicaoAtualX: 
            erro = posicaoAtualX - FRAME_WIDTH/2
            #print(erro) # para fins de debug
            
            if erro > 0: # define para qual lado buscar
                voltar = False
            else:
                voltar = True
                
            erroSetPoint = 15
            if erro > erroSetPoint or erro < -erroSetPoint:
                explorar()
            else:
                pass
        else:
            explorar()
		
        teclou = cv2.waitKey(30) & 0xFF
        if teclou == ord('q') or teclou == 27: # se apertar q ou ESC
            capture.release()
            cv2.destroyAllWindows()
            enviarMensagem("desligar", 0)
            break
        if teclou == ord('c'): # teclar c para configurar o trash hold
            configuraTreshHold = not configuraTreshHold

if __name__ == "__main__":
    main()
