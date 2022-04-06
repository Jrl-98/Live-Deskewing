import nidaqmx

class Camera:
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

if __name__ == '__main__':
    c = Camera('FilterCam/port1/line0')
    c.connect()
    for _ in range(500):
        c.snap()
    c.exit()
