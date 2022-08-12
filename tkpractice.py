# -*- coding: utf-8 -*-
"""
Created on Tue Jun 28 22:47:45 2022

@author: dougi
"""


import tkinter
from datetime import datetime
import time

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import yfinance as yf
import pygame as pg


import numpy as np

def on_key_press(event):
     print("you pressed {}".format(event.key))
     key_press_handler(event, canvas, toolbar)
 

class GUI:
    data = []
    dwell = 5
    def __init__(self):    
        root = tkinter.Tk()
        root.wm_title("Embedding in Tk")
        
        fig = Figure(figsize=(11.5, 6.5), dpi=100)
        t = np.arange(0, 3, .01)
        
        self.ax1 = fig.add_subplot(121)
        self.ax1.plot(GUI.data)
        self.ax2 = fig.add_subplot(122)
        self.ax2.plot(t, 2 * np.sin(2 * np.pi * t))
        
        self.canvas = FigureCanvasTkAgg(fig, master=root)  # A tk.DrawingArea.
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)
        #plt.ion()
        
        self.canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)
        
        button = tkinter.Button(master=root, text="Quit", command=self._quit)
        button.pack(side=tkinter.BOTTOM)
        self.live_plot("NIO")
        
        tkinter.mainloop()
    def live_plot(self,stock,limit = 15):
        loop = True
        counter = 0 
        while loop and counter < limit:
            pg.time.wait(GUI.dwell*1000) 
            t = time.time()
            curr = datetime.now().strftime("%H:%M_%a").split('_')
            ticker_yahoo = yf.Ticker(stock)
            data = ticker_yahoo.history()
            last_quote = data['Close'].iloc[-1]
            counter += 1 
            self.ax1.scatter(t,last_quote,color="b",marker="${0}$".format("A"))
            self.canvas.draw()
            
        
    
    
    
    
    

    def _quit(self,root):
        root.quit()     # stops mainloop
        root.destroy()  # this is necessary on Windows to prevent
                    # Fatal Python Error: PyEval_RestoreThread: NULL tstate

GUI()

# If you put root.destroy() here, it will cause an error if the window is
# closed with the window manager.