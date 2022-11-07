<img src="GUI_Images/LiveDeskewLogo.jpg" width="600">
<img src="GUI_Images/LAG_Logo.png" width="400">


# Live-Deskewing
This is a software package to display deskewed images in real time for lightsheet microscopes. It's aim is to make the live display from lighsheet microscopes easier to interpret. This will help in sample navigation and locating areas of interest within the sample. The software uses [pycro-manager](https://github.com/micro-manager/pycro-manager) to handle camera acquistion allowing so that it is compatiable with most modern scientific cameras. See our preprint paper on this software at https://arxiv.org/abs/2211.00645.

Please see the software user manual to help with getting started with the software. However, if you have an issues using the code that has not been addressed please feel free to email me at jrl70@cam.ac.uk. 

## Using Live Deskewing GUI
1) Open the camera in micromanager and select the ROI where the sheet is formed. NB: Smaller ROIs will have a higher final framerate
2) Run the script *Live_Deskew_GUI.py*
3) Press the *Start* button to begin displaying a live deskewed output.

## Things to note
- Both [pycro-manager](https://github.com/micro-manager/pycro-manager) and [nidaqmx](https://github.com/ni/nidaqmx-python) will need to be installed for the GUI to run
- Once opened, by default the software will only control the camera. To add other hardware to the GUI navigate to the *Control Settings* tab. Hardware configurations can either be manually set or loaded from a configuration file. 
- Before adding any hardware control into the GUI I would recommend starting the deskewing to check everything is correctly installed and working.  
- The sheet angle (angle subtended between the excitation sheet and the scan axis) and the image pixel size (size of camera pixel in the sample) must be set under *Deskewing Parameters* on the *Live Settings* tab. 
- Switching between 'Widefield' (single displayed image after each stack) and 'Confocal' (output is updated after each camera exposure) modes can be done using the dropdown box below the start and stop buttons. This can only be changed whilst the deskewing is not in operation. NB: If using 'Confocal' mode exposure times below 20ms may cause significant lag between camera exposure and image diplay due to plotting being slower than camera acquistion. 
- Brighness and Contrast of the output image can be adjusted using the *Min Intensity* and *Max Intensity* sliders. 
- The *Rotate* slider linearly changes the shear factor on the fly to effectively change the viewing angle to give an understanding of 3D structure of the sample. 
- The software can handle up to 4 lasers. Though this number can be arbitrarily increased by adding more buttons on the *Live Settings* tab. 
- Lasers can be controlled by either analogue voltage or a digital TTL signal. Currently only National Instruments DAQ cards are supported within the GUI. However, support for other hardware should be easy to incorperate. 
- Unless the *Allow Multiple Lasers* box is checked, turning a laser on will cause all other lasers to turn off and the filterwheel position to change. 

## Examples

### Global Update Mode - Supplementary Video 1

https://user-images.githubusercontent.com/56591782/162004554-b2fb6de8-8a08-4195-827c-5b5663868235.mov

### Rolling Update Mode - Supplementary Video 2

https://user-images.githubusercontent.com/56591782/162005417-42f945a7-e537-43a8-a2b5-10235bc5df28.mov

