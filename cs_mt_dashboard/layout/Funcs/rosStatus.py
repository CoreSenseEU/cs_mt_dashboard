import websocket
import json
import threading
import layout.Funcs.defs as defs

import time

#rosIP = '192.168.30.116'
#import yolo
status = None

def on_message(ws, message):
    global status
    wrapper = json.loads(message)
    #bypass rosbridge wrapper    
    if wrapper.get("topic") == "/mir_status_msg":
        inner = wrapper['msg']['data']
        data = json.loads(inner)
        template = data["message"]
        args = data["args"]
        status = template % args

def on_open(ws):
    subscribe_msg = {
        "op": "subscribe",
        "topic": "/mir_status_msg"
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

def getStatus():
    global status
    if status == None:
        time.sleep(1)
        #print("couldnt parse")
    if status != None:
        #print(status)
        return status


getStatus()
