import tkinter as tk
from tkinter import ttk
import threading 
from PIL import Image, ImageTk
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from enum import Enum
from KnowledgeEngineManager import EnergyUseCaseType
from datetime import datetime
class DeviceType(Enum):
    UNKNOWN =0
    TEMPERATURE_SENSOR =1
    WASHING_MACHINE = 2
    def GetDeviceType(data):
        if 'esa' in data: return DeviceType.WASHING_MACHINE
        if 'sensor' in data: return DeviceType.TEMPERATURE_SENSOR
        return DeviceType.UNKNOWN

class DeviceView(tk.Frame):
    

    def __init__(self,root, id, deviceType: DeviceType,manager):
        self.property_valueSource  = "N/A"
        self.property_powerSequenceState  = "N/A"
        self.property_powerSequenceSlotPowerType  = "N/A"
        self.property_contractualPLConsumptionMaxValue = 0
        self.property_nodeRemoteControllable = "enable"
        self.prefix = "http://"
        self.manager = manager
        self.deviceType = deviceType
        if deviceType == DeviceType.WASHING_MACHINE:
            iconname = "cleaning.png"
        elif deviceType == DeviceType.TEMPERATURE_SENSOR:
            iconname = "temperature.png"

        self.datasample_count =0
        self.id = id
        self.isFlexible_stop = False
        self.isFlexible_pause = False
        #self.isOperation = False
        self.data_x = []
        self.data_y = []

        frame = tk.Frame(root, bg='lavender', width=300, height=600, pady=10,padx = 10)
        #frame = tk.Frame(root, bg='brown', width=300, height=600, pady=10,padx = 10)
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        image = Image.open(r"examples/rest-api-demo/knowledge-bases/Images/"+iconname).resize((100, 100))
        my_img = ImageTk.PhotoImage(image)
        my_label = tk.Label(frame,image=my_img,bg='lavender')  
        my_label.img = my_img  
        my_label.grid( row=0,column=0, sticky=tk.N)

        self.CreateFlexibleStartUI(frame)
        frame_buttons2 = tk.Frame(frame, width=100,background='lavender', height=100, pady=10,padx = 20)
        frame_buttons2.grid( row=4,column=0, sticky=tk.N)

        label = tk.Label(frame_buttons2,text="Manual\nOperation",bg='lavender')
        label.pack(side=tk.LEFT)

        self.button_operation = tk.Button(frame_buttons2, text="Operation", command=self.operation_click)
        self.button_operation.pack(side=tk.RIGHT)
        

        self.frame = frame

        #self.figure = plt.figure(figsize=(2, 2))
        self.fig = plt.figure(figsize=(2, 2))
        self.fig.patch.set_facecolor('lavender')
        #plt.switch_backend('agg')
        #self.fig.patch.set_alpha(0)
        plt.subplots_adjust(left=0.18, bottom=0.15, right=0.95, top=0.95)
        self.ax = self.fig.add_subplot(111)
        
        self.scatter = FigureCanvasTkAgg(self.fig, frame)
        self.scatter.get_tk_widget().grid( row=6,column=0, sticky=tk.S)

        frame_scale = tk.Frame(frame,background='lavender', width=100, height=100, pady=10,padx = 20)
        frame_scale.grid( row=10,column=0, sticky=tk.N)

        scalelabel = tk.Label(frame_scale,text="Limit\nPower",bg='lavender')
        scalelabel.pack(side=tk.LEFT)

        self.scale = tk.Scale(frame_scale, from_=0, to=100, orient=tk.HORIZONTAL,length=200)
        self.scale.pack(side=tk.LEFT)
        self.scale_lastime_modify = datetime(1111,1,1,1,11,11)
        self.scale.bind("<ButtonRelease-1>", self.updateScaleValue)


        self.UpdateManualOperationUI()
    def CreateFlexibleStartUI(self,frame):

        #myframe = tk.Frame(frame, bg='lavender', width=300, height=600, pady=10,padx = 10)
        #myframe.grid( row=2,column=0, sticky=tk.N)

        frame_flexible = tk.Frame(frame,background='lavender',width=100, height=100, pady=10,padx = 20)
        frame_flexible.grid( row=2,column=0, sticky=tk.N)


        #Flexible start button
        label = tk.Label(frame_flexible,text="Flexible\nStart",bg='lavender')
        label.grid( row=0,column=0, sticky=tk.N)

       

        self.button_flexible_stop = tk.Button(frame_flexible, text="N/A", fg="black", command=self.flexible_stop_click)
        self.button_flexible_stop.grid( row=0,column=1, sticky=tk.W)

        self.button_flexible_apply = tk.Button(frame_flexible, text="Apply", fg="black", command=self.flexible_apply_click)
        self.button_flexible_apply.grid( row=0,column=1, sticky=tk.E)



        #earliest start 
        label = tk.Label(frame_flexible,text="Earliest Start Time: ",bg='lavender')
        label.grid( row=1,column=0, sticky=tk.N)

        self.text_flexible_earliestStartTime = tk.Text(frame_flexible,height = 1.4, width = 20)
        self.text_flexible_earliestStartTime.grid( row=1,column=1, sticky=tk.N)

        #latestEndTime
        label = tk.Label(frame_flexible,text="Latest End Time: ",bg='lavender')
        label.grid( row=2,column=0, sticky=tk.E)

        self.text_flexible_latestEndTime = tk.Text(frame_flexible,height = 1.4, width = 20)
        self.text_flexible_latestEndTime.grid( row=2,column=1, sticky=tk.N)

        #start Time
        label = tk.Label(frame_flexible,text="Start Time: ",bg='lavender')
        label.grid( row=3,column=0, sticky=tk.E)

        self.text_flexible_startTime = tk.Text(frame_flexible,height = 1.4, width = 20)#,bg='lavender')
        self.text_flexible_startTime.grid( row=3,column=1, sticky=tk.N)
        #self.text_flexible_startTime.configure(state='disabled')
        #endTime
        label = tk.Label(frame_flexible,text="End Time: ",bg='lavender')
        label.grid( row=4,column=0, sticky=tk.E)

        self.text_flexible_endTime = tk.Text(frame_flexible,height = 1.4, width = 20)#,bg='lavender')
        self.text_flexible_endTime.grid( row=4,column=1, sticky=tk.N)
        

        self.label_flexible_valueSource = tk.Label(frame_flexible,text="valueSource: " + self.property_valueSource,bg='lavender')
        self.label_flexible_valueSource.grid( row=5,column=0, sticky=tk.W)

        self.label_flexible_powerSequenceState = tk.Label(frame_flexible,text="powerSequenceState: " + self.property_powerSequenceState,bg='lavender')
        self.label_flexible_powerSequenceState.grid( row=5,column=1, sticky=tk.W)

        self.label_flexible_powerSequenceSlotPowerType = tk.Label(frame_flexible,text="powerSequenceSlotPowerType: "+ self.property_powerSequenceSlotPowerType,bg='lavender')
        self.label_flexible_powerSequenceSlotPowerType.grid( row=6,column=1, sticky=tk.W)

        

        
    def ReceiveData(self,data,requestingKnowledgeBaseId,energyUseCaseType):
        self.data = data
        if self.deviceType == DeviceType.TEMPERATURE_SENSOR:
            self.ReceiveData_Sensor(data,requestingKnowledgeBaseId)
        elif self.deviceType == DeviceType.WASHING_MACHINE:
            self.ReceiveData_WashingMachine(data,requestingKnowledgeBaseId)

        if energyUseCaseType== EnergyUseCaseType.FLEXIBLE_START:
            if 'earliestStartTime' in data and self.text_flexible_earliestStartTime.get("1.0","end") =='\n':
                #input = self.text_flexible_earliestStartTime.get("1.0","end")
                self.text_flexible_earliestStartTime.delete(1.0, "end")
                self.text_flexible_earliestStartTime.insert(1.0, data['earliestStartTime'])
            if 'latestEndTime' in data and self.text_flexible_latestEndTime.get("1.0","end") =='\n': 
                self.text_flexible_latestEndTime.delete(1.0, "end")
                self.text_flexible_latestEndTime.insert(1.0, data['latestEndTime'])
            if 'startTime' in data and self.text_flexible_startTime.get("1.0","end") =='\n':
                #self.text_flexible_startTime.configure(state='normal')
                self.text_flexible_startTime.delete(1.0, "end")
                self.text_flexible_startTime.insert(1.0, data['startTime'])
                #self.text_flexible_startTime.configure(state='disabled')
            if 'endTime' in data and self.text_flexible_endTime.get("1.0","end") =='\n':
                self.text_flexible_endTime.delete(1.0, "end")
                self.text_flexible_endTime.insert(1.0, data['endTime'])
            if 'powerSequenceState' in data:
                self.property_powerSequenceState = data['powerSequenceState']
                self.label_flexible_powerSequenceState.config(text=self.property_powerSequenceState)
            if 'valueSource' in data:
                self.property_valueSource = data['valueSource']
                self.label_flexible_valueSource.config(text=self.property_valueSource)
            if 'powerSequenceSlotPowerType' in data:
                self.property_powerSequenceSlotPowerType = data['powerSequenceSlotPowerType']
                self.label_flexible_powerSequenceSlotPowerType.config(text=self.property_powerSequenceSlotPowerType)
        elif energyUseCaseType== EnergyUseCaseType.LIMITATION_POWER_CONSUMPTION:
            if 'contractualPLConsumptionMaxValue' in data and ( (datetime.now() - self.scale_lastime_modify).total_seconds() > 5):
                self.property_contractualPLConsumptionMaxValue = int(data['contractualPLConsumptionMaxValue'])*100/65535
                self.scale.set(self.property_contractualPLConsumptionMaxValue)
                #print("\n\n\n\n",self.property_contractualPLConsumptionMaxValue,"\n\n\n")
            
        elif energyUseCaseType == EnergyUseCaseType.MANUAL_OPERATION:
            if 'nodeRemoteControllable' in data:
                self.property_nodeRemoteControllable = data['nodeRemoteControllable']
                print("\n\n\n\n\n\n\n","property_nodeRemoteControllable","\n",self.property_nodeRemoteControllable,"\n",energyUseCaseType,"\n\n\n\n\n")
            else: print("\n\n\n\n\n [ERROR MANUAL_OPERATION] \n\n\n")

        else: print("Error here")

    def ReceiveData_Sensor(self, data,requestingKnowledgeBaseId):
        self.datasample_count +=1
        self.data_x.append(self.datasample_count)
        self.data_y.append(float(data['temperature']))
        if len(self.data_y) > 50: self.data_x.pop(0);self.data_y.pop(0)

        self.UpdateUI_Chart()

    def ReceiveData_WashingMachine(self, data,requestingKnowledgeBaseId):
        self.datasample_count +=1

        if 'powerSequenceSlotValue' in data:
            self.data_x.append(self.datasample_count)
            self.data_y.append(float(data['powerSequenceSlotValue']))

        #print("Getting washingmachine data len=", len(self.data_x))
        if len(self.data_y) > 50: self.data_x.pop(0);self.data_y.pop(0)

        self.UpdateUI_Chart()


    def UpdateUI_Chart(self):
        self.ax.clear()
        self.ax.plot(self.data_x,self.data_y )
        self.scatter.draw()

    def updateScaleValue(self, event):
        print("on scale value changed " + str(self.scale.get()) + "\n\n\n")
        self.scale_lastime_modify = datetime.now()

    def flexible_stop_click(self):
        self.isFlexible_stop = not self.isFlexible_stop
        if self.isFlexible_stop:
            self.button_flexible_stop.config(text="ON", fg="green")
        else:
            self.button_flexible_stop.config(text="OFF", fg="black")

    def flexible_apply_click(self):
        data_earliestStartTime = self.text_flexible_earliestStartTime.get("1.0","end").replace('\n','')
        data_latestEndTime = self.text_flexible_latestEndTime.get("1.0","end").replace('\n','')
        data_startTime = self.text_flexible_startTime.get("1.0","end").replace('\n','')
        data_endTime = self.text_flexible_endTime.get("1.0","end").replace('\n','')
        print(data_earliestStartTime, data_latestEndTime)

        self.manager.Ask(EnergyUseCaseType.FLEXIBLE_START, 
                         {
            "esa": self.data['esa'],
            #"powerProfile": self.data['powerProfile'],
            #"alternativesgroup": self.data['alternativesgroup'],
            #"powerSequence": self.data['powerSequence'],
            #"earliestStartTime": self.prefix + data_earliestStartTime,
            #"latestEndTime": self.prefix + data_latestEndTime,
            "earliestStartTime":  data_earliestStartTime,
            "latestEndTime": data_latestEndTime,
            "startTime":  data_startTime,
            "endTime": data_endTime,
        } )
        self.text_flexible_earliestStartTime.delete(1.0, "end")
        self.text_flexible_latestEndTime.delete(1.0, "end")
        self.text_flexible_startTime.delete(1.0, "end")
        self.text_flexible_endTime.delete(1.0, "end")
        

        self.scale_lastime_modify = datetime(1111,1,1,1,11,11)
        self.manager.Ask(EnergyUseCaseType.LIMITATION_POWER_CONSUMPTION,
                          {
                              "esa": self.data['esa'],
                            'contractualPLConsumptionMaxValue' : self.scale.get()*65536/100
                          })

    def flexible_pause_click(self):
        self.isFlexible_pause = not self.isFlexible_pause
        if self.isFlexible_pause:
            self.button_flexible_pause.config(text="ON", fg="green")
        else:
            self.button_flexible_pause.config(text="OFF", fg="black")
        

    def operation_click(self):
        #self.isOperation = not self.isOperation
        if self.property_nodeRemoteControllable == 'disable':
            self.property_nodeRemoteControllable = "enable"
        elif self.property_nodeRemoteControllable == 'enable':
            self.property_nodeRemoteControllable = "disable"
        else: print("ERROR CANNOT UNDERSTANT: " + self.property_nodeRemoteControllable)
        self.UpdateManualOperationUI()
        # if self.isOperation:
        #     self.button_operation.config(text="Operation: ON", fg="green")
        # else:
        #     self.button_operation.config(text="Operation: OFF", fg="black")

    def UpdateManualOperationUI(self):
        if self.property_nodeRemoteControllable == 'disable':
            self.text_flexible_startTime.configure(state='disabled')
            self.text_flexible_endTime.configure(state='disabled')
            self.text_flexible_latestEndTime.configure(state='disabled')
            self.text_flexible_earliestStartTime.configure(state='disabled')
            self.button_flexible_stop['state'] = 'disabled'
            self.button_flexible_apply['state'] = 'disabled'
            self.button_operation.config(text="Operation: ON", fg="green")
            
        else:
            asd=123
            self.text_flexible_startTime.configure(state='normal')
            self.text_flexible_endTime.configure(state='normal')
            self.text_flexible_latestEndTime.configure(state='normal')
            self.text_flexible_earliestStartTime.configure(state='normal')
            self.button_flexible_stop['state'] = 'normal'
            self.button_flexible_apply['state'] = 'normal'
            self.button_operation.config(text="Operation: OFF", fg="black")
            


    
        
    
        