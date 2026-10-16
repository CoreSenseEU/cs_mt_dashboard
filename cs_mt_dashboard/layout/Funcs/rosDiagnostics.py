import websocket
import json
import threading
import layout.Funcs.defs as defs
import time

#add gesture recognition??
#import yolo
#publish results(labels ect) to a new topic

signal = None
battery = None
batteryTime = None
isCharging = None
frontLaser = None
backLaser = None
emergencyButt = None
laserFreq = None #get avg of front & back

#wifi - signal level
def on_message(ws, message):
    global signal
    global battery, batteryTime, isCharging
    global frontLaser, backLaser
    global emergencyButt
    data = json.loads(message)
    #bypass rosbridge wrapper
    if data.get("topic") == "/diagnostics":
        for status in data["msg"]["status"]:
            for kv in status.get("values", []):
                #signal
                if kv["key"] == "Signal Level":
                    signal = kv["value"]
                #battery
                if kv["key"] == "Remaining battery capacity [%]":
                    battery = kv["value"]
                if kv["key"] == "Remaining battery time [HH:MM:SS]":
                    batteryTime = kv["value"]
                if kv["key"] == "Charging relay":
                    isCharging = kv["value"]
                #lasers
                if kv["key"] == "Laser (Front)":
                    frontLaser = kv["value"]
                if kv["key"] == "Laser (Back)":
                    backLaser = kv["value"]
                #emergency stop
                if kv["key"] == "Emergency button": #?????
                    emergencyButt = kv["value"]


def on_open(ws):
    # subscribe to topic
    subscribe_msg = {
        "op": "subscribe",
        "topic": "/diagnostics"
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


def getsignal():
    global signal
    while signal is None:
        time.sleep(1)
  
    signal = signal.replace('dBm', '')
    signal = signal.replace('-','')
    return signal

def getBattery():
    global battery
    global batteryTime
    global isCharging

    while battery is None:
        time.sleep(1)
    while batteryTime is None:
        time.sleep(1)
    while isCharging is None:
        time.sleep(1)

    if battery is not None:
        battery = battery
        batteryTime = batteryTime #fix hrs mins secs
        isCharging = isCharging
        #breakdown time
        #hr:mi:se
        #01 34 67
        hrs = batteryTime[0:2]
        mins = batteryTime[3:5]
        secs = batteryTime[6:8]

        return battery, isCharging, hrs, mins, secs


