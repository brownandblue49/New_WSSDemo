from django.shortcuts import render
from django.http import HttpResponse  
import requests
from subprocess import run,PIPE
import os
from os.path import isfile
import sys
from django.views.generic import TemplateView
from wsinterfaceproject.functions.functions import handle_uploaded_file
from .forms import ProfileForm 
from django.core.files.storage import FileSystemStorage

import numpy as np
import cv2
import os
import sys
import shutil
import glob
from os import listdir
import math
import logging
from azure.storage.blob import BlockBlobService
from PIL import Image
from io import BytesIO
from datetime import datetime


def extractFrames(pathOut,filepath):
    print('Extracting frames')

    # Path to video file 
    cap = cv2.VideoCapture(filepath) 
    print(cap, isfile(filepath))
    #Reducing the frames per second of the video to 2
    cap.set(cv2.CAP_PROP_FPS, 2)   
    # Used as counter variable 
    x=1
    frameRate = cap.get(5) #frame rate
    numberOfPicturesPerSecond= 2
    blockBlobService = BlockBlobService(account_name='stworkersafety', account_key='7OyzTj7Y83+0/+DiuS9IVDoZcKrQ0pSjE4F4q8L/ltT+Dv4TbBXTSDrOu928L60SCzo7mq+P3fEv3B4aOL6Flw==')
    # start creating frames from video

    
    while(cap.isOpened()):
        print('Getting the frame')
        frameId = cap.get(1) #current frame number
        ret, frame = cap.read()
        if (ret != True):
            break

        # in case frame matches a multiple of the frame, create image
        if frameId  % math.floor(frameRate/numberOfPicturesPerSecond) == 0:
            logging.info("create cap" + str(x))
            # convert frame to PIL image
            frame_conv = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
            pilImage = Image.fromarray(frame_conv)
            #Calculate size = Height/2 * Width/2
            size = (round(pilImage.size[0]/2), round(pilImage.size[1]/2))
            #Resize using CV2
            pilImage = pilImage.resize(size, Image.ANTIALIAS)
            imgByteArr = BytesIO()
            pilImage.save(imgByteArr, format='jpeg')
            #print(type(pilImage))          
            imgByteArr = imgByteArr.getvalue()
            
            # write image to blob for logging
            now = datetime.strftime(datetime.now(), "%Y%m%dT%H%M%S%Z")
            imageFileName= 'epm_stage/image' +  str(int(x)) + "_img_" + now + ".jpg"
            #imageFileName= 'folder' + "/log/image" +  str(int(x)) + "_img.png"
            blockBlobService.create_blob_from_bytes('videoblob', imageFileName, imgByteArr)
            #Write to local directory
            pilImage.save(os.path.join(pathOut , "image{:d}".format(x))+now+".jpg")
            #cv2.imwrite(os.path.join(pathOut , "image{:d}.jpeg".format(x)),frame)
         # increment image
            x+=1
            
def uploadtoblob(filepath):
    block_blob_service = BlockBlobService(account_name='stworkersafety', account_key='7OyzTj7Y83+0/+DiuS9IVDoZcKrQ0pSjE4F4q8L/ltT+Dv4TbBXTSDrOu928L60SCzo7mq+P3fEv3B4aOL6Flw==')
    container_name ='videoblob\\epm_stage'

    #local_path = "D:\\Test\\test"

    for files in os.listdir(filepath):
        block_blob_service.create_blob_from_path(container_name,files,os.path.join(filepath,files),timeout=1000)   

# Create your views here.

def button(request):
    return render(request , 'home.html')

def home(request):
    return render(request , 'home.html')

def EPMFileUpload(request):
   return render(request, "EPMFileUpload.html")

def output(request):
    data = requests.get("https://reqres.in/api/users")    
    print(data.text)
    data = data.text
    return render(request , 'home.html' , {'data' : data})

def external(request):
    inp = request.POST.get('fileupload')
    filename = 'BreakSingleVideotoFrames.py'
    path = os.getcwd()+'\\'+filename
    print(path)
    if isfile(filename):
        print('Yup exists',type(filename))
    if isfile(path):
        print('Yup path exists', type(path))
    
    #run([sys.executable , filename, inp] ,shell=False ,stdout = PIPE) 
    media_path = './media/'
    frame_generated_path = './FramesGenerated/'
    for file_name in listdir(media_path):
            print(os.path.join('/media', file_name))
            file = os.path.join('/media', file_name)
            #file = media_path+file_name
            print(file)
            
            extractFrames(frame_generated_path , file )
   #uploadtoblob('./FramesGenerated')
   # out = "file submitted Successfully"
    return render(request , 'EPMFileUpload.html' )

def upload_file(request):  
    if request.method == 'POST': 
        uploaded_file = request.FILES['fileupload']
        fs = FileSystemStorage()
        fs.save(uploaded_file.name, uploaded_file)
        #print(uploaded_file.name)
        #print(uploaded_file.size)
        #profile = ProfileForm(request.POST, request.FILES)  
        #if profile.is_valid():  
        #    handle_uploaded_file(request.FILES['fileupload'])  
    #return HttpResponse("File uploaded successfuly")  
        return render(request,'EPMFileUpload.html')
        #return HttpResponse("File uploaded successfuly")

    else:  
    #    profile = ProfileForm()  
    #    return HttpResponse("Fuck") 
         print("nada")
        #return render(request,"EPMFileUpload.html",{'form':Profile})  
