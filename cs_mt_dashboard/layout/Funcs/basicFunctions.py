'''import API.APImir as APImir, shellyGateControl as shellyGateControl, defs as defs, MIRstatus as MIRstatus
import time
from tuya_relay_python import connect_to_relay'''
import layout.Funcs.API.APImir as APImir, layout.Funcs.defs as defs, layout.Funcs.MIRstatus as MIRstatus
import time


def clearqueue():
    return APImir.mirRequest("DELETE", "/mission_queue") 

def doMission(mission_id):
    data = {"mission_id": mission_id}
    return APImir.mirRequest("POST","/mission_queue", data)

#turns selected pos from dropdown to mission
def createAction(action):
    data = action
    response = APImir.mirRequestACT(
        "POST",
        f"/missions/{defs.DropDown}/actions",
        json = data)
    time.sleep(2)
    doMission(defs.DropDown)
    actionGUID = response.get('guid')
    time.sleep(10)
    deleteAction(actionGUID)
    #print(response)
    
    return 
#clears dropdown mission for next time
def deleteAction(actionGUID):
    data = actionGUID
    APImir.mirRequestACT(
        "DELETE",
        f"/missions/{defs.DropDown}/actions/{data}",
    )
    return 

def doMissionPOS(data):
    #data = {"mission_id": data}
    return APImir.mirRequest("POST","/mission_queue", data)


def disToTarget():
    statusData = APImir.mirRequest("GET", "/status") 
    return round(statusData.get("distance_to_next_target"))


def checkPLC1():
    plc1 = APImir.mirRequest('GET','/registers/1')
    value = plc1.get('value')
    return value

def setPLC1():
    doMission(defs.plc12)
    return

'''def pickUp():
    while checkPLC1() == 0  :
        time.sleep(1)  

        if checkPLC1() == 1: #waits for docking mission to finish
            print("Preparing pistons")
            #connect_to_relay.pick()
            time.sleep(3)  
            pistonUp() 
            setPLC1()
            #time.sleep(2)
            return 

def placeDown():
    while checkPLC1() == 0:
        time.sleep(1)  

        if checkPLC1() == 1:
            print("Preparing pistons")
            #connect_to_relay.place()
            time.sleep(5) 
            pistonDown()
            setPLC1() 
            time.sleep(2)  
            return
        
def pistonUp(): #tells dashboard status of pistons
    with open('layout/assets/pistonStat.txt', 'wt') as f:
        f.write('1')    
    return
def pistonDown():
    with open('layout/assets/pistonStat.txt', 'wt') as f:
        f.write('0')  
    return'''


#################################################################    
#BAY 1  old      
#################################################################  
'''def pickUpSequenceB1():
    doMission(defs.dockToShelfB1)
    doMission(defs.footprintWithShelf)
    pickUp()
    while checkPLC1() == 1:
        time.sleep(1)
        if checkPLC1() == 2:
            #time.sleep(5)
            doMission(defs.leaveDock)
            return
        
def depositSequenceB1():
    doMission(defs.dockToShelfB1)
    doMission(defs.defaultFootprint)
    placeDown()
    while checkPLC1() == 1:
        time.sleep(1)
        if checkPLC1() == 2:
            #time.sleep(5)
            doMission(defs.leaveDock)
            return'''
#################################################################    
#BAY 2  old
#################################################################  
'''def pickUpSequenceB2():
    doMission(defs.dockToShelfB2)
    doMission(defs.footprintWithShelf)
    pickUp()
    while checkPLC1() == 1:
        time.sleep(1)
        if checkPLC1() == 2:
            #time.sleep(2)
            doMission(defs.leaveDock)
            return

def depositSequenceB2():
    doMission(defs.dockToShelfB2)
    doMission(defs.defaultFootprint)
    placeDown()
    while checkPLC1() == 1:
        time.sleep(1)
        if checkPLC1() == 2:
            time.sleep(2)
            doMission(defs.leaveDock)
            return'''

