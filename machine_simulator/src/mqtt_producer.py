import paho.mqtt.client as paho
from paho import mqtt
import json

class mqtt_publisher:
    def __init__(self, address, port, clientID) -> None:
       
        self.mqttBroker = address
        self.port = port
        self.clientID = clientID
        self.client = None


    def connect_client(self):
        MQTT_KEEPALIVE_INTERVAL = 45
        self.client = paho.Client(self.clientID)
        self.client.connect(host=self.mqttBroker,port=self.port, keepalive=MQTT_KEEPALIVE_INTERVAL)
        

    def connect_client_secure(self, username, password):
        print("Creating secure connection", flush=True)
        MQTT_KEEPALIVE_INTERVAL = 45
        self.client = paho.Client(userdata=None, protocol=paho.MQTTv5)
        self.client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
        self.client.username_pw_set(username=username, password=password) 
        self.client.connect(host=self.mqttBroker,port=self.port, keepalive=MQTT_KEEPALIVE_INTERVAL)
        print("connected to MQTT broker", flush=True)



    def publish_to_topic(self, topic: str, data: dict):
        topic = topic +"/"+ str(data["metadata"]["machineID"])
        message = json.dumps(data)
        self.client.publish(topic=topic, payload=message)
        print(message, flush=True)