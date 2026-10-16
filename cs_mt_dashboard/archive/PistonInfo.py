import layout.Funcs.API.APIshelly as APIshelly

get = APIshelly.get
request = APIshelly.Request
post = APIshelly.post

id = "?id=0"
on = "&on=true"
off = "&on=false"
#funcs----------------------------------------------
def status():
    print("Status: ")
    status = get("Switch.GetStatus"+id)
    return print(status)

def config():
    print("Configuration: ")
    config = get("Switch.GetConfig"+id)
    return config


#main-----------------------------------------------
config()
status()