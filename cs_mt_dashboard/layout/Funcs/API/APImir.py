import requests
import json

baseURL = "http://192.168.30.45/api/v2.0.0"

#baseURL = "http://192.168.30.17/api/v2.0.0"
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

    #print(response.text)
    try:
        return response.json()   #translates & returns response from robot to us
    except ValueError:
        return response.text
    

def mirRequestACT(method, endpoint, json = None):   #method=get/post/delete
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
        json=json,
        #auth=(username, password)
    )

    #print(response.text)
    try:
        return response.json()   #translates & returns response from robot to us
    except ValueError:
        return response.text
    
def mirRequestPOS(method, endpoint, data = None):   #method=get/post/delete
    url = baseURL + endpoint + f"{data}"

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

    #print(response.text)
    try:
        return response.json()   #translates & returns response from robot to us
    except ValueError:
        return response.text
def mirRequestNOJSON(method, endpoint, data = None):   #method=get/post/delete
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

    #print(response.text)

    return response



