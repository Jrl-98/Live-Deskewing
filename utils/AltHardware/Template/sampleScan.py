class sampleScan:
    def __init__(self):
        self.stepsize = 0 
        self.scanrange = 0
        self.steps = 0

    def set_scanrange(self,scanrange):
        self.scanrange = scanrange # in um

    def set_steps(self,steps):
        self.steps = steps
        self.stepsize = (self.scanrange/steps)*10

    def createWaveform(self):
        print('Create Waveform here')    

    def connect(self):
        print('Connect to your hardware here')   

    def initPos(self):   
        print('Move to starting position here')    

    def nextPos(self):    
        print('Move to next scan location here')   

    def exit(self):
        print('Disconnect from hardware here')   

