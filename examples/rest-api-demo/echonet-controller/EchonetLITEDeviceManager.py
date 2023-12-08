import os
from datetime import datetime
import time
import random
import logging
import random
from utils_echonet_controller import *
from enum import Enum
import threading
from concurrent.futures import Future
from EchonetLITEDevice import EchonetLITEDevice,EnergyUseCaseType
from EchonetLITEDevice import EchonetLITEDeviceType
import json
import atexit


    
class EnergyUseCase:
    def __init__(self,type:EnergyUseCaseType,echonetLITEDeviceManager):
        self.echonetLITEDeviceManager = echonetLITEDeviceManager
        self.type = type
        self.kb_id = "http://jaist.org/devicees_" + str(type)+ str(random.randint(0,10000))
        self.kb_id_answer = self.kb_id + "_answer"
        self.kb_name = "EchonetLITEDeviceManager_" + str(type)
        self.kb_description = "An EchonetLITE Device Manager: " + str(type)

    def GetGraphByType(self):
        if self.type == EnergyUseCaseType.FLEXIBLE_START_MANUAL_OPERATION:
            return """
                        ?esa rdf:type saref:Device .
                        ?esa saref:isUsedFor ?commodity .
                        ?commodity rdf:type saref:Electricity .
                        ?esa saref:makesMeasurement ?commodityProperty .
                        ?commodityProperty saref:relatesToProperty ?power .
                        ?power rdf:type saref:Power .
                        ?esa saref:hasProfile ?powerProfile .
                        ?powerprofile rdf:type s4ener:PowerProfile .
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
                        ?powerSequenceSlotPower saref:relatesToProperty ?powerSequenceSlotProperty .
                        ?powerSequenceSlotPower s4ener:hasUsage ?powerSequenceSlotPowerType .
                        ?powerSequenceSlotPower saref:isMeasuredIn om:watt .
                        ?powerSequenceSlotPower saref:hasValue ?powerSequenceSlotValue .
                    """
        if self.type == EnergyUseCaseType.MONITORING_POWER_CONSUMPTION:
            return """
                ?esa rdf:type saref:Device .
                ?esa saref:isUsedFor ?commodity .
                ?commodity rdf:type saref:Electricity .
                ?esa saref:makesMeasurement ?monitoring_of_power_consumption .
                ?monitoring_of_power_consumption saref:relatesToProperty ?power .
                ?power rdf:type saref:Power .
                ?monitoring_of_power_consumption saref:isMeasuredIn ?unit .
                ?monitoring_of_power_consumption saref:hasValue ?value .
                    """
        if self.type == EnergyUseCaseType.LIMITATION_POWER_CONSUMPTION:
            return """
                ?esa rdf:type saref:Device .
                ?esa s4ener:receivesPowerLimit ?powerlimit .
                ?powerlimit rdf:type s4ener:PowerLimit .
                ?powerLimit s4ener:hasIdentifier ?powerLimitIdentifier .
                ?powerlimit s4ener:isChangeable ?powerLimitIsChangeable .
                ?powerlimit s4ener:isObligatory ?powerLimitIsObligatory .
                ?powerlimit s4ener:hasPowerLimitDuration ?powerLimitDuration .
                ?powerlimit s4ener:isActive ?powerlimitIsActive .
                ?powerlimit s4ener:hasDataPoint ?powerLimitConsumptionMax .
                ?powerLimitConsumptionMax rdf:type saref:Measurement .
                ?powerLimitConsumptionMax saref:isMeasuredIn ?powerLimitConsumptionMaxUnit .
                ?powerLimitConsumptionMax saref:hasValue ?powerLimitConsumptionMaxValue .
                ?esa s4ener:isBoundTo ?contractualPowerLimit . 
                ?contractualPowerLimit rdf:type s4ener:ContractualPowerLimit .
                ?contractualPowerLimit s4ener:hasDataPoint ?contractualPLConsumptionMax . 
                ?contractualPLConsumptionMax rdf:type saref:Measurement .
                ?contractualPLConsumptionMax saref:isMeasuredIn ?contractualPLConsumptionMaxUnit .
                ?contractualPLConsumptionMax saref:hasValue ?contractualPLConsumptionMaxValue .
                ?esa s4ener:isProtectedBy ?nominalPowerLimit .
                ?nominalPowerLimit rdf:type s4ener:NominalPowerLimit .
                ?nominalPowerLimit s4ener:hasDataPoint ?nominalPLConsumptionMax .
                ?nominalPLConsumptionMax rdf:type saref:Measurement .
                ?nominalPLConsumptionMax saref:isMeasuredIn ?nominalPLConsumptionMaxUnit .
                ?nominalPLConsumptionMax saref:hasValue ?nominalPLConsumptionMaxValue .
                ?esa saref:hasState ?failSafeState .
                ?failsafeState s4ener:hasFailsafeDuration ?failsafeStateDuration . 
                ?failsafeStateDuration s4ener:isChangeable ?failsafeStateDurationIsChangeable .
                ?esa s4ener:isLimitedWith ?failsafePowerLimit .
                ?failsafePowerLimit rdf:type s4ener:FailsafePowerLimit . 
                ?failsafePowerLimit s4ener:hasUsage ?failsafePLConsumption .
                ?failsafePLConsumptionMax rdf:type saref:Measurement .
                ?failsafePLConsumptionMax saref:isMeasuredIn ?failsafePLConsumptionMaxUnit .
                ?failsafePLConsumptionMax saref:hasValue ?failsafePLConsumptionMaxValue . 
                ?failsafePLConsumptionMax s4ener:isChangeable ?failsafePLConsumptionMaxIsChangeable .
                """
        if self.type == EnergyUseCaseType.MANAGEMENT_POWER_CONSUMPTION_INCENTIVE_TABLE:
            return """
                ?esa rdf:type saref4ener:Device .
                ?esa saref:hasProfile ?incentiveBasedProfile .
                ?incentiveBasedProfile rdf:type s4ener:IncentiveBasedProfile .
                ?incentiveBasedProfile saref:hasIdentifier ?incentiveBasedProfileId .
                ?incentiveBasedProfile s4ener:isChangeable ?incentiveBasedProfileIsChangeable .
                ?incentiveBasedProfile s4ener:requiresUpdate ?incentiveBasedProfileRequiresUpdate .
                ?incentiveBasedProfile s4ener:hasScopeType ?incentiveBasedProfileScopeType .
                ?incentiveBasedProfile s4ener:hasIncentiveType ?incentiveBasedProfileIncentiveType .
                ?incentiveBasedProfile s4ener:hasSlot ?incentiveTableSlot .
                ?incentiveTableSlot rdf:type s4ener:IncentiveTableSlot .
                ?incentiveTableSlot saref:hasIdentifier ?incentiveTableSlotId .
                ?incentiveTableSlot s4ener:hasEffectivePeriode ?incentiveTableTimeSlotInterval .
                ?incentiveTableTimeSlotInterval time:hasBeginning ?incentiveTableTimeSlotBeginning .
                ?incentiveTableTimeSlotInterval time:hasEnd ?incentiveTableTimeSlotEnd .
                ?incentiveTableSlot s4ener:hasIncentive ?incentive .
                ?incentive rdf:type s4ener:Incentive .
                ?incentive saref:hasIdentifier ?incentiveId .
                ?incentive saref:isMeasuredIn ?incentiveUnit .
                ?incentive saref:hasValue ?incentiveValue .
                ?incentive s4ener:hasLowerBoundary ?incentiveLowerBoundary .
                ?incentiveLowerBoundary saref:isMeasuredIn ?incentiveLowerBoundaryUnit .
                ?incentiveLowerBoundary saref:hasValue ?incentiveLowerBoundaryValue .
                ?incentive s4ener:hasUpperBoundary ?incentiveUpperBoundary .
                ?incentiveUpperBoundary saref:isMeasuredIn ?incentiveUpperBoundaryUnit .
                ?incentiveUpperBoundary saref:hasValue ?incentiveUpperBoundaryValue .
                """
        if self.type == EnergyUseCaseType.MANAGEMENT_POWER_CONSUMPTION_POWER_PLAN:
            return """
                ?esa rdf:type saref4ener:Device .
                ?esa saref:hasProfile ?incentiveBasedProfile .
                ?incentiveBasedProfile rdf:type s4ener:IncentiveBasedProfile .
                ?incentiveBasedProfile s4ener:hasPowerPlan ?powerPlan .
                ?powerPlan rdf:type s4ener:PowerPlan .
                ?powerPlan saref:hasIdentifier ?powerPlanId .
                ?powerPlan s4ener:isWritable ?powerPlanIsWritable .
                ?powerPlan s4ener:hasScopeType ?powerPlanScopeType .
                ?powerPlan s4ener:hasTimeSeries ?powerPlanTimeSeries . 
                ?powerPlanTimeSeries saref:hasIdentifier ?powerPlanTimeSeriesId .
                ?powerPlanTimeSeries s4ener:hasEffectivePeriode ?powerPlanTimeSeriesSlotInterval .
                ?powerPlanTimeSeriesSlotInterval time:hasBeginning ?powerPlanTimeSeriesSlotBeginning .
                ?powerPlanTimeSeriesSlotInterval time:hasEnd ?powerPlanTimeSeriesSlotEnd .
                ?powerPlanTimeSeries s4ener:hasUsage ?powerPlanTimeSeriesUsage .
                ?powerPlanTimeSeries saref:relatesToProperty ?powerPlanTimeSeriesProperty .
                ?powerPlanTimeSeries s4ener:hasDataPoint ?powerPlanDataPoint .
                ?powerPlanDataPoint saref:isMeasuredIn ?powerPlanDataPointUnit .
                ?powerPlanDataPoint saref:hasValue ?powerPlanDataPointValue .
                """
        print("\n\n\n Error \n\n\n")
        return None
    def SendData(self,data):
        x = threading.Thread(target=self.SendDataThread, args=(data,))
        try:
            x.start()
        except:
            EchonetLITEDeviceManager.instance.isShutDown = True
            print("Can't start new thread")
        
    def SendDataThread(self,data):
        now = datetime.now()
        post(
            [
                data
            ],
            self.ki_id,
            self.kb_id,
            self.echonetLITEDeviceManager.ke_endpoint,
        )
        print("\nSending data (", (datetime.now()-now).seconds, "seconds):", data)

    def UnRegisterKnowledgeBasePost(self):
        response = requests.delete(
             f"{self.echonetLITEDeviceManager.ke_endpoint}/sc", headers={"Knowledge-Base-Id": self.kb_id}
         )
        if response.ok == False:
            print("\n\n\n Error AT:",response.text ,"\n\n\n")
    def RegisterKnowledgeBasePost(self):
        print("\n\nRegistering (Post)", self.type)
        register_knowledge_base(self.kb_id, self.kb_name,
                                self.kb_description, self.echonetLITEDeviceManager.ke_endpoint)
        
        self.ki_id = register_post_knowledge_interaction(
            self.GetGraphByType(),
            None,
            "post-measurements",
            self.kb_id,
            self.echonetLITEDeviceManager.ke_endpoint,
            {
                "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                "saref": "https://saref.etsi.org/core/",
                "s4ener": "https://saref.etsi.org/core1/",
                "om": "https://saref.etsi.org/core2/",
                "saref4ener": "https://saref.etsi.org/core3/",
                "time": "https://saref.etsi.org/core4/",
            },
        )
    def UnRegisterKnowledgeBaseAnswer(self):
        response = requests.delete(
             f"{self.echonetLITEDeviceManager.ke_endpoint}/sc", headers={"Knowledge-Base-Id": self.kb_id_answer}
         )
        if response.ok == False:
            print("\n\n\n Error AT:",response.text ,"\n\n\n")
    def RegisterKnowledgeBaseAnswer(self):
        print("\n\nRegistering (Answer)", self.type)
        register_knowledge_base(self.kb_id_answer, self.kb_name,
                                self.kb_description, self.echonetLITEDeviceManager.ke_endpoint)
        
        self.ki_id_answer = register_answer_knowledge_interaction(
            self.GetGraphByType(),
            #None,
            "post-measurements",
            self.kb_id_answer,
            self.echonetLITEDeviceManager.ke_endpoint,
            {
                "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                "saref": "https://saref.etsi.org/core/",
                "s4ener": "https://saref.etsi.org/core1/",
                "om": "https://saref.etsi.org/core2/",
                "saref4ener": "https://saref.etsi.org/core3/",
                "time": "https://saref.etsi.org/core4/",
            },
        )
        x = threading.Thread(target=self.HandlingAsnwerThread, args=())
        x.start()
        
    def HandlingAsnwerThread(self):
        start_handle_loop(
        {
            self.ki_id_answer: self.Answer
        },
        self.kb_id_answer,
        self.echonetLITEDeviceManager.ke_endpoint,self)
    def Answer(self,bindings):
        self.echonetLITEDeviceManager.Answer(bindings)
        # for binding in bindings:
        #     present_measurement(binding)
        print(f"\n\n\n\n\n Answering a ask with data=\n{bindings} \n\n")
        return []
        KB_DATA = json.loads(os.getenv("KB_DATA"))
        data = match_bindings(
                bindings,
                KB_DATA,
            )
        print("\n\nKB=", KB_DATA,"\n\n")
        #data = bindings
        print(f"\n\n\n\n\n Answering a ask with data=\n{data} \n\n")
        return data
        return data#KB_DATA#bindings




class EchonetLITEDeviceManager:
    instance = None
    def __init__(self,ke_endpoint):
        self.isShutDown = False
        EchonetLITEDeviceManager.instance = self
        self.devices = {}
        self.ke_endpoint= ke_endpoint
        self.el_endpoint = "http://150.65.231.106:6000"
        self.initialized = False
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
        

        data = json.loads(response.text)
        for deviceInfo in  data['devices']:
            key = deviceInfo['id']
            desc = deviceInfo['manufacturer']['descriptions']['en']
            if key not in self.devices:
                #if key != 'washerDryer-1701394427.760471': continue #test only
                #if key != 'washerDryer-103188638647835413907134999069967199908': continue #test only
                
                deviceType = deviceInfo['deviceType']
                device = EchonetLITEDevice(EchonetLITEDeviceType(deviceType),
                                "http://jaist.org/"+ key+ str(random.randint(0,10000)),
                                deviceType+":"+key,
                                desc,
                                    self.ke_endpoint ,self.el_endpoint, key ,self    )
                self.devices[device.kb_id] = device
                print(f"\n\n\n\n Adding device: {device.kb_id}\n\n\n\n")
                #break #test only

        if len(self.devices) ==0: print('ERROR: Device not found on echonetLITE server; original len=',len(data['devices']))
            
        asd=123
    def RegisterGraphs(self):
        

        self.energyCases = {}
        self.energyCases[EnergyUseCaseType.FLEXIBLE_START_MANUAL_OPERATION]=EnergyUseCase(EnergyUseCaseType.FLEXIBLE_START_MANUAL_OPERATION,self)
        # self.energyCases[EnergyUseCaseType.MONITORING_POWER_CONSUMPTION]=EnergyUseCase(EnergyUseCaseType.MONITORING_POWER_CONSUMPTION,self)
        self.energyCases[EnergyUseCaseType.LIMITATION_POWER_CONSUMPTION]=EnergyUseCase(EnergyUseCaseType.LIMITATION_POWER_CONSUMPTION,self)
        # self.energyCases[EnergyUseCaseType.MANAGEMENT_POWER_CONSUMPTION_INCENTIVE_TABLE]=EnergyUseCase(EnergyUseCaseType.MANAGEMENT_POWER_CONSUMPTION_INCENTIVE_TABLE,self)
        # self.energyCases[EnergyUseCaseType.MANAGEMENT_POWER_CONSUMPTION_POWER_PLAN]=EnergyUseCase(EnergyUseCaseType.MANAGEMENT_POWER_CONSUMPTION_POWER_PLAN,self)
        #self.energyCases[EnergyUseCaseType.MANUAL_OPERATION]=EnergyUseCase(EnergyUseCaseType.MANUAL_OPERATION,self)


        for key in self.energyCases:
            self.energyCases[key].RegisterKnowledgeBasePost()
            self.energyCases[key].RegisterKnowledgeBaseAnswer()
            
        self.initialized = True

    def SendMultipleData(self,multipleData):
        for key in multipleData:
            data = multipleData[key]
            if key not in self.energyCases: continue
            self.energyCases[key].SendData(data)

    def StartLoop(self,isLoop=True):
        self.RegisterGraphs()
        self.GetInforFromEchonetLITEServer()
        
        
        if isLoop:
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n\n\n\n STOPPING, PLEASE WAIT !!! \n\n\n")
                self.isShutDown = True


    def Answer(self,bindings):
        for binding in bindings:
            if 'esa' in binding:
                key = binding['esa']
                if key in  self.devices:
                    self.devices[key].Answer(binding)
                else : print(f"\n\n\n\n[ERROR HERE] Cannot find device with the key {key} \n\n\n\n")
            else: print("\n\n\n\n[ERROR HERE] the key esa is not existed \n\n\n\n")

    def UnRegister(self):
        self.isShutDown = True
        for key in self.energyCases:
            self.energyCases[key].UnRegisterKnowledgeBasePost()
            self.energyCases[key].UnRegisterKnowledgeBaseAnswer()

if __name__ == '__main__':
    echonetLITEDeviceManager = EchonetLITEDeviceManager("http://150.65.230.93:8280/rest/")
    echonetLITEDeviceManager.StartLoop(False)