#from layout.Funcs.API import APIshelly
#from tuya_relay_python import connect_to_relay
import time


from layout.Funcs.API import APImir



mulLab = '4d5efe2a-f6c3-d3fe-556f-077cd8313b0c'
mulUuid= '5a66dbaf-0496-4d5a-a9c5-80e0ab554e6a'
vodafone = ''
#print(APImir.mirRequest('GET', '/wifi/networks'))

#current connection


def mullab():
    network = APImir.mirRequest('GET', f'/wifi/networks/{mulLab}')

    strength = network.get('strength')
    freq = network.get('frequency')
    security = network.get('security')

    return strength#, freq

def freq():
    network = APImir.mirRequest('GET', f'/wifi/networks/{mulLab}')
    freq = network.get('frequency')
 

    return freq
    
def ping(): #status response times
    start = time.time()
    
    try:
        response = APImir.mirRequestNOJSON('GET', '/status') 
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        return {"status": "error", "latency_ms": None, "error": str(e)}

    end = time.time()
    
    latency_ms = (end - start) * 1000
    latency_ms2 = round(latency_ms,2)
    
    return latency_ms2, response.status_code

def taskResponse():
    start = time.time()
    while True:
        if APImir.mirRequest('GET', '/status').get('state_id') == 5:
            end = time.time()
            timeTaken = (end-start)*1000
            #print(timeTaken)
            break

    return timeTaken


def stream():
    data = 'http://192.168.30.100:8082/1/config/list'
    #print(data)
    streamLat = 66
    return streamLat

'''def signallvl():
    driver = webdriver.Chrome()
    driver.get('http://192.168.30.17/monitoring/diagnostics')
    element = driver.find_element(
        By.CSS_SELECTOR,
        '[id = "diagnopstics_diagnostics_value_/Computer/WifiSignal Level"]'
    )

    signal = element.get_attribute('text_content')

    return signal
'''

def sensors(): 
    #load file at start, refresh if error(state id 10)
    return
#print(APImir.mirRequest('GET', '/wifi'))
