#from xml.etree.ElementInclude import LimitedRecursiveIncludeError
from ctypes.wintypes import RGB
from tkinter.constants import DISABLED, HORIZONTAL, NORMAL, VERTICAL
from PIL import Image, ImageTk
from utils.MotrisedFilterWheel import MotrisedFilterWheel
from utils.NIDAQlasers import Lasers
from utils.OPMLiveDeskewing import livedeskew
import tkinter as tk
from tkinter import SINGLE, ttk, simpledialog
import threading
import multiprocessing
import numpy as np
import time
import os
import nidaqmx

class LaserFilterWindow(tk.Toplevel):
    def __init__(self, parent):
        self.parent = parent
        super().__init__(self.parent.master)

        self.geometry('410x350')
        self.title('Add Laser and Filter')
        self.configure(bg='#6cace4')

        #Variables
        self.laserName = tk.StringVar()
        self.Method = tk.IntVar()
        self.Method.set(1)
        self.daqdolines_clicked = tk.StringVar()
        self.daqdolines_clicked.set(self.parent.daqdolines[0]) 
        self.daqaolines_clicked = tk.StringVar()
        self.daqaolines_clicked.set(self.parent.daqaolines[0]) 
        self.MaxAnoV = tk.IntVar()
        self.FilterName = tk.StringVar()
        self.FilterWheels_clicked = tk.StringVar()
        self.FilterWheels_clicked.set('Cairn OptoSpin') 
        self.WheelPos = tk.IntVar()

        #Objects
        self.laserName_label = tk.Label(self, text = "Laser Name:", fg='#000000', bg='#6cace4',bd = 0)
        self.laserName_entry = tk.Entry(self, textvariable=self.laserName, width=30)
        self.controlmethod_label = tk.Label(self, text = "Control Method:", fg='#000000', bg='#6cace4',bd = 0)
        self.TTL_radio = tk.Radiobutton(self, text="TTL", padx = 20, variable= self.Method, value=1, bg='#6cace4',activebackground='#6cace4',command = self.Control_method_changed)
        self.AnoV_radio = tk.Radiobutton(self, text="Analogue Voltage", padx = 20, variable= self.Method, value=2, bg='#6cace4',activebackground='#6cace4',command = self.Control_method_changed)
        self.TTLPort_label = tk.Label(self, text = "Port:", fg='#000000', bg='#6cace4',bd = 0)
        self.daqdolines_drop = ttk.Combobox(self, textvariable=self.daqdolines_clicked)
        self.daqdolines_drop['values'] = self.parent.daqdolines
        self.daqdolines_drop['state'] = 'readonly'
        self.AnoVPort_label = tk.Label(self, text = "Port:", fg='#000000', bg='#6cace4',bd = 0)
        self.daqaolines_drop = ttk.Combobox(self, textvariable=self.daqaolines_clicked)
        self.daqaolines_drop['values'] = self.parent.daqaolines
        self.daqaolines_drop['state'] = 'readonly'
        self.daqaolines_drop['state'] = DISABLED
        self.MaxAnoV_label = tk.Label(self, text = "Max Voltage:", fg='#000000', bg='#6cace4',bd = 0)
        self.MaxAnoV_entry = tk.Entry(self, textvariable=self.MaxAnoV, width=5)
        self.MaxAnoV_entry['state'] = DISABLED
        self.FilterWheel_label = tk.Label(self, text = "Filter Wheel:", fg='#000000', bg='#6cace4',bd = 0)
        self.FilterWheel_drop = ttk.Combobox(self, textvariable=self.FilterWheels_clicked)
        self.FilterWheel_drop['values'] = 'Cairn OptoSpin'
        self.FilterWheel_drop['state'] = 'readonly'
        self.FilterWheel_drop['state'] = DISABLED
        self.FilterName_label = tk.Label(self, text = "Filter Name:", fg='#000000', bg='#6cace4',bd = 0)
        self.FilterName_entry = tk.Entry(self, textvariable=self.FilterName, width=30)
        self.Wheelpos_label = tk.Label(self, text = "Wheel Position:", fg='#000000', bg='#6cace4',bd = 0)
        self.Wheelpos_entry = tk.Entry(self, textvariable=self.WheelPos, width=5)
        self.add = tk.Button(self, text = "Add", state = NORMAL, bd = 1, command = self.add_pressed)
        
        #Place Objects
        self.laserName_label.place(x = 5, y = 10)
        self.laserName_entry.place(x = 100, y = 10)
        self.controlmethod_label.place(x = 5, y = 50)
        self.TTL_radio.place(x = 120, y = 50)
        self.AnoV_radio.place(x = 220, y = 50)
        self.TTLPort_label.place(x = 10, y = 100)
        self.daqdolines_drop.place(x = 50, y = 100)
        self.AnoVPort_label.place(x = 210, y = 100)
        self.daqaolines_drop.place(x = 250, y = 100)
        self.MaxAnoV_label.place(x = 210, y = 130)
        self.MaxAnoV_entry.place(x = 290, y = 130)
        self.FilterWheel_label.place(x = 10, y = 180)
        self.FilterWheel_drop.place(x = 150, y = 180)
        self.FilterName_label.place(x = 5, y = 220)
        self.FilterName_entry.place(x = 100, y = 220)
        self.Wheelpos_label.place(x = 5, y = 260)
        self.Wheelpos_entry.place(x = 100, y = 260)
        self.add.place(x = 150, y = 300) 

        #Font
        self.laserName_label.config(font=('Helvatical bold',12))
        self.laserName_entry.config(font=('Helvatical bold',12))
        self.controlmethod_label.config(font=('Helvatical bold',12))
        self.TTL_radio.config(font=('Helvatical bold',10))
        self.AnoV_radio.config(font=('Helvatical bold',10))
        self.TTLPort_label.config(font=('Helvatical bold',10))
        self.daqaolines_drop.config(font=('Helvatical bold',8))
        self.daqdolines_drop.config(font=('Helvatical bold',8))
        self.AnoVPort_label.config(font=('Helvatical bold',10))
        self.MaxAnoV_entry.config(font=('Helvatical bold',10))
        self.MaxAnoV_label.config(font=('Helvatical bold',10))
        self.FilterWheel_label.config(font=('Helvatical bold',12))
        self.FilterWheel_drop.config(font=('Helvatical bold',8))
        self.FilterName_label.config(font=('Helvatical bold',10))
        self.FilterName_entry.config(font=('Helvatical bold',10))
        self.Wheelpos_label.config(font=('Helvatical bold',10))
        self.Wheelpos_entry.config(font=('Helvatical bold',10))
        self.add.config(font=('Helvatical bold',15))

    def Control_method_changed(self):
        if self.Method.get() == 1:
            self.daqdolines_drop['state'] = NORMAL
            self.daqaolines_drop['state'] = DISABLED
            self.MaxAnoV_entry['state'] = DISABLED
        else:
            self.daqdolines_drop['state'] = DISABLED
            self.daqaolines_drop['state'] = NORMAL
            self.MaxAnoV_entry['state'] = NORMAL

    def add_pressed(self):
        indx = self.parent.LaserFilter_LB.size() + 1
        if self.Method.get() == 1:
            string = self.laserName.get() + " @ " + self.daqdolines_clicked.get() + "  -->  " + self.FilterName.get() + " @ Position " + str(self.WheelPos.get())
        else:
            string = self.laserName.get() + " @ " + self.daqaolines_clicked.get() + "  -->  " + self.FilterName.get() + " @ Position " + str(self.WheelPos.get())
        self.parent.LaserFilter_LB.insert(indx,string)
        self.parent.LaserFilterCanvas.itemconfig(self.parent.LaserFilterLED, fill="orange")
        self.parent.laserNames.append(self.laserName.get())
        self.parent.laserfilterName.append(self.FilterName.get())
        self.parent.laserPort.append(self.daqdolines_clicked.get())
        self.parent.laserfilterPos.append(self.WheelPos.get())
        self.parent.laserTrigMethods.append(self.Method.get()) #1 = TLL, 0 = Voltage
        self.parent.lasermaxVolts.append(self.MaxAnoV.get())
        self.destroy()

class deskewApp:
    def __init__(self,master):
        self.master = master

        #Initialise the GUI Window
        self.master.wm_title("OPM Live Deskew v.1.4")
        self.master.configure(bg='#91B9A4')
        self.master.geometry("1200x600")

        #Defining Queues needed for communication 
        self.stopq = multiprocessing.Value('i', 0)
        self.dskwImgq = multiprocessing.Queue()
        self.dskwImgq2 = multiprocessing.Queue()
        self.dskwImgq3 = multiprocessing.Queue()
        self.rotateq = multiprocessing.Value('d', 0)

        self.DSKW = livedeskew(self.stopq,self.rotateq,self.dskwImgq,self.dskwImgq2,self.dskwImgq3)

        if (self.DSKW.new_height+40) > 760:
            self.master.geometry(str(self.DSKW.width+475+20) + "x" + str(self.DSKW.new_height+40))
        else:
            self.master.geometry(str(self.DSKW.width+475+20) + "x760")

        #GUI Variables 
        self.isLive = False
        self.clr1min = 10
        self.clr1max = 4000
        self.clr2min = 10
        self.clr2max = 4000
        self.clr3min = 10
        self.clr3max = 4000
        self.local_system = nidaqmx.system.System.local()

        self.clradjust = tk.StringVar(self.master,'1')
        self.laserson = [0, 0, 0, 0] #state for [laser1, laser2, laser3, laser4]
        self.laser1PWR = tk.IntVar() 
        self.laser2PWR = tk.IntVar() 
        self.laser3PWR = tk.IntVar() 
        self.laser4PWR = tk.IntVar() 
        self.allowMultiLasers = tk.IntVar() 
        self.laserlabels = []
        self.laserPWRentrys = []
        self.laserswitches = []

        self.laserNames = []
        self.laserPort = []
        self.laserfilterPos = []
        self.laserfilterName = []
        self.laserTrigMethods = []
        self.lasermaxVolts = []
        
        self.connectedLasers = []

        self.configfileDir = os.getcwd() #r"C:\Users\OPM_Admin\Documents\Python Scripts\WorkInProgress\GUI_for_FOM\ "
        self.configfileExt = r".txt"
        self.config_files = ["none"]
        [self.config_files.append(_) for _ in os.listdir(self.configfileDir) if _.endswith(self.configfileExt)]
        self.config_files_clicked = tk.StringVar()
        self.config_files_clicked.set( "none") 

        self.daqaolines = []
        self.find_daqaolines()
        self.daqaolines_clicked = tk.StringVar()
        self.daqaolines_clicked.set(self.daqaolines[0]) 
        self.daqdolines = []
        self.find_daqdolines()  
        self.daqdilines = []
        self.find_daqdilines()  
        self.daqdilines_clicked = tk.StringVar()
        self.daqdilines_clicked.set(self.daqdilines[0]) 

        self.Comp_options = ["Global Update Mode","Rolling Update Mode"]
        self.Comp_clicked = tk.StringVar()
        self.Comp_clicked.set( "Global Update Mode" ) 

        self.Proj_options = ["MIP","Single Slice"]
        self.Proj_clicked = tk.StringVar()
        self.Proj_clicked.set("MIP") 

        self.scn_range = tk.IntVar()  
        self.nostep = tk.IntVar() 
        self.exposure = tk.DoubleVar() 
        self.sheetangle = tk.DoubleVar()
        self.pixelsize = tk.DoubleVar()
        self.scanninggalvo = tk.IntVar() 
        self.altHardware = tk.IntVar() 
        self.preloadgalvo = tk.IntVar()
        self.galvominV = tk.DoubleVar() 
        self.galvomaxV = tk.DoubleVar() 
        self.galvooffV = tk.DoubleVar() 
        self.galvov2um = tk.DoubleVar() 
        self.LaserFilter = tk.IntVar() 
        self.FilterWheelConnected = False
        self.FilterWheelenabled = tk.IntVar()
        self.CameraTrigger = tk.IntVar()
        self.CameraTrigger_clicked = tk.StringVar()
        self.CameraTrigger_clicked.set(self.DSKW.Trigger_Options[0]) 
        self.OptoSplit = tk.IntVar()
        self.openFilterPos = tk.IntVar()
        
        self.Titleimg = ImageTk.PhotoImage(file=r"C:\Users\OPM_Admin\Documents\Python Scripts\WorkInProgress\GUI_for_FOM\GUI_Images\LiveDeskewLogo.jpg")
        self.Liveimg = ImageTk.PhotoImage(file=r"C:\Users\OPM_Admin\Documents\Python Scripts\WorkInProgress\GUI_for_FOM\GUI_Images\LiveButtonLogo.jpg")
        self.StopLiveimg = ImageTk.PhotoImage(file=r"C:\Users\OPM_Admin\Documents\Python Scripts\WorkInProgress\GUI_for_FOM\GUI_Images\StopLiveButtonLogo.jpg")
        self.OnSwitch = ImageTk.PhotoImage(file=r"C:\Users\OPM_Admin\Documents\Python Scripts\WorkInProgress\GUI_for_FOM\GUI_Images\onswitch.jpg")
        self.OffSwitch = ImageTk.PhotoImage(file=r"C:\Users\OPM_Admin\Documents\Python Scripts\WorkInProgress\GUI_for_FOM\GUI_Images\offswitch.jpg")
        self.Deskewedimg =  ImageTk.PhotoImage(image=Image.fromarray(np.zeros((self.DSKW.new_height,self.DSKW.width))))
        self.LAGLogo = ImageTk.PhotoImage(file=r"C:\Users\OPM_Admin\Documents\Python Scripts\WorkInProgress\GUI_for_FOM\GUI_Images\LAG_logo.png")

        #Define the GUI objects
        self.tabControl = ttk.Notebook(self.master)
        self.Livetab = ttk.Frame(self.tabControl, width=450, height=460)
        self.Controltab = ttk.Frame(self.tabControl, width=450, height=460)
       
        self.tabControl.add(self.Livetab, text ='Live Settings')
        self.tabControl.add(self.Controltab, text ='Control Settings')

        #Define the GUI objects
        #Master Objects
        self.TitleGrapic = tk.Label(self.master,image=self.Titleimg,bd = 0)
        self.button_live = tk.Button(self.master, image = self.Liveimg, bd = 0, command = self.start_live)
        self.button_Stop_live = tk.Button(self.master, state = DISABLED, image = self.StopLiveimg, bd = 0, command = self.stop_live)
        self.fps_label = tk.Label(self.master, text = "FPS: N/A", fg='#000000', bg='#91B9A4',bd = 0)
        self.Comp_drop = tk.OptionMenu(self.master ,self.Comp_clicked , *self.Comp_options, command = self.compModeSelect)
        self.videofeed = tk.Label(self.master, image=self.Deskewedimg)
        self.LogoGraphic = tk.Label(self.master, image=self.LAGLogo, bd=0)
        #Live Tab Objects
        self.maxslider = tk.Scale(self.Livetab, from_=10, to=8000, length = 200, label = 'Max Intensity', orient=VERTICAL,bd = 0,command=self.max_scale)
        self.minslider = tk.Scale(self.Livetab, from_=0, to=200, length = 200, label = 'Min Intensity', orient=VERTICAL,bd = 0,command=self.min_scale)
        self.Rotateslider = tk.Scale(self.Livetab, from_=0, to=90, length = 200, label = 'Rotate', state = DISABLED, orient=VERTICAL,bd = 0, command = self.rotate_scale)
        self.scan_range_label = tk.Label(self.Livetab, text = "Scan Range (um):",bd = 0)
        self.scan_entry = tk.Entry(self.Livetab, textvariable=self.scn_range, width=4)
        self.no_steps_label = tk.Label(self.Livetab, text = "No. Steps:",bd = 0)
        self.steps_entry = tk.Entry(self.Livetab, textvariable=self.nostep, width=4)
        self.exposure_label = tk.Label(self.Livetab, text = "Exposure Time (ms):", bd = 0)
        self.exposure_entry = tk.Entry(self.Livetab, textvariable=self.exposure, width=4)
        self.Deskew_Params_label = tk.Label(self.Livetab, text = "Deskew Parameters:", bd = 0)
        self.Sheet_angle_label = tk.Label(self.Livetab, text = "Sheet angle (degrees):", bd = 0)
        self.Sheet_angle_entry = tk.Entry(self.Livetab, textvariable=self.sheetangle, width=8)
        self.Pixel_size_label = tk.Label(self.Livetab, text = "Pixel size (um/px):", bd = 0)
        self.Pixel_size_entry = tk.Entry(self.Livetab, textvariable=self.pixelsize, width=8)
        self.Lasers_label = tk.Label(self.Livetab, text = "Lasers:", bd = 0)
        self.laser1_label = tk.Label(self.Livetab, text = "No Laser: @", bd = 0)
        self.laser1pwr_entry = tk.Entry(self.Livetab, textvariable=self.laser1PWR, width=4)
        self.laser1pwr_entry.bind('<Return>',lambda event, i = 0: self.laserChangePower(i))
        self.laser1pwr_label = tk.Label(self.Livetab, text = "%", bd = 0)
        self.laser1switch = tk.Button(self.Livetab, image = self.OffSwitch, bd = 0, command = lambda: self.laserChangeState(0))
        self.laser2_label = tk.Label(self.Livetab, text = "No Laser: @", bd = 0)
        self.laser2pwr_entry = tk.Entry(self.Livetab, textvariable=self.laser2PWR, width=4)
        self.laser2pwr_entry.bind('<Return>',lambda event, i = 1: self.laserChangePower(i))
        self.laser2pwr_label = tk.Label(self.Livetab, text = "%", bd = 0)
        self.laser2switch = tk.Button(self.Livetab, image = self.OffSwitch, bd = 0, command = lambda: self.laserChangeState(1))
        self.laser3_label = tk.Label(self.Livetab, text = "No Laser: @", bd = 0)
        self.laser3pwr_entry = tk.Entry(self.Livetab, textvariable=self.laser3PWR, width=4)
        self.laser3pwr_entry.bind('<Return>',lambda event, i = 2: self.laserChangePower(i))
        self.laser3pwr_label = tk.Label(self.Livetab, text = "%", bd = 0)
        self.laser3switch = tk.Button(self.Livetab, image = self.OffSwitch, bd = 0, command = lambda: self.laserChangeState(2))
        self.laser4_label = tk.Label(self.Livetab, text = "No Laser: @", bd = 0)
        self.laser4pwr_entry = tk.Entry(self.Livetab, textvariable=self.laser4PWR, width=4)
        self.laser4pwr_entry.bind('<Return>',lambda event, i = 3: self.laserChangePower(i))
        self.laser4pwr_label = tk.Label(self.Livetab, text = "%", bd = 0)
        self.laser4switch = tk.Button(self.Livetab, image = self.OffSwitch, bd = 0, command = lambda: self.laserChangeState(3))
        self.allowMultiLasers_check = tk.Checkbutton(self.Livetab, text = "Allow Multiple Lasers" , variable=self.allowMultiLasers, onvalue=1, offvalue=0)
        self.clr1_radiobutton = tk.Radiobutton(self.Livetab, text = 'Channel 1', variable = self.clradjust, value = '1', command=self.clr_channel_BC)
        self.clr2_radiobutton = tk.Radiobutton(self.Livetab, text = 'Channel 2', variable = self.clradjust, value = '2', command=self.clr_channel_BC)
        self.clr3_radiobutton = tk.Radiobutton(self.Livetab, text = 'Channel 3', variable = self.clradjust, value = '3', command=self.clr_channel_BC)

        self.laserlabels.append(self.laser1_label)
        self.laserlabels.append(self.laser2_label)
        self.laserlabels.append(self.laser3_label)
        self.laserlabels.append(self.laser4_label)
        self.laserPWRentrys.append(self.laser1pwr_entry)
        self.laserPWRentrys.append(self.laser2pwr_entry)
        self.laserPWRentrys.append(self.laser3pwr_entry)
        self.laserPWRentrys.append(self.laser4pwr_entry)
        self.laserswitches.append(self.laser1switch)
        self.laserswitches.append(self.laser2switch)
        self.laserswitches.append(self.laser3switch)
        self.laserswitches.append(self.laser4switch)
        #Contol Tab Objects
        self.Config_drop = ttk.Combobox(self.Controltab, textvariable=self.config_files_clicked)
        self.Config_drop['values'] = self.config_files
        self.Config_drop['state'] = 'readonly'
        self.Config_Apply = tk.Button(self.Controltab, text = "Apply", bd = 1, command = self.readConfigFile)
        self.config_label = tk.Label(self.Controltab, text = "Configuration file:", bd = 0)
        self.ScanningGalvo_label = tk.Label(self.Controltab, text = "Scanning:", bd = 0)
        self.ScanningGalvo_check = tk.Checkbutton(self.Controltab, text = "Enable" , variable=self.scanninggalvo, onvalue=1, offvalue=0, command = self.enableGalvo)
        self.ScanningGalvo_Apply = tk.Button(self.Controltab, text = "Apply", state = DISABLED, bd = 1, command = self.scanningGalvoApply)
        self.galvoCanvas = tk.Canvas(self.Controltab,height = 20, width = 20)
        self.ScanningGalvoLED = self.galvoCanvas.create_oval(10, 10, 20, 20)
        self.galvoCanvas.itemconfig(self.ScanningGalvoLED, fill="red")
        self.daqaolines_drop = ttk.Combobox(self.Controltab, textvariable=self.daqaolines_clicked)
        self.daqaolines_drop['values'] = self.daqaolines
        self.daqaolines_drop['state'] = 'readonly'
        self.daqaolines_label = tk.Label(self.Controltab, text = "Outut Port:", bd = 0)
        self.altHardware_check = tk.Checkbutton(self.Controltab, text = "Use alt. hardware:" , variable=self.altHardware, onvalue=1, offvalue=0, command = self.enableAltHardware)
        self.PreloadGalvo_check = tk.Checkbutton(self.Controltab, text = "Preload Voltages:" , variable=self.preloadgalvo, onvalue=1, offvalue=0, command = self.enableProload)
        self.daqdilines_drop = ttk.Combobox(self.Controltab, textvariable=self.daqdilines_clicked)
        self.daqdilines_drop['values'] = self.daqdilines
        self.daqdilines_drop['state'] = 'readonly'
        self.daqdilines_label = tk.Label(self.Controltab, text = "Trigger Port:", bd = 0)
        self.galvominV_label = tk.Label(self.Controltab, text = "Min (V):", bd = 0)
        self.galvominV_entry = tk.Entry(self.Controltab, textvariable=self.galvominV, width=6)
        self.galvomaxV_label = tk.Label(self.Controltab, text = "Max(V):", bd = 0)
        self.galvomaxV_entry = tk.Entry(self.Controltab, textvariable=self.galvomaxV, width=6)
        self.galvooffV_label = tk.Label(self.Controltab, text = "Off (V):", bd = 0)
        self.galvooffV_entry = tk.Entry(self.Controltab, textvariable=self.galvooffV, width=6)
        self.galvov2um_label = tk.Label(self.Controltab, text = "V2um (V):", bd = 0)
        self.galvov2um_entry = tk.Entry(self.Controltab, textvariable=self.galvov2um, width=6)
        self.LaserFilter_label = tk.Label(self.Controltab, text = "Lasers + Filters:", bd = 0)
        self.LaserFilter_check = tk.Checkbutton(self.Controltab, text = "Enable" , variable=self.LaserFilter, onvalue=1, offvalue=0, command = self.enableLaserFilter)
        self.LaserFilter_Apply = tk.Button(self.Controltab, text = "Apply", state = DISABLED, bd = 1, command = self.laserFilter_Apply)
        self.LaserFilterCanvas = tk.Canvas(self.Controltab,height = 20, width = 20)
        self.LaserFilterLED = self.LaserFilterCanvas.create_oval(10, 10, 20, 20)
        self.LaserFilterCanvas.itemconfig(self.LaserFilterLED, fill="red")
        self.LaserFilter_LB = tk.Listbox(self.Controltab, height = 4, width = 60, selectmode = SINGLE)
        self.LaserFilter_add = tk.Button(self.Controltab, text = "Add", state = NORMAL, bd = 1, command = self.addLaser_Filter)
        self.LaserFilter_remove = tk.Button(self.Controltab, text = "Remove", state = NORMAL, bd = 1, command = self.removeLaser_Filter)
        self.FilterWheel_check = tk.Checkbutton(self.Controltab, text = "Connect to Filterwheel" , variable=self.FilterWheelenabled, onvalue=1, offvalue=0)
        self.CameraTrigger_label = tk.Label(self.Controltab, text = "Camera Triggering:", bd = 0)
        self.CameraTrigger_check = tk.Checkbutton(self.Controltab, text = "Enable" , variable=self.CameraTrigger, onvalue=1, offvalue=0, command = self.enableCamera)
        self.CameraTrigger_Apply = tk.Button(self.Controltab, text = "Apply", state = DISABLED, bd = 1)
        self.CameraTriggerCanvas = tk.Canvas(self.Controltab,height = 20, width = 20)
        self.CameraTriggerLED = self.CameraTriggerCanvas.create_oval(10, 10, 20, 20)
        self.CameraTriggerCanvas.itemconfig(self.CameraTriggerLED, fill="red")
        self.CameraTrigger_selection_label = tk.Label(self.Controltab, text = "Camera Trigger Mode:", bd = 0)
        self.CameraTrigger_drop = ttk.Combobox(self.Controltab, textvariable=self.CameraTrigger_clicked)
        self.CameraTrigger_drop['values'] = self.DSKW.Trigger_Options
        self.CameraTrigger_drop['state'] = 'readonly'
        self.OptoSplit_label = tk.Label(self.Controltab, text = "OptoSplit (Triple):", bd = 0)
        self.OptoSplit_check = tk.Checkbutton(self.Controltab, text = "Enable" , variable=self.OptoSplit, onvalue=1, offvalue=0, command = self.enableOptoSplit)
        self.OptoSplit_Apply = tk.Button(self.Controltab, text = "Apply", state = DISABLED, bd = 1, command = self.OptoSplitApply)
        self.OptoSplitCanvas = tk.Canvas(self.Controltab,height = 20, width = 20)
        self.OptoSplitLED = self.OptoSplitCanvas.create_oval(10, 10, 20, 20)
        self.OptoSplitCanvas.itemconfig(self.OptoSplitLED, fill="red")
        self.OptosplitFilter_label = tk.Label(self.Controltab, text = "Open Filter Position:", bd = 0)
        self.OptosplitFilter_entry = tk.Entry(self.Controltab, textvariable=self.openFilterPos, width=6)
        self.Proj_label = tk.Label(self.Controltab, text = "Reconstruction mode:", bd = 0)
        self.Proj_drop = tk.OptionMenu(self.Controltab ,self.Proj_clicked , *self.Proj_options, command = self.projModeSelect)

        self.SaveConfig = tk.Button(self.Controltab, text = "Save Config File", bd = 1, command = self.saveConfigFile)

        #Set Normal/Disable States
        self.allowMultiLasers_check['state'] = DISABLED

        for entry in self.laserPWRentrys:
            entry['state'] = DISABLED

        for switch in self.laserswitches:
            switch['state'] = DISABLED

        self.daqaolines_drop['state'] = DISABLED
        self.PreloadGalvo_check['state'] = DISABLED
        self.altHardware_check['state'] = DISABLED
        self.daqdilines_drop['state'] = DISABLED
        self.galvominV_entry['state'] = DISABLED
        self.galvomaxV_entry['state'] = DISABLED
        self.galvooffV_entry['state'] = DISABLED
        self.galvov2um_entry['state'] = DISABLED

        self.LaserFilter_LB['state'] = DISABLED
        self.LaserFilter_add['state'] = DISABLED
        self.LaserFilter_remove['state'] = DISABLED

        self.CameraTrigger_drop['state'] = DISABLED

        self.OptosplitFilter_entry['state'] = DISABLED

        

        #Place the GUI objects
        #Master
        self.TitleGrapic.place(x= 50, y= 10)
        self.button_live.place(x=120,y=110)
        self.button_Stop_live.place(x=230,y=110)
        self.fps_label.place(x = 190, y = 200)
        self.Comp_drop.place(x = 160, y = 165)
        self.videofeed.place(x = 475, y = 20)
        self.LogoGraphic.place(x = 5, y = 730)
        #Live Tab
        self.tabControl.place(x= 5, y= 230)

        self.scan_range_label.place(x = 5, y = 10)
        self.scan_entry.place(x = 170, y = 10)

        self.no_steps_label.place(x = 5, y = 40)  
        self.steps_entry.place(x = 170, y = 40)

        self.exposure_label.place(x = 5, y = 70)  
        self.exposure_entry.place(x = 170, y = 70)

        self.Deskew_Params_label.place(x = 5, y = 100)

        self.Sheet_angle_label.place(x = 5, y = 120)
        self.Sheet_angle_entry.place(x = 150, y = 120)

        self.Pixel_size_label.place(x=5, y = 140)
        self.Pixel_size_entry.place(x = 150, y = 140)

        self.Lasers_label.place(x = 215,y = 10) 
        self.allowMultiLasers_check.place(x = 300, y = 10)
        self.laser1_label.place(x = 215,y = 40)  
        self.laser1pwr_entry.place(x = 315,y = 40)  
        self.laser1pwr_label.place(x = 350,y = 40)  
        self.laser1switch.place(x = 380, y = 40)
        self.laser2_label.place(x = 215,y = 70)  
        self.laser2pwr_entry.place(x = 315,y = 70)  
        self.laser2pwr_label.place(x = 350,y =70)  
        self.laser2switch.place(x = 380, y = 70)
        self.laser3_label.place(x = 215,y = 100)  
        self.laser3pwr_entry.place(x = 315,y = 100)  
        self.laser3pwr_label.place(x = 350,y = 100)  
        self.laser3switch.place(x = 380, y = 100)
        self.laser4_label.place(x = 215,y = 130)  
        self.laser4pwr_entry.place(x = 315,y = 130)  
        self.laser4pwr_label.place(x = 350,y = 130)  
        self.laser4switch.place(x = 380, y = 130)

        self.minslider.place(x = 5, y = 170)
        self.maxslider.place(x = 150, y = 170)
        self.Rotateslider.place(x = 300, y = 170)

        self.clr1_radiobutton.place(x = 5, y = 390)
        self.clr2_radiobutton.place(x = 80, y = 390)
        self.clr3_radiobutton.place(x = 155, y = 390)
        
        #Control Tab
        self.config_label.place(x = 5, y = 10)
        self.Config_drop.place(x = 150, y= 10)
        self.Config_Apply.place(x = 315, y= 10 )

        self.ScanningGalvo_label.place(x = 5, y= 40)
        self.ScanningGalvo_check.place(x = 150, y= 40)
        self.ScanningGalvo_Apply.place(x = 300, y= 40 )
        self.galvoCanvas.place(x = 350, y= 40 )

        self.daqaolines_label.place(x = 5, y= 70)
        self.daqaolines_drop.place(x = 80, y= 70)
        self.altHardware_check.place(x = 300, y= 70)

        self.PreloadGalvo_check.place(x = 5, y = 100)
        self.daqdilines_label.place(x = 130, y= 100)
        self.daqdilines_drop.place(x = 200, y= 100)

        self.galvominV_label.place(x = 10, y = 130)
        self.galvominV_entry.place(x = 60, y = 130)
        self.galvomaxV_label.place(x = 110, y = 130)
        self.galvomaxV_entry.place(x = 160, y = 130)
        self.galvooffV_label.place(x = 210, y = 130)
        self.galvooffV_entry.place(x = 260, y = 130)
        self.galvov2um_label.place(x = 310, y = 130)
        self.galvov2um_entry.place(x = 360, y = 130)

        self.LaserFilter_label.place(x = 5, y= 160)
        self.LaserFilter_check.place(x = 150, y= 160)
        self.LaserFilter_Apply.place(x = 300, y= 160 )
        self.LaserFilterCanvas.place(x = 350, y= 160 )
        
        self.LaserFilter_LB.place(x = 5, y= 190)
        self.LaserFilter_add.place(x = 375, y= 190)

        self.LaserFilter_remove.place(x = 375, y= 210)

        self.FilterWheel_check.place(x = 10, y = 260)

        self.CameraTrigger_label.place(x = 10, y= 290)
        self.CameraTrigger_check.place(x = 150, y= 290)
        self.CameraTrigger_Apply.place(x = 300, y= 290 )
        self.CameraTriggerCanvas.place(x = 350, y= 290 )

        self.CameraTrigger_selection_label.place(x = 10, y= 330)
        self.CameraTrigger_drop.place(x = 150, y= 330)

        self.OptoSplit_label.place(x = 10, y= 370)
        self.OptoSplit_check.place(x = 150, y= 370)
        self.OptoSplit_Apply.place(x = 300, y= 370 )
        self.OptoSplitCanvas.place(x = 350, y= 370 )

        self.OptosplitFilter_label.place(x = 10, y= 400)
        self.OptosplitFilter_entry.place(x = 150, y= 400)

        self.Proj_label.place(x = 10, y = 430)
        self.Proj_drop.place(x = 175, y = 430)
        self.SaveConfig.place(x = 310, y = 430)

        #Set Initial values for GUI Objects
        self.maxslider.set(4000)
        self.minslider.set(10)
        self.scn_range.set(self.DSKW.get_scanRange())
        self.nostep.set(self.DSKW.get_depth())
        self.exposure.set(1)
        self.Rotateslider.set(0)
        self.openFilterPos.set(4)
        self.sheetangle.set(self.DSKW.getSheetAngle())
        self.pixelsize.set(self.DSKW.getPixelPitch())

        #Set fonts 
        self.fps_label.config(font=('Helvatical bold',15))
        self.Lasers_label.config(font=('Helvatical bold',12))
        self.maxslider.config(font=('Helvatical bold',10))
        self.minslider.config(font=('Helvatical bold',10))
        self.Rotateslider.config(font=('Helvatical bold',10))
        self.scan_entry.config(font=('Helvatical bold',12))
        self.steps_entry.config(font=('Helvatical bold',12))
        self.exposure_entry.config(font=('Helvatical bold',12))
        self.scan_range_label.config(font=('Helvatical bold',12))
        self.no_steps_label.config(font=('Helvatical bold',12))
        self.exposure_label.config(font=('Helvatical bold',12))
        self.Comp_drop.config(font=('Helvatical bold',10))
        self.Proj_drop.config(font=('Helvatical bold',10))
        self.config_label.config(font=('Helvatical bold',12))
        self.Config_drop.config(font=('Helvatical bold',8))
        self.Config_Apply.config(font=('Helvatical bold',10))
        self.ScanningGalvo_label.config(font=('Helvatical bold',12))
        self.ScanningGalvo_check.config(font=('Helvatical bold',10))
        self.ScanningGalvo_Apply.config(font=('Helvatical bold',10))
        self.daqaolines_drop.config(font=('Helvatical bold',8))
        self.daqaolines_label.config(font=('Helvatical bold',10))
        self.LaserFilter_label.config(font=('Helvatical bold',12))
        self.LaserFilter_check.config(font=('Helvatical bold',10))
        self.LaserFilter_Apply.config(font=('Helvatical bold',10))
        self.CameraTrigger_label.config(font=('Helvatical bold',12))
        self.CameraTrigger_selection_label.config(font=('Helvatical bold',10))
        self.CameraTrigger_drop.config(font=('Helvatical bold',8))
        self.CameraTrigger_check.config(font=('Helvatical bold',10))
        self.CameraTrigger_Apply.config(font=('Helvatical bold',10))
        self.OptoSplit_label.config(font=('Helvatical bold',12))
        self.OptoSplit_check.config(font=('Helvatical bold',10))
        self.OptoSplit_Apply.config(font=('Helvatical bold',10))
        self.Proj_label.config(font=('Helvatical bold',12))
        self.SaveConfig.config(font=('Helvatical bold',12))

    def find_daqaolines(self):
        for device in self.local_system.devices:
            for line in device.ao_physical_chans.channel_names:
                self.daqaolines.append(line)

    def find_daqdolines(self):
        for device in self.local_system.devices:
            for line in device.do_lines.channel_names:
                self.daqdolines.append(line)
    
    def find_daqdilines(self):
        for device in self.local_system.devices:
            for line in device.terminals:
                self.daqdilines.append(line)

    def compModeSelect(self,value):
        if value ==  "Global Update Mode":
            self.DSKW.setDisplayMode(True)
        else:
            self.DSKW.setDisplayMode(False)

    def projModeSelect(self,value):
        if value ==  "MIP":
            self.DSKW.setSingleSlice(False)
        else:
            self.DSKW.setSingleSlice(True)

    def laserChangeState(self,i):
        laserNos = list(range(4))
        laserNos.remove(i) 
        if not self.laserson[i]:
            if self.FilterWheelConnected:
                if self.allowMultiLasers.get():
                    self.FilterWheel.move_filter(self.openFilterPos.get())
                else:
                    self.FilterWheel.move_filter(self.connectedLasers[i].get_filterPos())
            self.connectedLasers[i].set_power(int(self.laserPWRentrys[i].get()))
            time.sleep(50/1000) #Wait for filter to move Cairn OptoSpin takes ~50ms
            self.laserson[i] = 1
            self.laserswitches[i].configure(image = self.OnSwitch)
            if not self.allowMultiLasers.get():
                for no in laserNos:
                    self.laserson[no] = 0
                    self.laserswitches[no].configure(image = self.OffSwitch)
                    if no < len(self.connectedLasers):
                        self.connectedLasers[no].change_state(False)
            self.connectedLasers[i].change_state(True)
        else:
            self.laserson[i] = 0
            self.laserswitches[i].configure(image = self.OffSwitch)
            self.connectedLasers[i].change_state(False)

    def laserChangePower(self,i):
        self.connectedLasers[i].set_power(int(self.laserPWRentrys[i].get()))
        self.connectedLasers[i].update()

    def readConfigFile(self):
        if not self.config_files_clicked.get() == 'none':
            #Clear all current hardware settings
            self.laserNames = []
            self.laserPort = []
            self.laserfilterPos = []
            self.laserfilterName = []
            self.laserTrigMethods = []
            self.lasermaxVolts = []

            self.LaserFilter_LB.delete(0,self.LaserFilter_LB.size())

            lines = []
            with open(self.config_files_clicked.get()) as f:
                lines = f.readlines()
        
            i = 0
            if 'Scanning' in lines[i]:
                if 'True' in lines[i]:
                    i =+ 1
                    self.scanninggalvo.set(1)
                    self.enableGalvo()
                    if 'Alt. Hardware' in lines[i]:
                        self.altHardware.set(1)
                        self.enableAltHardware()
                    else:
                        info = lines[i].split(':') #OutPort:TrigBool:TrigPort:MinV:MaxV:OffV:V2um
                        self.daqaolines_clicked.set(info[0])
                        if 'True' in info[1]:
                            self.preloadgalvo.set(1)
                            self.enableProload()
                            self.daqdilines_clicked.set(info[2])
                        self.galvominV.set(float(info[3]))
                        self.galvomaxV.set(float(info[4]))
                        self.galvooffV.set(float(info[5]))
                        self.galvov2um.set(float(info[6].replace('\n','')))
                    self.scanningGalvoApply()
            i += 1          
            if 'Laser' in lines[i]:
                if 'True' in lines[i]:
                    i += 1
                    self.LaserFilter.set(1)
                    self.enableLaserFilter()
                    while 'end' not in lines[i]:
                        info = lines[i].split(':') #Trig method:Laser Name:Laser Port:Max Volts:Filter Name:Filter Position
                        self.laserTrigMethods.append(int(info[0]))
                        self.laserNames.append(info[1])
                        self.laserPort.append(info[2])
                        self.lasermaxVolts.append(float(info[3]))
                        self.laserfilterName.append(info[4])
                        self.laserfilterPos.append(int(info[5].replace('\n','')))
                        string = info[1] + " @ " + info[2] + "  -->  " + info[4]+ " @ Position " + str(int(info[5].replace('\n','')))
                        self.LaserFilter_LB.insert(i,string)
                        i += 1
                    self.laserFilter_Apply()
            i += 1          
            if 'Camera' in lines[i]:
                if 'True' in lines[i]:
                    i += 1
                    self.CameraTrigger.Set(1)
                    self.enableCamera()
                    info = lines[i].split(':')
                    #self.cameraPort = info[1]
                    self.CameraTrigger_clicked.set(info[0])

            i += 1 
            if 'OptoSpilt' in lines[i]:
                 if 'True' in lines[i]:
                    i += 1
                    self.OptoSplit.set(1)
                    self.enableOptoSplit()
                    info = lines[i]
                    self.OptosplitFilter_entry.set(int(info.replace('\n','')))
                    self.OptoSplitApply()

            i += 1 
            if 'Reconstruction' in lines[i]:
                if 'MIP' in lines[i]:
                    self.Proj_clicked.set('MIP')
                    self.projModeSelect('MIP')
                else:
                    self.Proj_clicked.set('Single Slice')
                    self.projModeSelect('Single Slice')

            

    def saveConfigFile(self):
        USER_INP = simpledialog.askstring(title="Config Save Name",prompt="What would you like to save this configuration as?:")
        if not USER_INP == None:
            with open(os.path.join(os.getcwd(),USER_INP+'.txt'), 'w') as f:
                if self.scanninggalvo.get():
                    f.write('Scanning: True')
                    f.write('\n')
                    if self.altHardware.get():
                        f.write('Alt. Hardware')
                        f.write('\n')
                    else:
                        if self.preloadgalvo.get():
                            stringTowrite = self.daqaolines_clicked.get() + ':' + 'True' + ':' + self.daqdilines_clicked.get() + ':' + str(self.galvominV.get()) + ':' + str(self.galvomaxV.get()) + ':' + str(self.galvooffV.get()) + ':' + str(self.galvov2um.get())
                        else:
                            stringTowrite = self.daqaolines_clicked.get() + ':' + 'False' + ':' + 'None' + ':' + str(self.galvominV.get()) + ':' + str(self.galvomaxV.get()) + ':' + str(self.galvooffV.get()) + ':' + str(self.galvov2um.get())
                        f.write(stringTowrite)
                        f.write('\n')
                else:
                    f.write('Scanning: False')
                    f.write('\n')
                    
                if self.LaserFilter.get():
                    f.write('Laser: True')
                    f.write('\n')
                    for i in range(len(self.laserPort)):
                        stringTowrite = str(self.laserTrigMethods[i]) + ':' + self.laserNames[i] + ':' + self.laserPort[i] + ':' + str(self.lasermaxVolts[i]) + ':' + self.laserfilterName[i] + ':' + str(self.laserfilterPos[i])
                        f.write(stringTowrite)
                        f.write('\n')
                    f.write('end')
                    f.write('\n')
                else:
                    f.write('Lasers: False')
                    f.write('\n')

                if self.CameraTrigger.get():
                    f.write('Camera: True')
                    f.write('\n')
                    f.write('self.CameraTrigger_clicked.get()')
                    f.write('\n')
                else:
                    f.write('Camera: False')
                    f.write('\n')

                if self.OptoSplit.get():
                    f.write('OptoSplit: True')
                    f.write('\n')
                    f.write(str(self.OptosplitFilter_entry.get()))
                else:
                    f.write('OptoSplit: False')
                    f.write('\n')

                if 'MIP' in self.Proj_clicked.get():
                    f.write('Reconstruction Mode: MIP')
                    f.write('\n')                   
                else:
                    f.write('Reconstruction Mode: Single Slice')
                    f.write('\n')

    def enableGalvo(self):
        if self.scanninggalvo.get():
            self.daqaolines_drop['state'] = NORMAL
            self.PreloadGalvo_check['state'] = NORMAL
            self.altHardware_check['state'] = NORMAL
            self.galvominV_entry['state'] = NORMAL
            self.galvomaxV_entry['state'] = NORMAL
            self.galvooffV_entry['state'] = NORMAL
            self.galvov2um_entry['state'] = NORMAL
            self.ScanningGalvo_Apply['state'] = NORMAL
            self.galvoCanvas.itemconfig(self.ScanningGalvoLED, fill="orange")
        else:
            self.daqaolines_drop['state'] = DISABLED
            self.PreloadGalvo_check['state'] = DISABLED
            self.altHardware_check['state'] = DISABLED
            self.daqdilines_drop['state'] = DISABLED
            self.galvominV_entry['state'] = DISABLED
            self.galvomaxV_entry['state'] = DISABLED
            self.galvooffV_entry['state'] = DISABLED
            self.galvov2um_entry['state'] = DISABLED
            self.ScanningGalvo_Apply['state'] = DISABLED
            self.galvoCanvas.itemconfig(self.ScanningGalvoLED, fill="red")
            self.DSKW.disableGalvo()
            self.DSKW.disableAltHard()

    def enableAltHardware(self):
        if self.altHardware.get():
            self.daqaolines_drop['state'] = DISABLED
            self.PreloadGalvo_check['state'] = DISABLED
            self.daqdilines_drop['state'] = DISABLED
            self.galvominV_entry['state'] = DISABLED
            self.galvomaxV_entry['state'] = DISABLED
            self.galvooffV_entry['state'] = DISABLED
            self.galvov2um_entry['state'] = DISABLED
            self.galvoCanvas.itemconfig(self.ScanningGalvoLED, fill="orange")
        else:
            self.daqaolines_drop['state'] = NORMAL
            self.PreloadGalvo_check['state'] = NORMAL
            self.galvominV_entry['state'] = NORMAL
            self.galvomaxV_entry['state'] = NORMAL
            self.galvooffV_entry['state'] = NORMAL
            self.galvov2um_entry['state'] = NORMAL
            self.galvoCanvas.itemconfig(self.ScanningGalvoLED, fill="orange")
            self.DSKW.disableGalvo()
    
    def enableProload(self):
        if self.preloadgalvo.get():
            self.daqdilines_drop['state'] = NORMAL
        else:
            self.daqdilines_drop['state'] = DISABLED
        self.galvoCanvas.itemconfig(self.ScanningGalvoLED, fill="orange")

        
    def enableLaserFilter(self):
        if self.LaserFilter.get():
            self.LaserFilter_LB['state'] = NORMAL
            self.LaserFilter_add['state'] = NORMAL
            self.LaserFilter_remove['state'] = NORMAL
            self.LaserFilter_Apply['state'] = NORMAL
            self.LaserFilterCanvas.itemconfig(self.LaserFilterLED, fill="orange")
        else:
            self.LaserFilter_LB['state'] = DISABLED
            self.LaserFilter_add['state'] = DISABLED
            self.LaserFilter_remove['state'] = DISABLED
            self.LaserFilter_Apply['state'] = DISABLED
            self.LaserFilterCanvas.itemconfig(self.LaserFilterLED, fill="red")
            [label.configure(text = 'No Laser @') for label in self.laserlabels]
            [entry.configure(state = DISABLED) for entry in self.laserPWRentrys]
            [switch.configure(state = DISABLED) for switch in self.laserswitches]

            self.closeAllConnectedLasers()

    def enableCamera(self):
        if self.CameraTrigger.get():
            self.CameraTrigger_drop['state'] = NORMAL
            self.CameraTrigger_Apply['state'] = NORMAL
            self.CameraTriggerCanvas.itemconfig(self.CameraTriggerLED, fill="orange")
        else:
            self.CameraTrigger_drop['state'] = DISABLED
            self.CameraTrigger_Apply['state'] = DISABLED
            self.CameraTriggerCanvas.itemconfig(self.CameraTriggerLED, fill="red")

    def enableOptoSplit(self):
        if self.OptoSplit.get():
            self.OptosplitFilter_entry['state'] = NORMAL
            self.OptoSplit_Apply['state'] = NORMAL
            self.OptoSplitCanvas.itemconfig(self.CameraTriggerLED, fill="orange")
        else:
            self.OptosplitFilter_entry['state'] = DISABLED
            self.OptoSplit_Apply['state'] = DISABLED
            self.allowMultiLasers_check['state'] = DISABLED
            self.OptoSplitCanvas.itemconfig(self.CameraTriggerLED, fill="red")
        
    def closeAllConnectedLasers(self):
        for laser in self.connectedLasers: #Empty Connected laser list
            laser.exit()
        self.connectedLasers = []

    def scanningGalvoApply(self):
        if not self.altHardware.get():
            port = self.daqaolines_clicked.get()
            max = self.galvomaxV.get()
            min = self.galvominV.get()      
            off = self.galvooffV.get()
            v2um = self.galvov2um.get()

            self.DSKW.set_galvoParams(port,max,min,off,v2um)
            
            

            if self.preloadgalvo.get():
                self.DSKW.enablePreloadGalvo()
                self.DSKW.setGalvoTriggerPort(self.daqdilines_clicked.get())
            else:
                self.DSKW.disablePrelodGalvo()
        else:
            print('Using alternative hardware')
            self.DSKW.enableAltHard()

        self.DSKW.enableGalvo()
        self.galvoCanvas.itemconfig(self.ScanningGalvoLED, fill="green")

    def laserFilter_Apply(self):
        [label.configure(text = 'No Laser @') for label in self.laserlabels]
        [entry.configure(state = DISABLED) for entry in self.laserPWRentrys]
        [switch.configure(state = DISABLED) for switch in self.laserswitches]

        if self.FilterWheelConnected: #Close Filterwheel if connected 
            self.FilterWheel.exit()
            self.FilterWheelConnected = False

        self.closeAllConnectedLasers()

        if self.FilterWheelenabled.get():
            self.FilterWheel = MotrisedFilterWheel()
            self.FilterWheelConnected = True

        self.LaserFilterCanvas.itemconfig(self.LaserFilterLED, fill="green")
        for i in range(self.LaserFilter_LB.size()):   
            self.laserlabels[i].configure(text = self.laserNames[i] + ' @')
            
            self.laserswitches[i].configure(state = NORMAL)
            if self.laserTrigMethods[i] == 1:
                laser = Lasers('TTL')
            else:
                self.laserPWRentrys[i].configure(state = NORMAL)
                laser = Lasers('Voltage')
            laser.set_maxVoltage(self.lasermaxVolts[i])
            laser.set_filterPos(self.laserfilterPos[i])
            laser.connect(self.laserPort[i])
            self.connectedLasers.append(laser)
 
    def addLaser_Filter(self):
        window = LaserFilterWindow(self)
        window.grab_set()

    def removeLaser_Filter(self):
        if self.LaserFilter_LB.size() > 0: #Check that there are lasers in the box
            indx = self.LaserFilter_LB.curselection()
            if not len(indx) == 0: #Check that a laser is selected
                self.LaserFilter_LB.delete(indx)
                self.laserNames.pop(int(indx[0]))
                self.laserPort.pop(int(indx[0]))
                self.laserfilterPos.pop(int(indx[0]))
                self.laserTrigMethods.pop(int(indx[0]))
                self.lasermaxVolts.pop(int(indx[0]))
                self.LaserFilterCanvas.itemconfig(self.LaserFilterLED, fill="orange")

    def OptoSplitApply(self):
        self.allowMultiLasers_check['state'] = NORMAL
        self.OptoSplitCanvas.itemconfig(self.CameraTriggerLED, fill="green")

    def start_live(self):
        self.stopq.value = 0
        shearFactor = self.DSKW.get_shearFactor()
        newshearFactor = shearFactor*((90-int(self.Rotateslider.get()))/90)
        self.rotateq.value = newshearFactor
        self.isLive = True
        if self.allowMultiLasers.get():
            self.DSKW.setOptoSplit(True)
        else:
            self.DSKW.setOptoSplit(False)
        self.button_Stop_live['state'] = NORMAL
        self.button_live['state'] = DISABLED
        self.steps_entry['state'] = DISABLED
        self.scan_entry['state'] = DISABLED
        self.exposure_entry['state'] = DISABLED
        self.Sheet_angle_entry['state'] = DISABLED
        self.Pixel_size_entry['state'] = DISABLED
        self.allowMultiLasers_check['state'] = DISABLED
        if not self.DSKW.getSingleSlice():
            self.Rotateslider['state'] = NORMAL
        self.DSKW.setScanRange(self.scn_range.get())
        self.DSKW.setDepth(self.nostep.get())
        self.DSKW.setExposure(self.exposure.get())
        self.DSKW.setSheetAngle(self.sheetangle.get())
        self.DSKW.setPixelPitch(self.pixelsize.get())

        self.DSKW.GPU_MultiProcess()
        fps_thread = threading.Thread(target= self.plot)
        fps_thread.start()

    def stop_live(self):
        self.isLive = False
        self.stopq.value = 1
        self.button_Stop_live['state'] = DISABLED
        self.steps_entry['state'] = NORMAL
        self.scan_entry['state'] = NORMAL
        self.exposure_entry['state'] = NORMAL
        self.Sheet_angle_entry['state'] = NORMAL
        self.Pixel_size_entry['state'] = NORMAL
        self.button_live['state'] = NORMAL
        self.allowMultiLasers_check['state'] = NORMAL
        self.Rotateslider.set(0)
        self.Rotateslider['state'] = DISABLED

    def plot(self):
        start = time.perf_counter_ns()
        if not self.DSKW.getOptoSplit(): #Only one colour at a time
            while True: 
                
                if not self.dskwImgq.empty():
                    image_array = self.dskwImgq.get() # empty data from reconstruction pool
                    if isinstance(image_array, str):
                        break
                    else:
                        vmin = self.clr1min
                        vmax = self.clr1max
                        image_array [image_array  < vmin] = 0
                        image_array [image_array  > vmax] = vmax
                        image_array  = ((image_array/vmax)*255).astype("uint8")
                        # run the update function 
                        img =  ImageTk.PhotoImage(image=Image.fromarray(image_array)) # convert numpy array to tikner object 
                        
                        
                        self.videofeed.configure(image=img) # update the GUI element
                        self.videofeed.image = img
                        finish = time.perf_counter_ns()

                        plottime = (finish-start)/1E6
                        
                        
                            
            
                        fps = 1E3/plottime
                        self.fps_label['text'] = f'FPS: {"{:.1f}".format(fps)}'
                        start = time.perf_counter_ns()
        else:
            image_array = np.zeros((self.DSKW.new_height,self.DSKW.width,3))
            while True: 
                if not self.dskwImgq.empty() and not self.dskwImgq2.empty() and not self.dskwImgq3.empty():
                    image_array1 = self.dskwImgq.get() 
                    image_array2 = self.dskwImgq2.get() 
                    image_array3 = self.dskwImgq3.get() 
                    if isinstance(image_array1, str) or isinstance(image_array2, str) or isinstance(image_array2, str):
                        break
                    else:
                        image_array1 [image_array1  < self.clr1min] = 0
                        image_array1  = (image_array1/self.clr1max)*255
                        image_array2 [image_array2  < self.clr2min] = 0
                        image_array2  = (image_array2/self.clr2max)*255
                        image_array3 [image_array3  < self.clr3min] = 0
                        image_array3  = (image_array3/self.clr3max)*255

                        image_array[:,:,0] = image_array1
                        image_array[:,:,1] = image_array2
                        image_array[:,:,2] = image_array3

                        image_array = image_array.astype(np.uint8)
                        # run the update function 
                        print('here')
                        img =  ImageTk.PhotoImage(image=Image.fromarray(image_array, mode = 'RGB')) # convert numpy array to tikner object 
                        
                        self.videofeed.configure(image=img) # update the GUI element
                        self.videofeed.image = img
                        finish = time.perf_counter_ns()
            
                        fps = 1E9/(finish-start)
                        self.fps_label['text'] = f'FPS: {"{:.1f}".format(fps)}'
                        start = time.perf_counter_ns()
        img =  ImageTk.PhotoImage(image=Image.fromarray(np.zeros((self.DSKW.new_height,self.DSKW.width)))) # convert numpy array to tikner object 
        self.videofeed.configure(image=img) # update the GUI element
        self.videofeed.image = img
        self.fps_label['text'] = 'FPS: N/A'

    def clr_channel_BC(self):
        if self.clradjust.get() == '1':
            self.minslider.set(self.clr1min)
            self.maxslider.set(self.clr1max)
        elif self.clradjust.get() == '2':
            self.minslider.set(self.clr2min)
            self.maxslider.set(self.clr2max)
        else:
            self.minslider.set(self.clr3min)
            self.maxslider.set(self.clr3max)

    def min_scale(self,value):
        if self.clradjust.get() == '1':
            self.clr1min = int(value)
        elif self.clradjust.get() == '2':
            self.clr2min = int(value)
        else:
            self.clr3min = int(value)
    
    def max_scale(self,value):
        if self.clradjust.get() == '1':
            self.clr1max = int(value)
        elif self.clradjust.get() == '2':
            self.clr2max = int(value)
        else:
            self.clr3max = int(value)

    def rotate_scale(self,value):
        shearFactor = self.DSKW.get_shearFactor()
        newshearFactor = shearFactor*((90-int(value))/90)
        self.rotateq.value = newshearFactor

if __name__ == '__main__':
    root = tk.Tk()
    my_gui = deskewApp(root)
    root.mainloop()
    my_gui.closeAllConnectedLasers()

