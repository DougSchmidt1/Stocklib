# -*- coding: utf-8 -*-
"""
Created on Fri Jan 29 00:01:00 2021

@author: dougi
"""


# import cv2
# import numpy as np
# import os 
# from matplotlib import pyplot as plt
# print(os.getcwd())
# fig=plt.figure(0)
# img=r'C:\Users\dougi\Downloads\Doug.jpg'
# print(os.path.exists(img))
# img=cv2.imread(img)
# cv2.imshow('TEST WINDOW',img)


import numpy as np
import cv2

# multiple cascades: https://github.com/Itseez/opencv/tree/master/data/haarcascades

#https://github.com/Itseez/opencv/blob/master/data/haarcascades/haarcascade_frontalface_default.xml
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
#https://github.com/Itseez/opencv/blob/master/data/haarcascades/haarcascade_eye.xml
eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')

cap = cv2.VideoCapture(0)

while 1:
    ret, img = cap.read()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)