import websocket
import json
import threading
import layout.Funcs.defs as defs
import time

#rosIP = '192.168.30.116'
#import yolo
global px, py, pz
global ox, oy, oz, ow
global data
px = None
pz = None
py = None

def on_message(ws, message):
    global status
    global px, py, pz
    global data
    data = json.loads(message)
    
    if data.get("topic") == "/amcl_pose":
        position = data["msg"]["pose"]["pose"]["position"]
        px = position["x"]
        py = position["y"]
        pz = position["z"]

def on_open(ws):
    subscribe_msg = {
        "op": "subscribe",
        "topic": "/amcl_pose"
    }
    ws.send(json.dumps(subscribe_msg))

ws = websocket.WebSocketApp(
    f"ws://{defs.rosIP}:9595",
    on_message=on_message,
    on_open=on_open
)

wst=threading.Thread(target=ws.run_forever)
wst.daemon = True
wst.start()

def getPos():
    global status
    global px, py, pz
    if px == None:
        time.sleep(1)
        #print("waiting")
    else:
        #print(px, py, pz)
        return px, py, pz

def getLocation():
    getPos()
    global px
    #print(px)
    if px is not None:
        if px > 61:
            robotLocation = 1
        if px > 43 and px < 61:
            robotLocation = 2
        if px < 43:
            robotLocation = 3
        return robotLocation
