from dash import Dash, html, dcc
from dash.dependencies import Input, Output

import dash_bootstrap_components as dbc
import dash_player

COLOURS = { #CHANGE TO VODAFONE THEME + ADD LOGOS
    'red':"#AF1D18",
    'white': "#FFFFFF",
    'backgnd': "#EBEBEB",
    'black': "#1A1A1A",
    'green': '#8FC78F',
    'orange': "#E2870F",
    #'red': "#C52620"
}

COLOURS3 ={'colour'}
'''
if modekeystate() == 'Available':
    COLOURS2 = {'colour': "#78CF78"}
else:
    COLOURS2 = {'colour': "#662222" }'''

layout = html.Div(
    style = {'backgroundColor': COLOURS['backgnd'],'font-family':'Monospace', 'font-size':'14px', 'line-height':'1'}, children= [ 
    
    
    dbc.Container([  
        dbc.Row([#title bar - row 1
            dbc.Col(html.Div([ #r1c1
                html.H1('MiR Stats',
                    style={
                        'color': COLOURS['black'],
                        'width':'100%',
                        'padding':'5px',
                        #'backgroundColor': COLOURS['red'],
                        'borderRadius':'5px',
                        'margin':'0px',
                        'verticalAlign':'top'})
            ]), width = 8),

            dbc.Col(html.Div([ # r1c2
                html.Img(src='assets/IMR-Primary Logo_RGB.png',
                    style ={'width': '100%',
                        'verticalAlign':'top', 
                        'float':'right',
                        'margin':'0px'})
            ]), width = 2),               
            dbc.Col(html.Div([ #r1c3
                html.Img(src='assets/vodafone.png',
                    style ={'width': '60%',
                        'verticalAlign':'top', 
                        'float':'right',
                        'margin':'0px'})
            ]), width = 2)

        ],   
        style = {
            'backgroundColor': COLOURS['white'],
            'width':'100%'
            }
        ), #row1 close
  #fine^
#################################################################    
#LEFT COL         
#################################################################      
# #1st column------------------------------------
                
        dbc.Row([ #row 2 open                
            dbc.Col( #r2c1
                dbc.Row([ #inside r2c1
                    dbc.Col(html.Div([  #LEFT r2c1          
                        html.H3('Status:',
                            style = {
                                'color': COLOURS['white'],
                                'padding':'8px',
                                'backgroundColor': COLOURS['red'],
                                'borderRadius':'10px',
                                'margin':'5px',
                                'verticalAlign':'top',
                                'height':'40px'}),

                            html.Div(id= 'battery'),
                            html.Div(id='time')],
                        #other data in this block enter here
                            style={
                                'color': COLOURS['black'],
                                'width':'100%',
                                'padding':'8px',
                                'backgroundColor': COLOURS['white'],
                                'borderRadius':'10px',
                                'margin':'5px',
                                'verticalAlign':'top',
                                'display': 'inline-block',
                                'height': '120px'
                                }
                    )),

                    dbc.Col(html.Div([ #r2c1c2 
                        html.H3(id = 'state', 
                            style={
                                'color': COLOURS['white'],
                                'padding':'8px',
                                'backgroundColor': COLOURS['red'],
                                'borderRadius':'10px',
                                'margin':'5px',
                                'verticalAlign':'top',
                                'height':'40px'}),
                        #html.P('Executing: '),
                        html.P(id = 'text'),
                        html.P(id = 'pending')], 
                            style={
                                'color': COLOURS['black'],
                                'width':'100%',
                                'padding':'8px',
                                'backgroundColor': COLOURS['white'],
                                'borderRadius':'10px',
                                'margin':'5px',
                                'verticalAlign':'top',
                                'display': 'inline-block',
                                'height': '120px'
                                }
                    )),
                
                dbc.Row([ #R2c1r2 {middle}
                    dbc.Col(html.Div([ #col 3
                        html.H3('Tasks:', 
                            style={
                                'color': COLOURS['white'],
                                'padding':'8px',
                                'backgroundColor': COLOURS['red'],
                                'borderRadius':'10px',
                                'margin':'5px',
                                'verticalAlign':'top'
                                }
                        ),
                        
                                
                        dcc.Button('Leahs Desk', id = 'mydesk', n_clicks = 0),
                        dcc.Button('Dock', id = 'dock', n_clicks = 0),
                        dcc.Button('Pick up',id = 'pick', n_clicks = 0 ),
                        dcc.Button('Place down', id='place', n_clicks = 0),
                        dcc.Button('Collect shelf', id='pickUpSequenceB1', n_clicks = 0),
                        dcc.Button('Deposit shelf', id='depositSequenceB1', n_clicks = 0),

                        html.Div(id ='container', children = '')], 

                            style={
                                'color': COLOURS['black'],
                                'width':'100%',
                                'padding':'10px',
                                'backgroundColor': COLOURS['white'],
                                'borderRadius':'10px',
                                'margin':'10px',
                                'verticalAlign':'top',
                                'display': 'inline-block',
                                'height': '150px'
                                }
                    )) #r2c1r2 close                
                ]),
                dbc.Row([
                    dbc.Col(html.Div([ #col 3
                        html.H3('Data:', 
                            style={
                                'color': COLOURS['white'],
                                'padding':'8px',
                                'backgroundColor': COLOURS['red'],
                                'borderRadius':'10px',
                                'margin':'5px',
                                'verticalAlign':'top'
                                }
                        ),


                    ]))


                ])
                ])
            ),
#################################################################    
#RIGHT COL         
#################################################################            
            dbc.Col( #r2c2 MAP
                html.Div([ 
                    html.Img(src='http://192.168.30.100:8081/', 
                        style={'width': '100%',
                            'width': '100%',
                            'padding':'10px',
                            'backgroundColor': COLOURS['red'],
                            'borderRadius':'10px',
                            'margin':'10px',
                            'verticalAlign':'top',
                            'display': 'inline-block'})])
            ) #r2c2 close
        ]),
    ]),#row 5
dcc.Interval(
    id='interval-component',
    interval=2*1000,
    n_intervals=0)
])
