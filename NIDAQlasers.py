import nidaqmx

class Lasers:
    def __init__(self,type):
        self.port = nidaqmx.Task()
        self.type = type
        self.connected = 0 
        self.power = 0 #Percentage power
        self.max_voltage = 0
        self.on = False
        self.filterPos = 0

    def set_power(self,pwr):
        self.power = pwr

    def set_maxVoltage(self,volts):
        self.max_voltage = volts

    def set_filterPos(self,Pos):
        self.filterPos = Pos

    def get_filterPos(self):
        return self.filterPos

    def connect(self,portName):
        if self.type == 'TTL':
            self.port.do_channels.add_do_chan(portName)
            self.connected = 1 
        elif self.type == 'Voltage':
            self.port.ao_channels.add_ao_voltage_chan(portName,'mychannel',0,5)
            self.connected = 1 

    def change_state(self, state):
        if state:
            self.on = True
            if self.type == 'TTL':
                self.port.write(True)
            elif self.type == 'Voltage':
                volts = self.max_voltage * (self.power/100)
                self.port.write(volts)
        else:
            self.on = False
            if self.type == 'TTL':
                self.port.write(False)
            elif self.type == 'Voltage':
                self.port.write(0)

    def update(self):
        if self.on:
            if self.type == 'Voltage':
                volts = self.max_voltage * (self.power/100)
                self.port.write(volts)
            
    def exit(self):
        self.port.close()