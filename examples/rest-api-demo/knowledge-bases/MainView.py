import tkinter as tk
from tkinter import ttk
import threading 
from PIL import Image, ImageTk
from DeviceView import DeviceView
from DeviceView import DeviceType

class MainView(threading.Thread):
    def __init__(self, thread_name, thread_ID,manager): 
        self.manager = manager
        threading.Thread.__init__(self) 
        self.thread_name = thread_name 
        self.thread_ID = thread_ID 

    def run(self):
        self.devices = {}
        self.root = tk.Tk()
        self.root.geometry("600x800")
        self.root.title('Demonstation')
        self.root.geometry('{}x{}'.format(900, 650))

        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)

        #self.AddDevice("http://example.org/sensor",DeviceType.TEMPERATURE_SENSOR)
        #self.AddDevice("http://example.org/washingmachine/mc1",DeviceType.WASHING_MACHINE)


        self.root.mainloop()
    def RunOnMainThread(self):
        self.run()
    def ReceiveData(self, data,requestingKnowledgeBaseId,energyUseCaseType):
        if not hasattr(self,'devices'):  return
        if requestingKnowledgeBaseId in self.devices:
             self.devices[requestingKnowledgeBaseId].ReceiveData(data,requestingKnowledgeBaseId,energyUseCaseType)
        else: 
            type = DeviceType.GetDeviceType(data)
            if type == DeviceType.UNKNOWN: 
                print("Cannot find view",type)
                return
            self.AddDevice(requestingKnowledgeBaseId,type)    

    def AddDevice(self, deviceId, deviceType:DeviceType):
        frame  = DeviceView(self.root,deviceId,deviceType,self.manager)
        index = len(self.devices)
        frame.frame.grid(row=index//3, column =index%3)
        self.devices[frame.id] = frame
    
if __name__ == "__main__":
    mainView = MainView("My tkinter thread", 1000) 
    mainView.start() 