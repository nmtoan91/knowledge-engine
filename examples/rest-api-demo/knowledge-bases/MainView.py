import tkinter as tk
from tkinter import ttk
import threading 
from PIL import Image, ImageTk
from DeviceView import DeviceView

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

        frame1  = DeviceView(root,"<https://example.org/sensor/1>",iconname="temperature.png")
        frame2  = DeviceView(root,"<https://example.org/washingmachine/1>",iconname="cleaning.png")
        frame1.frame.grid(row=0, column =0)
        frame2.frame.grid(row=0, column =1)

        self.devices[frame1.id] = frame1
        self.devices[frame2.id] = frame2

        root.mainloop()
    def RevieveData(self, data):
        if 'sensor' in data.keys():
            if data['sensor']  in self.devices:
                self.devices[data['sensor']].RevieveData_Sensor(data)
            else: print("Cannot find view for sensor:" + data['sensor'])
        elif 'esa' in data.keys():
            if data['esa']  in self.devices:
                self.devices[data['esa']].RevieveData_WashingMachine(data)
            else: print("Cannot find view for esa: " + data['esa'])

        else: print("Cannot find view")
    
if __name__ == "__main__":
    mainView = MainView("My tkinter thread", 1000) 
    mainView.start() 