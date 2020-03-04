import websocket
import tkinter as tk 
from tkinter import filedialog,messagebox
#load for load and run mp3 file
from pygame import mixer 
#load for websocket
import asyncio
import websockets
import json
#load for image
from PIL import Image,ImageTk
import requests
from io import BytesIO
#load for datetime
from datetime import datetime
from threading import Thread
try:
    import thread
except ImportError:
    import _thread as thread
import time

def on_message(ws, message):
    try: 
      print(message)
      message_receive.set(message)
      # alert_with_pygame(json.loads(message))
    except Exception as error:
      ws.close()
      
            


def on_error(ws, error):
    # messagebox.showwarning(
    #     "Warning",
    #     "Can't connect to server websocket! "
    # )
    print(error)

def on_close(ws):
    chang_state_button(button2)
    chang_state_button(button_stop)
    label_image.config(image='')
    label_image.image=''
    state_websocket.set("NGAT ket noi !!!")
    response_from_server_ws.set("Wait for connect web-socket !")
    print("### closed ###")

def on_open(ws):
    def run(*args):
        for i in range(3):
            time.sleep(1)
            ws.send("Hello %d" % i)
        time.sleep(1)
        ws.close()
        print("thread terminating...")
    thread.start_new_thread(run, ())


def warning ():  
    label1 = tk.Label(root, text= 'Warning !', fg='green', font=('helvetica', 12, 'bold'))
    canvas.create_window(250, 200, window=label1)

def file_audio():
    try:
        file_name = filedialog.askopenfilename(title = "Select file",filetypes = (("mp3 files","*.mp3"),("all files","*.*")))
        text.set("Input your audio file (default is 'alert.mp3')")
    except:
        messagebox.showwarning(
            "Warning",
            "Input your audio file!"
        )
        text.set("Input your audio file (default is 'alert.mp3')")
        return
    text.set(file_name)

def alert_with_pygame(message_from_server,link_file_audio = '../alert.mp3'):
    try:
        mixer.init()
        get_link = text.get()
        link_file_audio = get_link if get_link !="Input your audio file (default is 'alert.mp3')"  else link_file_audio 
        # print(link_file_audio)
        mixer.music.load(link_file_audio)
        # warning()
        # print("stream_id: "+ message_from_server['stream_id'] + ' | Vehicle: '+ message_from_server['name'])
        # response_test.set("stream_id: "+ message_from_server['stream_id'] + ' | Vehicle: '+ message_from_server['name'])
        
        #THIS MUST EDIT FROM HERE
        timestamp = float(message_from_server['timestamp'])

        dt_object = datetime.fromtimestamp(timestamp)
        # print("dt_object =", dt_object)
        
        mess="Attendant at: "+ str(dt_object)
        response_from_server_ws.set(mess)
        print("HELLO")
        # url = "http://113.161.233.21:9001/img?frames=9550&id_folder=20200113092716&id_image=20200113092716283&bbox=945,159,117,136&crop=true"
        url=message_from_server['imageface']+"&crop=true"
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        img = img.resize((150,150))
        photo = ImageTk.PhotoImage(img)
        label_image.config(image=photo)
        # label_image['image'] = photo # keep a reference!
        label_image.image = photo # keep a reference!

        # label_image.image
      
        mixer.music.play()
        root.update()
    except:
        raise Exception("LOI KHONG MO DUOC FILE MP3")

def run_forever_when_recv_websocket():
    websocket_server = server_websocket.get()
    websocket.enableTrace(True)
    global ws
    ws = websocket.WebSocketApp(websocket_server,
                      on_message = on_message,
                      on_error = on_error,
                      on_close = on_close)
    # ws.on_open = on_open
    ws.run_forever()

def run_websocket_Threading():
    thread_ws = Thread(target = run_forever_when_recv_websocket,daemon=True)
    thread_ws.start()

    state_websocket.set("Da KET NOI !!!")
    chang_state_button(button2)
    chang_state_button(button_stop)
    response_from_server_ws.set("Wait for message from server")
    task_check_message()

def task_check_message():
    message = message_receive.get()
    message_receive.set("")
    if message:
        print ("DA NHAN DUOC  MESSAGE: "+message)
        alert_with_pygame(json.loads(message))
        # message_receive.set("")
    # else :
    #     print("KHONG NHAN DUOC TIN NHAN NAO")
    loop()

def loop():
    root.after(100,task_check_message)

def stop_connect_websocket():
    ws.close()


def chang_state_button(button):
	state = button['state']
	if state == 'disabled':
		button.config(state='normal',bg='brown')
	elif state == 'normal':
		button.config(state='disabled',bg='white')

root= tk.Tk()
root.title("app_lert")

canvas = tk.Canvas(root, width = 500, height = 500)
canvas.pack()
    
button1 = tk.Button(text='INPUT AUDIO',command=file_audio, bg='brown',fg='white')
canvas.create_window(250, 50, window=button1)

text =  tk.StringVar() 
label_text=tk.Label(root,textvariable=text)
text.set("Input your audio file (default is 'alert.mp3')")
canvas.create_window(250,80,window = label_text)

server_websocket =  tk.StringVar()
# server_websocket.set("ws://analytic.vnpttiengiang.vn:30555/ws/detected_objects")
server_websocket.set("ws://113.161.233.21:8081/ws/alerted_objects/00000000-0000-0000-0000-000000000019") 
# server_websocket.set("ws://192.168.55.165:1234")

#label to show image
label_image = tk.Label(root)
canvas.create_window(250,380,window=label_image)

entry_server_websocket=tk.Entry(root,textvariable=server_websocket,width=60)
canvas.create_window(250,110,window = entry_server_websocket)

button2 = tk.Button(text='RUN',command=run_websocket_Threading, width=5, bg='brown',fg='white')
canvas.create_window(220, 140, window=button2)
button_stop = tk.Button(text='STOP',command=stop_connect_websocket, width=5, bg='brown',fg='white')
canvas.create_window(280, 140, window=button_stop)

#state of websocket
state_websocket = tk.StringVar()
state_websocket.set("Chua Ket Noi")
label_state_websocket = tk.Label(root,textvariable=state_websocket)
canvas.create_window(250,175,window=label_state_websocket)

#print response to UI
response_test = tk.StringVar()
label_response_from_server = tk.Label(root,textvariable=response_test)
canvas.create_window(250,230,window=label_response_from_server)

#reponse from server
response_from_server_ws = tk.StringVar()
# response_from_server_ws.set("Wait for connect websocket")
label_response_from_server = tk.Label(root,textvariable=response_from_server_ws)
canvas.create_window(250,260,window=label_response_from_server)

chang_state_button(button_stop)

message_receive = tk.StringVar()
message_label = tk.Label(root,textvariable=message_receive)
canvas.create_window(250,480,window=message_label)

# def disable_event():
#     print("exit complete application")
#     root.destroy()

# root.protocol("WM_DELETE_WINDOW", disable_event)

# def task():
#     print("HELLO")
# root.after(1000,task)time_send

root.mainloop()