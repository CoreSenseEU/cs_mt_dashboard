import requests
import json




id = "shellyplus1pm-fcb467285ecc"
baseURL = "http://192.168.30.113" 

#helper funcs--------------------------------------
#REQUEST---------------
def Request(method, url, body = None):
    url = baseURL + url
    
    response = requests.request(
        method,
        url,
        json=body
    )
    data = response.json()
    return json.dumps(data, indent = 4)


#GET--------------
def get(url):
    url = baseURL + "/rpc/" + url
    response = requests.get(
        url
    )
    data = response.json()
    return json.dumps(data, indent = 4)


#POST--------------
def post(url, body):
    url = baseURL + "/rpc/" + url
    response = requests.post(
        url,
        body
    )
    data = response.json()
    return json.dumps(data, indent = 4)




















