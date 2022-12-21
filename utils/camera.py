import nidaqmx

class camera:
    def __init__(self,portName):
        self.port = nidaqmx.Task()
        self.portName = portName
        self.connected = 0

    def connect(self):
        self.port.do_channels.add_do_chan(self.portName)
        self.connected = 1

    def snap(self):
        self.port.write(True)
        self.port.write(False)

    def exit(self):
        self.port.close()