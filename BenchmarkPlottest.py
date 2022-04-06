import multiprocessing 
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter.constants import DISABLED, HORIZONTAL, NORMAL
import numpy as np
from PIL import Image, ImageTk
import time
import threading
from pycromanager import Bridge
from utils.OPMLiveDeskewing import livedeskew

class BenchmarkingApp():
    def __init__(self,master):
        self.master = master

        #Initialise the GUI Window
        self.master.wm_title("OPM Live Deskew BenchMarking")
        self.master.configure(bg='#91B9A4')

        bridge = Bridge()
        core = bridge.get_core()
        self.exposuretime = 5
        core.set_exposure(self.exposuretime)
        core.set_roi(0,0,1304,87)

        self.vmingui = tk.IntVar()
        self.vmaxgui = tk.IntVar()

        self.q1 = multiprocessing.Queue()
        self.q2 = multiprocessing.Queue()
        self.q3 = multiprocessing.Queue()
        self.q4 = multiprocessing.Queue()
        self.q5 = multiprocessing.Queue()

        self.DSKW = livedeskew(self.q1,self.q2,self.q3,self.q4,self.q5)
        self.DSKW.setDisplayMode(False)

        self.Deskewedimg =  ImageTk.PhotoImage(image=Image.fromarray(np.zeros((self.DSKW.new_height,self.DSKW.width))))

        self.master.geometry([str(self.DSKW.width+20) + "x" + str(self.DSKW.new_height+60)])

        self.videofeed = tk.Label(self.master, image=self.Deskewedimg)
        self.minslider = tk.Scale(self.master, from_=0, to=200, length = 200, label = 'Min Intensity', orient=HORIZONTAL,bd = 0)
        self.maxslider = tk.Scale(self.master, from_=0, to=200, length = 200, label = 'Max Intensity', orient=HORIZONTAL,bd = 0)
        self.startbenchmark = tk.Button(self.master, text = "Start", bd = 1, command =  self.startBenchmarking)
        self.plotresult = tk.Button(self.master, text = "Plot Result", bd = 1, command =  self.plot)

        self.minslider.set(0)
        self.maxslider.set(200)

        self.videofeed.pack()
        self.startbenchmark.pack()
        self.plotresult.pack()
        self.minslider.pack()
        self.maxslider.pack()

        self.DSKW.setDisplayMode(False)

        self.depth = self.DSKW.get_depth()
        self.totalno = 2
        self.no_imgs = self.depth*self.totalno
        self.imgs = []

        startFOV = 10
        stopFOV = 300
        steps = 5

        self.FOVRange = np.linspace(startFOV,stopFOV,steps)
        self.snapspeed = 0
        self.deskewspeed = []
        self.plotspeed = []

    def plot(self):  
        plt.plot(self.FOVRange, list(map(lambda x: 1000/x, self.Snaptime)), label = "Snap")
        plt.plot(self.FOVRange, list(map(lambda x: 1000/x, self.deskewspeed)), label = "Deskew")
        plt.plot(self.FOVRange, list(map(lambda x: 1000/x, self.plotspeed)), label = "Plot")
        plt.legend()
        plt.show()

    def displayResults(self):
        self.videofeed.configure(image=self.Deskewedimg) # update the GUI element
        self.videofeed.image = self.Deskewedimg
        print('---FOVs, um---')  
        print(self.FOVRange)
        print('---Snap Time, ms---')  
        print(self.snapspeed)
        print('---Deskew Time, ms---')  
        print(self.deskewspeed)
        print('---Plot Time, ms---')  
        print(self.plotspeed)

        self.Snaptime = self.snapspeed*np.ones_like(self.FOVRange)
        with open('Confocal_BenchmarkResult_'+str(self.exposuretime)+'msexps.txt', 'w') as f:
            f.write("FOV, Snap Time, Deskew Time, Plot Time\n")
            for i in range(len(self.FOVRange)):
                f.write("{}, {}, {}, {}\n".format(self.FOVRange[i], self.Snaptime[i],self.deskewspeed[i],self.plotspeed[i]))
        
    def startBenchmarking(self):
        benchmark_thread = threading.Thread(target= self.snapBenchmark)
        benchmark_thread.start()

    def snapBenchmark(self):
        bridge = Bridge()
        core = bridge.get_core()
        print('Starting Snapping')
        start = time.perf_counter_ns()
        for _ in range(self.no_imgs):
            self.imgs.append(self.DSKW.grab_frame(core,))   
        self.imgs.append('END') 
        for im in self.imgs:
            self.q4.put(im)
        finish = time.perf_counter_ns()
        print('Snapping Complete')

        self.snapspeed = ((finish-start)/1E6)/self.no_imgs#self.totalno

        self.deskewBenchmark()

    def deskewBenchmark(self):
        #Deskewing Speed Test
        i = 1
        for FOV in self.FOVRange:
            print(i)
            i += 1
            self.DSKW.setScanRange(FOV)
            for im in self.imgs:
                self.q1.put(im)
            print('Starting Deskew')
            start = time.perf_counter_ns()
            self.DSKW.GPU_deskew_max(self.q1,self.q5)
            finish = time.perf_counter_ns()
            print('Deskew Complete')

            self.deskewspeed.append(((finish-start)/1E6)/self.no_imgs)

            self.plotBenchmark()
        self.displayResults()

    def plotBenchmark(self):
        print('Starting Plotting')
        plottime = []
        start = time.perf_counter_ns()
        while True: 
            if not self.q5.empty():
                image_array = self.q5.get() # empty data from reconstruction pool
                if isinstance(image_array, str):
                    break
                else:
                    vmin = self.minslider.get()
                    vmax = self.maxslider.get()
                    image_array [image_array  < vmin] = 0
                    image_array  = ((image_array/vmax)*255).astype("uint8")
                    # run the update function 
                    img =  ImageTk.PhotoImage(image=Image.fromarray(image_array)) # convert numpy array to tikner object 
                    
                    self.videofeed.configure(image=img) # update the GUI element
                    self.videofeed.image = img

                    finish = time.perf_counter_ns()
                    plottime.append((finish-start)/1E6)
                    start = time.perf_counter_ns()
        self.plotspeed.append(np.mean(plottime))
        print('Plotting Complete')

if __name__ == '__main__':
    root = tk.Tk()
    my_gui = BenchmarkingApp(root)
    root.mainloop()
    








