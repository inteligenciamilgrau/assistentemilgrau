import queue
import numpy as np
import sounddevice as sd
import tensorflow as tf
from tkinter import Tk, Canvas, PhotoImage, NW
from ctypes import windll

avatar_player = "yellow"
mic_device = 0  # id of the audio device by default
sempre_por_cima = True

## opcional: codigo para tirar a barra sem remover o icone
GWL_EXSTYLE=-20
WS_EX_APPWINDOW=0x00040000
WS_EX_TOOLWINDOW=0x00000080

def set_appwindow(root):
    hwnd = windll.user32.GetParent(root.winfo_id())
    style = windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
    style = style & ~WS_EX_TOOLWINDOW
    style = style | WS_EX_APPWINDOW
    windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)
    root.wm_withdraw()
    root.after(3000, lambda: root.wm_deiconify())


root = Tk()
root.attributes('-transparentcolor','#f0f0f0')
if sempre_por_cima:
    root.attributes('-topmost', True) # sempre no topo
canvas = Canvas(root, width=520, height=600)
canvas.pack()

if avatar_player == "bob":
    img_fechada_tk = PhotoImage(file="mouths/boca_bob_1.png")
    img_fechada_tk = img_fechada_tk.subsample(3)

    img_pose1_tk = PhotoImage(file="poses/pose_bob_crop_1.png")
    img_pose1_tk = img_pose1_tk.subsample(3)

    abertura_boca = 10
    mouth_position = (284, 198)

    pose_container = canvas.create_image(0, 0, anchor=NW, image=img_pose1_tk)
    mouth_container = canvas.create_image(mouth_position[0], mouth_position[1], anchor=NW, image=img_fechada_tk)

elif avatar_player == "golfinho":
    img_fechada_tk = PhotoImage(file="mouths/dolphin_1_mouth.png")
    img_fechada_tk = img_fechada_tk.subsample(2)

    img_pose1_tk = PhotoImage(file="poses/dolphin_1_pose.png")
    img_pose1_tk = img_pose1_tk.subsample(2)

    abertura_boca = 6
    mouth_position = (110, 60 + abertura_boca)

    pose_container = canvas.create_image(0, 0, anchor=NW, image=img_pose1_tk)
    mouth_container = canvas.create_image(mouth_position[0], mouth_position[1], anchor=NW, image=img_fechada_tk)
elif avatar_player == "yellow":
    img_fechada_tk = PhotoImage(file="mouths/mouth0009.png")
    img_aberta_tk = PhotoImage(file="mouths/mouth0001.png")
    img_pose1_tk = PhotoImage(file="poses/pose0082.png")
    mouth_position = (100,300)
    pose_container = canvas.create_image(-220, -220, anchor=NW, image=img_pose1_tk)
    mouth_container = canvas.create_image(mouth_position[0], mouth_position[1], anchor=NW, image=img_fechada_tk)

sem_borda = True
if sem_borda:
    root.overrideredirect(True)  # remove a barra
    root.after(500, lambda: set_appwindow(root))

lastClickX = 0
lastClickY = 0
def SaveLastClickPos(event):
    global lastClickX, lastClickY
    lastClickX = event.x
    lastClickY = event.y


def Dragging(event):
    x, y = event.x - lastClickX + root.winfo_x(), event.y - lastClickY + root.winfo_y()
    root.geometry("+%s+%s" % (x , y))

desligar_assistente = False
def desligar(event):
    global desligar_assistente
    desligar_assistente = True

root.bind('<Button-3>', SaveLastClickPos)
root.bind('<B3-Motion>', Dragging)
root.bind("<ButtonRelease-2>", desligar)

model = tf.keras.models.load_model('2023_04_28_01_09_03_950295.h5')
tamanho_amostra = 4000

# Lets define audio variables
# We will use the default PC or Laptop mic to input the sound

window = 1000  # window for the data
downsample = 1  # how much samples to drop
channels = [1]  # a list of audio channels
interval = 30  # this is update interval in miliseconds for plot

# lets make a queue
q = queue.Queue()
# Please note that this sd.query_devices has an s in the end.
device_info = sd.query_devices(mic_device, 'input')
samplerate = device_info['default_samplerate']
length = int(window * samplerate / (1000 * downsample))
# lets print it
print("Sample Rate: ", samplerate)
# Now we require a variable to hold the samples
plotdata = np.zeros((length, len(channels)))
# Lets look at the shape of this plotdata
print("plotdata shape: ", plotdata.shape)

# We will use an audio call back function to put the data in queue
last_state = ""

def audio_callback(indata, frames, time, status):
    global last_state
    # global plotdata
    q.put(indata[::downsample, [0]])

""" INPUT FROM MIC """
stream = sd.InputStream(device=mic_device, channels=max(channels), samplerate=samplerate, callback=audio_callback)

with stream:
    while not desligar_assistente:
        while True:
            try:
                data = q.get_nowait()
            except queue.Empty:
                break
            shift = len(data)
            plotdata = np.roll(plotdata, -shift, axis=0)

            # Elements that roll beyond the last position are
            # re-introduced
            plotdata[-shift:, :] = data

        testar = plotdata[-tamanho_amostra:].copy()
        try:
            result = model.predict(testar.T, verbose=0)
            resultado = {0: "Fechando", 1: "Abrindo"}
            final = resultado[np.argmax(result)]

            x_offset = 200
            y_offset = 250

            if final == "Fechando" and not last_state == "Fechando":
                last_state = "Fechando"

                if avatar_player == "bob" or avatar_player == "golfinho":
                    canvas.move(mouth_container, 0, -abertura_boca)
                elif avatar_player == "yellow":
                    canvas.itemconfig(mouth_container, image=img_fechada_tk)

            elif final == "Abrindo" and not last_state == "Abrindo":
                last_state = "Abrindo"

                if avatar_player == "bob" or avatar_player == "golfinho":
                    canvas.move(mouth_container, 0, abertura_boca)
                elif avatar_player == "yellow":
                    canvas.itemconfig(mouth_container, image=img_aberta_tk)

        except Exception as e:
            print("rede ruim", e)
        root.update()
