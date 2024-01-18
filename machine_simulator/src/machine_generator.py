from bdb import GENERATOR_AND_COROUTINE_FLAGS
import faulthandler
import os
import threading
from threading import Event


from random import  randint
from time import sleep
from mqtt_producer import mqtt_publisher
from faker import Faker

fake = Faker()

machine_id_counter = 1




class machine():
    def __init__ (self) -> None:
        global machine_id_counter
        self.machine_id = "machine" + str(machine_id_counter)
        machine_id_counter+=1
        self.temperature = 0
        self.load = 0
        self.power = 0
        self.vibration = 0
        self.barcode= fake.ean(length=8)
        self.provider=fake.company()
        self.fault = False
        self.previous_fault_state = False

    def toggle_fault(self):
        self.previous_fault_state = self.fault
        self.fault = True
    
    def toggle_fault_off(self):
        self.previous_fault_state = self.fault
        self.fault = False

    def returnMachineID(self):
        return self.machine_id

   
    def returnTemperature(self):
        currentLoad = self.load
        if currentLoad >= 90: self.temperature = randint(95, 120)
        elif currentLoad > 65: self.temperature = randint(80, 90)
        elif currentLoad >= 40: self.temperature = randint(35, 40)
        elif currentLoad > 0: self.temperature = randint(29, 34)
        else: self.temperature = 20
        return self.temperature

    def setLoad(self, state, fault):
        print(self.fault, flush=True)
        if self.fault == True:
            state = 'fault'
            print("Fault state activated", flush=True)

        if state == 'grab_package':
            self.load = 42
        elif state == 'wrap_package':
            self.load = 71
        elif state == 'place_bow':
            self.load = 30
        elif state == 'place_package':
            self.load = 42
        elif state == 'fault':
            if self.load == 100:
                self.load = 90
            else:
                self.load = 100
  
       

    def returnPower(self):
        currentLoad = self.load
        if currentLoad >= 90: self.power = randint(400, 500)
        elif currentLoad > 65: self.power = randint(300, 320)
        elif currentLoad >= 40: self.power = randint(200, 220)
        elif currentLoad == 0: self.power = 0
        else: self.power = randint(180, 199)
        
        return self.power
    
        
    def returnVibration(self):
        currentLoad = self.load
        if currentLoad >= 100: self.vibration = randint(69, 70)
        elif currentLoad == 90: self.vibration = randint(90, 92)
        elif currentLoad >= 70: self.vibration = 90
        elif currentLoad >= 41: self.vibration = randint(80, 85)
        elif currentLoad == 0: self.vibration  = 0
        else: self.vibration = randint(70, 75)
        return self.vibration

    def returnMachineHealth(self):
        # trigger load first as needs to be constent:
        return {"metadata":{"machineID": self.returnMachineID(), 
                "barcode": self.barcode, "provider": self.provider}, 
                "data": [ {"temperature": self.returnTemperature()}, 
                         {"load": self.load}, 
                         {"power": self.returnPower()}, 
                         {"vibration": self.returnVibration()}]
                         }



def runMachine(m):
    BROKER = os.getenv('BROKER', "localhost")
    PORT = int(os.getenv('PORT', "8883"))
    USERNAME = os.getenv('USERNAME', None)
    PASSWORD = os.getenv('PASSWORD', None)
    counter = 0



    mqttProducer = mqtt_publisher(address=BROKER, port=PORT, clientID=m.returnMachineID())
    if USERNAME is not None and PASSWORD is not None:
        mqttProducer.connect_client_secure(username=USERNAME, password=PASSWORD)
    else:
        mqttProducer.connect_client()

    sleeptime = 1

    while True:
            for i in range(0, 10):
                m.setLoad("grab_package", m.fault)
                mqttProducer.publish_to_topic(topic="machine", data=m.returnMachineHealth())
                sleep(0.5)
                i += 1
            for i in range(0, 15):
                m.setLoad("wrap_package", m.fault)
                mqttProducer.publish_to_topic(topic="machine", data=m.returnMachineHealth())
                sleep(0.5)
                i += 1
            for i in range(0, 5):
                m.setLoad("place_bow", m.fault)
                mqttProducer.publish_to_topic(topic="machine", data=m.returnMachineHealth())
                sleep(0.5)
                i += 1
            for i in range(0, 10):
                m.setLoad("place_package", m.fault)
                mqttProducer.publish_to_topic(topic="machine", data=m.returnMachineHealth())
                sleep(0.5)
                i += 1
        
            sleep(sleeptime)




