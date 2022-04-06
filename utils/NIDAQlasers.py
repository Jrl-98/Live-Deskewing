import nidaqmx

class Lasers:
    def __init__(self,type):
        self.port = nidaqmx.Task()
        self.type = type
        self.connected = 0 
        self.power = 0 #Percentage power
        self.max_voltage = 0

    def set_power(self,pwr):
        self.power = pwr

    def set_maxVoltage(self,volts):
         self.max_voltage = volts

    def connect(self,portName):
        if self.type == 'TTL':
            self.port.do_channels.add_do_chan(portName)
            self.connected = 1 
        elif self.type == 'Voltage':
            self.port.ao_channels.add_ao_voltage_chan(portName,'mychannel',0,5)
            self.connected = 1 

    def change_state(self, state):
        if state:
            if self.type == 'TTL':
                self.port.write(True)
            elif self.type == 'Voltage':
                volts = self.max_voltage * (self.power/100)
                self.port.write(volts)
        else:
            if self.type == 'TTL':
                self.port.write(False)
            elif self.type == 'Voltage':
                self.port.write(0)

    def update(self):
        if self.type == 'Voltage':
            volts = self.max_voltage * (self.power/100)
            self.port.write(volts)
            
    def exit(self):
        self.port.close()

#'ScanLaser/port1/line0'