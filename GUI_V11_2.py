import PIL
import tkinter
import cv2
import PIL.Image
import imageio
from PIL import Image, ImageTk
import time
import numpy as np
# tkinter components import
import tkinter as tk
from tkinter import messagebox as tkm
from tkinter.scrolledtext import ScrolledText as tkst
from  tkinter.filedialog import askopenfilename
import os
from tkinter import *
from tkinter.ttk import *
# Files needed to print the pdf document
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
import cgi
import tempfile
from pathlib import Path
import NanoCamMZ as nano

zooming_flag=False
zoomingfactor_global= 100
framerate= 30# 15 fps frame rate
pollensize = 20 # global param to set the size of the minimal observable pollen
camwidth= 1280  # set the resolution for the camera
camheight=720  # set the resolution for the camera
video_source_global=0 #param to set source of video when 0 selects camera
gflip=0

# partially source from https://medium.com/lifeandtech/executable-gui-with-python-fc79562a5558
class ResizingCanvas(tk.Canvas):
    """ The class that will be used for the resizing of the window"""
    def __init__(self, parent, **kwargs):
        tk.Canvas.__init__(self, parent, **kwargs)
        self.bind("<Configure>", self.on_resize)
        self.height = self.winfo_reqheight()
        self.width = self.winfo_reqwidth()

    def on_resize(self, event):
        # determine the ratio of old width/height to new width/height
        wscale = float(event.width) / self.width
        hscale = float(event.height) / self.height
        self.width = event.width
        self.height = event.height
        # resize the canvas
        self.config(width=self.width, height=self.height)
        # rescale all the objects tagged with the "all" tag
        self.scale("all", 0, 0, wscale, hscale)

class FrameRate:
    """ This class helps to select framerate for the recording"""
    def framerate_5(self):
        global framerate
        framerate = 15
    def framerate_10(self):
        global framerate
        framerate = 15
    def framerate_15(self):
        global framerate
        framerate = 15
    def framerate_20(self):
        global framerate
        framerate = 20
    def framerate_25(self):
        global framerate
        framerate = 25
    def framerate_30(self):
        global framerate
        framerate = 30

    def framerate_60(self):
        global framerate
        framerate = 60

class CamResolution:
    """ The class to set the resolution of the camera for the pi"""
       
    def make_hq(self):
        global camwidth, camheight
        camwidth=2960
        camheight=1440
        
        
    def make_1440p(self):
        global camwidth, camheight
        camwidth=2560
        camheight=1440
        
    def make_1080p(self):
        global camwidth, camheight
        camwidth=1920
        camheight=1080

    def make_720p(self):
        global camwidth, camheight
        camwidth=1280
        camheight=720

    def make_480p(self):
        global camwidth, camheight
        camwidth=640
        camheight=480

    def change_res(self,width, height):
        global camwidth, camheight
        camwidth=width
        camheight=height

# class video_source_selection:
#     """ The class to select video source"""
#     def __init__(self, video_source=0):
#         self.video_source=video_source
    
#     def select_camera(self):
#         return cv2.VideoCapture(video_source=0)
    
#     def select_recording(self):
        
        
    
        
class Zoom:
    """ This class incorporate zooming function of the images"""
    def __init__(self,zoomfactor=100,size=(640,560)):
        self.zoomfactor=zoomfactor # size of the zoom coefficient
        self.size=size # size of the camera resolution
        
        
    def zoomin(self):
        """ function to control zooming in of the images"""
        global zooming_flag
        global zoomingfactor_global
        self.zoomfactor=self.zoomfactor-5
        zoomingfactor_global = self.zoomfactor
        zooming_flag= True
        if self.zoomfactor >=5:
            return self.zoomfactor
        else:
            return 5
        
    
    def zoomout(self):
        """ function to control zooming out of images"""
        global zooming_flag
        self.zoomfactor=self.zoomfactor+5
        zoomingfactor_global = self.zoomfactor
        if self.zoomfactor < 1000:
            return self.zoomfactor
        else:
            zooming_flag=False
            return 100020
        
    def zoomimage(self,frame):
        """ function that will zoom image based on zoomfactor"""
        scale = self.zoomfactor
        if scale == 100:
            return frame
        else:
            #size=(int(self.vid.width),int(self.vid.height))# this is the size of the frame recorded
            
            width, height, channels = frame.shape
            #prepare the crop
            centerX,centerY=int(height/2),int(width/2)
            radiusX,radiusY= int(scale*height/100),int(scale*width/100)

            minX,maxX=centerX-radiusX,centerX+radiusX
            minY,maxY=centerY-radiusY,centerY+radiusY

            cropped = frame[minY:maxY , minX:maxX]
            # The size of the recorded window remains same only
            resized_cropped = cv2.resize(cropped, self.size,interpolation = cv2.INTER_LINEAR)
            return resized_cropped
class Jetson_cam:
    """ This class helps to initiate Jetson  CSI camera  connected to port0. It also let us upload
    video."""

    def __init__(self,cwidth,cheight,fps, video_source=0):
        global zoomingfactor_global, camheight, camwidth, framerate, gflip
          # use nanocamera pacckage to use for the initiating  jetson CSI camera
        self.camera = nano.Camera(flip=gflip, width=camwidth, height=camheight, fps=framerate)
        if not self.camera.isReady():
            raise ValueError("Unable to open video source", video_source)
        self.width= camwidth
        self.height= camheight
        # This will compose the zoom class for the zooming applications
        self.zooming= Zoom(zoomingfactor_global,(self.width,self.height))

    def get_frame(self):
        """ Method to get frame from camera""" 
        global zooming_flag
        global zoomingfactor_global
        global camheight,camwidth
        if self.camera.isReady():
            frame = self.camera.read()
            if np.any(frame):
                ret = True    # this ret flag is done  to make this class comatable to MyVideoCapture class
            else:
                ret = False
            if zooming_flag:
                frame=self.zooming.zoomimage(frame)
                    
            return (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        else:
            return(ret, None)
        # Release the video source when the object is destroyed
    def __del__(self):
        if self.camera.isReady():
            self.camera.release()
   

        
# partially sourced from: https://solarianprogrammer.com/2018/04/21/python-opencv-show-video-tkinter-window/
class MyVideoCapture:
    """ This class helps to capture the image from camera and release it when not needed
. Alternatively it will aslo accept the recorded video for the analysis"""
    def __init__(self, cwidth,cheight,video_source=0):
        # Open the video source
        global zoomingfactor_global, camheight, camwidth,framerate
        
        self.vid = cv2.VideoCapture(video_source)
        #self.resolution= CamResolution()
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", video_source)

        # Get video source width and height
        #self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        #self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
        # get frame rate of the recorded video
        framerate=self.vid.get(cv2.CAP_PROP_FPS)

        self.vid.set(3,cwidth)
        self.vid.set(4,cheight)
        #self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        #self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.width= cwidth
        self.height= cheight
        # This will compose the zoom class for the zooming applications
        self.zooming= Zoom(zoomingfactor_global,(self.width,self.height))


    def get_frame(self):
        global zooming_flag
        global zoomingfactor_global
        global camheight,camwidth
        
        self.vid.set(3,camwidth)
        self.vid.set(4,camheight)
        ret, frame = self.vid.read()
        #print("##################",frame.shape)
        if self.vid.isOpened():
            #self.vid.set(3,camwidth)
            #self.vid.set(4,camheight)
            ret, frame = self.vid.read()
            if ret:
                # Return a boolean success flag and the current frame converted to BGR
                if zooming_flag:
                    frame=self.zooming.zoomimage(frame)
                    
                return (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            else:
                return (ret, None)
        else:
            return (ret, None)

    # Release the video source when the object is destroyed
    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()
            
# partially sourced from: https://solarianprogrammer.com/2018/04/21/python-opencv-show-video-tkinter-window/
# https://medium.com/lifeandtech/executable-gui-with-python-fc79562a5558
class App:
    def __init__(self, window, window_title):
        global zoomingfactor_global
        global framerate,gflip
        global camwidth, camheight,video_source_global
        self.window = window
        self.window.title(window_title)

        self.after_id = None  # this is a param to start and stop recordings
        self.stop_flag=False
        self.zoomfactor=100   # This is defualt value which will be used for zoom in and out
        self.rate = framerate
        self.video_source = 0
        self.select_frate=FrameRate() # Class for frame rate selection
         # open video source (by default this will try to open the computer webcam)
        #self.vid = MyVideoCapture(camwidth, camheight,self.video_source)
        
        #self.vid = MyVideoCapture(camwidth, camheight,'channel_clip.mp4')

        self.vid=Jetson_cam(camwidth,camheight,framerate, self.video_source)
        self.size= (int(self.vid.width),int(self.vid.height))
        # This will compose the zoom class for the zooming applications
        self.zooming= Zoom(zoomingfactor_global,self.size)
        # This will be used to set the resolution
        self.resol=CamResolution()

        # Create a canvas that can fit the above video source size
        self.canvas = tk.Canvas(window, width = self.vid.width, height = self.vid.height+50)
        self.canvas.pack(pady= 10)
                # to make a frame
        self.frame = tk.Frame(self.window, bg='white')

        # Button that lets the user take a snapshot
        self.btn_snapshot=tk.Button(window, text="Snapshot", width=10, command=self.snapshot)
        self.btn_snapshot.pack(side='left', padx= 10)
        
        # Button that lets the user take a snapshot
        #self.btn_snapshot2=tk.Button(window, text="Snapshot2", width=10, command=self.snapshot)
        #self.btn_snapshot2.pack(side='left',padx= 10)
        
        # Button that lets the user record video
        self.btn_record=tk.Button(window, text="Record", width=10, command=self.recordplanevideo)
        self.btn_record.pack(side='left', padx= 10)
        
        # Button that lets the user zoom into video
        self.btn_zoomin=tk.Button(window, text="Zoom++", width=10, command=self.zooming.zoomin)
        self.btn_zoomin.pack(side='left',padx= 10)
        self.btn_zoomout=tk.Button(window, text="Zoom--", width=10, command=self.zooming.zoomout)
        self.btn_zoomout.pack(side='left',padx= 10)
        
        self.btn_PS=tk.Button(window, text="PollenSize", width=10, command=self.enter_pollen_size)
        self.btn_PS.pack(side='left',padx= 10)
        
        self.btn_record_ai=tk.Button(window, text="AI-record", width=10, command=self.recordvideo_ai)
        self.btn_record_ai.pack(side='left', padx= 10)
        
        
        self.btn_exit=tk.Button(window, text="Quit", width=10, command=window.destroy)
        self.btn_exit.pack(side='left',padx= 10)
        

        
        # to place a menu item in the window
        self.menu = tk.Menu(window)
        window.config(menu=self.menu)

        # all the commands for the submenu File
        self.subMenu_file = tk.Menu(self.menu)
        self.menu.add_cascade(label="Video Source", menu=self.subMenu_file)
        self.subMenu_file.add_command(label="Open Camera",
                                      command=self.open_camera)
        self.subMenu_file.add_command(label="Open File",
                                      command=self.open_file)
       # self.subMenu_file.add_command(label="Save",
                                      #command=self.save_report_pdf)
        self.subMenu_file.add_separator()
        #self.subMenu_file.add_command(label="Print", command=self.print_file)
        #self.subMenu_file.add_separator()
        self.subMenu_file.add_command(label="Exit", command=window.destroy)
        
        # all the commands for the submenu frramerate
        self.subMenu_resol = tk.Menu(self.menu)
        self.menu.add_cascade(label="Frame rate", menu=self.subMenu_resol)
        self.subMenu_resol.add_command(label="5fps", command=self.select_frate.framerate_5)
        self.subMenu_resol.add_command(label="10fps",command=self.select_frate.framerate_10)
        self.subMenu_resol.add_command(label="15fps", command=self.select_frate.framerate_15)
        self.subMenu_resol.add_command(label="20fps",command=self.select_frate.framerate_20)
        self.subMenu_resol.add_command(label="25fps",command=self.select_frate.framerate_25)
        self.subMenu_resol.add_command(label="30fps", command=self.select_frate.framerate_30)
        #self.subMenu_resol.add_command(label="480p",command=self.resol.make_480p)
        #self.subMenu_resol.add_command(label="Custom",command=self.resol.change_res)
        
        
        # all the commands for the submenu zoom
        #self.subMenu_PS = tk.Menu(self.menu)
        #self.menu.add_cascade(label="Pollen Size", menu=self.subMenu_PS)
        #self.subMenu_PS.add_command(label="Enter Value", command=self.enter_pollen_size())
        
        
        
        # all the commands for the submenu zoom
        #self.subMenu_zoom = tk.Menu(self.menu)
        #self.menu.add_cascade(label="Zoom", menu=self.subMenu_zoom)
        #self.subMenu_zoom.add_command(label="Zoom", command=self.open_zoom)
        #self.subMenu_zoom.add_command(label="Zoom-In",command=self.zoom_in)
        #self.subMenu_zoom.add_command(label="Zoom-Out",command=self.zoom_out)
        
        # all the commands for the submenu resolution
        self.subMenu_resol = tk.Menu(self.menu)
        self.menu.add_cascade(label="Resolution", menu=self.subMenu_resol)
        self.subMenu_resol.add_command(label="HQ", command=self.resol.make_hq)
        self.subMenu_resol.add_command(label="1440p",command=self.resol.make_1440p)
        self.subMenu_resol.add_command(label="1080p",command=self.resol.make_1080p)
        self.subMenu_resol.add_command(label="720p", command=self.resol.make_720p)
        self.subMenu_resol.add_command(label="480p",command=self.resol.make_480p)
        #self.subMenu_resol.add_command(label="Custom",command=self.resol.change_res)

        # all the commands for the submenu Help
        self.subMenu_help = tk.Menu(self.menu)
        self.menu.add_cascade(label="Help", menu=self.subMenu_help)
        self.subMenu_help.add_command(label="Help", command=self.open_help)
        self.subMenu_help.add_command(label="Print Diag",
                                      command=self.open_wiring_diag)

        ############################################################################################

        # After it is called once, the update method will be automatically called every delay milliseconds
        self.delay = 15
        self.update()
        ci = Path('./captured_images') # path to store AI-cpatured images
        pi = Path('./processed_images') # path to store images of individual pollens captured in AI-recording
        if not ci.exists():
            os.mkdir('./captured_images') #create directory if not existing 
        if not pi.exists():
            os.mkdir('./processed_images') # create directory if not existing

        self.window.mainloop()

  # partailly resourced from
  # https://stackoverflow.com/questions/50870405/how-can-i-zoom-my-webcam-in-open-cv-python

    def enter_pollen_size(self):
        """ This function will set the pollen size"""
        global pollensize 
            # Toplevel object which will 
        # be treated as a new window
        def retrieve_input():
            global pollensize 
            pollensize = int(inputtxt.get(1.0, "end-1c"))
            #print("pollensize",inp)
        newWindow = Toplevel(self.window)
      
        # sets the title of the
        # Toplevel widget
        newWindow.title("New Window")
      
        # sets the geometry of toplevel
        newWindow.geometry("200x200")
      
        # A Label widget to show in toplevel
        tk.Label(newWindow, 
              text ="Enter Pollen Size before AI-recording").pack()
        inputtxt = tk.Text(newWindow, height = 10,width = 25,bg = "light yellow")
        inputtxt.pack()
        buttonCommit=tk.Button(newWindow, width=5, text="Enter", 
                    command=lambda: retrieve_input())
        buttonCommit.pack(side='left',padx= 5)
        buttonClose=tk.Button(newWindow, width=5, text="Quit", 
                    command=newWindow.destroy)
        buttonClose.pack(side='left',padx= 5)
        #self.window


    def recordplanevideo(self):
        # this function  is recording .avi file with 15 fps rate can be changed
        global camwidth,camheight
 
        
        #size=(int(self.vid.width),int(self.vid.height))# this is the size of the frame recorded
        size=(camwidth,camheight)
        result = cv2.VideoWriter('output_'+ time.strftime("%d-%m-%Y-%H-%M-%S")+'.mp4',
                         cv2.VideoWriter_fourcc(*'MJPG'),
                         self.rate, size)
        
        while(True):
            ret,frame = self.vid.get_frame()  # referring to the video variable in MyVideoCapture class
            scale = self.zoomfactor

            if np.any(frame):
                
                # the image is only resized if zoomed else it will be as it is
                resized_cropped = self.zooming.zoomimage(frame)
                resized_cropped = cv2.cvtColor(resized_cropped, cv2.COLOR_BGR2RGB)

                # Write the frame into the
                # file 'output.mp4'
                if video_source_global == 0:
                    result.write(resized_cropped)

                # Display the frame
                # saved in the file

                cv2.imshow('Press ESC to stop recording', resized_cropped)
                #cv2.imwrite('image'+time.strftime("%d-%m-%Y-%H-%M-%S")+'.jpg',resized_cropped)
                

                # Press S on keyboard
                # to stop the process
                key = cv2.waitKey(1)  # waiting for keybord input
                if key== 27:  # read esc key
                    break   

            else:
                break
        cv2.destroyWindow('Press ESC to stop recording') # this will only close the recording window
     
    def recordvideo_ai(self):
        # this function  is recording .avi file with 15 fps rate can be changed
    
        global pollensize
        global camwidth,camheight
        
        #size=(int(self.vid.width),int(self.vid.height))# this is the size of the frame recorded
        size=(camwidth,camheight)
        result = cv2.VideoWriter('output_'+ time.strftime("%d-%m-%Y-%H-%M-%S")+'.mp4',
                    cv2.VideoWriter_fourcc(*'MJPG'),
                    self.rate, size)
        #result = cv2.VideoWriter('output_'+ time.strftime("%d-%m-%Y-%H-%M-%S")+'avi',
                         #cv2.VideoWriter_fourcc(*'XVID'),
                         #self.rate, size)
        
        while(True):
            ret,frame = self.vid.get_frame()  # referring to the video variable in MyVideoCapture class
            scale = self.zoomfactor
            image_count=1

            if np.any(frame):
                
                # the image is only resized if zoomed else it will be as it is
                resized_cropped = self.zooming.zoomimage(frame)
                resized_cropped = cv2.cvtColor(resized_cropped, cv2.COLOR_BGR2RGB)
                # Write the frame into the file 'output.avi'
                if video_source_global == 0:
                    result.write(resized_cropped)

                # Display the frame
                # saved in the file

                #cv2.imshow('Press ESC to stop recording', resized_cropped)
                imgContour = resized_cropped.copy()
                
                imgtmp2 = resized_cropped.copy()
                # Grayscale
                imgGray = cv2.cvtColor(imgContour, cv2.COLOR_BGR2GRAY)
                # Gaussian smoothing
                imgBlur = cv2.GaussianBlur(imgGray, (7, 7), 1)
                # Edge detection
                imgCanny = cv2.Canny(imgBlur, 40, 50)
                #cv2.imshow('Press ESC to stop recording', imgCanny)
                    # Find contour, cv2.RETR_ExTERNAL=get external contour points, CHAIN_APPROX_NONE=get all pixels
                contours, hierarchy = cv2.findContours(imgCanny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
                contours=sorted(contours,key=lambda x:cv2.contourArea(x),reverse = True) # Just select the biggest contour
                # Cycle contours, judge each shape
                sub_image_count=1
                for cnt in contours:
                    # Get the outline area
                    area = cv2.contourArea(cnt)
                    
                    #print(area)
                    # Set the area range to the existence of graphics
                    #if 500> area > 200:
                    if area > pollensize:
                        imgtmp =imgContour.copy()
                        imgtmp2 = resized_cropped.copy()
                        # Draw all contours and display them
                        #cv2.imwrite('./captured_images/'+'image_'+str(image_count)+'.jpg',imgtmp)
                        #cv2.drawContours(imgContour, cnt, -1, (255, 0, 0), 3)
                        # Calculate the circumference of all contours to facilitate polygon fitting
                       # peri = cv2.arcLength(cnt, True)
                        # Polygon fitting, get the edges of each shape
                        #approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
                        #print(len(approx))
                        #objCor = len(approx)
                        # Get the x, y, w, h of each shape
                        x, y, w, h = cv2.boundingRect(cnt)
                        cv2.rectangle(imgContour, (x-20, y-20), (x + w+20, y + h+20), (0, 255, 0), 2)
                        #cv2.rectangle(imgtmp, (x-20, y-20), (x + w+20, y + h+20), (0, 255, 0), 2)                        
                        
                        #cv2.imwrite('./captured_images/'+'image'+time.strftime("%d-%m-%Y-%H-%M-%S")+'.jpg',imgContour)
                        #cv2.imwrite('./captured_images/'+'image_marked_'+str(image_count)+'.jpg',imgContour)
                        #cv2.imshow('Press ESC to stop recording', imgContour)
                        #cv2.imwrite('image'+time.strftime("%d-%m-%Y-%H-%M-%S")+'.jpg',resized_cropped)
                        #cv2.imwrite('./processed_images/shaped_image'+time.strftime("%d-%m-%Y-%H-%M-%S")+'.jpg',imgContour[y-30:y+h+30,x-30:x+w+30])
                        img_selected = imgtmp2[y-30:y+h+30,x-30:x+w+30]
                        if np.any(img_selected):  # Images are saved only when they result in valid numpy array
                            #cv2.imwrite('./processed_images/image_'+str(image_count)+'_'+str(sub_image_count)+'.jpg',img_selected)
                            cv2.imwrite('./processed_images/image_'+time.strftime("%d-%m-%Y-%H-%M-%S")+'.jpg',img_selected)
                        #break
                        sub_image_count+=1
                    image_count+=1
                    cv2.imshow('Press ESC to stop recording', imgContour)
                

                         
                # Press S on keyboard
                # to stop the process
                key = cv2.waitKey(1)  # waiting for keybord input
                if key== 27:  # read esc key
                    break   

            else:
                break
        cv2.destroyWindow('Press ESC to stop recording') # this will only close the recording window

        

    def snapshot(self):
        global zooming_flag
        # Get a frame from the video source
        ret, frame = self.vid.get_frame()

        if ret:
            if zooming_flag: 
                frame = self.zooming.zoomimage(frame)
            cv2.imwrite("frame-" + time.strftime("%d-%m-%Y-%H-%M-%S") + ".jpg", cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))

    def update(self):
        global zooming_flag # global flag to remind that zooming is done
    
        # Get a frame from the video source
        ret,frame = self.vid.get_frame()

        if np.any(frame):
            if zooming_flag:
                frame = self.zooming.zoomimage(frame)
            self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame))
            self.canvas.create_image(0, 0, image = self.photo, anchor = tkinter.NW)

        self.window.after(self.delay, self.update)
    def open_camera(self):
        """ Function to select camera as the source of video"""
        global video_source_global,camwidth,camheight,framerate
        video_source_global=0
        # Video course will be camera
        self.video_source=0
        self.vid=Jetson_cam(camwidth,camheight,framerate, self.video_source)
        #self.vid = MyVideoCapture(camwidth, camheight,self.video_source)
        #return cv2.VideoCapture(0) # return the camera object
    
    
 # let's the user open up any kind of file from the computer with the GUI
    def open_file(self):
        """Function to select recorded file as the source of video"""
        global video_source_global,camwidth,camheight,framerate
        video_source_global=1
        self.window.fileName = askopenfilename(title="Select file")
        # print(self.master.fileName)
        if self.window.fileName:
            #change the vid source to the file opened for processing
            self.video_source=self.window.fileName
            #self.vid=Jetson_cam(camwidth,camheight,framerate, self.video_source)
            self.vid = MyVideoCapture(camwidth, camheight,self.video_source)


    # To open up the help document
    def open_help(self):
        help_add = "Help.txt"
        if help_add:
            os.startfile(help_add)
        else:
            tkm.showinfo('Message Info', "Sorry the help isn't available")

    # To open the wiring diagram
    def open_wiring_diag(self):
        diag_add = "wiring_diagram.jpg"
        if diag_add:
            os.startfile(diag_add)
        else:
            tkm.showinfo('Message Info', "Sorry the help isn't available")
            

# Create a window and pass it to the Application object
#App(tkinter.Tk(), "Tkinter and OpenCV",'channel_clip.mp4')
#App(tkinter.Tk(), "Tkinter and OpenCV",'trial9_Trim1.mp4')
App(tkinter.Tk(), "Tkinter and OpenCV")


