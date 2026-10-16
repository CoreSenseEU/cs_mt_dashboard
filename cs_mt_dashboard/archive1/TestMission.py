import requests
import json
import TestStuff.MissionsTest as MissionsTest
import TestStuff.SoundsTest as SoundsTest
#--------------------------------------------------------------------------------------------------------------------------
# MiR100 IP and credentials
mirIP = "192.168.30.17"
username = "distributor"
password = "distributor"
baseURL = "http://192.168.30.17/api/v2.0.0"
#--------------------------------------------------------------------------------------------------------------------------
#helper function
def mirRequest(method, endpoint, data = None):   #method=get/post/delete
    url = baseURL + endpoint

    headers  = {
        "Authorization": "Basic ZGlzdHJpYnV0b3I6NjJmMmYwZjFlZmYxMGQzMTUyYzk1ZjZmMDU5NjU3NmU0ODJiYjhlNDQ4MDY0MzNmNGNmOTI5NzkyODM0YjAxNA==",
        "Accept-Language" : "en_US",
        "Content-Type": "application/json"
    }


    response = requests.request(
        method, 
        url,
        headers = headers,
        json=data,
        #auth=(username, password)
    )

    print(response.text)
    try:
        return response.json()   #translates & returns response from robot to us
    except ValueError:
        return response.text
#--------------------------------------------------------------------------------------------------------------------------
#robot actions

def clearqueue():
    return mirRequest("DELETE", "/mission_queue")
                      
                      
def goto(mission_id):
    data = {"mission_id": mission_id}
    return mirRequest("POST","/mission_queue", data)

#--------------------------------------------------------------------------------------------------------------------------
#main method
if __name__ == "__main__":

    i = 0

    print("on my way dawg")
    clearqueue()

    while i<=2:
        goto(MissionsTest.End)
        goto(MissionsTest.Start)
        i += 1





    
