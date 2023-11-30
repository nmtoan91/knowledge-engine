import tkinter as tk
from tkinter import ttk
import threading 
from PIL import Image, ImageTk
from DeviceView import DeviceView
from DeviceView import DeviceType

class MainView(threading.Thread):
    def __init__(self, thread_name, thread_ID): 
        threading.Thread.__init__(self) 
        self.thread_name = thread_name 
        self.thread_ID = thread_ID 

    def run(self):
        self.devices = {}
        root = tk.Tk()
        root.geometry("600x800")
        root.title('Demonstation')
        root.geometry('{}x{}'.format(600, 500))

        root.columnconfigure(0, weight=1)
        root.columnconfigure(1, weight=1)

        frame1  = DeviceView(root,"http://example.org/sensor",DeviceType.TEMPERATURE_SENSOR)
        frame2  = DeviceView(root,"http://example.org/washingmachine/mc1",DeviceType.WASHING_MACHINE)
        frame1.frame.grid(row=0, column =0)
        frame2.frame.grid(row=0, column =1)

        self.devices[frame1.id] = frame1
        self.devices[frame2.id] = frame2

        root.mainloop()
    def RevieveData(self, data,requestingKnowledgeBaseId):
        if requestingKnowledgeBaseId in self.devices:
             self.devices[requestingKnowledgeBaseId].RevieveData(data,requestingKnowledgeBaseId)
        else: print("Cannot find view")
    
if __name__ == "__main__":
    mainView = MainView("My tkinter thread", 1000) 
    mainView.start() 