from datetime import datetime
import time
import random
import logging
import random
from utils_echonet_controller import *
from enum import Enum
import threading
from concurrent.futures import Future
from EchonetLITEDevice import EchonetLITEDevice
from EchonetLITEDevice import EchonetLITEDeviceType
import json


class EnergyUseCase(Enum):
    UNKNOWN=0,
    FLEXIBLE_START=1
    MONITORING_POWER_CONSUMPTION = 2
    LIMITATION_POWER_CONSUMPTION=3
    MANAGEMENT_POWER_CONSUMPTION_INCENTIVE_TABLE=4
    MANUAL_OPERATION=6
    MANAGEMENT_POWER_CONSUMPTION_POWER_PLAN=5
    
    
    
    def GetGraphByType(type):
        if type == EnergyUseCase.FLEXIBLE_START:
            return """
            ?esa rdf:type saref:Device .
            ?esa saref:isUsedFor ?commodity .
            ?commodity rdf:type saref:Electricity .
            ?esa saref:makesMeasurement ?commodityProperty .
            ? commodityProperty saref:relatesToProperty ?power .
            ?power rdf:type saref:Power .
            ?esa saref:hasProfile ?powerProfile .
            ?powerprofile rdf:type s4ener:PowerProfile  .
            ?powerprofile s4ener:isRemoteControllable ?nodeRemoteControllable .
            ?powerprofile s4ener:supportsReselection ?supportsReselection .
            ?powerProfile saref:consistsOf ?alternativesgroup .
            ?alternativesgroup rdf:type s4ener:AlternativesGroup .
            ?alternativesgroup saref:hasIdentifier ?alternativesID .
            ?alternativesgroup saref:consistsOf ?powerSequence .
            ?powerSequence rdf:type s4ener:PowerSequence .
            ?powerSequence saref:hasIdentifier ?sequenceID .
            ?powerSequence saref:hasState ?powerSequenceState .
            ?powerSequence s4ener:activeSlotNumber ?activeSlotNumber .
            ?powerSequence s4ener:isRemoteControllable ?sequenceRemoteControllable .
            ?powerSequence s4ener:hasStartTime ?startTime .
            ?powerSequence s4ener:hasEndTime ?endTime .
            ?powerSequence s4ener:hasEarliestStartTime ?earliestStartTime . 
            ?powerSequence s4ener:hasLatestEndTime ?latestEndTime .
            ?powerSequence s4ener:isPausable ?isPausable .
            ?powerSequence s4ener:isStoppable ?isStoppable .
            ?powerSequence s4ener:hasValueSource ?valueSource . 
            ?powerSequence saref:consistsOf ?powerSequenceSlot .
            ?powerSequenceSlot rdf:type s4ener:Slot .
            ?powerSequenceSlot saref:hasIdentifier ?powerSequenceSlotNumber .
            ?powerSequenceSlot s4ener:hasDefaultDuration ?powerSequenceSlotDefaultDuration .
            ?powerSequenceSlot s4ener:hasSlotValue ?powerSequenceSlotPower .
            ?powerSequenceSlotPower rdf:type saref:Measurement .
            ?powerSequenceSlotPower saref:relatesToProperty?powerSequenceSlotProperty .
            ?powerSequenceSlotPower s4ener:hasUsage ?powerSequenceSlotPowerType .
            ?powerSequenceSlotPower saref:isMeasuredIn om:watt .
            ?powerSequenceSlotPower saref:hasValue ?powerSequenceSlotValue .
            """
        if type == EnergyUseCase.MONITORING_POWER_CONSUMPTION:
        if type == EnergyUseCase.LIMITATION_POWER_CONSUMPTION:
        if type == EnergyUseCase.MANAGEMENT_POWER_CONSUMPTION_INCENTIVE_TABLE:
        if type == EnergyUseCase.MANAGEMENT_POWER_CONSUMPTION_POWER_PLAN:
        if type == EnergyUseCase.MANUAL_OPERATION:



class EchonetLITEDeviceManager:
    def __init__(self,ke_endpoint):
        self.devices = {}
        self.ke_endpoint= ke_endpoint
        self.el_endpoint = "http://150.65.231.106:6000"
    def AddTestDevices(self):
        device = EchonetLITEDevice(EchonetLITEDeviceType.TEMPERATURE_SENSOR,
                                "http://example.org/sensor" + str(random.randint(0,10000)),
                                "Sensor",
                                "A temperature sensor",
                                    self.ke_endpoint,self.el_endpoint ,None ,self    )
        self.devices[device.kb_id] = device

        device = EchonetLITEDevice(EchonetLITEDeviceType.WASHING_MACHINE,
                                "http://example.org/washingmachine" + str(random.randint(0,10000)),
                                "Washingmachine",
                                "A Washingmachine sensor",
                                    self.ke_endpoint      ,self.el_endpoint,None,self)
        self.devices[device.kb_id] = device
    def GetInforFromEchonetLITEServer(self):
        response = requests.get(self.el_endpoint + "/elapi/v1/devices/")
        print(response)
        print(response.text)

        data = json.loads(response.text)
        for deviceInfo in  data['devices']:
            key = deviceInfo['id']
            desc = deviceInfo['manufacturer']['descriptions']['en']
            if key not in self.devices:
                deviceType = deviceInfo['deviceType']
                device = EchonetLITEDevice(EchonetLITEDeviceType(deviceType),
                                "http://jaist.org/device_"+ key+ str(random.randint(0,10000)),
                                deviceType+":"+key,
                                desc,
                                    self.ke_endpoint ,self.el_endpoint, key ,self    )
                self.devices[device.kb_id] = device
                break #test only
            
        asd=123
    def RegisterGraph(self):
        self.kb_id = "http://jaist.org/devicees_" + str(random.randint(0,10000))
        self.kb_name = "EchonetLITEDeviceManager"
        self.kb_description = "An EchonetLITE Device Manager"
        register_knowledge_base(self.kb_id, self.kb_name,
                                self.kb_description, self.ke_endpoint)
        

        data = """
                        ?sensor rdf:type saref:Sensor .
                        ?measurement saref:measurementMadeBy ?sensor .
                        ?measurement saref:isMeasuredIn saref:TemperatureUnit .
                        ?measurement saref:hasValue ?temperature .
                        ?measurement saref:hasTimestamp ?timestamp .
                    """
        


        self.ki_id = register_post_knowledge_interaction(
            data,
            None,
            "post-measurements",
            self.kb_id,
            self.ke_endpoint,
            {
                "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                "saref": "https://saref.etsi.org/core/",
            },
        )
    def StartLoop(self,isLoop=True):
        self.GetInforFromEchonetLITEServer()
        if isLoop:
            while True:
                time.sleep(2)

if __name__ == '__main__':
    echonetLITEDeviceManager = EchonetLITEDeviceManager("http://150.65.230.93:8280/rest/")
    echonetLITEDeviceManager.StartLoop(False)