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
        self.fault = not self.fault

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

    def setLoad(self, load):
        # TODO dont randomise    
        self.load = load
       

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
        if currentLoad >= 90: self.vibration = 83
        elif currentLoad >= 70: self.vibration = 90
        elif currentLoad >= 41: self.vibration = randint(90, 91)
        elif currentLoad == 0: self.vibration  = 0
        elif currentLoad == 40: self.vibration = randint(85, 90) # We want this to be normal machine health
        else: self.vibration = randint(50, 85)
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
    PORT = int(os.getenv('PORT', "1883"))
    USERNAME = os.getenv('USERNAME', None)
    PASSWORD = os.getenv('PASSWORD', None)
    counter = 0
    counter2 = 0



    mqttProducer = mqtt_publisher(address=BROKER, port=PORT, clientID=m.returnMachineID())
    if USERNAME is not None and PASSWORD is not None:
        mqttProducer.connect_client_secure(username=os.getenv('USERNAME'), password=os.getenv('PASSWORD'))
    else:
        mqttProducer.connect_client()

    sleeptime = 0.5
    m.setLoad(40)
   
    
    
    while True:
        # Check if fault state has changed from True to False
        if m.previous_fault_state and not m.fault:
            print("Fault state changed from True to False", flush=True)
            m.setLoad(40)
            m.previous_fault_state = False

        # Chance of fault
        if m.fault:
            print(f"{m.returnMachineID()} fault activate. Current load: {m.load}", flush=True)
            if counter >= 5:
                current_load = m.load
                if current_load < 100:
                        print("Increasing load", flush=True)
                        new_load = current_load + 5
                        print(f"New load: {new_load}", flush=True)
                        m.setLoad(new_load)
                        counter = 0
                else:
                        print("Load already at 100", flush=True)
                        new_load = 41
                        print(f"New load: {new_load}", flush=True)
                        m.setLoad(new_load)
                        counter = 0
            counter += 1


           

        # Publish messages
        check_machine = m.returnMachineHealth()
        #print(check_machine,flush=True)
        mqttProducer.publish_to_topic(topic="machine", data=check_machine)
        
        sleep(sleeptime)





