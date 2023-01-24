import nidaqmx 
import numpy as np 

class sampleScan:
    def __init__(self,portName,extTrig=False,extTrigPort=''):
        self.port = nidaqmx.Task()
        self.portName = portName
        self.extTrigPort = extTrigPort #'/ScanLaser/PFI11'
        self.extTrig = extTrig
        self.minV = 0
        self.maxV = 0
        self.offV = 0 
        self.v2um = 0
        self.waveform = []
        self.pos = 0
        self.scanrange = 0
        self.steps = 0
        self.connected = 0

    def set_minV(self,volts):
        self.minV = volts
    
    def set_maxV(self,volts):
        self.maxV = volts

    def set_offV(self,volts):
        self.offV = volts

    def set_v2um(self,volts):
        self.v2um = volts

    def set_scanrange(self,scanrange):
        self.scanrange = scanrange

    def set_steps(self,steps):
        self.steps = steps

    def createWaveform(self):
        self.pos = 0
        voltage_range = self.scanrange*self.v2um
        startV = self.offV - voltage_range/2
        stopV = self.offV + voltage_range/2
        ramp = np.linspace(startV,stopV,self.steps)
        self.waveform = np.concatenate((ramp,np.flip(ramp)))      

    def connect(self):
        self.port.ao_channels.add_ao_voltage_chan(self.portName,'mychannel',self.minV,self.maxV)
        if self.extTrig:
            self.port.timing.cfg_samp_clk_timing(1000,self.extTrigPort,active_edge = nidaqmx.constants.Edge.RISING, sample_mode = nidaqmx.constants.AcquisitionType.CONTINUOUS, samps_per_chan = 50)
            self.port.out_stream.offset = 0
            self.port.out_stream.regen_mode = nidaqmx.constants.RegenerationMode.ALLOW_REGENERATION
        self.connected = 1 

    def preloadGalvo(self):
        self.port.write(self.waveform)
        self.port.start()

    def initPos(self):    
        #self.port.write(self.waveform[0])
        self.pos = 0

    def nextPos(self):    
        self.port.write(self.waveform[self.pos])
        if self.pos == (self.steps*2)-1:
             self.pos = 0
        else:
             self.pos += 1
            
    def exit(self):
        if self.extTrig:
            self.port.stop()
        self.port.close()
