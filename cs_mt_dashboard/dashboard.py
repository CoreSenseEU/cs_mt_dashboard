from dash import Dash, html, ctx, Patch, dash
from dash.exceptions import PreventUpdate
import layout.Funcs.network as network, layout.Funcs.subscriber as subscriber
from dash.dependencies import Input, Output, State
from layout.Funcs.MIRstatus import getBattery, timeRemaining, stateID, getError, misText
import layout.Funcs.rosDiagnostics as rosDiagnostics
import layout.Funcs.missions as missions
import layout.Funcs.basicFunctions as basicFunctions
import numpy as np
import layout.Funcs.API.APImir as APImir
import layout.Funcs.networkMap as networkMap
import layout.Funcs.defs as defs
import layout.Funcs.rosDiagnostics as rosDiagnostics
import layout.Funcs.rosNavGoal as rosNavGoal
import layout.Funcs.rosStatus as rosStatus
import layout.Funcs.rosAMCL as rosAMCL
import pandas as pd
from shapely.geometry import Point, Polygon
import json
import plotly.express as px
import math
import plotly.graph_objects as go
from scipy.ndimage import gaussian_filter
import layout.Funcs.basicFunctions as bf
import dash_bootstrap_components as dbc
import threading
from layout.layout2 import layout2 
import layout.layout2 as layoutfile

foxglove_state = {
    "connected": False,
    "channels": {},
    "latest": {},
}
foxglove_lock = threading.Lock()
rosNavGoal

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
 
'''app.clientside_callback(
    """
    function(n_intervals) {
        if (!window.fpsMetrics) {
            window.fpsMetrics = {
                lastTime: performance.now(),
                frameCount: 0,
                currentFps: 60
            };
            
            // Loop that increments counts every time the browser updates the screen
            function countLoop() {
                window.fpsMetrics.frameCount++;
                requestAnimationFrame(countLoop);
            }
            requestAnimationFrame(countLoop);
        }
        
        let now = performance.now();
        let elapsed = now - window.fpsMetrics.lastTime;
        
        // Every 1 second, calculate the true FPS score
        if (elapsed >= 1000) {
            window.fpsMetrics.currentFps = Math.round((window.fpsMetrics.frameCount * 1000) / elapsed);
            window.fpsMetrics.frameCount = 0;
            window.fpsMetrics.lastTime = now;
        }
        
        // Returns the value to the Dash dcc.Store element
        return window.fpsMetrics.currentFps;
    }
    """,
    Output('browser-fps-store', 'data'),
    Input('fps-ticker', 'n_intervals')
)'''

app.layout = layout2
df = pd.read_csv('layout/assets/networkData.csv')
colourscale = px.colors.named_colorscales()
#callbacks-----------------------------------

@app.callback(
    Output('battery', 'children'),
    Output('time', 'children'),
    Output('robotLocation', 'children'),
    Input('interval-component','n_intervals')
)
def updateStats(n):
    battery, isCharging, hrs, mins, secs = rosDiagnostics.getBattery()
    rl = rosAMCL.getLocation()
    return(
        html.P("Battery: {}%".format(battery)),
        html.P("Time remaining: {}hrs, {}mins, {}secs".format(hrs, mins, secs)),
        html.P(f"- Robot is in Bay {rl}")
        #html.P("Charging?:{}".format(isCharging))
       )
    


@app.callback( #buttons
    Output('buttonCont', 'children'),
    #Output('text','children'),
    
    Input('charge', 'n_clicks'),
    Input('cfb1', 'n_clicks'),
    #Input('dab1', 'n_clicks'),
    Input('cfb2', 'n_clicks'),
    Input('b2LEFT', 'n_clicks'),
    #Input('dab2', 'n_clicks'),
    Input('pick', 'n_clicks'),
    Input('place', 'n_clicks'),
    Input('clear', 'n_clicks'),
    prevent_initial_call=True
    )


def buttonClicked(b1,b2,b3,b4,b5,b6,b7):
    if not ctx.triggered_id:
        raise PreventUpdate
    
    elif 'charge' == ctx.triggered_id:
        print('button works')
        rosNavGoal.charge()
        #network.taskResponse()
    elif 'cfb1' == ctx.triggered_id:
        print('button works')

        rosNavGoal.b1()
        #network.taskResponse()
        

    elif 'cfb2' == ctx.triggered_id:
        rosNavGoal.b2()
        #network.taskResponse()

    elif 'b2LEFT' == ctx.triggered_id:

        network.taskResponse()
    
    #---temporary---
    elif 'pick' == ctx.triggered_id:  
        defs.pick()
        network.taskResponse()
    elif 'place' == ctx.triggered_id:  
        defs.place()
        network.taskResponse()
    #---------------
    #elif 'refresh' == ctx.triggered_id:
        #missions.positions.refreshList()
        #network.taskResponse()
    
    elif 'clear' == ctx.triggered_id:
        bf.clearqueue()

    return dash.no_update


'''@app.callback(
    Output('ddOutput','children'),
    Input('submit', 'n_clicks'),
    State('posList', 'value')        
)

def dropdown(n_clicks, value):
    with open('layout/assets/PositionList.csv') as f:
        reader = csv.DictReader(f, delimiter=',')
        for row in reader:
            if row['label'] == value:
                data = row['guid']             
                if n_clicks > 0:
                    action = {
                        "action_type": "move",
                        "priority": 1,
                        "parameters": [
                            {
                                "id": "position",
                                "value": data
                            },
                            {
                                "id": "retries",
                                "value": 10
                            },
                            {
                                "id": "distance_threshold",
                                "value": 0.1
                            }
                        ]
                    }
                    bf.createAction(action)
    return '''


@app.callback(
    Output('signallevel', 'children'),
    Input('interval-component','n_intervals')
)
def networkinfo(n):
    signallevel = rosDiagnostics.getsignal()
    freq = network.freq()
    return(
        html.P(f'Strength: -{signallevel}'),
        html.P(f'Frequency: {freq}') 
    )
@app.callback(
    Output('latency', 'children'),
    Input('interval-component','n_intervals')
)
def latencyinfo(n):
    latency, status_code = network.ping()
    return(
        html.P(f'Latency: {latency}ms'),
        html.P(f'Status code: {status_code}')
    )   

'''@app.callback(
    Output('fps', 'children'),
    Input('interval-component','n_intervals')
)
def stream(n): 
    fps = subscriber.getfps()
    return(
        html.P(f'FPS: {fps}')
    )
@app.callback(
        Output('actualfps','children'),
        Input('browser-fps-store', 'data')
)

def update_python_fps_readout(actual_fps):
    if actual_fps == 0:
        return "Measuring..."
    return #print(f"Dashboard FPS: {actual_fps} FPS")
'''
'''@app.callback(
    Output('taskLatency', 'children'),
    Input('container', 'children')
)
def taskResponseTime(n):
    time = network.taskResponse()
    return( 
        html.P(f'Time taken = {time}ms')
    )'''

@app.callback(
    Output('errors', 'children'),
    Input('interval-component', 'n_intervals')
)
def errors(n):
    errors = getError()
    if errors == 67:
        return html.P('No errors!')
    else:
        return html.P(errors)
#'''


@app.callback(
    Output('plot', 'figure'),
    Input('interval-comp2', 'n_intervals')
)



def graph(n):
    # networkMap.getData() #uncomment to build network map
    df = pd.read_csv('layout/assets/networkData.csv')
    fig = go.Figure()
    
    # Spatial limits matching your red site perimeter geometry
    x_min, x_max = 30.0, 75.0
    y_min, y_max = 25.0, 65.0

    # Drawing site perimeter
    fig.add_trace(go.Scatter(
        x = [31.45,31.15,43.85,43.5,34.8,35.1,50.05,52.75,52.4,43.45,43.9,62.25,61.8,55.9,56.05,62.15,61.85,73.45,73.15,69,69.25,61.6,61.65,31.45],
        y = [59.9,26.9,27.05,38.65,38.55,29.15,29.5,34.35,47.45,47.2,27.35,27.8,47.55,47.4,31.25,31.3,46.4,46.5,62.35,62.3,50.05,50.05,59.95,59.9],
        mode='lines',
        line=dict(color='red', width=1.5),
        line_shape='linear',
        showlegend=False
    ))

    # 1. CRITICAL FIX: Dramatically increase grid density for pinpoint accuracy
    # This shrinks the physical size of individual grid cells so data doesn't look blocky
    nx = 80
    ny = 60

    signal_sum, yedges, xedges = np.histogram2d(
        df["y"],
        df["x"],
        bins=[ny, nx],
        range=[[y_min, y_max], [x_min, x_max]],
        weights=df["signallevel"]
    )
    counts, _, _ = np.histogram2d(
        df["y"],
        df["x"],
        bins=[ny, nx],
        range=[[y_min, y_max], [x_min, x_max]]
    )

    has_data = (counts > 0).astype(float)
    
    with np.errstate(divide='ignore', invalid='ignore'):
        avg = np.divide(signal_sum, counts)
        avg_filled = np.where(counts == 0, 0, avg)

    # 2. CRITICAL FIX: Match the blur radius to your fine high-res grid
    # A sigma of 1.5 on a 150x120 grid keeps the true value tightly localized
    # If it is still too wide, drop this to 1.0. If too sharp, push to 2.0.
    sigma_val = 1.5 
    smoothed_signal = gaussian_filter(avg_filled, sigma=sigma_val)
    smoothed_mask = gaussian_filter(has_data, sigma=sigma_val)

    with np.errstate(divide='ignore', invalid='ignore'):
        smoothed_avg = np.divide(smoothed_signal, smoothed_mask)

    # 3. Tighten the cutoff boundary so the signal color does not spread too far
    smoothed_avg[smoothed_mask < 0.15] = np.nan

    # Extract high-resolution bin centers
    xcentres = (xedges[:-1] + xedges[1:]) / 2
    ycentres = (yedges[:-1] + yedges[1:]) / 2

    custom_colors = [
        [0.0, "#2A71DD"],
        [0.5, "#ddbd2c"],
        [1.0, "#ec2626"]
    ]

    # 4. Heatmap trace handles high-resolution sparse dots effortlessly
    fig.add_trace(
        go.Heatmap(
            x=xcentres,        
            y=ycentres,        
            z=smoothed_avg,    
            colorscale=custom_colors,
            zmin=20,
            zmax=90,
            zsmooth='best', # Blends tiny high-res pixels flawlessly
            showscale=True,
            hoverongaps=False
        )
    )

    # Secure layout limits
    fig.update_layout(
        plot_bgcolor='white', 
        xaxis_title='X coordinate',
        yaxis_title='Y coordinate',
        uirevision='constant',
        xaxis=dict(
            tickmode='linear',  
            dtick=5,
            range=[x_min, x_max]
        ),
        yaxis=dict(
            tickmode='linear',
            dtick=5,
            range=[y_min, y_max]
        )
    )
    
    return fig

@app.callback(
    Output('map', 'figure'),
    Input('interval-comp2', 'n_intervals')
)
def updateMap(n):
    fig2 = go.Figure()
    x_min, x_max = 30.0, 75.0
    y_min, y_max = 25.0, 65.0

    xs = np.linspace(x_min, x_max, 100)
    ys = np.linspace(y_min, y_max, 100)
    xx, yy = np.meshgrid(xs, ys)

    fig2.add_trace(go.Scatter(
        x=xx.flatten(),
        y=yy.flatten(),
        mode='markers',
        marker=dict(size=10, opacity=0),
        hoverinfo='none',   # <-- was 'skip'; 'skip' also disables click events
        showlegend=False,
    ))

    fig2.update_layout(
        plot_bgcolor='white',
        xaxis_title='X coordinate',
        yaxis_title='Y coordinate',
        uirevision='constant',
        width=600,
        height=600,
        margin=dict(l=60, r=20, t=20, b=60),
        xaxis=dict(
            range=[x_min, x_max],
            constrain='domain',
        ),
        yaxis=dict(
            range=[y_min, y_max],
            scaleanchor="x",
            scaleratio=1,
            constrain='domain',
        ),
    )

    fig2.add_layout_image(
        dict(
            source="/assets/IMRsiteMap.png",
            xref="x",
            yref="y",
            x=32.2,
            y=62.45,
            sizex=42.3,
            sizey=38.45,
            opacity=0.4,
            layer="below",
        )
    )

    return fig2


@app.callback(
    Output('click-output', 'children'),
    Output('slider-output', 'children'),
    Input('slider', 'value'),
    Input('map', 'clickData')
)
def mapClick(value, clickData):
    perimeter = [(31.45,59.9), (31.15,26.9), (62.25,27.8), (61.85, 46.5),
                 (73.45, 46.55), (73.15,62.35), (69,62.3), (69.25,50.05),
                 (61.6,50.05), (61.65,59.95), (31.45,59.9)]
    validPerimeter = Polygon(perimeter)

    if clickData is None :
        return ("Use the slider to set an orientation, then click a position on the map to send a nav goal.",
                f"Orientation = {value}")

    point = clickData['points'][0]   # <-- was clickData['goal'][0]
    x = point['x']
    y = point['y']
    w = (value * (math.pi/180))
    if validPerimeter.contains(Point(x, y)):
        print(f'Goal: x = {x}, y = {y}, w = {w}')
        rosNavGoal.mapGoal(x,y,w)
        return ("Goal sent!", f"Going to x: {round(x, 0)}, y: {round(y, 0)} w: {round(w,0)}")
    else:
        return ("Invalid position!",
                f"Orientation = {value}")
    
if __name__ == '__main__':
    #app.run(debug=True)
    #app.run(host='0.0.0.0', port=8055, debug=False) #run this for use over wifi
    app.run(debug=True)