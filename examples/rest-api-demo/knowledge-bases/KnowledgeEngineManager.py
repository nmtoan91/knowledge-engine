from datetime import datetime
import time
import random
import logging
import random
from utils import *
from enum import Enum
import threading
from concurrent.futures import Future
import json

class EnergyUseCaseType(Enum):
    UNKNOWN=0,
    FLEXIBLE_START_MANUAL_OPERATION="FLEXIBLE_START_MANUAL_OPERATION"
    MONITORING_POWER_CONSUMPTION = "MONITORING_POWER_CONSUMPTION"
    LIMITATION_POWER_CONSUMPTION="LIMITATION_POWER_CONSUMPTION"
    MANAGEMENT_POWER_CONSUMPTION_INCENTIVE_TABLE="MANAGEMENT_POWER_CONSUMPTION_INCENTIVE_TABLE"
    MANAGEMENT_POWER_CONSUMPTION_POWER_PLAN="MANAGEMENT_POWER_CONSUMPTION_POWER_PLAN"
    #MANUAL_OPERATION="MANUAL_OPERATION"

    
class EnergyUseCase:
    def __init__(self,type:EnergyUseCaseType,manager):
        self.manager = manager
        self.type = type
        self.kb_id = "http://jaist.org/devicees_" + str(type)+ str(random.randint(0,10000))
        self.kb_id_ask = self.kb_id + "_ask"
        self.kb_name = "UIManager_" + str(type)
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
        # if self.type == EnergyUseCaseType.MANUAL_OPERATION:
        #     return """
        #         ?esa rdf:type saref:Device .
        #         ?esa saref:isUsedFor ?commodity .
        #         ?commodity rdf:type saref:Electricity .
        #         ?esa saref:makesMeasurement ?commodityProperty .
        #         ?commodityProperty saref:relatesToProperty ?power .
        #         ?power rdf:type saref:Power .
        #         ?esa saref:hasProfile ?powerProfile .
        #         ?powerprofile rdf:type s4ener:PowerProfile  .
        #         ?powerprofile s4ener:isRemoteControllable ?nodeRemoteControllable .
        #         ?powerprofile s4ener:supportsReselection ?supportsReselection .
        #         ?powerProfile saref:consistsOf ?alternativesgroup .
        #         ?alternativesgroup rdf:type s4ener:AlternativesGroup .
        #         ?alternativesgroup saref:hasIdentifier ?alternativesID .
        #         ?alternativesgroup saref:consistsOf ?powerSequence .
        #         ?powerSequence rdf:type s4ener:PowerSequence .
        #         ?powerSequence saref:hasIdentifier ?sequenceID .
        #         ?powerSequence saref:hasState ?powerSequenceState .
        #         ?powerSequence s4ener:activeSlotNumber ?activeSlotNumber .
        #         ?powerSequence s4ener:isRemoteControllable ?sequenceRemoteControllable .
        #         ?powerSequence s4ener:hasStartTime ?startTime .
        #         ?powerSequence s4ener:hasEndTime ?endTime .
        #         ?powerSequence s4ener:hasEarliestStartTime ?earliestStartTime . 
        #         ?powerSequence s4ener:hasLatestEndTime ?latestEndTime .
        #         ?powerSequence s4ener:isPausable ?isPausable .
        #         ?powerSequence s4ener:isStoppable ?isStoppable .
        #         ?powerSequence s4ener:hasValueSource ?valueSource . 
        #         ?powerSequence saref:consistsOf ?powerSequenceSlot .
        #         ?powerSequenceSlot rdf:type s4ener:Slot .
        #         ?powerSequenceSlot saref:hasIdentifier ?powerSequenceSlotNumber .
        #         ?powerSequenceSlot s4ener:hasDefaultDuration ?powerSequenceSlotDefaultDuration .
        #         ?powerSequenceSlot s4ener:hasSlotValue ?powerSequenceSlotPower .
        #         ?powerSequenceSlotPower rdf:type saref:Measurement .
        #         ?powerSequenceSlotPower saref:relatesToProperty?powerSequenceSlotProperty .
        #         ?powerSequenceSlotPower s4ener:hasUsage ?powerSequenceSlotPowerType .
        #         ?powerSequenceSlotPower saref:isMeasuredIn om:watt .
        #         ?powerSequenceSlotPower saref:hasValue ?powerSequenceSlotValue .
        #         """
        print("\n\n\n Error \n\n\n")
        return None
    def SendData(self,data):
        x = threading.Thread(target=self.SendDataThread, args=(data,))
        x.start()
        
    def SendDataThread(self,data):
        now = datetime.now()
        post(
            [
                data
            ],
            self.ki_id,
            self.kb_id,
            self.manager.ke_endpoint,
        )
        print("\nSending data (", (datetime.now()-now).seconds, "seconds):", data)

    def UnRegisterKnowledgeBaseReact(self):
        response = requests.delete(
             f"{self.manager.ke_endpoint}/sc", headers={"Knowledge-Base-Id": self.kb_id}
         )
        if response.ok == False:
            print("\n\n\n Error AT:",response.text ,"\n\n\n")
    def RegisterKnowledgeBaseReact(self):
        print("\n\nRegistering (REACT)", self.type)
        register_knowledge_base(self.kb_id, self.kb_name,
                                self.kb_description, self.manager.ke_endpoint)
        
        self.ki_id = register_react_knowledge_interaction(
            self.GetGraphByType(),
            None,
            "react-measurements",
            self.kb_id,
            self.manager.ke_endpoint,
            {
                "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                "saref": "https://saref.etsi.org/core/",
                "s4ener": "https://saref.etsi.org/core1/",
                "om": "https://saref.etsi.org/core2/",
                "saref4ener": "https://saref.etsi.org/core3/",
                "time": "https://saref.etsi.org/core4/",
            },
        )
        x = threading.Thread(target=self.my_react_loop, args=())
        x.start()
    def UnRegisterKnowledgeBaseAsk(self):
        response = requests.delete(
             f"{self.manager.ke_endpoint}/sc", headers={"Knowledge-Base-Id": self.kb_id_ask}
         )
        if response.ok == False:
            print("\n\n\n Error AT:",response.text ,"\n\n\n")
    def RegisterKnowledgeBaseAsk(self):
        print("\n\nRegistering (ASK", self.type)
        register_knowledge_base(self.kb_id_ask, self.kb_name,
                                self.kb_description, self.manager.ke_endpoint)
        
        self.ki_id_ask = register_ask_knowledge_interaction(
            self.GetGraphByType(),
            "ask-measurements",
            self.kb_id_ask,
            self.manager.ke_endpoint,
            {
                "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                "saref": "https://saref.etsi.org/core/",
                "s4ener": "https://saref.etsi.org/core1/",
                "om": "https://saref.etsi.org/core2/",
                "saref4ener": "https://saref.etsi.org/core3/",
                "time": "https://saref.etsi.org/core4/",
            },
        )

    def present_measurement(self,binding: dict[str, str],requestingKnowledgeBaseId, historical: bool = False):
        # s = "data="
        # for key, value in binding.items() :
        #     s += f"{key}:{value}  "
        # print(s)

        self.manager.mainView.ReceiveData(binding,requestingKnowledgeBaseId,self.type)


    def handle_react_measurements(self,bindings,requestingKnowledgeBaseId):
        #now = datetime.now()
        for binding in bindings:
            self.present_measurement(binding,requestingKnowledgeBaseId)
        #print("end receving: ", (datetime.now() - now).seconds,"seconds")
        return []
    def my_react_loop(self):
        #time.sleep(1)
        start_handle_loop(
        {
            self.ki_id: self.handle_react_measurements,
        },
        self.kb_id,
        self.manager.ke_endpoint,
    )
    def Ask(self,structuredData):
        x = threading.Thread(target=self.Ask_, args=(structuredData,))
        x.start()
    def Ask_(self,structuredData):
        data = ask(
            [
                structuredData
            ],
            self.ki_id_ask,
            self.kb_id_ask,
            self.manager.ke_endpoint,
        )
        print("\n\n\n\n Asked and responsed: ",data,'\n\n')
        


