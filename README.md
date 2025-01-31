# VDA5050 Robot Simulator

This project provides a Python-based simulator for testing VDA5050-compatible AGVs (Automated Guided Vehicles). It creates dummy robots that communicate using the VDA5050 protocol over MQTT, making it ideal for testing Fleet Management Systems (FMS).

## Features

- Simulates multiple AGVs simultaneously
- Implements VDA5050 protocol communication
- MQTT-based message exchange
- Simulated movement and battery states
- Error simulation capabilities
- Real-time state updates
- Visualization data publishing

## Requirements

- Python 3.7+
- paho-mqtt
- python-dotenv

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the project root with the following variables (optional):
```
MQTT_BROKER_HOST=localhost
MQTT_BROKER_PORT=1883
```

## Usage

Run the simulator:
```bash
python robot.py
```

By default, it will create 3 dummy robots that connect to the local MQTT broker.

## MQTT Topics

Each robot subscribes and publishes to the following topics:

- Order topic: `uagv/{robot_id}/order`
- State topic: `uagv/{robot_id}/state`
- Visualization topic: `uagv/{robot_id}/visualization`

## Testing

You can test the robots by publishing order messages to the order topic. Example order message:

```json
{
    "orderId": "order_123",
    "nodes": [
        {
            "nodeId": "node1",
            "x": 10.0,
            "y": 20.0
        },
        {
            "nodeId": "node2",
            "x": 30.0,
            "y": 40.0
        }
    ]
}
```
