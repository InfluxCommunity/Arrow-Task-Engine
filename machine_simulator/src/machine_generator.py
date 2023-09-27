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
        if currentLoad >= 190: self.temperature = randint(95, 120)
        elif currentLoad > 110: self.temperature = randint(80, 90)
        elif currentLoad >= 40: self.temperature = randint(35, 40)
        elif currentLoad > 0: self.temperature = randint(29, 34)
        else: self.temperature = 20
        return self.temperature

    def setLoad(self, load):
        # TODO dont randomise    
        self.load = load
       

    def returnPower(self):
        currentLoad = self.load
        if currentLoad >= 190: self.power = randint(400, 500)
        elif currentLoad > 110: self.power = randint(300, 320)
        elif currentLoad >= 40: self.power = randint(200, 220)
        elif currentLoad == 0: self.power = 0
        else: self.power = randint(180, 199)
        
        return self.power
    
        
    def returnVibration(self):
        currentLoad = self.load
        if currentLoad >= 190: self.vibration = randint(500, 600)
        elif currentLoad > 110: self.vibration = randint(300, 500)
        elif currentLoad == 0: self.vibration  = 0
        elif currentLoad >= 40: self.vibration = randint(80, 90)
        else: self.vibration = randint(50, 79)
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

    sleeptime = 1
    m.setLoad(randint(10, 50))
    increasing = True
    
    
    while True:
        # Check if fault state has changed from True to False
        if m.previous_fault_state and not m.fault:
            m.setLoad(50)
            m.previous_fault_state = False

        # Chance of fault
        if m.fault:
            if counter2 == 5:
                current_load = m.load
                if current_load < 200:
                    new_load = min(current_load + 20, 200)
                    m.setLoad(new_load)
                counter2 = 0
        else:
            if counter2 == 5:
                # Gradually change load between 50 and 99
                current_load = m.load
                if increasing:
                    new_load = current_load + 5
                    if new_load >= 99:
                        increasing = False
                else:
                    new_load = current_load - 5
                    if new_load <= 50:
                        increasing = True
                
                m.setLoad(new_load)
                counter2 = 0
           

        # Publish messages
        check_machine = m.returnMachineHealth()
        #print(check_machine,flush=True)
        mqttProducer.publish_to_topic(topic="machine", data=check_machine)
        
        sleep(sleeptime)
        counter = counter + 1
        counter2 = counter2 + 1




