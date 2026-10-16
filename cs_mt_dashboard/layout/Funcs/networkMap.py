from dash import dcc
import pandas as pd
import plotly.express as px
from layout.Funcs.API import APImir
import layout.Funcs.rosAMCL as rosAMCL
import layout.Funcs.rosDiagnostics as ros
import csv
import time
import layout.Funcs.network as network


colours = {
    'excellent':"#2BC1D4",
    'good':"#44A744",
    'weak':"#ECB246",
    'dead':"#BD2D23"
}

def getData():
    #print('getting data')
    #coords = APImir.mirRequest('GET', '/status').get('position')
    state = APImir.mirRequest('GET', '/status').get('state_text')
    px, py, pz = rosAMCL.getPos()

    signallevel = ros.getsignal()
    #print(x,y) 
    #print(strength)
    fields=['x','y','signallevel']
    data = [
        #['x','y','strength'],
        {'x':px,'y':py,'signallevel':signallevel}
    ]
    if state != 'Pause':
        with open('layout/assets/networkData.csv', mode = 'at', newline='') as d:
            writer = csv.DictWriter(d, fieldnames=fields)
            writer.writerows(data)
            d.close()
    return
'''
def plot():
    i = 0
    getData()
    #time.sleep(2)
    with open('networkData.csv', mode = 'r') as d:
        df = pd.read_csv(d)
        reader = csv.reader(d)
        next(reader,None) #skip header
        for row in reader:
            fig = px.scatter(df, x='x_column',y='y_column', title='plot')
            fig.update_traces(marker=dict(size=10, color='red', symbol='circle'))
            fig.show()

        
            return fig
'''
