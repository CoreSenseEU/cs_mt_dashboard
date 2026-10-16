from layout.Funcs.basicFunctions import doMission, checkPLC1
import layout.Funcs.defs as defs
from layout.Funcs.API import APImir
import time
import json
import requests
import csv

def charge():
    check()
    misText = 'Going to charger'
    doMission(defs.chargingStation)
    charging()
    return 
'''
def cfb1():#collect shelf from bay 1
    print('adding to plc2')
    check()
    print('Collecting trolley from Bay 1')
    doMission(defs.dockToShelfB1)
    doMission(defs.footprintWithShelf)
    print('picking up shelf')
    pickUp()
    print('leaving dock')
    doMission(defs.leaveDock)   
    doMission(defs.plc2add)
    return

def dab1(): #deposit shelf at b1
    check()
    print('Depositing trolley at Bay 1')
    doMission(defs.dockToShelfB1)
    doMission(defs.defaultFootprint)
    placeDown()
    print('leaving')
    doMission(defs.leaveDock)   
    doMission(defs.plc2add)
    return

def dab2(): #deposit bay 2 dock
    check()
    print('Depositing trolley at Bay 2')
    doMission(defs.dockToShelfB2)
    doMission(defs.defaultFootprint)
    placeDown()
    print('leaving')
    doMission(defs.leaveDock)   
    doMission(defs.plc2add)
    return 



def cfb2(): #collect from bay2
    check()
    print('Collecting trolley from Bay 2')
    doMission(defs.dockToShelfB2)
    doMission(defs.footprintWithShelf)
    pickUp()
    print('leaving')
    doMission(defs.leaveDock)   
    doMission(defs.plc2add)  
    return'''

def da(): #testing for now
    check()
    doMission(defs.LeahsDesk)
    
    return
def bay3():
    doMission(defs.LeahsDesk)
    #doMission(defs.plc2add)   
    return

def cfb1NP():#collect shelf from bay 1
    print('Collecting trolley from Bay 1')
    doMission(defs.dockToShelfB1)
    doMission(defs.leaveDock)   
    return

def dab1NP(): #deposit shelf at b1
    print('Depositing trolley at Bay 1')
    doMission(defs.dockToShelfB1)
    doMission(defs.leaveDock)   
    return

def dab2NP(): #deposit bay 2 dock
    print('Depositing trolley at Bay 2')
    doMission(defs.dockToShelfB2)
    doMission(defs.leaveDock)   
    return



def cfb2NP(): #collect from bay2
    print('Collecting trolley from Bay 2')
    doMission(defs.dockToShelfB2)
    doMission(defs.leaveDock)   
    return

def daNP(): #testing for now
    doMission(defs.LeahsDesk)
    
    return
def bay3NP():
    doMission(defs.LeahsDesk)
    #doMission(defs.plc2add)   
    return

#----marathon stuff------------
def marathonNP(): #no pickup
    x = 0
    while x < 100:
        cfb1NP()
        dab2NP()
        bay3NP()
        cfb2NP()
        dab1NP()
        bay3NP()
        x = x+1
    return
'''
def marathon():
    i = 0 #laps
    j = 1
    while i <= 100 and j < 10:
        
        #print('checking plc')
        #doMission(defs.plc2reset)
        while checkPLC2() == 0:
            print(f'Marathon Lap {i}')
            doMission(defs.plc2add)
            print('plc = 0, collecting from b1')
            cfb1()
       
            
        while checkPLC2() == 2:

            doMission(defs.plc2add)
            print('plc = 2, depositing at b2')
            dab2()
            
        while checkPLC2() == 4:

            doMission(defs.plc2add)
            print('plc = 4, going to b3')
            bay3()
            time.sleep(10)
            
        while checkPLC2() == 6:
 
            doMission(defs.plc2add)
            print('plc = 6, collecting from b2')
            cfb2()
            
        while checkPLC2()== 8:
            doMission(defs.plc2add)
            print('plc = 8, depositing at b1')
            dab1()
            i = i + 1
            print('resetting plc2')
            
            doMission(defs.plc12)
            doMission(defs.leaveDock)
            doMission(defs.plc2reset)
    return'''
#-------------------------------------

def clearQ():
    return APImir.mirRequest("DELETE", "/mission_queue")


def checkPLC2():
    plc2 = APImir.mirRequest('GET','/registers/2')
    value = plc2.get('value')
    return value
#----------------BAY 2 logic ------------------------------------

def b2LEFT(): #deposit left bay2
    doMission(defs.Desk1)
    inc() #tells program mir is intside gate, & will need to run exit sequence to carry out next mission
    return 

def check(): #checks if mir is inside gate
    print('checking if in gate 1')
    with open('layout/assets/data.txt', 'rt') as f:
        x = f.read()
        f.close()
        if '2' in x:
            print('Leaving charging station.')
            doMission(defs.leaveCharger) #reverses out of dock to avoid spinning & hitting sides
        if '1' in x:
            print('In gate, executing exit mission.')
        if '0' in x:
            print('Not in gate, continuing.')
        return
 
def inc(): #inside gate
    with open('layout/assets/data.txt', 'wt') as f:
        f.write('1')
    return 
def dec(): #not in gate
    with open('layout/assets/data.txt', 'wt') as f:
        f.write('0')
    return 
def charging():
    with open('layout/assets/data.txt', 'wt') as f:
        f.write('2')
    return 

def checktest(): 
    print('checking if in gate 1')
    with open('layout/assets/data.txt', 'rt') as f:
        x = f.read()
        f.close()
        print(x)
        if '1' in x:
            print('In gate, executing exit mission.')
            dec()
        if '0' in x:
            print('Not in gate, continuing.')
        return
    
# -------------Dropdown list----------------------

class positions:
    #writes guids and names of POSITIONS to csv    
    def refreshList():
        with open('layout/assets/PositionList.csv', 'r+') as f:
            f.readline() # read one line
            f.truncate(f.tell()) # terminate the file here
        headers  = {
            "Authorization": "Basic ZGlzdHJpYnV0b3I6NjJmMmYwZjFlZmYxMGQzMTUyYzk1ZjZmMDU5NjU3NmU0ODJiYjhlNDQ4MDY0MzNmNGNmOTI5NzkyODM0YjAxNA==",
            "Accept-Language" : "en_US",
            "Content-Type": "application/json"
        }
        url = 'http://192.168.30.45/api/v2.0.0/maps/bd07dd40-7461-11f1-80be-f44d306dcb63/positions'
        data = APImir.mirRequest('GET',f'/maps/{defs.allBays}/positions')
        response = requests.get(url, headers= headers)
        total = int(response.headers.get('x-total-count',0))

        i = 0
        allnames = []
        allguids = []
        while i < total:
            names = data[i].get('name')
            guids = data[i].get('guid')
            allnames.append(names)
            allguids.append(guids)
            i = i+1
        j = 0
        while j < total:
            fields = ['label', 'guid']
            data = [
                {f'label': allnames[j], 'guid': allguids[j]}
            ]


            with open('layout/assets/PositionList.csv', mode = 'at', newline='') as d:  
                
                writer = csv.DictWriter(d, fieldnames=fields)
                writer.writerows(data)
                j=j+1
                d.close()
        return
    
    #func to turn to mission in basicFunctions