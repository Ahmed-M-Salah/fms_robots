import json
import time
import random
import paho.mqtt.client as mqtt
from datetime import datetime
import threading
import logging
import os
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VDA5050Robot:
    def __init__(self, robot_id, broker_host="localhost", broker_port=1883):
        self.robot_id = robot_id
        self.manufacturer = "DummyManufacturer"
        self.serial_number = f"SN{random.randint(1000, 9999)}"
        
        # MQTT client setup
        self.client = mqtt.Client(f"robot_{robot_id}")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.broker_host = broker_host
        self.broker_port = broker_port
        
        # Set different starting positions based on robot_id
        robot_number = int(robot_id.split('_')[1])
        self.start_positions = {
            1: {"x": 200.0, "y": 200.0, "theta": 0.0},
            2: {"x": 150.0, "y": 150.0, "theta": 90.0},
            3: {"x": -150.0, "y": -150.0, "theta": 180.0},
            4: {"x": 200.0, "y": -200.0, "theta": 270.0},
            5: {"x": -300.0, "y": 300.0, "theta": 45.0}
        }
        
        # Robot state
        default_pos = {"x": 0.0, "y": 0.0, "theta": 0.0}
        self.position = self.start_positions.get(robot_number, default_pos).copy()
        self.velocity = {"linear": 0.0, "angular": 0.0}
        self.battery_level = 100
        self.operation_mode = "AUTOMATIC"
        self.errors = []
        self.order_id = None
        self.last_node_id = "START"
        self.order_update_id = 0
        self.state_update_id = 0
        
        # Topics
        self.order_topic = f"uagv/{self.robot_id}/order"
        self.state_topic = f"uagv/{self.robot_id}/state"
        self.visualization_topic = f"uagv/{self.robot_id}/visualization"

    def connect(self):
        """Connect to MQTT broker"""
        try:
            self.client.connect(self.broker_host, self.broker_port)
            self.client.loop_start()
            logger.info(f"Robot {self.robot_id} connected to MQTT broker")
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")

    def on_connect(self, client, userdata, flags, rc):
        """Callback when connected to MQTT broker"""
        logger.info(f"Robot {self.robot_id} connected with result code {rc}")
        self.client.subscribe(self.order_topic)

    def on_message(self, client, userdata, msg):
        """Handle incoming MQTT messages"""
        try:
            payload = json.loads(msg.payload.decode())
            logger.info(f"Robot {self.robot_id} received message on topic {msg.topic}: {payload}")
            
            if msg.topic == self.order_topic:
                self.handle_order(payload)
        except json.JSONDecodeError:
            logger.error(f"Failed to decode message: {msg.payload}")

    def handle_order(self, order):
        """Handle incoming order"""
        self.order_id = order.get("orderId")
        self.order_update_id += 1
        logger.info(f"Robot {self.robot_id} handling order: {self.order_id}")
        
        # Simulate order execution
        threading.Thread(target=self.execute_order, args=(order,)).start()

    def execute_order(self, order):
        """Simulate order execution"""
        nodes = order.get("nodes", [])
        for node in nodes:
            # Simulate movement to node
            self.move_to_node(node)
            time.sleep(2)  # Simulate movement time
            self.last_node_id = node.get("nodeId")
            self.publish_state()

    def move_to_node(self, node):
        """Simulate movement to a node"""
        target_x = node.get("x", 0)
        target_y = node.get("y", 0)
        
        # Simple linear interpolation
        steps = 10
        dx = (target_x - self.position["x"]) / steps
        dy = (target_y - self.position["y"]) / steps
        
        for _ in range(steps):
            self.position["x"] += dx
            self.position["y"] += dy
            self.battery_level = max(0, self.battery_level - 0.1)
            self.publish_state()
            time.sleep(0.5)

    def publish_state(self):
        """Publish robot state"""
        self.state_update_id += 1
        state = {
            "headerId": {
                "timestamp": datetime.utcnow().isoformat(),
                "version": "1.0",
                "manufacturer": self.manufacturer,
                "serialNumber": self.serial_number,
                "stateUpdateId": self.state_update_id
            },
            "state": {
                "orderId": self.order_id,
                "lastNodeId": self.last_node_id,
                "operatingMode": self.operation_mode,
                "batteryState": {
                    "batteryCharge": self.battery_level
                },
                "errors": self.errors,
                "position": {
                    "x": float(self.position["x"]),
                    "y": float(self.position["y"]),
                    "theta": float(self.position["theta"])
                },
                "velocity": self.velocity
            }
        }
        
        self.client.publish(self.state_topic, json.dumps(state))
        self.publish_visualization()

    def publish_visualization(self):
        """Publish visualization data"""
        vis_data = {
            "robotId": self.robot_id,
            "position": self.position,
            "batteryLevel": self.battery_level,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.client.publish(self.visualization_topic, json.dumps(vis_data))

    def simulate_error(self, error_type="TECHNICAL_ERROR"):
        """Simulate a robot error"""
        error = {
            "errorType": error_type,
            "errorDescription": f"Simulated {error_type}",
            "errorLevel": "WARNING"
        }
        self.errors.append(error)
        self.publish_state()

    def clear_errors(self):
        """Clear all errors"""
        self.errors = []
        self.publish_state()

def main():
    # Load environment variables
    load_dotenv()
    
    # Get MQTT broker details from environment variables or use defaults
    broker_host = os.getenv("MQTT_BROKER_HOST", "localhost")
    broker_port = int(os.getenv("MQTT_BROKER_PORT", 1883))
    
    # Create and start multiple robots
    robots = []
    num_robots = 3  # Number of dummy robots to create
    
    for i in range(num_robots):
        robot = VDA5050Robot(f"robot_{i+1}", broker_host, broker_port)
        robot.connect()
        robots.append(robot)
        logger.info(f"Started robot_{i+1}")
    
    try:
        while True:
            # Periodically update robot states
            for robot in robots:
                robot.publish_state()
            time.sleep(5)
    except KeyboardInterrupt:
        logger.info("Shutting down robots...")
        for robot in robots:
            robot.client.loop_stop()
            robot.client.disconnect()

if __name__ == "__main__":
    main()
