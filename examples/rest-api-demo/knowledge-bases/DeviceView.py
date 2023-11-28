import tkinter as tk
from tkinter import ttk
import threading 
from PIL import Image, ImageTk
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class DeviceView(tk.Frame):
    

    def __init__(self,root, id):
        self.id = id
        self.isFlexible = False
        self.isOperation = False
        self.data_x = []
        self.data_y = []

        frame = tk.Frame(root, bg='lavender', width=300, height=600, pady=10,padx = 10)
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        image = Image.open(r"examples/rest-api-demo/knowledge-bases/Images/lightbulb.png").resize((100, 100))
        my_img = ImageTk.PhotoImage(image)
        my_label = tk.Label(frame,image=my_img)  
        my_label.img = my_img  
        my_label.grid( row=0,column=0, sticky=tk.N)

        frame_buttons = tk.Frame(frame, width=100, height=100, pady=10,padx = 20)
        frame_buttons.grid( row=2,column=0, sticky=tk.N)

        
        self.button_flexible = tk.Button(frame_buttons, text="Flexible: OFF", fg="black", command=self.flexible_click)
        self.button_flexible.pack(side=tk.LEFT)

        self.button_operation = tk.Button(frame_buttons, text="Operation", command=self.operation_click)
        self.button_operation.pack(side=tk.LEFT)
        self.UpdateUI_button_operation()




        #self.datalabel = tk.Label(frame,text="Status")
        #self.datalabel.grid( row=6,column=0, sticky=tk.S)

        self.frame = frame

        #self.figure = plt.figure(figsize=(2, 2))
        self.fig = plt.figure(figsize=(2, 2))
        self.ax = self.fig.add_subplot(111)
        

        # x = np.linspace(-1, 1, 50)
        # y = 2*x + 1
        # self.ax.plot(x, y)
        self.scatter = FigureCanvasTkAgg(self.fig, frame)
        self.scatter.get_tk_widget().grid( row=4,column=0, sticky=tk.S)

        frame_scale = tk.Frame(frame, width=100, height=100, pady=10,padx = 20)
        frame_scale.grid( row=8,column=0, sticky=tk.N)

        scalelabel = tk.Label(frame_scale,text="Limit\nPower")
        scalelabel.pack(side=tk.LEFT)

        self.scale = tk.Scale(frame_scale, from_=0, to=100, orient=tk.HORIZONTAL,length=200)
        self.scale.pack(side=tk.LEFT)
        self.scale.bind("<ButtonRelease-1>", self.updateScaleValue)

    def RevieveData(self, data):
        self.data_x.append(len(self.data_x))
        self.data_y.append(float(data['temperature']))
        if len(self.data_y) > 100: self.data_x.pop(0);self.data_y.pop(0)

        self.UpdateUI_Chart()

    def UpdateUI_Chart(self):
        self.ax.clear()
        self.ax.plot(self.data_x,self.data_y )
        self.scatter.draw()

    def updateScaleValue(self, event):
        print("scale value: " + str(self.scale.get()))
    def flexible_click(self):
        self.isFlexible = not self.isFlexible
        self.UpdateUI_button_flexible()
    def operation_click(self):
        self.isOperation = not self.isOperation
        self.UpdateUI_button_operation()

    def UpdateUI_button_flexible(self):
        if self.isFlexible:
            self.button_flexible.config(text="Flexible: ON", fg="green")
        else:
            self.button_flexible.config(text="Flexible: OFF", fg="black")
    def UpdateUI_button_operation(self):
        if self.isOperation:
            self.button_operation.config(text="Operation: ON", fg="green")
        else:
            self.button_operation.config(text="Operation: OFF", fg="black")