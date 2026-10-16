import math, time, json
import roslibpy
import layout.Funcs.defs as defs
#send position coords to ros2 mission script?

#00rosIP ='192.168.30.25' #defs.rosIP
rosIP = '10.100.200.204' #ethernet

client = roslibpy.Ros(host=rosIP, port=9595)
client.run()

dock_pub = roslibpy.Topic(client, '/dash_dock', 'std_msgs/String')
goal_pub = roslibpy.Topic(client, '/dash_goal', 'std_msgs/String')

def dock(name, ep): 
    print('publishing dock topic')
    #publisher = roslibpy.Topic(client, '/dash_dock', 'std_msgs/String')
    info = json.dumps({'name': name, 'pos': ep})
    msg = roslibpy.Message({'data': info})
    dock_pub.publish(msg)
    print('close')

def goal(name, goal):
    #publisher = roslibpy.Topic(client, '/dash_goal', 'std_msgs/String')
    info = json.dumps({'name': name, 'pos': goal})
    msg = roslibpy.Message({'data': info})
    #goal_pub.publish(msg)

def mapGoal(x, y, w):
    print('publishing map goal')
    #ublisher = roslibpy.Topic(client, '/dash_goal', 'std_msgs/String')
    info = json.dumps({'x': x, 'y': y, 'w': w})
    msg = roslibpy.Message({'data': info})
    goal_pub.publish(msg)



def charge():
    print('charge called')
    name = 'charger'
    ep = defs.chargerEP
    dock(name, ep)
    return 

def b1():
    name = 'charger'
    ep = defs.bay1EP
    dock(name, ep)
    return 

def b2():
    name = 'charger'
    ep = defs.bay2EP
    dock(name, ep)
    return 

'''ep = '[33.255, 44.786, -3.124157]'
name = 'charger'
dock(name, ep)
time.sleep(1)
dock(name, ep)
client.terminate()'''