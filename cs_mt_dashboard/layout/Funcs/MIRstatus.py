'''import basicFunctions as basicFunctions
from API import APImir
import defs as defs
import shellyStatsForMir as shellyStatsForMir
import shellyGateControl as shellyGateControl'''
import layout.Funcs.basicFunctions as basicFunctions
from layout.Funcs.API import APImir
import layout.Funcs.defs as defs
import layout.Funcs.rosDiagnostics as rosDiagnostics
import time, json
import pandas as pd
import base64


#statusData = APImir.mirRequest("GET", "/status") 

def status():
    
    return    

def getBattery():
    battery, isCharging, hrs, mins, secs = rosDiagnostics.getBattery()
    if battery < 30 & isCharging == False:
        charging = True
        autoCharge()
    return battery
   # elif battery <= 53:
    #    
    #return battery
def autoCharge():
    charging = True
    basicFunctions.doMission(defs.chargingStation)
    stat = APImir.mirRequest("GET", "/status").get('mission_text')
    bat = APImir.mirRequest("GET", "/status").get('battery_percentage')
    if bat == '100.0':
        charging = False

    return
           
def isAvailable():
    statusData = APImir.mirRequest("GET", "/status")
    check = statusData.get('mission_text')
    print(check)
    true = 'Waiting for new missions...'
    if check == true:
        return 'available'
    else:
        return False            

    #return print[f"Battery: {round(batteryStat)}%"]
    return 
def timeRemaining(): 
    statusData = APImir.mirRequest("GET", "/status")
    totalSec = statusData.get("battery_time_remaining")
    sec = totalSec%60
    totalMinRem = (totalSec - sec)/60
    min = round(totalMinRem%60)
    hrs = round((totalMinRem - min)/60)
    #text = f"{hrs} hours, {min} minutes, {sec} seconds"
    return hrs, min, sec
    
def mapData():
    encoded = base64.b64encode(open("AllBays.png", "rb").read()).decode()
    return encoded 


def disToTarget():
    statusData = APImir.mirRequest("GET", "/status")
    dis = statusData.get("distance_to_next_target")  
    return round(dis)
    
def misText():
    statusData = APImir.mirRequest("GET", "/status")
    text = statusData.get('mission_text')
    
    return text

def modekeystate():
    statusData = APImir.mirRequest("GET", "/status")
    state = statusData.get('mode_key_state')
    if state == 'idle' and getBattery() > 20:
        return 'Available'
    else:
        return 'On a mission'

def getNet():
    statusData = APImir.mirRequest("GET", "/status")
    try:
        if statusData.status_code == 200:
            return 1 #connected
        else:
            return 2 # error
    except:
        return 3 #emergency stop/ offline
    
#################################################################    
#State IDs       
################################################################# 
def stateID():
    statusData = APImir.mirRequest("GET", "/status")
    stateid = statusData.get('state_id')
    if stateid == 0:
        return 'Starting up'
    elif stateid == 3:
        return 'Ready for mission'
    elif stateid == 4:
        return 'Paused'
    elif stateid == 10:
        return 'Emergency stop'
    elif stateid ==5:
        return 'Executing Mission'

def getError():
    statusData = APImir.mirRequest("GET", "/status")
    error = statusData.get('errors')
    if error == []:
        return 67
    else:
        return error



#df = pd.read_csv("MIRstatus.csv")
#main------------------------------------------