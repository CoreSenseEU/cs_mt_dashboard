#!/usr/bin/env python3
import sys
import json
import random
import base64
from datetime import datetime, timedelta
import requests
import subprocess

# Import PyQt5 first to avoid Qt conflicts
from PyQt5.QtWidgets import (QMessageBox, QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QGroupBox, QLabel, QSlider, QPushButton, QTableWidget, 
                            QTableWidgetItem, QTextEdit, QLineEdit, QComboBox, QCheckBox,
                            QScrollArea, QFrame, QSplitter, QGridLayout, QHeaderView, QFileDialog)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread, pyqtSlot
from PyQt5.QtGui import QColor, QPixmap, QImage
import pyqtgraph as pg

# Import OpenCV after PyQt5
import cv2
import numpy as np

try:
    import rclpy
    from rclpy.node import Node
    from rcl_interfaces.msg import Parameter, ParameterValue, ParameterType
    from rcl_interfaces.srv import SetParameters
    from geometry_msgs.msg import Twist
    ROS2_AVAILABLE = True
except ImportError:
    ROS2_AVAILABLE = False
    print("ROS2 packages not found. Running in simulation mode only.")

class StatusIndicator(QWidget):
    def __init__(self, active=False, label="", parent=None):
        super().__init__(parent)
        self.active = active
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.indicator = QFrame(self)
        self.indicator.setFixedSize(10, 10)
        self.indicator.setStyleSheet(
            f"background-color: {'#ef4444' if not active else '#22c55e'}; border-radius: 5px;")
        
        self.label = QLabel(label, self)
        
        self.layout.addWidget(self.indicator)
        self.layout.addWidget(self.label)
        self.layout.addStretch(1)
    
    def set_active(self, active):
        self.active = active
        self.indicator.setStyleSheet(
            f"background-color: {'#ef4444' if not active else '#22c55e'}; border-radius: 5px;")

class ROS2ParameterTuningDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Initialize data
        self.current_params = {
            'max_velocity': 0.5,
            'obstacle_threshold': 0.3,
            'goal_tolerance': 0.2
        }
        self.parameter_sets = []
        self.performance_data = []
        self.failures = []
        self.llm_suggestions = []
        self.collecting_data = False
        self.connected_to_ros = False
        self.ros_node = None
        
        # Image-related attributes
        self.current_image_path = None
        
        # Set up the UI
        self.init_ui()
        
        # Generate mock data for initial display
        self.generate_mock_data()
        
        # Update UI
        self.update_charts()
        self.update_parameter_table()
        self.update_failure_log()
        self.update_llm_suggestions()
        
        # Set up timers
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.simulate_data_update)
        self.update_timer.start(5000)  # Update every 5 seconds

        # Add cmd_vel related state for visualization
        self.cmd_vel_values = {
            'linear': {'x': [], 'y': [], 'z': []},
            'angular': {'x': [], 'y': [], 'z': []}
        }
        self.cmd_vel_timestamps = []
        
        # Initialize ROS2 if available
        if ROS2_AVAILABLE:
            self.init_ros2()
    
    def init_ui(self):
        self.setWindowTitle("ROS2 Parameter Tuning Dashboard with Vision")
        self.setGeometry(100, 100, 1400, 900)
        
        # Main widget and layout
        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        
        # Title
        title_label = QLabel("ROS2 Parameter Tuning Dashboard with Vision")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #1e40af; margin-bottom: 10px;")
        main_layout.addWidget(title_label)
        
        # Status indicators
        status_layout = QHBoxLayout()
        
        # ROS2 connection status
        self.ros_status = StatusIndicator(False, "Disconnected from ROS2")
        status_layout.addWidget(self.ros_status)
        
        # Connect button
        self.connect_button = QPushButton("Connect to ROS2")
        self.connect_button.clicked.connect(self.toggle_ros_connection)
        status_layout.addWidget(self.connect_button)
        
        # Data collection status
        self.collection_status = StatusIndicator(False, "Data collection paused")
        status_layout.addWidget(self.collection_status)
        
        # Collection control buttons
        self.collection_button = QPushButton("Start Collection")
        self.collection_button.clicked.connect(self.toggle_data_collection)
        status_layout.addWidget(self.collection_button)
        
        self.export_button = QPushButton("Export Training Data")
        self.export_button.clicked.connect(self.export_training_data)
        status_layout.addWidget(self.export_button)
        
        main_layout.addLayout(status_layout)
        
        # Parameter controls
        param_group = QGroupBox("Current Parameters")
        param_layout = QGridLayout(param_group)
        
        # Max Velocity slider
        param_layout.addWidget(QLabel("Max Velocity:"), 0, 0)
        self.velocity_slider = QSlider(Qt.Horizontal)
        self.velocity_slider.setRange(1, 15)
        self.velocity_slider.setValue(int(self.current_params['max_velocity'] * 10))
        self.velocity_slider.valueChanged.connect(
            lambda val: self.handle_param_change('max_velocity', val / 10))
        param_layout.addWidget(self.velocity_slider, 0, 1)
        self.velocity_label = QLabel(f"{self.current_params['max_velocity']} m/s")
        param_layout.addWidget(self.velocity_label, 0, 2)
        
        # Obstacle Threshold slider
        param_layout.addWidget(QLabel("Obstacle Threshold:"), 1, 0)
        self.obstacle_slider = QSlider(Qt.Horizontal)
        self.obstacle_slider.setRange(1, 8)
        self.obstacle_slider.setValue(int(self.current_params['obstacle_threshold'] * 10))
        self.obstacle_slider.valueChanged.connect(
            lambda val: self.handle_param_change('obstacle_threshold', val / 10))
        param_layout.addWidget(self.obstacle_slider, 1, 1)
        self.obstacle_label = QLabel(f"{self.current_params['obstacle_threshold']} m")
        param_layout.addWidget(self.obstacle_label, 1, 2)
        
        # Goal Tolerance slider
        param_layout.addWidget(QLabel("Goal Tolerance:"), 2, 0)
        self.tolerance_slider = QSlider(Qt.Horizontal)
        self.tolerance_slider.setRange(5, 50)
        self.tolerance_slider.setValue(int(self.current_params['goal_tolerance'] * 100))
        self.tolerance_slider.valueChanged.connect(
            lambda val: self.handle_param_change('goal_tolerance', val / 100))
        param_layout.addWidget(self.tolerance_slider, 2, 1)
        self.tolerance_label = QLabel(f"{self.current_params['goal_tolerance']} m")
        param_layout.addWidget(self.tolerance_label, 2, 2)
        
        # Apply button
        self.apply_button = QPushButton("Apply Parameters")
        self.apply_button.clicked.connect(self.apply_parameters)
        param_layout.addWidget(self.apply_button, 3, 1, 1, 2)
        
        main_layout.addWidget(param_group)
        
        # Create main content splitter (3 columns now)
        main_splitter = QSplitter(Qt.Horizontal)
        
        # Left column - Performance chart and parameter comparison
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # Performance Chart
        chart_group = QGroupBox("Performance Over Time")
        chart_layout = QVBoxLayout(chart_group)
        
        self.performance_graph = pg.PlotWidget()
        self.performance_graph.setBackground('w')
        self.performance_graph.setLabel('left', 'Value')
        self.performance_graph.setLabel('bottom', 'Time')
        self.performance_graph.addLegend()
        self.success_curve = self.performance_graph.plot(
            [], [], pen=pg.mkPen(color='#8884d8', width=2), name='Success Rate')
        self.time_curve = self.performance_graph.plot(
            [], [], pen=pg.mkPen(color='#82ca9d', width=2), name='Execution Time')
        
        chart_layout.addWidget(self.performance_graph)
        left_layout.addWidget(chart_group)

        # cmd_vel visualization
        cmd_vel_group = QGroupBox("Robot Velocity (cmd_vel)")
        cmd_vel_layout = QVBoxLayout(cmd_vel_group)
        
        # Current velocity display
        current_vel_layout = QHBoxLayout()
        
        # Linear velocity display
        linear_box = QGroupBox("Linear Velocity")
        linear_layout = QVBoxLayout(linear_box)
        
        self.linear_x_label = QLabel("X: 0.0 m/s")
        self.linear_y_label = QLabel("Y: 0.0 m/s")
        self.linear_z_label = QLabel("Z: 0.0 m/s")
        
        linear_layout.addWidget(self.linear_x_label)
        linear_layout.addWidget(self.linear_y_label)
        linear_layout.addWidget(self.linear_z_label)
        
        current_vel_layout.addWidget(linear_box)
        
        # Angular velocity display
        angular_box = QGroupBox("Angular Velocity")
        angular_layout = QVBoxLayout(angular_box)
        
        self.angular_x_label = QLabel("X: 0.0 rad/s")
        self.angular_y_label = QLabel("Y: 0.0 rad/s")
        self.angular_z_label = QLabel("Z: 0.0 rad/s")
        
        angular_layout.addWidget(self.angular_x_label)
        angular_layout.addWidget(self.angular_y_label)
        angular_layout.addWidget(self.angular_z_label)
        
        current_vel_layout.addWidget(angular_box)
        cmd_vel_layout.addLayout(current_vel_layout)
        
        # Velocity history graph
        self.cmd_vel_graph = pg.PlotWidget()
        self.cmd_vel_graph.setBackground('w')
        self.cmd_vel_graph.setLabel('left', 'Velocity')
        self.cmd_vel_graph.setLabel('bottom', 'Time')
        self.cmd_vel_graph.addLegend()
        
        self.linear_x_curve = self.cmd_vel_graph.plot(
            [], [], pen=pg.mkPen(color='#ff0000', width=2), name='Linear.x')
        self.angular_z_curve = self.cmd_vel_graph.plot(
            [], [], pen=pg.mkPen(color='#0000ff', width=2), name='Angular.z')
        
        cmd_vel_layout.addWidget(self.cmd_vel_graph)
        left_layout.addWidget(cmd_vel_group)
        
        # Parameter Set Comparison
        param_comparison_group = QGroupBox("Parameter Set Comparison")
        param_comparison_layout = QVBoxLayout(param_comparison_group)
        
        self.parameter_table = QTableWidget()
        self.parameter_table.setColumnCount(9)
        self.parameter_table.setHorizontalHeaderLabels([
            "Max Velocity", "Obstacle Threshold", "Goal Tolerance", 
            "Success Rate", "Avg Time", "Collisions", "Failures", "Tests", "Actions"
        ])
        self.parameter_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        param_comparison_layout.addWidget(self.parameter_table)
        
        left_layout.addWidget(param_comparison_group)
        
        # Middle column - Image Analysis
        middle_widget = QWidget()
        middle_layout = QVBoxLayout(middle_widget)
        
        # Image view
        image_group = QGroupBox("Image Analysis")
        image_layout = QVBoxLayout(image_group)
        
        # Image display
        self.image_display = QLabel()
        self.image_display.setFixedSize(320, 240)
        self.image_display.setStyleSheet("border: 1px solid #ccc; background-color: #f0f0f0;")
        self.image_display.setAlignment(Qt.AlignCenter)
        self.image_display.setText("No Image Loaded")
        image_layout.addWidget(self.image_display)
        
        # Image controls
        image_controls = QHBoxLayout()
        
        self.upload_button = QPushButton("Upload Image")
        self.upload_button.clicked.connect(self.upload_image)
        image_controls.addWidget(self.upload_button)
        
        self.analyze_button = QPushButton("Analyze with Llama")
        self.analyze_button.clicked.connect(self.analyze_image)
        self.analyze_button.setEnabled(False)
        image_controls.addWidget(self.analyze_button)
        
        image_layout.addLayout(image_controls)
        middle_layout.addWidget(image_group)
        
        # Vision Analysis Results
        vision_group = QGroupBox("Vision Analysis")
        vision_layout = QVBoxLayout(vision_group)
        
        # Custom vision prompt
        vision_layout.addWidget(QLabel("Vision Prompt:"))
        self.vision_prompt = QLineEdit()
        self.vision_prompt.setPlaceholderText("What do you see in this image? Describe any obstacles or navigation hazards.")
        vision_layout.addWidget(self.vision_prompt)
        
        # Analysis results
        self.vision_results = QTextEdit()
        self.vision_results.setReadOnly(True)
        self.vision_results.setMaximumHeight(200)
        self.vision_results.setPlaceholderText("Vision analysis results will appear here...")
        vision_layout.addWidget(self.vision_results)
        
        # Vision history
        vision_layout.addWidget(QLabel("Recent Vision Analyses:"))
        self.vision_history = QTextEdit()
        self.vision_history.setReadOnly(True)
        self.vision_history.setMaximumHeight(150)
        vision_layout.addWidget(self.vision_history)
        
        middle_layout.addWidget(vision_group)
        
        # Right column - LLM suggestions and failures
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # LLM Suggestions
        llm_group = QGroupBox("AI Suggestions")
        llm_layout = QVBoxLayout(llm_group)
        
        llm_header = QHBoxLayout()
        llm_header.addWidget(QLabel("LLM's Analysis:"))
        llm_header.addStretch(1)
        llm_header.addWidget(QLabel(f"Updated {datetime.now().strftime('%H:%M:%S')}"))
        llm_layout.addLayout(llm_header)
        
        self.suggestions_area = QTextEdit()
        self.suggestions_area.setReadOnly(True)
        self.suggestions_area.setMaximumHeight(200)
        llm_layout.addWidget(self.suggestions_area)
        
        # Failures Log
        llm_layout.addWidget(QLabel("Recent Failures:"))
        self.failures_area = QTextEdit()
        self.failures_area.setReadOnly(True)
        self.failures_area.setMaximumHeight(200)
        llm_layout.addWidget(self.failures_area)
        
        right_layout.addWidget(llm_group)
        
        # LLM Integration Settings
        llm_settings_group = self.create_llm_settings_ui()
        right_layout.addWidget(llm_settings_group)
        
        # Add widgets to splitter
        main_splitter.addWidget(left_widget)
        main_splitter.addWidget(middle_widget)
        main_splitter.addWidget(right_widget)
        main_splitter.setSizes([450, 350, 450])  # Initial sizes
        
        main_layout.addWidget(main_splitter)
        
        # Initialize vision analysis history
        self.vision_analyses = []
    
    def upload_image(self):
        """Upload an image from file system"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "", 
            "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        
        if file_path:
            self.current_image_path = file_path
            
            # Display the image
            pixmap = QPixmap(file_path)
            scaled_pixmap = pixmap.scaled(
                self.image_display.size(), 
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            )
            self.image_display.setPixmap(scaled_pixmap)
            self.analyze_button.setEnabled(True)
    
    def analyze_image(self):
        """Analyze the uploaded image with Llama"""
        if not self.current_image_path:
            QMessageBox.warning(self, "Analysis Failed", "No image loaded")
            return
        
        try:
            prompt = self.vision_prompt.text()
            if not prompt:
                prompt = "What do you see in this image? Describe any obstacles, objects, or navigation hazards that might be relevant for a robot."
            
            analysis_result = self.call_ollama_api(self.current_image_path, prompt)
            
            if analysis_result:
                self.vision_results.setPlainText(analysis_result)
                
                timestamp = datetime.now().strftime("%H:%M:%S")
                history_entry = {
                    "timestamp": datetime.now(),
                    "prompt": prompt,
                    "result": analysis_result[:100] + "..." if len(analysis_result) > 100 else analysis_result,
                    "full_result": analysis_result,
                    "image_path": self.current_image_path
                }
                self.vision_analyses.append(history_entry)
                self.update_vision_history()
                
                if any(keyword in analysis_result.lower() for keyword in ["obstacle", "hazard", "navigation", "path", "blocked"]):
                    self.add_vision_suggestion(analysis_result)
                
        except Exception as e:
            QMessageBox.critical(self, "Analysis Error", f"Error analyzing image: {str(e)}")
    
    def update_compare_button_state(self):
        """Enable/disable compare button based on number of analyses"""
        if hasattr(self, 'compare_button'):
            self.compare_button.setEnabled(len(self.vision_analyses) >= 2)
    
    def compare_images(self):
        """Compare the last two analyzed images"""
        if len(self.vision_analyses) < 2:
            QMessageBox.warning(self, "Comparison Failed", "Need at least 2 analyzed images to compare")
            return
        
        try:
            last_two = self.vision_analyses[-2:]
            
            comparison_prompt = f"""Compare these two image analyses and highlight the key differences:

Image 1 Analysis: {last_two[0]['full_result']}

Image 2 Analysis: {last_two[1]['full_result']}

Please provide:
1. Key differences between the images
2. Changes in obstacles or navigation hazards
3. Any safety implications for robot navigation
4. Recommendations based on the comparison"""
            
            # Use text-only comparison since we're comparing analysis results
            comparison_result = self.call_ollama_text_api(comparison_prompt)
            
            if comparison_result:
                # Display comparison result
                self.vision_results.setPlainText(f"COMPARISON RESULT:\n\n{comparison_result}")
                
                # Add to history
                history_entry = {
                    "timestamp": datetime.now(),
                    "prompt": "Image Comparison",
                    "result": comparison_result[:100] + "..." if len(comparison_result) > 100 else comparison_result,
                    "full_result": comparison_result,
                    "image_path": "comparison"
                }
                self.vision_analyses.append(history_entry)
                self.update_vision_history()
                
                if any(keyword in comparison_result.lower() for keyword in ["difference", "change", "hazard", "risk"]):
                    self.add_vision_suggestion(f"Image Comparison: {comparison_result}")
            
        except Exception as e:
            QMessageBox.critical(self, "Comparison Error", f"Error comparing images: {str(e)}")
    
    def call_ollama_text_api(self, prompt):
        """Call Ollama API with text-only prompt (no image)"""
        payload = {
            "model": "llama4:latest",
            "prompt": prompt,
            "stream": False
        }
        
        ollama_api_url = "http://10.100.252.201:11434/api/generate"
        response = requests.post(ollama_api_url, json=payload, timeout=30)
        
        if response.status_code == 200:
            return response.json().get("response", "")
        else:
            raise Exception(f"Ollama API error: {response.status_code} - {response.text}")
    
    def call_ollama_api(self, image_path, prompt):
        """Call Ollama API with image and prompt"""
        with open(image_path, "rb") as img_file:
            img_base64 = base64.b64encode(img_file.read()).decode("utf-8")
        
        payload = {
            "model": "llama4:latest",
            "prompt": prompt,
            "images": [img_base64],
            "stream": False
        }
        
        ollama_api_url = "http://10.100.252.201:11434/api/generate"
        response = requests.post(ollama_api_url, json=payload, timeout=30)
        
        if response.status_code == 200:
            return response.json().get("response", "")
        else:
            raise Exception(f"Ollama API error: {response.status_code} - {response.text}")
    
    def update_vision_history(self):
        """Update the vision history display"""
        html = ""
        for analysis in reversed(self.vision_analyses[-5:]):  # Show last 5
            timestamp_str = analysis["timestamp"].strftime("%H:%M:%S")
            html += f"""
            <div style="margin-bottom: 8px; border-bottom: 1px solid #e5e7eb; padding-bottom: 4px;">
                <div style="font-size: 12px; color: #4b5563; font-weight: bold;">{timestamp_str}</div>
                <div style="font-size: 11px; color: #6b7280;">{analysis["result"]}</div>
            </div>
            """
        
        if not html:
            html = "<div style='font-style: italic; color: #6b7280;'>No vision analyses yet.</div>"
        
        self.vision_history.setHtml(html)
    
    def add_vision_suggestion(self, vision_result):
        """Add vision analysis result as an LLM suggestion"""
        suggestion_text = f"Vision Analysis: {vision_result[:150]}..."
        
        new_suggestion = {
            "timestamp": datetime.now(),
            "suggestion": suggestion_text,
            "confidence": 0.85
        }
        
        self.llm_suggestions.append(new_suggestion)
        if len(self.llm_suggestions) > 5:
            self.llm_suggestions = self.llm_suggestions[-5:]
        
        self.update_llm_suggestions()
    
    def init_ros2(self):
        """Initialize ROS2 node and connections"""
        try:
            rclpy.init(args=None)
            self.ros_node = Node('parameter_dashboard')
            self.connected_to_ros = True
            self.ros_status.set_active(True)
            self.ros_status.label.setText("Connected to ROS2")
            self.connect_button.setText("Disconnect from ROS2")

            self.linear_x = []
            self.angular_z = []
            self.time_data = []
            
            # Set up ROS2 communication
            self.cmd_vel_subscriber = self.ros_node.create_subscription(
                Twist,
                '/cmd_vel',
                self.handle_cmd_vel_update,
                10
            )
            
            # Start ROS2 spinner
            self.ros_spinner = QTimer(self)
            self.ros_spinner.timeout.connect(self.spin_ros)
            self.ros_spinner.start(100)
            
        except Exception as e:
            print(f"Failed to initialize ROS2: {e}")
            self.connected_to_ros = False
    
    def spin_ros(self):
        """Spin ROS2 node once"""
        if self.ros_node and self.connected_to_ros:
            rclpy.spin_once(self.ros_node, timeout_sec=0)
    
    def handle_cmd_vel_update(self, msg):
        """Handle cmd_vel updates from ROS2"""
        try:
            self.vel_x = msg.linear.x
            self.ang_z = msg.angular.z
            self.linear_x_label.setText(f"X: {msg.linear.x:.2f} m/s")
            self.linear_y_label.setText(f"Y: {msg.linear.y:.2f} m/s")
            self.linear_z_label.setText(f"Z: {msg.linear.z:.2f} m/s")
            self.angular_x_label.setText(f"X: {msg.angular.x:.2f} rad/s")
            self.angular_y_label.setText(f"Y: {msg.angular.y:.2f} rad/s")
            self.angular_z_label.setText(f"Z: {msg.angular.z:.2f} rad/s")
        except Exception as e:
            print(f"Error updating cmd_vel display: {e}")

    def toggle_ros_connection(self):
        """Connect or disconnect from ROS2"""
        if self.connected_to_ros:
            if self.ros_node:
                self.ros_node.destroy_node()
                rclpy.shutdown()
                self.ros_node = None
            self.connected_to_ros = False
            self.ros_status.set_active(False)
            self.ros_status.label.setText("Disconnected from ROS2")
            self.connect_button.setText("Connect to ROS2")
            self.ros_spinner.stop()
        else:
            self.init_ros2()
    
    def generate_mock_data(self):
        """Generate initial mock data for the dashboard"""
        self.performance_data = []
        for i in range(20):
            timestamp = datetime.now() - timedelta(minutes=(20-i)*5)
            self.performance_data.append({
                "timestamp": timestamp,
                "parameters": {
                    "max_velocity": 0.3 + (i % 4) * 0.2,
                    "obstacle_threshold": 0.2 + (i % 3) * 0.1,
                    "goal_tolerance": 0.1 + (i % 3) * 0.1
                },
                "success_rate": 0.7 + random.random() * 0.3,
                "execution_time": 10 + random.random() * 5,
                "collision_count": int(random.random() * 3),
                "failure_reason": "Obstacle avoidance failed" if i % 5 == 0 else 
                               "Path planning timeout" if i % 7 == 0 else 
                               "Goal unreachable" if i % 9 == 0 else None
            })
        
        # Extract unique parameter sets
        unique_sets = {}
        for item in self.performance_data:
            params = item["parameters"]
            key = f"{params['max_velocity']}-{params['obstacle_threshold']}-{params['goal_tolerance']}"
            
            if key not in unique_sets:
                unique_sets[key] = {
                    "parameters": params,
                    "tests": 0,
                    "avg_success": 0,
                    "avg_time": 0,
                    "collisions": 0,
                    "failures": 0
                }
            
            unique_sets[key]["tests"] += 1
            unique_sets[key]["avg_success"] += item["success_rate"]
            unique_sets[key]["avg_time"] += item["execution_time"]
            unique_sets[key]["collisions"] += item["collision_count"]
            if item["failure_reason"]:
                unique_sets[key]["failures"] += 1
        
        # Calculate averages
        for key in unique_sets:
            set_data = unique_sets[key]
            set_data["avg_success"] /= set_data["tests"]
            set_data["avg_time"] /= set_data["tests"]
        
        self.parameter_sets = list(unique_sets.values())
        
        # Generate mock failures
        self.failures = []
        for item in self.performance_data:
            if item["failure_reason"]:
                self.failures.append({
                    "timestamp": item["timestamp"],
                    "reason": item["failure_reason"],
                    "parameters": item["parameters"],
                    "context": f"Navigation failed at position ({random.random()*10:.2f}, {random.random()*10:.2f})"
                })
        
        # Generate mock LLM suggestions
        self.llm_suggestions = [
            {
                "timestamp": datetime.now(),
                "suggestion": "Your obstacle_threshold is likely too low (0.2) for safe navigation. When combined with high velocity (0.9), the robot doesn't have enough time to respond to obstacles. Try increasing obstacle_threshold to at least 0.4.",
                "confidence": 0.89
            },
            {
                "timestamp": datetime.now() - timedelta(minutes=10),
                "suggestion": "Path planning timeouts are occurring when max_velocity > 0.7 and goal_tolerance < 0.15. This creates challenging planning scenarios. Consider either reducing velocity or increasing tolerance.",
                "confidence": 0.76
            }
        ]
    
    def simulate_data_update(self):
        """Simulate new data coming in (for demo purposes)"""
        if not self.collecting_data:
            return
            
        timestamp = datetime.now()
        new_data = {
            "timestamp": timestamp,
            "parameters": dict(self.current_params),
            "success_rate": min(0.95, 0.5 + 
                               (self.current_params["obstacle_threshold"] * 0.5) + 
                               (self.current_params["goal_tolerance"] * 0.5) - 
                               (self.current_params["max_velocity"] * 0.1) +
                               (random.random() * 0.1)),
            "execution_time": max(5, 8 + 
                                (self.current_params["max_velocity"] * -2) + 
                                (self.current_params["obstacle_threshold"] * 3) +
                                (random.random() * 2)),
            "collision_count": int(max(0, (0.5 - self.current_params["obstacle_threshold"]) * 5 * random.random())),
            "failure_reason": None
        }
        
        if random.random() < 0.2:
            if self.current_params["obstacle_threshold"] < 0.3 and self.current_params["max_velocity"] > 0.7:
                new_data["failure_reason"] = "Obstacle avoidance failed"
            elif self.current_params["max_velocity"] > 1.0 and self.current_params["goal_tolerance"] < 0.2:
                new_data["failure_reason"] = "Path planning timeout"
        
        self.performance_data.append(new_data)
        if len(self.performance_data) > 50:
            self.performance_data = self.performance_data[-50:]
        
        self.update_parameter_sets(new_data)
        
        if new_data["failure_reason"]:
            self.failures.append({
                "timestamp": timestamp,
                "reason": new_data["failure_reason"],
                "parameters": dict(self.current_params),
                "context": f"Navigation failed at position ({random.random()*10:.2f}, {random.random()*10:.2f})"
            })
            
            if len(self.failures) > 20:
                self.failures = self.failures[-20:]
        
        self.update_charts()
        self.update_parameter_table()
        self.update_failure_log()
    
    def update_parameter_sets(self, new_data):
        """Update the parameter sets statistics with new data"""
        params = new_data["parameters"]
        key = f"{params['max_velocity']}-{params['obstacle_threshold']}-{params['goal_tolerance']}"
        
        existing_set = None
        for param_set in self.parameter_sets:
            set_params = param_set["parameters"]
            set_key = f"{set_params['max_velocity']}-{set_params['obstacle_threshold']}-{set_params['goal_tolerance']}"
            if set_key == key:
                existing_set = param_set
                break
        
        if existing_set:
            existing_set["tests"] += 1
            existing_set["avg_success"] = ((existing_set["avg_success"] * (existing_set["tests"] - 1)) + 
                                         new_data["success_rate"]) / existing_set["tests"]
            existing_set["avg_time"] = ((existing_set["avg_time"] * (existing_set["tests"] - 1)) + 
                                      new_data["execution_time"]) / existing_set["tests"]
            existing_set["collisions"] += new_data["collision_count"]
            if new_data["failure_reason"]:
                existing_set["failures"] += 1
        else:
            self.parameter_sets.append({
                "parameters": dict(params),
                "tests": 1,
                "avg_success": new_data["success_rate"],
                "avg_time": new_data["execution_time"],
                "collisions": new_data["collision_count"],
                "failures": 1 if new_data["failure_reason"] else 0
            })
    
    def update_charts(self):
        """Update the performance charts with the latest data"""
        if not self.performance_data:
            return
            
        timestamps = [i for i in range(len(self.performance_data))]
        success_rates = [item["success_rate"] for item in self.performance_data]
        exec_times = [item["execution_time"] for item in self.performance_data]
        
        self.success_curve.setData(timestamps, success_rates)
        self.time_curve.setData(timestamps, exec_times)
        
        axis = self.performance_graph.getAxis('bottom')
        ticks = []
        step = max(1, len(timestamps) // 5)
        for i in range(0, len(timestamps), step):
            if i < len(timestamps):
                ticks.append((i, self.performance_data[i]["timestamp"].strftime("%H:%M")))
        axis.setTicks([ticks])
    
    def update_parameter_table(self):
        """Update the parameter comparison table"""
        self.parameter_table.setRowCount(0)
        
        for i, param_set in enumerate(self.parameter_sets):
            self.parameter_table.insertRow(i)
            
            self.parameter_table.setItem(i, 0, QTableWidgetItem(f"{param_set['parameters']['max_velocity']:.1f}"))
            self.parameter_table.setItem(i, 1, QTableWidgetItem(f"{param_set['parameters']['obstacle_threshold']:.1f}"))
            self.parameter_table.setItem(i, 2, QTableWidgetItem(f"{param_set['parameters']['goal_tolerance']:.2f}"))
            self.parameter_table.setItem(i, 3, QTableWidgetItem(f"{param_set['avg_success']:.2f}"))
            self.parameter_table.setItem(i, 4, QTableWidgetItem(f"{param_set['avg_time']:.2f} s"))
            self.parameter_table.setItem(i, 5, QTableWidgetItem(f"{param_set['collisions']}"))
            self.parameter_table.setItem(i, 6, QTableWidgetItem(f"{param_set['failures']}"))
            self.parameter_table.setItem(i, 7, QTableWidgetItem(f"{param_set['tests']}"))
            
            apply_btn = QPushButton("Apply")
            apply_btn.clicked.connect(lambda _, idx=i: self.apply_param_set(idx))
            self.parameter_table.setCellWidget(i, 8, apply_btn)
    
    def update_failure_log(self):
        """Update the failures log text area"""
        html = ""
        for failure in reversed(self.failures):
            timestamp_str = failure["timestamp"].strftime("%H:%M:%S")
            params = failure["parameters"]
            param_str = f"v={params['max_velocity']:.1f}, obs={params['obstacle_threshold']:.1f}, tol={params['goal_tolerance']:.2f}"
            
            html += f"""
            <div style="margin-bottom: 8px; border-bottom: 1px solid #e5e7eb; padding-bottom: 8px;">
                <div style="font-weight: bold; color: #b91c1c;">{failure["reason"]}</div>
                <div style="font-size: 12px; color: #4b5563;">{failure["context"]}</div>
                <div style="font-size: 12px; color: #6b7280;">Parameters: {param_str} • {timestamp_str}</div>
            </div>
            """
        
        if not html:
            html = "<div style='font-style: italic; color: #6b7280;'>No failures recorded.</div>"
            
        self.failures_area.setHtml(html)
    
    def update_llm_suggestions(self):
        """Update the LLM suggestions text area"""
        html = ""
        for suggestion in reversed(self.llm_suggestions):
            timestamp_str = suggestion["timestamp"].strftime("%H:%M:%S")
            confidence = int(suggestion["confidence"] * 100)
            
            html += f"""
            <div style="margin-bottom: 8px; border-bottom: 1px solid #dbeafe; padding-bottom: 8px;">
                <div style="font-size: 14px; color: #1e40af;">{suggestion["suggestion"]}</div>
                <div style="font-size: 12px; color: #6b7280;">Confidence: {confidence}% • {timestamp_str}</div>
            </div>
            """
        
        if not html:
            html = "<div style='font-style: italic; color: #6b7280;'>No suggestions available yet.</div>"
            
        self.suggestions_area.setHtml(html)
    
    def handle_param_change(self, param, value):
        """Handle changes to parameter sliders"""
        self.current_params[param] = value
        
        if param == 'max_velocity':
            self.velocity_label.setText(f"{value} m/s")
        elif param == 'obstacle_threshold':
            self.obstacle_label.setText(f"{value} m")
        elif param == 'goal_tolerance':
            self.tolerance_label.setText(f"{value} m")
    
    def apply_param_set(self, index):
        """Apply a parameter set from the table to the current parameters"""
        if index < 0 or index >= len(self.parameter_sets):
            return
            
        param_set = self.parameter_sets[index]
        self.current_params = dict(param_set["parameters"])
        
        self.velocity_slider.setValue(int(self.current_params['max_velocity'] * 10))
        self.obstacle_slider.setValue(int(self.current_params['obstacle_threshold'] * 10))
        self.tolerance_slider.setValue(int(self.current_params['goal_tolerance'] * 100))
        
        self.velocity_label.setText(f"{self.current_params['max_velocity']} m/s")
        self.obstacle_label.setText(f"{self.current_params['obstacle_threshold']} m")
        self.tolerance_label.setText(f"{self.current_params['goal_tolerance']} m")
    
    def apply_parameters(self):
        """Apply the current parameters to the ROS2 system"""
        print(f"Applying parameters: {self.current_params}")
        
        if self.connected_to_ros and self.ros_node:
            try:
                print("Sending parameters to ROS2 node")
            except Exception as e:
                print(f"Error applying parameters: {e}")
        else:
            print("Not connected to ROS2, parameters only applied locally")
    
    def toggle_data_collection(self):
        """Toggle data collection on/off"""
        self.collecting_data = not self.collecting_data
        
        if self.collecting_data:
            self.collection_status.set_active(True)
            self.collection_status.label.setText("Collecting data for LLM training")
            self.collection_button.setText("Stop Collection")
        else:
            self.collection_status.set_active(False)
            self.collection_status.label.setText("Data collection paused")
            self.collection_button.setText("Start Collection")
    
    def export_training_data(self):
        """Export the collected data for LLM training"""
        try:
            data = {
                "performanceData": [
                    {
                        "timestamp": item["timestamp"].isoformat(),
                        "parameters": item["parameters"],
                        "success_rate": item["success_rate"],
                        "execution_time": item["execution_time"],
                        "collision_count": item["collision_count"],
                        "failure_reason": item["failure_reason"]
                    } for item in self.performance_data
                ],
                "parameterSets": self.parameter_sets,
                "failures": [
                    {
                        "timestamp": item["timestamp"].isoformat(),
                        "reason": item["reason"],
                        "parameters": item["parameters"],
                        "context": item["context"]
                    } for item in self.failures
                ],
                "visionAnalyses": [
                    {
                        "timestamp": item["timestamp"].isoformat(),
                        "prompt": item["prompt"],
                        "result": item["result"]
                    } for item in self.vision_analyses
                ]
            }
            
            file_path = "ros2_navigation_training_data_with_vision.json"
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
                
            print(f"Data exported to {file_path}")
        except Exception as e:
            print(f"Error exporting data: {e}")

    def create_llm_settings_ui(self):
        """Create the LLM Integration Settings UI section"""
        llm_settings_group = QGroupBox("LLM Integration Settings")
        llm_settings_layout = QGridLayout(llm_settings_group)
        
        # LLM Mode Selection
        llm_settings_layout.addWidget(QLabel("Integration Method:"), 0, 0)
        self.llm_mode = QComboBox()
        self.llm_mode.addItems(["API Key", "HTTP Endpoint", "Curl Command"])
        self.llm_mode.currentIndexChanged.connect(self.toggle_llm_mode)
        llm_settings_layout.addWidget(self.llm_mode, 0, 1)
        
        # Provider selection for API key mode
        llm_settings_layout.addWidget(QLabel("LLM Provider:"), 1, 0)
        self.llm_provider = QComboBox()
        self.llm_provider.addItems(["Llama", "Claude", "DeepSeek", "Custom Endpoint"])
        llm_settings_layout.addWidget(self.llm_provider, 1, 1)
        
        # API Key input
        llm_settings_layout.addWidget(QLabel("API Key:"), 2, 0)
        self.api_key = QLineEdit()
        self.api_key.setEchoMode(QLineEdit.Password)
        self.api_key.setPlaceholderText("Enter API key")
        llm_settings_layout.addWidget(self.api_key, 2, 1)
        
        # HTTP Endpoint
        llm_settings_layout.addWidget(QLabel("HTTP Endpoint:"), 3, 0)
        self.http_endpoint = QLineEdit()
        self.http_endpoint.setPlaceholderText("http://localhost:11434/api/chat")
        self.http_endpoint.setVisible(False)
        llm_settings_layout.addWidget(self.http_endpoint, 3, 1)
        
        # Curl Command
        llm_settings_layout.addWidget(QLabel("Curl Command:"), 4, 0)
        self.curl_command = QTextEdit()
        self.curl_command.setPlaceholderText('curl http://localhost:11434/api/chat \\\n'
                                            '-d \'{"model": "llama3.2-vision", "messages": [{"role": "user", "content": "$PROMPT", "images": ["$IMAGE"]}], "stream": false}\'')
        self.curl_command.setVisible(False)
        self.curl_command.setMaximumHeight(100)
        llm_settings_layout.addWidget(self.curl_command, 4, 1)
        
        # Custom prompt
        llm_settings_layout.addWidget(QLabel("Custom Prompt:"), 5, 0)
        self.custom_prompt = QTextEdit()
        self.custom_prompt.setPlaceholderText(
            "You are an expert in ROS2 navigation. Analyze the following navigation performance data...")
        self.custom_prompt.setMaximumHeight(100)
        llm_settings_layout.addWidget(self.custom_prompt, 5, 1)
        
        # Real-time data
        self.realtime_suggestions = QCheckBox("Request real-time suggestions from LLM")
        llm_settings_layout.addWidget(self.realtime_suggestions, 6, 0, 1, 2)
        
        # Test LLM Connection and Request Suggestion buttons
        button_layout = QHBoxLayout()
        
        self.test_llm_button = QPushButton("Test LLM Connection")
        self.test_llm_button.clicked.connect(self.test_llm_connection)
        button_layout.addWidget(self.test_llm_button)
        
        self.request_suggestion_button = QPushButton("Request Suggestion")
        self.request_suggestion_button.clicked.connect(self.request_llm_suggestion)
        button_layout.addWidget(self.request_suggestion_button)
        
        llm_settings_layout.addLayout(button_layout, 7, 0, 1, 2)
        
        # Save settings button
        save_llm_button = QPushButton("Save LLM Settings")
        save_llm_button.clicked.connect(self.save_llm_settings)
        llm_settings_layout.addWidget(save_llm_button, 8, 0, 1, 2)
        
        return llm_settings_group

    def toggle_llm_mode(self, index):
        """Toggle between different LLM integration modes"""
        self.api_key.setVisible(False)
        self.llm_provider.setVisible(False)
        self.http_endpoint.setVisible(False)
        self.curl_command.setVisible(False)
        
        if index == 0:  # API Key
            self.api_key.setVisible(True)
            self.llm_provider.setVisible(True)
        elif index == 1:  # HTTP Endpoint
            self.http_endpoint.setVisible(True)
        elif index == 2:  # Curl Command
            self.curl_command.setVisible(True)

    def test_llm_connection(self):
        """Test the connection to the LLM"""
        try:
            test_prompt = "This is a test request. Please respond with 'Connection successful'."
            
            mode = self.llm_mode.currentIndex()
            
            if mode == 0:  # API Key
                provider = self.llm_provider.currentText()
                api_key = self.api_key.text()
                
                if not api_key:
                    QMessageBox.warning(self, "Test Failed", "API Key is required")
                    return
                
                response = self.call_llm_api(provider, api_key, test_prompt)
                
            elif mode == 1:  # HTTP Endpoint
                endpoint = self.http_endpoint.text()
                
                if not endpoint:
                    QMessageBox.warning(self, "Test Failed", "HTTP Endpoint is required")
                    return
                    
                headers = {"Content-Type": "application/json"}
                payload = {
                    "model": "llama3.2-vision",
                    "messages": [{"role": "user", "content": test_prompt}],
                    "stream": False
                }
                
                response = requests.post(endpoint, headers=headers, json=payload)
                response.raise_for_status()
                response = response.json()
                
            elif mode == 2:  # Curl Command
                curl_cmd = self.curl_command.toPlainText()
                
                if not curl_cmd:
                    QMessageBox.warning(self, "Test Failed", "Curl Command is required")
                    return
                    
                curl_cmd = curl_cmd.replace("$PROMPT", test_prompt)
                curl_cmd = curl_cmd.replace('"images": ["$IMAGE"]', '"images": []')
                
                result = subprocess.run(
                    curl_cmd, 
                    shell=True, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE, 
                    text=True
                )
                
                if result.returncode != 0:
                    raise Exception(f"Curl command failed: {result.stderr}")
                
                try:
                    response = json.loads(result.stdout)
                except json.JSONDecodeError:
                    response = {"text": result.stdout}
            
            response_text = str(response)[:200] + "..." if len(str(response)) > 200 else str(response)
            QMessageBox.information(self, "Test Successful", f"LLM connection successful!\nResponse: {response_text}")
            
        except Exception as e:
            QMessageBox.critical(self, "Test Failed", f"Error: {str(e)}")

    def call_llm_api(self, provider, api_key, prompt):
        """Call the LLM API using the provider and API key"""
        if provider == "Llama":
            headers = {"Content-Type": "application/json"}
            payload = {
                "model": "llama3.2-vision",
                "messages": [{"role": "user", "content": prompt}],
                "stream": False
            }
            response = requests.post(
                "http://localhost:11434/api/chat",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()
            
        elif provider == "Claude":
            headers = {
                "x-api-key": api_key,
                "Content-Type": "application/json"
            }
            payload = {
                "model": "claude-3-opus-20240229",
                "max_tokens": 1000,
                "messages": [{"role": "user", "content": prompt}]
            }
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()
            
        raise ValueError(f"Unsupported provider: {provider}")

    def save_llm_settings(self):
        """Save the LLM settings"""
        QMessageBox.information(self, "Settings Saved", "LLM settings have been saved.")
        
        if self.realtime_suggestions.isChecked():
            if not hasattr(self, 'llm_suggestion_timer') or not self.llm_suggestion_timer.isActive():
                self.llm_suggestion_timer = QTimer(self)
                self.llm_suggestion_timer.timeout.connect(self.request_llm_suggestion)
                self.llm_suggestion_timer.start(60000)
        else:
            if hasattr(self, 'llm_suggestion_timer') and self.llm_suggestion_timer.isActive():
                self.llm_suggestion_timer.stop()

    def request_llm_suggestion(self):
        """Request a suggestion from the LLM based on current data"""
        if not self.performance_data:
            return
        
        try:
            class DateTimeEncoder(json.JSONEncoder):
                def default(self, obj):
                    if isinstance(obj, datetime):
                        return obj.isoformat()
                    return super().default(obj)
            
            current_params = dict(self.current_params)
            
            prompt = self.custom_prompt.toPlainText()
            if not prompt:
                prompt = "You are an expert in ROS2 navigation parameter tuning. "
                prompt += "Based on the following data, suggest parameter improvements:"
            
            prompt += f"\n\nCurrent Parameters: {json.dumps(current_params)}"
            
            mode = self.llm_mode.currentIndex()
            
            response_text = ""
            
            if mode == 0:  # API Key
                provider = self.llm_provider.currentText()
                api_key = self.api_key.text()
                
                if not api_key:
                    print("API Key is required for LLM suggestions")
                    return
                    
                response = self.call_llm_api(provider, api_key, prompt)
                
                if provider == "Claude":
                    response_text = response.get("content", [{}])[0].get("text", "")
                elif provider == "Llama":
                    response_text = response.get("message", {}).get("content", "")
                else:
                    response_text = str(response)
                
            elif mode == 1:  # HTTP Endpoint
                endpoint = self.http_endpoint.text()
                
                if not endpoint:
                    print("HTTP Endpoint is required for LLM suggestions")
                    return
                    
                headers = {"Content-Type": "application/json"}
                payload = {
                    "model": "llama3.2-vision",
                    "messages": [{"role": "user", "content": prompt}],
                    "stream": False
                }
                
                response = requests.post(endpoint, headers=headers, json=payload)
                response.raise_for_status()
                result = response.json()
                response_text = result.get("message", {}).get("content", str(result))
                
            elif mode == 2:  # Curl Command
                curl_cmd = self.curl_command.toPlainText()

                if not curl_cmd:
                    print("Curl Command is required for LLM suggestions")
                    return
                
                curl_cmd = curl_cmd.replace("$PROMPT", prompt)
                curl_cmd = curl_cmd.replace('"images": ["$IMAGE"]', '"images": []')
                
                result = subprocess.run(
                    curl_cmd,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                if result.returncode != 0:
                    print(f"Curl command failed: {result.stderr}")
                    return
                
                try:
                    response = json.loads(result.stdout)
                    if isinstance(response, dict) and "message" in response:
                        response_text = response["message"].get("content", "")
                    else:
                        response_text = str(response)
                except json.JSONDecodeError:
                    response_text = result.stdout

                # Parse Llama response format
                import re
                matches = re.findall(r'"content":"([^"]*)"', response_text)
                if matches:
                    response_text = "".join(matches)
                    response_text = response_text.replace('\\n', '\n').replace('\\"', '"')

            if response_text:
                new_suggestion = {
                    "timestamp": datetime.now(),
                    "suggestion": response_text[:500] + "..." if len(response_text) > 500 else response_text,
                    "confidence": 0.9
                }
                self.llm_suggestions.append(new_suggestion)
                if len(self.llm_suggestions) > 5:
                    self.llm_suggestions = self.llm_suggestions[-5:]
                self.update_llm_suggestions()
             
        except Exception as e:
            print(f"Error requesting LLM suggestion: {e}")

    def closeEvent(self, event):
        """Clean up resources when closing the application"""
        self.update_timer.stop()
        
        if self.connected_to_ros:
            if hasattr(self, 'ros_spinner'):
                self.ros_spinner.stop()
            if self.ros_node:
                self.ros_node.destroy_node()
                rclpy.shutdown()
        
        super().closeEvent(event)


def main():
    app = QApplication(sys.argv)
    window = ROS2ParameterTuningDashboard()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()