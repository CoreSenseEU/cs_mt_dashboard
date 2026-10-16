def init_ros2(self):
    """Initialize ROS2 node and connections"""
    try:
        rclpy.init(args=None)
        self.ros_node = Node('parameter_dashboard')
        self.connected_to_ros = True
        self.ros_status.set_active(True)
        self.ros_status.label.setText("Connected to ROS2")
        self.connect_button.setText("Disconnect from ROS2")
        
        # Set up ROS2 communication
        
        # Subscribe to navigation status
        self.status_subscriber = self.ros_node.create_subscription(
            String,
            '/navigation/status',
            self.handle_status_update,
            10
        )
        
        # Subscribe to failure events
        self.failure_subscriber = self.ros_node.create_subscription(
            String,
            '/navigation/failures',
            self.handle_failure_update,
            10
        )
        
        # Create a client for the parameter service
        self.param_client = self.ros_node.create_client(
            SetParameters, 
            'set_parameters'
        )
        
        # Start ROS2 spinner in a separate thread
        self.ros_spinner = QTimer(self)
        self.ros_spinner.timeout.connect(self.spin_ros)
        self.ros_spinner.start(100)  # 10 Hz
        
        self.get_logger().info("ROS2 connections initialized")
        
    except Exception as e:
        print(f"Failed to initialize ROS2: {e}")
        self.connected_to_ros = False

def handle_status_update(self, msg):
    """Handle status updates from the navigation node"""
    try:
        status_data = json.loads(msg.data)
        
        # Convert string timestamp to datetime
        status_data["timestamp"] = datetime.fromisoformat(status_data["timestamp"])
        
        # Add to performance data
        self.performance_data.append(status_data)
        if len(self.performance_data) > 50:  # Keep only the most recent 50 data points
            self.performance_data = self.performance_data[-50:]
        
        # Update parameter sets if collecting data
        if self.collecting_data:
            self.update_parameter_sets(status_data)
        
        # Update UI
        self.update_charts()
        self.update_parameter_table()
        
    except Exception as e:
        print(f"Error processing status update: {e}")

def handle_failure_update(self, msg):
    """Handle failure updates from the navigation node"""
    try:
        failure_data = json.loads(msg.data)
        
        # Convert string timestamp to datetime
        failure_data["timestamp"] = datetime.fromisoformat(failure_data["timestamp"])
        
        # Add to failures
        self.failures.append(failure_data)
        if len(self.failures) > 20:  # Keep only the most recent 20 failures
            self.failures = self.failures[-20:]
        
        # Update UI
        self.update_failure_log()
        
        # Occasionally generate a new suggestion
        if random.random() < 0.3:
            self.generate_new_suggestion()
        
    except Exception as e:
        print(f"Error processing failure update: {e}")

def apply_parameters(self):
    """Apply the current parameters to the ROS2 system"""
    if not self.connected_to_ros or not self.param_client:
        print("Not connected to ROS2")
        return
    
    # Wait for service to be available
    if not self.param_client.wait_for_service(timeout_sec=1.0):
        print("Parameter service not available")
        return
    
    try:
        # Create parameter request
        request = SetParameters.Request()
        
        # Add parameters
        max_vel_param = Parameter()
        max_vel_param.name = 'max_velocity'
        max_vel_param.value.type = ParameterType.PARAMETER_DOUBLE
        max_vel_param.value.double_value = self.current_params['max_velocity']
        
        obs_thresh_param = Parameter()
        obs_thresh_param.name = 'obstacle_threshold'
        obs_thresh_param.value.type = ParameterType.PARAMETER_DOUBLE
        obs_thresh_param.value.double_value = self.current_params['obstacle_threshold']
        
        goal_tol_param = Parameter()
        goal_tol_param.name = 'goal_tolerance'
        goal_tol_param.value.type = ParameterType.PARAMETER_DOUBLE
        goal_tol_param.value.double_value = self.current_params['goal_tolerance']
        
        request.parameters = [max_vel_param, obs_thresh_param, goal_tol_param]
        
        # Send request
        future = self.param_client.call_async(request)
        
        # Process response in ROS spinner callback
        future.add_done_callback(self.handle_parameter_response)
        
        print(f"Sending parameters to ROS2: {self.current_params}")
        
    except Exception as e:
        print(f"Error applying parameters: {e}")

def handle_parameter_response(self, future):
    """Handle the response from the parameter service"""
    try:
        response = future.result()
        if all(response.results):
            print("All parameters applied successfully")
        else:
            print(f"Some parameters failed to apply: {response.results}")
    except Exception as e:
        print(f"Service call failed: {e}")

def get_logger(self):
    """Get the ROS2 logger"""
    if self.ros_node:
        return self.ros_node.get_logger()
    else:
        # Return a simple logger if ROS node is not available
        class SimpleLogger:
            def info(self, msg):
                print(f"INFO: {msg}")
            def warn(self, msg):
                print(f"WARN: {msg}")
            def error(self, msg):
                print(f"ERROR: {msg}")
        return SimpleLogger()