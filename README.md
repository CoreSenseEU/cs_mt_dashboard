# Description
Creates an interactive dashboard for a mobile robot via ROS2, retrieving robot data, and allowing for Nav2 control over the web.

# Prequisites

Requires ROS1 driver bridging to ROS2. Follow setup instructions on [this repository](https://github.com/leahtyndall/mir_ros2_bridge_stack)

### Dependencies
Create directory & virtual enviornment & install
```
mkdir cs_dashboard && cd cs_dashboard
python3 -m venv venv
source venv/bin/activate
pip install numpy dash dash-bootstrap-components pandas plotly requests tinytuya websocket-client scipy shapely roslibpy websockets
```


# Installation:
1. Go to directory `cd cs_dashboard`
2. Clone repository `git clone https://github.com/leahtyndall/cs_mt_dashboard.git`

3. Run a websocket server from ROS2 pc
```
ros2 run rosbridge_server rosbridge_webocket --port=<port>
```
**NOTE**
- In 'defs.py' replace rosIP with your ROS2 PC IP.
  

- Run dashboard.py & go to IP address given to access dashboard

# Summary of files:
- assets - images, cvs data files, txt logic files ect
- APIs - Connect to Mir/shelly to handle requests
- defs.py - Defines missions from mir
<!--- mirStatus.py - retrieves status info from mir
- missions.py - contains docking/undocking sequences & other buttons on dash -->
- network.py - to be updated...void?
- networkMap.py - records robot position and signal strength data to be plotted
- rosAMCL.py - 
- rosDiagnostics.py - recieves signal level from mir ros driver
- rosStatus.py -
- rvizGUI.py - 
<!--- shellyGateControl.py - runs gate control
- shellyStatsdorMir.py - gets status of gate (combine^?)-->
- layout2.py - plotly dash layout of dashboard
- dashboard.py - handles all call backs, creates map plot
