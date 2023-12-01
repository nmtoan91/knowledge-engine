import datetime
import time
import random
import logging
import random
from utils_echonet_controller import *
from enum import Enum
def generate_random_temperature(start=15.0, end=20.0):
    assert end > start
    return start + (end - start) * random.random()

class EchonetLITEDeviceType(Enum):
    UNKNOWN =0
    TEMPERATURE_SENSOR =1
    WASHING_MACHINE = 2
    def GetGraphByType(type):
        if type == EchonetLITEDeviceType.TEMPERATURE_SENSOR:
            return """
                        ?sensor rdf:type saref:Sensor .
                        ?measurement saref:measurementMadeBy ?sensor .
                        ?measurement saref:isMeasuredIn saref:TemperatureUnit .
                        ?measurement saref:hasValue ?temperature .
                        ?measurement saref:hasTimestamp ?timestamp .
                    """
        
        if type == EchonetLITEDeviceType.WASHING_MACHINE:
            return  """
                        ?esa rdf:type saref:Device .
                        ?esa saref:isUsedFor ?commodity .
                        ?commodity rdf:type saref:Electricity .
                        ?esa saref:makesMeasurement ?monitoring_of_power_consumption .
                        ?monitoring_of_power_consumption saref:relatesToProperty ?power .
                        ?power rdf:type saref:Power .
                        ?monitoring_of_power_consumption saref:isMeasuredIn ?unit .
                        ?monitoring_of_power_consumption saref:hasValue ?value .
                    """
    




class EchonetLITEDevice:
    def __init__(self,type:EchonetLITEDeviceType,kb_id,kb_name,kb_description,ke_endpoint):
        self.measurement_counter = 0
        self.type = type
        self.kb_id = kb_id
        self.kb_name = kb_name
        self.kb_description= kb_description
        self.ke_endpoint = ke_endpoint
        self.RegisterKnowledgeBase()
    def RegisterKnowledgeBase(self):
        register_knowledge_base(self.kb_id, self.kb_name, self.kb_description, self.ke_endpoint)
        self.ki_id = register_post_knowledge_interaction(EchonetLITEDeviceType.GetGraphByType(self.type),
                                                        None,
                                                        self.kb_name,
                                                        self.kb_id,
                                                        self.ke_endpoint,
                                                        {
                                                            "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                                                            "saref": "https://saref.etsi.org/core/",
                                                        },                
                                                        )
    def TryToSendData(self):
        now = datetime.datetime.now()
        self.measurement_counter+=1
        value = generate_random_temperature(80, 100)
        if self.type == EchonetLITEDeviceType.TEMPERATURE_SENSOR:
            data = {
                    "sensor": f"<https://example.org/sensor/1>",
                    "measurement": f"<https://example.org/sensor/1/measurement/{self.measurement_counter}>",
                    "temperature": f"{value}",
                    "timestamp": f'"{now.isoformat()}"',
                }
        elif self.type == EchonetLITEDeviceType.WASHING_MACHINE:
            data = {
                    "esa": "<https://example.org/washingmachine/1>",
                    "commodity": "<https://example.org/commodity/electric>",
                    "monitoring_of_power_consumption": f"<https://example.org/sensor/1/measurement/{self.measurement_counter}>",
                    "power": f"<https://example.org/power/123>",
                    "unit": f'"watt"',
                    "value": f"{value}",
                }
        else: print("Error")
        
        now = datetime.datetime.now()
       
        post(
            [
                data
            ],
            self.ki_id,
            self.kb_id,
            self.ke_endpoint,
        )
        print("end posting: ", (datetime.datetime.now() - now).seconds,"seconds")

