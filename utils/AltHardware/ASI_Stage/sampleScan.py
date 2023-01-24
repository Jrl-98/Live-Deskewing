import serial
import time

class sampleScan:
    def __init__(self):
        self.asi_stage_serialport = 'COM3'
        self.asi_stage_baudrate = 9600
        self.currentPosNo = 0
        self.stepsize = 0 # 10 = 1um for asi commands
        self.scanrange = 0
        self.steps = 0
        self.settleTime = 200 #Settle time for stage in ms

    def set_scanrange(self,scanrange):
        self.scanrange = scanrange # in um

    def set_steps(self,steps):
        self.steps = steps
        self.stepsize = (self.scanrange/steps)*10

    def createWaveform(self):
        print('Doing nothing here')    

    def connect(self):
        print('Connecting to ASI Stage Control')
        self.ASI_StageSer = serial.Serial(self.asi_stage_serialport,self.asi_stage_baudrate)
        print('stage baudrate is ', self.asi_stage_baudrate)
        self.ASI_StageSer.bytesize = serial.EIGHTBITS # bits per byte
        self.ASI_StageSer.parity = serial.PARITY_NONE
        self.ASI_StageSer.stopbits = serial.STOPBITS_ONE
        self.ASI_StageSer.timeout = 5
        self.ASI_StageSer.xonxoff = False #disable software flow conrol
        self.ASI_StageSer.rtscts = False #disable hardware (RTS/CTS) flow control
        self.ASI_StageSer.dsrdtr =  False #disable hardware (DSR/DTR) flow control
        self.ASI_StageSer.writeTimeout = 0 #timeout for write

        if not self.ASI_StageSer.isOpen():
            try:
                self.ASI_StageSer.open()
            except Exception as e:
                print('Exception: Opening serial port: '+ str(e))

    def initPos(self):    
        self.pos = -1

    def nextPos(self):    
        ASI_ZCommand = 'movrel x=' + str(self.stepsize) +'\r\n'
        self.ASI_StageSer.write(str.encode(ASI_ZCommand)) 
        time.sleep(self.settleTime/1000)
        self.pos += 1
        if self.pos == self.steps:
            self.pos = 0 
            self.stepsize = -1 * self.stepsize

            
    def exit(self):
        try:
            ASI_ZCommand = 'TTL x=0' +'\r\n'
            self.ASI_StageSer.write(str.encode(ASI_ZCommand)) 
            self.ASI_StageSer.close()
        except Exception as e:
            print('Exception: Opening serial port: '+ str(e))
