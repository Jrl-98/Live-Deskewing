import nidaqmx
import numpy as np
import time

class ScanGalvo:
    def __init__(self,portName):
        self.port = nidaqmx.Task()
        self.portName = portName
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
        self.connected = 1 

    def initGalvoPos(self):    
        self.port.write(self.waveform[0])

    def nextPos(self):    
        self.port.write(self.waveform[self.pos])
        if self.pos == (self.steps*2)-1:
            self.pos = 0
        else:
            self.pos += 1
            
    def exit(self):
        self.port.close()

# if __name__ == '__main__':
#     g = ScanGalvo('ScanLaser/ao1')
#     g.set_maxV(2)
#     g.set_minV(-2)
#     g.set_offV(0)
#     g.set_v2um(0.0165)
#     g.set_scanrange(100)
#     g.set_steps(50)
#     g.connect()
#     g.createWaveform()
#     g.initGalvoPos()
#     for _ in range(500):
#         g.nextPos()
#         time.sleep(10/1000)

#     g.exit()

