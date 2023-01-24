from pycromanager import Core
import torch.multiprocessing as multiprocessing
import numpy as np
import torch
import math
import utils.sampleScan as sampleScan
import utils.camera as camera

class livedeskew:
    def __init__(self,stopq,rotateq,dskwImgq,dskwImgq2,dskwImgq3):
        core = Core()
        #core.set_roi(0,0,1304,87)

        if core.is_sequence_running():
            core.stop_sequence_acquisition() # turn camera off

        self.dtype = torch.half
        #core.set_roi(306,789,1761,696)
        self.stopq = stopq
        self.rotateq = rotateq
        self.dskwImgq = dskwImgq
        self.dskwImgq2 = dskwImgq2
        self.dskwImgq3 = dskwImgq3
        self.qcam = multiprocessing.Queue()
       
        self.exposuretime = 1
        self.ScanRange = 75
        self.depth = 50
        self.z_step = self.ScanRange/self.depth
        self.sheetangle = 32.8
        self.XY_pixel_pitch = 0.115
        self.fullchipx = 988
        self.fullchipy = 696
    
        #self.shearFactor =np.sin(30 *np.pi / 180) * self.stageStep / self.XY_pixel_pitch
        self.shearFactor = np.cos(self.sheetangle * np.pi/180) * (self.z_step/self.XY_pixel_pitch)
        self.height = core.get_image_height()
        self.width = core.get_image_width()
        self.new_height = math.ceil(self.height+self.shearFactor*(self.depth-1))

        self.Trigger_Options = []
        self.find_TriggerOptions(core)

        self.scanGalvo = False
        self.preloadGalvo = False
        self.altScanHardware = False #True = Hardware other than NIDAQ cards
        self.galvoTriggerPort = ''
        self.cameraExtTrig = False
        self.optosplit = False
        self.widefieldMode = True
        self.singleSlice = False # True = only show a single slice crossesction, False = Perform full extended volume projection
        self.compute_warp = True #True
        self.interplationmode = 'bilinear' #linear | bilinear | bicubic | trilinear

        #[startx,stopx,starty,stopy]
        self.windowsize = [950,200]#[1700,200]
        self.colour1roi = [0,950,26,226]#[0,1700,26,226]
        self.colour2roi = [10,960,245,445]#[10,1710,245,445]
        self.colour3roi = [20,970,487,687]#[20,1720,487,687]

        #self.device = torch.device('cpu')
        self.device = torch.device("cuda:0")
    
    def setSingleSlice(self,bool):
        self.singleSlice = bool

    def getSingleSlice(self):
        return self.singleSlice

    def setDisplayMode(self,bool):
        self.widefieldMode = bool #True = Widefield

    def setOptoSplit(self,bool):
        self.optosplit = bool
    
    def getOptoSplit(self):
        return self.optosplit

    def setExposure(self,value):
        self.exposuretime = value 

    def get_scanRange(self):
        return self.ScanRange

    def get_shearFactor(self):
        return self.shearFactor

    def get_depth(self):
        return self.depth

    def set_galvoParams(self,port,max,min,off,v2um):
        self.galvoPort = port
        self.galvomaxV = max
        self.galvominV = min
        self.galvooffV = off
        self.galvov2um = v2um

    def enableGalvo(self):
        self.scanGalvo = True

    def disableGalvo(self):
        self.scanGalvo = False

    def enableAltHard(self):
        self.altScanHardware = True

    def disableAltHard(self):
        self.altScanHardware = False

    def enablePreloadGalvo(self):
        self.preloadGalvo = True

    def disablePrelodGalvo(self):
        self.preloadGalvo = False

    def setGalvoTriggerPort(self,port):
        self.galvoTriggerPort = port

    def find_TriggerOptions(self,core):
        devices =  core.get_loaded_devices()
        if core.has_property(devices.get(0),'TriggerMode'):
            allowed = core.get_allowed_property_values(devices.get(0), 'TriggerMode')
            [self.Trigger_Options.append(allowed.get(i)) for i in range(allowed.size())]
        else:
            self.Trigger_Options.append('Internal Trigger')

    def getSheetAngle(self):
        return self.sheetangle

    def setSheetAngle(self,angle):
        self.sheetangle = angle
        self.shearFactor = np.cos(self.sheetangle * np.pi/180) * (self.z_step/self.XY_pixel_pitch)

    def getPixelPitch(self):
        return self.XY_pixel_pitch

    def setPixelPitch(self,pitch): 
        self.XY_pixel_pitch = pitch
        self.shearFactor = np.cos(self.sheetangle * np.pi/180) * (self.z_step/self.XY_pixel_pitch)

    def setDepth(self,Value):
        self.depth = Value
        self.z_step = self.ScanRange/self.depth
        self.shearFactor = np.cos(self.sheetangle * np.pi/180) * (self.z_step/self.XY_pixel_pitch)
        self.new_height = math.ceil(self.height+self.shearFactor*(self.depth-1))

    def setScanRange(self,Value):
        self.ScanRange = Value
        self.z_step = self.ScanRange/self.depth
        self.shearFactor = np.cos(self.sheetangle * np.pi/180) * (self.z_step/self.XY_pixel_pitch)
        self.new_height = math.ceil(self.height+self.shearFactor*(self.depth-1))

    def GPU_MultiProcess(self):
        core = Core()
        core.clear_circular_buffer()
        self.height = core.get_image_height()
        self.width = core.get_image_width()
        self.shearFactor = np.cos(self.sheetangle * np.pi/180) * (self.z_step/self.XY_pixel_pitch)
        self.new_height = math.ceil(self.height+self.shearFactor*(self.depth-1))
        processes = []

        if not self.optosplit:
            proc_Cam = multiprocessing.Process(target=self.snap)
            processes.append(proc_Cam)
            proc_deskew = multiprocessing.Process(target=self.GPU_deskew_max, args=(self.qcam,self.dskwImgq,))
            processes.append(proc_deskew)
        else:
            #core.set_roi(306,789,1761,696)
            core.set_roi(628,789,988,696)
            self.height = self.windowsize[1]
            self.width = self.windowsize[0]
            self.new_height = math.ceil(self.height+self.shearFactor*(self.depth-1))

            self.fullchipx = core.get_image_height()
            self.fullchipy = core.get_image_width()

            clr1q = multiprocessing.Queue()
            clr2q = multiprocessing.Queue()
            clr3q = multiprocessing.Queue()

            proc_Cam = multiprocessing.Process(target=self.snap)
            processes.append(proc_Cam)
            proc_split = multiprocessing.Process(target=self.split_colours, args = (clr1q,clr2q,clr3q,))
            processes.append(proc_split)
            proc_deskew1 = multiprocessing.Process(target=self.GPU_deskew_max, args=(clr1q,self.dskwImgq,))
            processes.append(proc_deskew1)
            proc_deskew2 = multiprocessing.Process(target=self.GPU_deskew_max, args=(clr2q,self.dskwImgq2,))
            processes.append(proc_deskew2)
            proc_deskew3 = multiprocessing.Process(target=self.GPU_deskew_max, args=(clr3q,self.dskwImgq3,))
            processes.append(proc_deskew3)

        for process in processes:
            process.start()
       
    def snap(self):
        self.camcount = 0
        core = Core()
        core.set_exposure(self.exposuretime)
        if self.scanGalvo:
            if not self.altScanHardware:
                if self.preloadGalvo:
                    g = sampleScan.sampleScan(self.galvoPort,extTrig=True,extTrigPort= self.galvoTriggerPort)
                else:
                    g = sampleScan.sampleScan(self.galvoPort)
                g.set_maxV(self.galvomaxV)
                g.set_minV(self.galvominV)
                g.set_offV(self.galvooffV)
                g.set_v2um(self.galvov2um)
            else:
                g = sampleScan.sampleScan()
            g.set_scanrange(self.ScanRange)
            g.set_steps(self.depth)
            g.connect()
            g.createWaveform()
            if self.cameraExtTrig:
                cam = camera.camera('FilterCam/port1/line0')
                cam.connect()
                if core.is_sequence_running():
                    core.stop_sequence_acquisition() # turn camera off
                core.start_continuous_sequence_acquisition(0) # start the camera
                if self.preloadGalvo:
                    g.preloadGalvo()
                    img = self.ExtTrig_grab_frame(core,cam,)
                    while True:
                        if self.stopq.value:
                            break   
                        img = self.ExtTrig_grab_frame(core,cam,)
                        self.qcam.put(img)
                else:
                    g.initPos()
                    g.nextPos()
                    while True:
                        if self.stopq.value:
                            break   
                        img = self.ExtTrig_grab_frame(core,cam,)
                        g.nextPos()
                        self.qcam.put(img)
                self.qcam.put('END')
                cam.snap()
                core.stop_sequence_acquisition() # stop the camera
                cam.exit()
            else:
                if self.preloadGalvo:
                    g.preloadGalvo()
                    img = self.grab_frame(core,)
                    while True:
                        if self.stopq.value:
                                break   
                        img = self.grab_frame(core,)
                        self.qcam.put(img)
                else:
                    g.initPos()
                    g.nextPos()
                    while True:
                        if self.stopq.value:
                            break   
                        img = self.grab_frame(core,)
                        g.nextPos()
                        self.qcam.put(img)
                self.qcam.put('END')
            g.exit()
        else:
            if self.cameraExtTrig:
                cam = camera.camera('FilterCam/port1/line0')
                cam.connect()
                if core.is_sequence_running():
                    core.stop_sequence_acquisition() # turn camera off
                core.start_continuous_sequence_acquisition(0) # start the camera
                while True:
                    if self.stopq.value:
                        break   
                    img = self.ExtTrig_grab_frame(core,cam,)
                    g.nextPos()
                    self.qcam.put(img)
                self.qcam.put('END')
                cam.snap()
                core.stop_sequence_acquisition() # stop the camera
                cam.exit()
            else:
                while True:
                    if self.stopq.value:
                        break                    
                    self.qcam.put(self.grab_frame(core,))
                self.qcam.put('END')   

    def grab_frame(self,core): 
        core.snap_image()
        tagged_image = core.get_image()
        return tagged_image

    def ExtTrig_grab_frame(self,core,cam): 
        cam.snap()
        self.camcount = 1
        count = core.get_remaining_image_count()
        while count == self.camcount:
            count = core.get_remaining_image_count()
        tagged_image = core.get_last_image()
        self.camcount += 1
        return tagged_image

    def split_colours(self,clr1q,clr2q,clr3q):
        while True: 
            if not self.qcam.empty():
                image_array = self.qcam.get()
                if isinstance(image_array, str):
                    clr1q.put('END')
                    clr2q.put('END')
                    clr3q.put('END')
                    break
                else:
                    image_array =  np.squeeze(np.reshape(image_array,(-1, self.fullchipx,self.fullchipy)))
                    clr1q.put(image_array[self.colour1roi[2]:self.colour1roi[3],self.colour1roi[0]:self.colour1roi[1]])
                    clr2q.put(image_array[self.colour2roi[2]:self.colour2roi[3],self.colour2roi[0]:self.colour2roi[1]])
                    clr3q.put(image_array[self.colour3roi[2]:self.colour3roi[3],self.colour3roi[0]:self.colour3roi[1]])
                    
    def GPU_deskew_max(self,in_imgq,out_imgq):
        osf = self.shearFactor
        combined_im = torch.zeros([self.height, self.width,2], device=self.device, dtype=self.dtype)
        final_im = torch.zeros([self.new_height, self.width], device=self.device, dtype=self.dtype) 
        if not self.widefieldMode:
            prev_full_im = torch.zeros([self.new_height, self.width], device=self.device, dtype=self.dtype)
        i = 0
        lefttoright = True
        while True: 
            if not in_imgq.empty():
                image_array = in_imgq.get()
                if isinstance(image_array, str):
                    out_imgq.put('END')
                    break
                else:
                    if not self.optosplit:
                        image_array =  np.squeeze(np.reshape(image_array,(-1, self.height, self.width)))
                    image_array = torch.from_numpy(image_array.astype("float16")).to(self.device)

                    if self.singleSlice:
                        window_width = 6
                        image_array[0:int((self.height/2)) - window_width, 0:self.width] = 0
                        image_array[int((self.height/2) + window_width): self.height, 0:self.width] = 0

                    if lefttoright: 
                        startH = math.ceil(self.shearFactor*(i))
                        stopH = math.ceil(self.shearFactor*(i)+self.height)

                        previmg = final_im[startH:stopH, 0:self.width]
                        final_im[startH:stopH, 0:self.width] = self.GPU_max_proj(combined_im, previmg, image_array)
                        if not self.widefieldMode:
                            prev_full_im[startH:stopH, 0:self.width] = final_im[startH:stopH, 0:self.width]
                    else:
                        startH = np.ceil(self.new_height-self.shearFactor*(i)-self.height).astype('int')
                        stopH = np.ceil(self.new_height-self.shearFactor*(i)).astype('int')

                        previmg = final_im[startH:stopH, 0:self.width]
                        final_im[startH:stopH, 0:self.width]= self.GPU_max_proj(combined_im, previmg, image_array)
                        if not self.widefieldMode:
                            prev_full_im[startH:stopH, 0:self.width] = final_im[startH:stopH, 0:self.width]
                    i += 1
                    
                    if not self.widefieldMode:
                        if self.compute_warp:
                            shear = osf-self.shearFactor
                            if not shear == 0:
                                pixel_ratio = self.z_step/self.XY_pixel_pitch 
                                angle = np.arctan(shear/pixel_ratio)
                                scale = np.cos(angle)
                                warped_prev_full_im = torch.unsqueeze(torch.unsqueeze(prev_full_im,0),0)
                                warped_prev_full_im = torch.nn.functional.interpolate(warped_prev_full_im, mode = self.interplationmode, size=(int(self.new_height*scale),self.width), align_corners=False)
                                warped_prev_full_im = torch.squeeze(warped_prev_full_im)
                                disp_array = warped_prev_full_im.cpu().detach().numpy()   
                            else:
                                disp_array = prev_full_im.cpu().detach().numpy() 
                        else:
                            disp_array = prev_full_im.cpu().detach().numpy()   
                        out_imgq.put(disp_array.astype("uint16"))  

                    if i == self.depth:
                        i = 0  
                        if self.widefieldMode:
                            if self.compute_warp:
                                shear = osf-self.shearFactor
                                if not shear == 0:
                                    pixel_ratio = self.z_step/self.XY_pixel_pitch 
                                    angle = np.arctan(shear/pixel_ratio)
                                    scale = np.cos(angle)
                                    final_im = torch.unsqueeze(torch.unsqueeze(final_im,0),0)
                                    final_im = torch.nn.functional.interpolate(final_im, mode = self.interplationmode, size=(int(self.new_height*scale),self.width), align_corners=False)
                                    final_im = torch.squeeze(final_im)
                            disp_array = final_im.cpu().detach().numpy()   
                            out_imgq.put(disp_array.astype("uint16")) 
                        #else:
                        #    prev_full_im = final_im
                         
                        self.shearFactor = self.rotateq.value
                        self.new_height = math.ceil(self.height+self.shearFactor*(self.depth-1))
                        if not self.widefieldMode:
                            [prev_h,prev_w] = final_im.size()
                            if prev_h == self.new_height:
                                prev_full_im = final_im
                            else:
                                prev_full_im = torch.zeros([self.new_height, self.width], device=self.device, dtype=self.dtype)   
                            

                        final_im = torch.zeros([self.new_height, self.width], device=self.device, dtype=self.dtype)      
                        if lefttoright:
                            lefttoright = False
                        else:
                            lefttoright = True

    def GPU_max_proj(self,combined_im, old_image,new_image):
        combined_im[:,:,0] = old_image
        combined_im[:,:,1] = new_image
        final_im = torch.amax(combined_im, 2)
        return final_im

