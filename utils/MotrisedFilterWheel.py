import nidaqmx

class MotrisedFilterWheel:
    def __init__(self):
        self.binaryPos = [False,False,False,False]

        self.port7 = nidaqmx.Task()
        self.port0 = nidaqmx.Task()
        self.port1 = nidaqmx.Task()
        self.port2 = nidaqmx.Task()

        self.port7.do_channels.add_do_chan('FilterCam/port2/line7')
        self.port0.do_channels.add_do_chan('FilterCam/port2/line0')
        self.port1.do_channels.add_do_chan('FilterCam/port2/line1')
        self.port2.do_channels.add_do_chan('FilterCam/port2/line2')

        print('Optospin Connected...')

    def set_position(self):
        self.binaryPos = [False,False,False,False]
        self.pos_to_binary(self.pos,0)
    
    def pos_to_binary(self,pos,depth):
        if pos >= 1:
            self.pos_to_binary(pos // 2, depth + 1)
        if pos % 2:
            self.binaryPos[depth] = True
        else:
            self.binaryPos[depth] = False

    def move_filter(self,pos):
        self.pos = pos
        self.set_position()
        self.port7.write(False)

        self.port0.write(self.binaryPos[0])
        self.port1.write(self.binaryPos[1])
        self.port2.write(self.binaryPos[2])

        self.port7.write(True)
        self.port7.write(False)

    def exit(self):
        self.port7.close()
        self.port0.close()
        self.port1.close()
        self.port2.close()
    
 

