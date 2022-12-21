import multiprocessing 
import matplotlib.pyplot as plt
import tkinter as tk
import datetime
from tkinter.constants import DISABLED, HORIZONTAL, NORMAL
import numpy as np
from PIL import Image, ImageTk
import time
import threading
from pycromanager import Core
from utils.OPMLiveDeskewing import livedeskew

### Need to comment out line 342 'out_imgq.put('END')' in OPMLiveDeskewing to work properly

class LiveBenchMarking():
    def __init__(self,stopq,rotateq,dskwImgq,dskwImgq2,dskwImgq3):
        self.dskwImgq = dskwImgq
        self.dskwImgq3 = dskwImgq3
        self.TEST = livedeskew(stopq,rotateq,dskwImgq,dskwImgq2,dskwImgq3)
        self.deskewspeed = []
        self.TEST.setDepth(140)

    def set_deskew_speed(self,speed):
        self.deskewspeed = speed

    def set_imgs(self,imgs):
        self.imgs = imgs

    def set_FOV_Range(self,range):
        self.FOVRange = range

    def deskewBenchmark(self):
        #Deskewing Speed Test
        i = 1
        for FOV in self.FOVRange:
            print(i)
            i += 1
            self.TEST.setScanRange(FOV)
            for im in self.imgs:
                self.TEST.qcam.put(im)
            print('Starting Deskew')
            start = time.perf_counter_ns()
            self.TEST.GPU_deskew_max(self.TEST.qcam,self.dskwImgq3)
            finish = time.perf_counter_ns()
            print('Deskew Complete')

            self.dskwImgq.put(((finish-start)/1E6))

        self.dskwImgq3.put('End')

class BenchmarkingApp():
    def __init__(self,master):
        self.master = master

        #Initialise the GUI Window
        self.master.wm_title("OPM Live Deskew BenchMarking")
        self.master.configure(bg='#91B9A4')

        core = Core()
        self.exposuretime = 0.5
        core.set_exposure(self.exposuretime)
        core.set_roi(0,0,1304,174)

        self.vmingui = tk.IntVar()
        self.vmaxgui = tk.IntVar()

        self.q1 = multiprocessing.Value('i', 0)
        self.q2 = multiprocessing.Value('d', 0)
        self.q3 = multiprocessing.Queue()
        self.q4 = multiprocessing.Queue()
        self.q5 = multiprocessing.Queue()

        self.DSKW = LiveBenchMarking(self.q1,self.q2,self.q3,self.q4,self.q5)
        self.DSKW.TEST.setDisplayMode(True)
        self.q2.value = self.DSKW.TEST.get_shearFactor()

        self.Deskewedimg =  ImageTk.PhotoImage(image=Image.fromarray(np.zeros((self.DSKW.TEST.new_height,self.DSKW.TEST.width))))

        self.master.geometry([str(self.DSKW.TEST.width+20) + "x" + str(self.DSKW.TEST.new_height+60)])

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

        self.DSKW.TEST.setDisplayMode(True)

        self.depth = self.DSKW.TEST.get_depth()
        self.totalno = 1
        self.no_imgs = self.depth*self.totalno
        self.imgs = []

        startFOV = 1
        stopFOV = 575
        steps = 11

        self.FOVRange = np.linspace(startFOV,stopFOV,steps)
        self.DSKW.set_FOV_Range(self.FOVRange)
        self.snapspeed = 0
        self.plotspeed = []
        self.deskewspeed = []

    def plot(self):  
        plt.plot(self.FOVRange,self.Snaptime, label = "Snap")
        plt.plot(self.FOVRange, self.deskewspeed, label = "Deskew")
        plt.plot(self.FOVRange, self.plotspeed, label = "Plot")
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
        with open('Widefield_BenchmarkResult_3_'+str(self.exposuretime)+'msexps' + str(self.no_imgs) + 'no_imgs'+ datetime.datetime.now().strftime('saved_%d%m%YT%H%M') + '.txt', 'w') as f:
            f.write("FOV, Snap Time, Deskew Time, Plot Time\n")
            for i in range(len(self.FOVRange)):
                f.write("{}, {}, {}, {}\n".format(self.FOVRange[i], self.Snaptime[i],self.deskewspeed[i],self.plotspeed[i]))
        
    def startBenchmarking(self):
        self.snapBenchmark()
        benchmark_process = multiprocessing.Process(target= self.DSKW.deskewBenchmark)
        benchmark_process.start()
        
        benchmark_thread = threading.Thread(target= self.plotBenchmark)
        benchmark_thread.start()

    def snapBenchmark(self):
        core = Core()
        print('Starting Snapping')
        start = time.perf_counter_ns()
        for _ in range(self.no_imgs):
            self.imgs.append(self.DSKW.TEST.grab_frame(core,))   
        self.imgs.append('END') 
        
        for im in self.imgs:
            self.q4.put(im)
        finish = time.perf_counter_ns()
        print('Snapping Complete')

        self.snapspeed = ((finish-start)/1E6)#self.totalno

        self.DSKW.set_imgs(self.imgs)

    def plotBenchmark(self):
        print('Starting Plotting')
        while True: 
            if not self.q5.empty():
                start = time.perf_counter_ns() #Start here so not timing time when waiting
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
                    self.plotspeed.append((finish-start)/1E6)
                    self.deskewspeed.append(self.q3.get())
                    
        #self.plotspeed.append(np.mean(plottime))
        print('Plotting Complete')
        self.displayResults()

if __name__ == '__main__':
    root = tk.Tk()
    my_gui = BenchmarkingApp(root)
    root.mainloop()
    








