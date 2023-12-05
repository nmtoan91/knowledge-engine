from datetime import datetime
import time
import random
import logging
import random
from utils_echonet_controller import *
from enum import Enum
import threading
from concurrent.futures import Future
import json
#from EchonetLITEDeviceManager import  EnergyUseCase, EnergyUseCaseType

class EnergyUseCaseType(Enum):
    UNKNOWN=0,
    FLEXIBLE_START="FLEXIBLE_START"
    MONITORING_POWER_CONSUMPTION = "MONITORING_POWER_CONSUMPTION"
    LIMITATION_POWER_CONSUMPTION="LIMITATION_POWER_CONSUMPTION"
    MANAGEMENT_POWER_CONSUMPTION_INCENTIVE_TABLE="MANAGEMENT_POWER_CONSUMPTION_INCENTIVE_TABLE"
    MANAGEMENT_POWER_CONSUMPTION_POWER_PLAN="MANAGEMENT_POWER_CONSUMPTION_POWER_PLAN"
    MANUAL_OPERATION="MANUAL_OPERATION"

def generate_random_temperature(start=15.0, end=20.0):
    assert end > start
    return start + (end - start) * random.random()


class EchonetLITEDeviceType(Enum):
    UNKNOWN = 0
    TEMPERATURE_SENSOR = 1
    WASHING_MACHINE = 2
    AIR_CONDITIONER_VENTILATION_FAN = 'airConditionerVentilationFan'
    HYBRID_WATER_HEATER = 'hybridWaterHeater'
    WASHER_DRYER = 'washerDryer'
    INSTANTANEOUS_WATER_HEATER = 'instantaneousWaterHeater'
    FLOOR_HEATER = 'floorHeater'
    ELECTRIC_WATER_HEATER = 'electricWaterHeater'
    BATHROOM_HEATER_DRYER = 'bathroomHeaterDryer'
    VENTILATION_FAN = 'ventilationFan'

class EchonetLITEDevice:
    def __init__(self, type: EchonetLITEDeviceType, kb_id, kb_name, kb_description, ke_endpoint,el_endpoint,el_id,echonetLITEDeviceManager):
        self.el_id = el_id
        self.el_endpoint = el_endpoint
        self.measurement_counter = 0
        self.type = type
        self.kb_id = kb_id
        self.kb_name = kb_name
        self.kb_description = kb_description
        self.ke_endpoint = ke_endpoint
        self.echonetLITEDeviceManager = echonetLITEDeviceManager
        self.isDirty = False
        self.structureData = {}
        #self.GetData()
        x = threading.Thread(target=self.GetDataThread, args=())
        x.start()
        #x.join()

        self.property_earliestStartTime = datetime.now().isoformat()
        self.property_latestEndTime = datetime.now().isoformat()
        self.property_startTime = datetime.now().isoformat()
        self.property_endTime = datetime.now().isoformat()
        self.property_powerSequenceState = "s4ener:Inactive"
    def GetDataThread(self):
        while True:
            self.GetData()   
            time.sleep(2)
            if self.echonetLITEDeviceManager.isShutDown:
                break
                
    def Answer(self,bindings):
        if 'earliestStartTime' in bindings:
            self.property_earliestStartTime = bindings['earliestStartTime']
        if 'latestEndTime' in bindings:
            self.property_latestEndTime = bindings['latestEndTime']
        if 'startTime' in bindings:
            self.property_startTime = bindings['startTime']
        if 'endTime' in bindings:
            self.property_endTime = bindings['endTime']
        if 'powerSequenceState' in bindings:
            self.property_powerSequenceState = bindings['powerSequenceState']
        
        #self.StartSendingThread()
    def GetData(self):
        sotangdan =1
        response = requests.get(self.el_endpoint+'/elapi/v1/devices/' + self.el_id+'/properties')
        self.el_data =data = json.loads(response.text)
        prefix = "http://jaist.ac.com/"
        esa = self.kb_id#prefix+"esa"+self.el_id
        commodity = prefix+"commodity" + self.el_id
        commodityProperty = prefix+"commodityProperty"+ self.el_id
        power= prefix + "power" +  self.el_id
        powerProfile= prefix +"powerProfile" +  self.el_id
        nodeRemoteControllable =  "True"
        supportsReselection = "True"
        alternativesgroup = prefix + "alternativesgroup" + self.el_id
        alternativesID = "echonet" +  self.el_id
        powerSequence = prefix + "powerSequence" + self.el_id
        sequenceID= powerSequence + str(sotangdan)
        powerSequenceState = self.property_powerSequenceState  #Important  Scheduled, Inactive, Invalid, Running, Paused, SchduledPaused, Pending, Completed
        activeSlotNumber = 1
        sequenceRemoteControllable = "True"

        startTime=  self.property_startTime
        endTime = self.property_endTime
        earliestStartTime = self.property_earliestStartTime
        latestEndTime= self.property_latestEndTime
        isPausable= "False"
        isStoppable= "True"
        valueSource= "s4ener:"+"Measured" # Calculated, Empirical
        powerSequenceSlot= prefix + "powerSequenceSlot" + self.el_id
        powerSequenceSlotNumber= "1251121"
        powerSequenceSlotDefaultDuration= "P0Y1M3DT4H5M10S"
        powerSequenceSlotPower = prefix + "powerSequenceSlotPower" + self.el_id
        powerSequenceSlotProperty= "s4ener:"+"Power"
        powerSequenceSlotPowerType= "s4ener:"+"Expected" #or "Minimum" "Maximum"
        #IMPORTANT
        powerSequenceSlotValue= data['instantaneousElectricPowerConsumption']
        data_FLEXIBLE_START = {
            "esa": f"{esa}",
            "commodity": f"{commodity}",
            "commodityProperty": f"{commodityProperty}",
            "power": f"{power}",
            "powerProfile": f"{powerProfile}",
            "nodeRemoteControllable": f"{nodeRemoteControllable}",
            "supportsReselection": f"{supportsReselection}",
            "alternativesgroup": f"{alternativesgroup}",
            "alternativesID": f"{alternativesID}",
            "powerSequence":f"{powerSequence}",
            "sequenceID" : f"{sequenceID}",
            "powerSequenceState": f"{powerSequenceState}",
            "activeSlotNumber": f"{activeSlotNumber}",
            "sequenceRemoteControllable": f"{sequenceRemoteControllable}",
            "startTime":f"{startTime}",
            "endTime":f"{endTime}",
            "earliestStartTime": f"{earliestStartTime}",
            "latestEndTime": f"{latestEndTime}",
            "isPausable": f"{isPausable}",
            "isStoppable" : f"{isStoppable}",
            "valueSource": f"{valueSource}",
            "powerSequenceSlot": f"{powerSequenceSlot}",
            "powerSequenceSlotNumber" : f"{powerSequenceSlotNumber}",
            "powerSequenceSlotDefaultDuration": f"{powerSequenceSlotDefaultDuration}",
            "powerSequenceSlotPower": f"{powerSequenceSlotPower}",
            "powerSequenceSlotProperty": f"{powerSequenceSlotProperty}",
            "powerSequenceSlotPowerType": f"{powerSequenceSlotPowerType}",
            "powerSequenceSlotValue": f"{powerSequenceSlotValue}"
        }
        self.structureData[EnergyUseCaseType.FLEXIBLE_START] = data_FLEXIBLE_START


        monitoring_of_power_consumption = "monitoring_of_power_consumption"
        unit= "unit"
        value = 23

        data_MONITORING_POWER_CONSUMPTION = {
            "esa": f"<https://example.org/power/{esa}>",
            "commodity": f"<https://example.org/commodity/{commodity}>",
            "monitoring_of_power_consumption": f"{monitoring_of_power_consumption}",
            "power": f"{power}",
            "unit": f"{unit}",
            "value": f"{value}",
            
        }
        self.structureData[EnergyUseCaseType.MONITORING_POWER_CONSUMPTION] = data_MONITORING_POWER_CONSUMPTION



        powerlimit = "powerlimit"
        powerLimitIdentifier= "powerLimitIdentifier"
        powerLimitIsChangeable= "powerLimitIsChangeable"
        powerLimitIsObligatory= "powerLimitIsObligatory"
        powerLimitDuration = "powerLimitDuration"
        powerlimitIsActive = "powerlimitIsActive"
        powerLimitConsumptionMax = "powerLimitConsumptionMax"
        powerLimitConsumptionMaxUnit = "powerLimitConsumptionMaxUnit"
        powerLimitConsumptionMaxValue = "powerLimitConsumptionMaxValue"
        contractualPowerLimit = "contractualPowerLimit"
        contractualPLConsumptionMax= "contractualPLConsumptionMax"
        contractualPLConsumptionMaxUnit= "contractualPLConsumptionMaxUnit"
        contractualPLConsumptionMaxValue= "contractualPLConsumptionMaxValue"
        nominalPowerLimit= "nominalPowerLimit"
        nominalPLConsumptionMax= "nominalPLConsumptionMax"
        nominalPLConsumptionMaxUnit= "nominalPLConsumptionMaxUnit"
        failSafeState = "failSafeState"
        failsafeStateDuration= "failsafeStateDuration"
        failsafeStateDurationIsChangeable = "failsafeStateDurationIsChangeable"
        failsafePowerLimit= "failsafePowerLimit"
        failsafePLConsumption = "failsafePLConsumption"
        failsafePLConsumptionMax= "failsafePLConsumptionMax"
        failsafePLConsumptionMaxUnit= "failsafePLConsumptionMaxUnit"
        failsafePLConsumptionMaxValue= "failsafePLConsumptionMaxValue"
        failsafePLConsumptionMaxIsChangeable= "failsafePLConsumptionMaxIsChangeable"
        data_LIMITATION_POWER_CONSUMPTION = {
            "esa": f"<https://example.org/power/{esa}>",
            "powerlimit":f"{powerlimit}",
            "powerLimitIdentifier":f"{powerLimitIdentifier}",
            "powerLimitIsChangeable":f"{powerLimitIsChangeable}",
            "powerLimitIsObligatory":f"{powerLimitIsObligatory}",
            "powerLimitDuration":f"{powerLimitDuration}",
            "powerlimitIsActive":f"{powerlimitIsActive}",
            "powerLimitConsumptionMax":f"{powerLimitConsumptionMax}",
            "powerLimitConsumptionMaxUnit":f"{powerLimitConsumptionMaxUnit}",
            "powerLimitConsumptionMaxValue":f"{powerLimitConsumptionMaxValue}",
            "contractualPowerLimit":f"{contractualPowerLimit}",
            "contractualPLConsumptionMax":f"{contractualPLConsumptionMax}",
            "contractualPLConsumptionMaxUnit":f"{contractualPLConsumptionMaxUnit}",
            "contractualPLConsumptionMaxValue":f"{contractualPLConsumptionMaxValue}",
            "nominalPowerLimit":f"{nominalPowerLimit}",
            "nominalPLConsumptionMax":f"{nominalPLConsumptionMax}",
            "nominalPLConsumptionMaxUnit":f"{nominalPLConsumptionMaxUnit}",
            "failSafeState":f"{failSafeState}",
            "failsafeStateDuration":f"{failsafeStateDuration}",
            "failsafeStateDurationIsChangeable":f"{failsafeStateDurationIsChangeable}",
            "enfailsafePowerLimitdTime":f"{failsafePowerLimit}",
            "failsafePLConsumption":f"{failsafePLConsumption}",
            "failsafePLConsumptionMax":f"{failsafePLConsumptionMax}",
            "failsafePLConsumptionMaxUnit":f"{failsafePLConsumptionMaxUnit}",
            "failsafePLConsumptionMaxValue":f"{failsafePLConsumptionMaxValue}",
            "failsafePLConsumptionMaxIsChangeable":f"{failsafePLConsumptionMaxIsChangeable}",
        }
        self.structureData[EnergyUseCaseType.LIMITATION_POWER_CONSUMPTION] = data_LIMITATION_POWER_CONSUMPTION


        incentiveBasedProfile="incentiveBasedProfile"
        incentiveBasedProfileId="incentiveBasedProfileId"
        incentiveBasedProfileIsChangeable="incentiveBasedProfileIsChangeable"
        incentiveBasedProfileRequiresUpdate="incentiveBasedProfileRequiresUpdate"
        incentiveBasedProfileScopeType="incentiveBasedProfileScopeType"
        incentiveBasedProfileIncentiveType="incentiveBasedProfileIncentiveType"
        incentiveTableSlot="incentiveTableSlot"
        incentiveTableSlotId="incentiveTableSlotId"
        incentiveTableTimeSlotInterval="incentiveTableTimeSlotInterval"
        incentiveTableTimeSlotBeginning="incentiveTableTimeSlotBeginning"
        incentiveTableTimeSlotEnd="incentiveTableTimeSlotEnd"
        incentive="incentive"
        incentiveId="incentiveId"
        incentiveUnit="incentiveUnit"
        incentiveValue="incentiveValue"
        incentiveLowerBoundary="incentiveLowerBoundary"
        incentiveLowerBoundaryUnit="incentiveLowerBoundaryUnit"
        incentiveLowerBoundaryValue="incentiveLowerBoundaryValue"
        incentiveUpperBoundary="incentiveUpperBoundary"
        incentiveUpperBoundaryUnit="incentiveUpperBoundaryUnit"
        incentiveUpperBoundaryValue="incentiveUpperBoundaryValue"


        data_MANAGEMENT_POWER_CONSUMPTION_INCENTIVE_TABLE = {
            "esa": f"<https://example.org/power/{esa}>",
            "incentiveBasedProfile":f"{incentiveBasedProfile}",
            "incentiveBasedProfileId":f"{incentiveBasedProfileId}",
            "incentiveBasedProfileIsChangeable":f"{incentiveBasedProfileIsChangeable}",
            "incentiveBasedProfileRequiresUpdate":f"{incentiveBasedProfileRequiresUpdate}",
            "incentiveBasedProfileScopeType":f"{incentiveBasedProfileScopeType}",
            "incentiveBasedProfileIncentiveType":f"{incentiveBasedProfileIncentiveType}",
            "incentiveTableSlot":f"{incentiveTableSlot}",
            "incentiveTableSlotId":f"{incentiveTableSlotId}",
            "incentiveTableTimeSlotInterval":f"{incentiveTableTimeSlotInterval}",
            "incentiveTableTimeSlotBeginning":f"{incentiveTableTimeSlotBeginning}",
            "incentiveTableTimeSlotEnd":f"{incentiveTableTimeSlotEnd}",
            "incentive":f"{incentive}",
            "incentiveId":f"{incentiveId}",
            "incentiveUnit":f"{incentiveUnit}",
            "incentiveValue":f"{incentiveValue}",
            "incentiveLowerBoundary":f"{incentiveLowerBoundary}",
            "incentiveLowerBoundaryUnit":f"{incentiveLowerBoundaryUnit}",
            "incentiveLowerBoundaryValue":f"{incentiveLowerBoundaryValue}",
            "incentiveUpperBoundary":f"{incentiveUpperBoundary}",
            "incentiveUpperBoundaryUnit":f"{incentiveUpperBoundaryUnit}",
            "incentiveUpperBoundaryValue":f"{incentiveUpperBoundaryValue}",
        }
        self.structureData[EnergyUseCaseType.MANAGEMENT_POWER_CONSUMPTION_INCENTIVE_TABLE] = data_MANAGEMENT_POWER_CONSUMPTION_INCENTIVE_TABLE

        IncentiveBasedProfile="IncentiveBasedProfile"
        powerPlan="powerPlan"
        powerPlanId="powerPlanId"
        powerPlanIsWritable="powerPlanIsWritable"
        powerPlanScopeType="powerPlanScopeType"
        powerPlanTimeSeries="powerPlanTimeSeries"
        powerPlanTimeSeriesId="powerPlanTimeSeriesId"
        powerPlanTimeSeriesSlotInterval="powerPlanTimeSeriesSlotInterval"
        powerPlanTimeSeriesSlotBeginning="powerPlanTimeSeriesSlotBeginning"
        powerPlanTimeSeriesSlotEnd="powerPlanTimeSeriesSlotEnd"
        powerPlanTimeSeriesUsage="powerPlanTimeSeriesUsage"
        powerPlanTimeSeriesProperty="powerPlanTimeSeriesProperty"
        powerPlanDataPoint="powerPlanDataPoint"
        powerPlanDataPointUnit="powerPlanDataPointUnit"
        powerPlanDataPointValue="powerPlanDataPointValue"
        data_MANAGEMENT_POWER_CONSUMPTION_POWER_PLAN = {
            "esa": f"<https://example.org/power/{esa}>",
            "incentiveBasedProfile":f"{incentiveBasedProfile}",
            "IncentiveBasedProfile":f"{IncentiveBasedProfile}",
            "powerPlan":f"{powerPlan}",
            "powerPlanId":f"{powerPlanId}",
            "powerPlanIsWritable":f"{powerPlanIsWritable}",
            "powerPlanScopeType":f"{powerPlanScopeType}",
            "powerPlanTimeSeries":f"{powerPlanTimeSeries}",
            "powerPlanTimeSeriesId":f"{powerPlanTimeSeriesId}",
            "powerPlanTimeSeriesSlotInterval":f"{powerPlanTimeSeriesSlotInterval}",
            "powerPlanTimeSeriesSlotBeginning":f"{powerPlanTimeSeriesSlotBeginning}",
            "powerPlanTimeSeriesSlotEnd":f"{powerPlanTimeSeriesSlotEnd}",
            "powerPlanTimeSeriesUsage":f"{powerPlanTimeSeriesUsage}",
            "powerPlanTimeSeriesProperty":f"{powerPlanTimeSeriesProperty}",
            "powerPlanDataPoint":f"{powerPlanDataPoint}",
            "powerPlanDataPointUnit":f"{powerPlanDataPointUnit}",
            "powerPlanDataPointValue":f"{powerPlanDataPointValue}",
        }
        self.structureData[EnergyUseCaseType.MANAGEMENT_POWER_CONSUMPTION_POWER_PLAN] = data_MANAGEMENT_POWER_CONSUMPTION_POWER_PLAN


        data_MANAGEMENT_POWER_CONSUMPTION_POWER_PLAN = {
            "esa": f"<https://example.org/power/{esa}>",
            "commodity": f"{commodity}",
            "commodityProperty": f"{commodityProperty}",
            "power": f"{power}",
            "powerProfile": f"{powerProfile}",
            "nodeRemoteControllable": f"{nodeRemoteControllable}",
            "supportsReselection": f"{supportsReselection}",
            "alternativesgroup": f"{alternativesgroup}",
            "alternativesID": f"{alternativesID}",
            "powerSequence": f"{powerSequence}",
            "sequenceID": f"{sequenceID}",
            "powerSequenceState": f"{powerSequenceState}",
            "activeSlotNumber": f"{activeSlotNumber}",
            "sequenceRemoteControllable": f"{sequenceRemoteControllable}",
            "startTime": f"{startTime}",
            "endTime": f"{endTime}",
            "earliestStartTime": f"{earliestStartTime}",
            "latestEndTime": f"{latestEndTime}",
            "isPausable": f"{isPausable}",
            "isStoppable": f"{isStoppable}",
            "valueSource": f"{valueSource}",
            "powerSequenceSlot": f"{powerSequenceSlot}",
            "powerSequenceSlotNumber": f"{powerSequenceSlotNumber}",
            "powerSequenceSlotDefaultDuration": f"{powerSequenceSlotDefaultDuration}",
            "powerSequenceSlotPower": f"{powerSequenceSlotPower}",
            "powerSequenceSlotProperty": f"{powerSequenceSlotProperty}",
            "powerSequenceSlotPowerType": f"{powerSequenceSlotPowerType}",
            "powerSequenceSlotValue": f"{powerSequenceSlotValue}",
        }
        self.structureData[EnergyUseCaseType.MANAGEMENT_POWER_CONSUMPTION_POWER_PLAN] = data_MANAGEMENT_POWER_CONSUMPTION_POWER_PLAN

        while self.echonetLITEDeviceManager.initialized == False:
            time.sleep(1)
        self.echonetLITEDeviceManager.SendMultipleData(self.structureData)

        asd=123


    # def TryToSendData(self):
    #     if not self.isDirty: return

    #     now = datetime.now()
    #     self.measurement_counter += 1
    #     value = generate_random_temperature(80, 100)
    #     if self.type == EchonetLITEDeviceType.TEMPERATURE_SENSOR:
    #         data = {
    #             "sensor": f"<https://example.org/sensor/1>",
    #             "measurement": f"<https://example.org/sensor/1/measurement/{self.measurement_counter}>",
    #             "temperature": f"{value}",
    #             "timestamp": f'"{now.isoformat()}"',
    #         }
    #     elif self.type == EchonetLITEDeviceType.WASHING_MACHINE:
    #         data = {
    #             "esa": "<https://example.org/washingmachine/1>",
    #             "commodity": "<https://example.org/commodity/electric>",
    #             "monitoring_of_power_consumption": f"<https://example.org/sensor/1/measurement/{self.measurement_counter}>",
    #             "power": f"<https://example.org/power/123>",
    #             "unit": f'"watt"',
    #             "value": f"{value}",
    #         }
    #     else:
    #         print("Error")

    #     now = datetime.now()

    #     post(
    #         [
    #             data
    #         ],
    #         self.ki_id,
    #         self.kb_id,
    #         self.ke_endpoint,
    #     )
    #     print("\nSending data (", (datetime.now()-now).seconds, "seconds):", data,"\n")
