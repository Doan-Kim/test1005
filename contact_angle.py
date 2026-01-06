import pandas as pd
import os
import numpy as np
import cv2

# global variables
_imageno = 0
_contours = []
img_num = 0
_startframe = 0

def read_data(src,height,surface,degree,vis,num):
    print("Reading data...")
    savepath = src + str(height) + "CM_" + surface + "_" + str(degree) + "_"+str(vis)+"_" + num + "/_DATA.csv"
    Data = pd.read_csv(savepath)


def read_contourdata(src,height,surface,degree,vis,num,dev_show=False):
    global _imageno,_contours
    print("Reading contour data...")
    temppath = src + str(height) + "CM_" + surface + "_" + str(degree) + "_" + str(vis) + "_" + num + "/Contour Files/"
    file_lst = os.listdir(temppath)   
    contours = []
    _imageno = len(file_lst)-1
    for i in range(len(file_lst)):
        _src = temppath + 'Imagenumber_' + str(i) + '/'
        _file_list2 = os.listdir(_src)
        temp = []
        for k in range(len(_file_list2)):
            path = temppath + 'Imagenumber_' +  str(i) + "/" + _file_list2[k]
            if k > 0:
                t = np.load(path)
                temp.append(t)
            elif k == 0:
                temp = [np.load(path)]
            else:
                temp = None
                print('empty')
        if len(temp) > 0:
            contours.append(temp)
        else:
            contours.append(0)
    _contours = contours
    if dev_show:
        for i in range (len(_contours)):
            contour2binimage(_contours[i])
        print("End loading Contours")

def contour2binimage(ctr,dev_show=False):
    img = np.full((1024, 1024), 0, np.uint8)
    if ctr == 0:

        if dev_show:
            cv2.imshow('a',img)
            cv2.waitKey(1)
        return img
    img = cv2.drawContours(img,ctr,-1,255,-1)
    if dev_show:
        cv2.imshow('a', img)
        cv2.waitKey(1)
    return img

def show_contactangle(shutdown_Key):
    global img_num
    cv2.destroyAllWindows()
    cv2.namedWindow("TRIM")
    starthitFrame = 0
    cv2.createTrackbar("frame", "TRIM", starthitFrame, _imageno, _trackbar)
    cv2.setTrackbarMin("frame", "TRIM", starthitFrame)
    cv2.setTrackbarMax("frame", "TRIM", _imageno)
    while cv2.waitKey(1) != ord(shutdown_Key):
        _img = contour2binimage(_contours[img_num])
        cv2.imshow("TRIM", _img)


    def _trackbar(x):
        img_num = cv2.getTrackbarPos("frame", "TRIM")

def get_contactangle_contour():
    print("")