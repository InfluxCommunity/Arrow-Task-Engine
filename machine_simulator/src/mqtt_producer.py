import paho.mqtt.client as paho
from paho import mqtt
import json
import time


        # setting callbacks for different events to see if it works, print the message etc.
def on_connect(client, userdata, flags, rc, properties=None):
        print("CONNACK received with code %s." % rc)

    # with this callback you can see if your publish was successful
def on_publish(client, userdata, mid, properties=None):
        print("mid: " + str(mid))

    # print which topic was subscribed to
def on_subscribe(client, userdata, mid, granted_qos, properties=None):
        print("Subscribed: " + str(mid) + " " + str(granted_qos))

    # print message, useful for checking if it was successful
def on_message(client, userdata, msg):
        print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))


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
        self.client.on_connect = on_connect

        self.client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
        self.client.username_pw_set(username=username, password=password) 
        self.client.connect(host=self.mqttBroker,port=self.port, keepalive=MQTT_KEEPALIVE_INTERVAL)
        # setting callbacks, use separate functions like above for better visibility
        self.client.on_subscribe = on_subscribe
        self.client.on_message = on_message
        self.client.on_publish = on_publish
        print("connected to MQTT broker", flush=True)



    def publish_to_topic(self, topic: str, data: dict):
        topic = topic +"/"+ str(data["metadata"]["machineID"])
        message = json.dumps(data)
        self.client.publish(topic=topic, payload=message)
        print(message, flush=True)