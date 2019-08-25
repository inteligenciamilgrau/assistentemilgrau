import cv2 # pip install opencv-python

print("Versão do OpenCV:", cv2.__version__)

webCam = cv2.VideoCapture(1)

while(True):
    conectou, imagem = webCam.read()
    cv2.imshow("Rosto", imagem)
    
    teclou = cv2.waitKey(1) & 0xFF
    if teclou == ord('q') or teclou == 27: # se apertar q ou ESC
        break

webCam.release()
cv2.destroyAllWindows()
