import pandas as pd
import os
import cv2
import numpy as np
import tracemalloc
import time
import threading
from multiprocessing import Pool
import matplotlib.pyplot as plt
import gc
ticktime = []
tickname = []
img_num = 0
Val2 = 0
C_num = 450
YLocation = 0
img0_draw = 0
StartFrame = 0
EndFrame = 1
kernelsize = 1
kernelsize2 = 1
thresholdvalue = 128
def readcontour(ctr):
    img = np.full((1024, 1024, 3), (255, 255, 255), np.uint8)
    for i in range(len(ctr)):
        for j in range(len(ctr[i])):
            tempx = ctr[i][j][0][0]
            tempy = ctr[i][j][0][1]
            cv2.line(img, (tempx, tempy), (tempx, tempy), (0, 0, 0), 1)
    cv2.imshow('a',img)
    cv2.waitKey(100)
    return 0
def contour2binimage(ctr):
    img = np.full((1024, 1024), 0, np.uint8)
    if ctr == 0:
        #cv2.imshow('a',img)
        #cv2.waitKey(1)
        return img
    img = cv2.drawContours(img,ctr,-1,255,-1)
    #cv2.imshow('a', img)
    #cv2.waitKey(1)
    return img
def contour2points(ref):
    ctr = ref[0]
    listx = []
    listy = []
    for i in range(len(ctr)):
        ax = ctr[i][0]
        ay = ctr[i][1]
        listx.append(ax)
        listy.append(ay)
    return listx, listy
def detect_Diameter(ref):
    Image = ref[0]
    a1 = ref[1]
    b1 = ref[2]
    impactx = ref[3]
    impacty = ref[4]
    w, h, c = Image.shape
    horizonline = get_horizonline(a1, b1, w)
    pointLref = (0, b1)
    pointRref = (1024, int(a1 * 1024 + b1))
    pointL = [0, 0]
    pointR = [0, 0]
    pointRim = [0, 0]
    LengthL, LengthR = 0, 0
    # Image must be binary image (channel 3)
    bin_Image = cv2.cvtColor(Image, cv2.COLOR_BGR2GRAY)
    contour, _ = cv2.findContours(bin_Image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    mma = np.zeros(len(contour))
    if len(contour) == 0:
        print("zero contour")
        return [0, 0]
    marea = 0
    refx, refy = 0, 0
    for a in range(len(contour)):
        if len(contour[a]) < 30:
            continue
        area = cv2.contourArea(contour[a])
        M = cv2.moments(contour[a])

        for b in range(len(contour[a])):
            ax = contour[a][b][0][0]
            ay = contour[a][b][0][1]
            d = point2line([ax, ay], [a1, b1])
            if d <= 3 and len(contour[a]) > 30:
                mma[a] = 1

        if marea < area and mma[a] == 1:
            marea = area
            refx, refy = int(M['m10'] / M['m00']), int(M['m01'] / M['m00'])
    mdL, mdR = 99999999, 99999999
    maL, mbL = 0, 0
    maR, mbR = 0, 0
    rimD = 0

    for a in range(len(contour)):
        if mma[a] == 1:
            for b in range(len(contour[a])):
                ax = contour[a][b][0][0]
                ay = contour[a][b][0][1]
                temp = (ax, ay)
                dL = point2point(temp, pointLref)
                dR = point2point(temp, pointRref)
                D = point2line([ax, ay], [a1, b1])
                val = a1 * ax + b1 - ay
                if ax < refx and dL < mdL and D <= 3:
                    mdL = dL
                    maL, mbL = a, b
                    pointL = [ax, ay]
                if ax > refx and dR < mdR and D <= 3:
                    mdR = dR
                    maR, mbR = a, b
                    pointR = [ax, ay]
                if val >= 0 and D > rimD:
                    rimD = D
                    pointRim = [ax, ay]
    '''
    for x in range(0,w):
        if Image[horizonline[x][1],horizonline[x][0]].mean() > 128:
            mx = horizonline[x][0]
            my = horizonline[x][1]
            if pointL[0] > mx:
                pointL = [mx,my]
            elif impactx < mx and pointR[0] < mx:
                pointR = [mx,my]
    '''

    LengthL = np.sqrt((impactx - pointL[0]) ** 2 + (impacty - pointL[1]) ** 2)
    LengthR = np.sqrt((impactx - pointR[0]) ** 2 + (impacty - pointR[1]) ** 2)
    if impactx < pointL[0]:
        LengthL *= -1
    Image = cv2.circle(Image, (int(impactx), int(impacty)), 3, (0, 255, 0), 5)
    Image = cv2.circle(Image, (int(pointL[0]), int(pointL[1])), 3, (0, 0, 255), 5)
    Image = cv2.circle(Image, (int(pointR[0]), int(pointR[1])), 3, (255, 0, 0), 5)
    Image = cv2.circle(Image, (refx, refy), 3, (255, 255, 0), 5)
    Image = cv2.circle(Image, (int(pointRim[0]), int(pointRim[1])), 3, (255, 0, 255), 5)

    # cv2.imshow("aa",Image)
    # cv2.waitKey(10)

    return [pointL, pointR, LengthL, LengthR, rimD]
def detect_Diameter_contour(ref):
    contour = ref[0]
    a1 = ref[1]
    b1 = ref[2]
    impactx = ref[3]
    impacty = ref[4]
    nowi = ref[5]
    #horizonline = get_horizonline(a1, b1, 1024)
    pointLref = (0, b1)
    pointRref = (1024, int(a1 * 1024 + b1))
    pointL = [0, 0]
    pointR = [0, 0]
    pointRim = [0, 0]
    LengthL, LengthR = 0, 0
    # Image must be binary image (channel 3)
    mma = np.zeros(len(contour))
    if len(contour) == 0:
        print("zero contour")
        return [0, 0]
    marea = 0
    refx, refy = 0, 0
    for a in range(len(contour)):
        if len(contour[a]) < 30:
            continue
        area = cv2.contourArea(contour[a])
        M = cv2.moments(contour[a])

        for b in range(len(contour[a])):
            ax = contour[a][b][0][0]
            ay = contour[a][b][0][1]
            d = point2line([ax, ay], [a1, b1])
            if d <= 3 and len(contour[a]) > 30:
                mma[a] = 1

        if marea < area and mma[a] == 1:
            marea = area
            refx, refy = int(M['m10'] / M['m00']), int(M['m01'] / M['m00'])
    mdL, mdR = 99999999, 99999999
    maL, mbL = 0, 0
    maR, mbR = 0, 0
    rimD = 0

    for a in range(len(contour)):
        if mma[a] == 1:
            for b in range(len(contour[a])):
                ax = contour[a][b][0][0]
                ay = contour[a][b][0][1]
                temp = (ax, ay)
                dL = point2point(temp, pointLref)
                dR = point2point(temp, pointRref)
                D = point2line([ax, ay], [a1, b1])
                val = a1 * ax + b1 - ay
                if ax < refx and dL < mdL and D <= 3:
                    mdL = dL
                    maL, mbL = a, b
                    pointL = [ax, ay]
                if ax > refx and dR < mdR and D <= 3:
                    mdR = dR
                    maR, mbR = a, b
                    pointR = [ax, ay]
                if val >= 0 and D > rimD:
                    rimD = D
                    pointRim = [ax, ay]
    '''
    for x in range(0,w):
        if Image[horizonline[x][1],horizonline[x][0]].mean() > 128:
            mx = horizonline[x][0]
            my = horizonline[x][1]
            if pointL[0] > mx:
                pointL = [mx,my]
            elif impactx < mx and pointR[0] < mx:
                pointR = [mx,my]
    '''

    LengthL = np.sqrt((impactx - pointL[0]) ** 2 + (impacty - pointL[1]) ** 2)
    LengthR = np.sqrt((impactx - pointR[0]) ** 2 + (impacty - pointR[1]) ** 2)
    if impactx < pointL[0]:
        LengthL *= -1


    Image = contour2binimage(contour)
    Image = cv2.cvtColor(Image, cv2.COLOR_GRAY2BGR)
    Image = cv2.circle(Image, (int(impactx), int(impacty)), 3, (0, 255, 0), 5)
    Image = cv2.circle(Image, (int(pointL[0]), int(pointL[1])), 3, (0, 0, 255), 5)
    Image = cv2.circle(Image, (int(pointR[0]), int(pointR[1])), 3, (255, 0, 0), 5)
    Image = cv2.circle(Image, (refx, refy), 3, (255, 255, 0), 5)
    Image = cv2.circle(Image, (int(pointRim[0]), int(pointRim[1])), 3, (255, 0, 255), 5)
    cv2.imshow("aa",Image)
    cv2.waitKey(1)

    return [pointL, pointR, LengthL, LengthR, rimD]
def detect_Rimheight(ref):
    Image = ref[0]
    a = ref[1]
    b = ref[2]
def detect_Diameter_Velocity(ref):
    image2 = ref[0]
    points2 = ref[1]

    _imagecon2 = image2
    cv2.fillConvexPoly(_imagecon2, points2, (255, 255, 255))
    _img2 = cv2.GaussianBlur(_imagecon2, (33, 33), sigmaX=0, sigmaY=0)
    _img2 = cv2.cvtColor(_img2, cv2.COLOR_RGB2GRAY)
    _, temp2 = cv2.threshold(_img2, 20, 255, cv2.THRESH_BINARY_INV)
    contour2, _ = cv2.findContours(temp2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    reval = []
    # ---- contour 2 용도-----
    if len(contour2) == 0:
        reval = [(0, 0, 0)]
    else:
        marea, ma, _mcx, _mcy = 0, 0, 0, 0
        for a in range(len(contour2)):
            if len(contour2[a]) < 5:
                reval = [(0, 0, 0)]
            _area = cv2.contourArea(contour2[a])
            if marea < _area:
                marea = _area
                ma = a
                M = cv2.moments(contour2[a])
                _mcx = int(M["m10"] / M["m00"])
                _mcy = int(M["m01"] / M["m00"])
        reval = ([fit_circle(contour2data(contour2[ma]))])
    [(cx, cy, cr)] = reval
    image = cv2.circle(image2, (int(cx), int(cy)), int(cr), (0, 255, 0), 5)
    return [reval]
def detect_Diameter_Velocity_onlycontour(ref):
    contours = ref[0]
    points2 = ref[1]

    contour2 = contours
    reval = []
    # ---- contour 2 용도-----
    if contour2 == 0:
        reval = [(0, 0, 0)]
        return [reval]
    else:
        marea, ma, _mcx, _mcy = 0, 0, 0, 0
        for a in range(len(contour2)):
            if len(contour2[a]) < 5:
                reval = [(0, 0, 0)]
            _area = cv2.contourArea(contour2[a])
            if marea < _area:
                marea = _area
                ma = a
                M = cv2.moments(contour2[a])
                _mcx = int(M["m10"] / M["m00"])
                _mcy = int(M["m01"] / M["m00"])
        reval = ([fit_circle(contour2data(contour2[ma]))])
    [(cx, cy, cr)] = reval
    #image = cv2.circle(image2, (int(cx), int(cy)), int(cr), (0, 255, 0), 5)
    return [reval]
def get_horizonline(a, b, w):
    h = []
    for x in range(w):
        y = int(a * x + b)
        if y < 0:
            y = 0
        if y > 1023:
            y = 1023
        h.append([x, y])
    return h
def detect_lineonpoint(image, a, b, w, h):
    horizonline = get_horizonline(a, b, w)
    for x in range(0, w):
        if image[horizonline[x][1], horizonline[x][0]].mean() > 128:
            return True
    return False
def contour2linepoint(contour,a,b,mdis):
    '''
    :param contour: contour
    :param a: line A
    :param b: line B
    :param mdis: minimum distance
    :return: contour hit line average point (x,y). if didn't hit on the line, return (-1,-1)
    '''
    memi = 0
    memx = []
    memy = []
    memdis = 9999999999
    if contour == 0:
        return (-1,-1)

    # testbin = contour2binimage(contour)
    # testbin = cv2.cvtColor(testbin, cv2.COLOR_GRAY2RGB)
    for k in range(len(contour)):
        for i in range(len(contour[k])):
            _tempx = contour[k][i][0][0]
            _tempy = contour[k][i][0][1]
            dis = point2line([_tempx,_tempy],[a,b])
            '''
            testbin = cv2.circle(testbin,(int(_tempx),int(_tempy)),1,(0,0,255),5)
            testbin = cv2.line(testbin,(int(0),int(b)),(int(1024),int(1024*a+b)),(255,0,0),5)
            print("distance :",dis)
            cv2.imshow("aa",testbin)
            cv2.waitKey(1)
            '''
            if mdis > dis:
                memi = i
                memx.append(_tempx)
                memy.append(_tempy)
                memdis = dis

                # testbin = cv2.circle(testbin,(int(_tempx),int(_tempy)),1,(0,0,255),5)

        _x = np.mean(memx)
        _y = np.mean(memy)
    if memi == 0 or memdis > mdis:
        return (-1,-1)
    #print(memdis)

    # cv2.imshow("aa",testbin)
    # cv2.waitKey(0)

    return (_x,_y)
def detect_impactpoint(image, a, b, w):
    horizonline = get_horizonline(a, b, w)
    mx = []
    my = []
    for x in range(0, w):
        if image[horizonline[x][1], horizonline[x][0]].mean() > 128:
            mx.append(horizonline[x][0])
            my.append(horizonline[x][1])
    X = np.mean(mx)
    Y = np.mean(my)
    return (X, Y)
def heavywork(image, alpha):
    # re = np.clip((1+alpha)*image-128-alpha,0,255).astype(np.uint8)
    re = np.core.umath.maximum(np.core.umath.minimum((1 + alpha) * image - 128 - alpha, 255), 0).astype(np.uint8)
    return re
def src_list(src, type):
    '''
    this function make Images set's src list by 2D array(list) form.
    [ folder 0, image 0, ... ,image 1000
      ...
      folder n, image 0, ... ,image 1000]

    src : def its searching src. it must be string type.
    type : set image type or file type. it must be string type. ex) asdf.PNG <-- "PNG" is type.
    def_show : boolean type. if check is TRUE, it show the windows form to check what you use in folder. if FLASE, it takes all file in this folder.

    '''
    src_fulllist = []
    file_lst = os.listdir(src)
    print(file_lst[0], "and", len(file_lst) - 1, "other files.")
    tickrecord("", "start_read_src")
    for z in range(len(file_lst)):
        # reset list
        src_list = []
        path = src + file_lst[z]
        file_lst2 = os.listdir(path)
        score = 0
        for file in file_lst2:
            # if score > 700:
            #       continue
            if type in file:
                filepath = path + '/' + file
                src_list.append(filepath)
                score += 1

        src_fulllist.append(src_list)
    print(tickrecord("start_read_src", "end_read_src"), '\t sec read src list')
    return src_fulllist, file_lst
def point2line(point, line):
    '''
    :param point: [x,y]
    :param line:  [a,b,c], ax+by+c = 0
    :return: distance for sqrt
    '''
    x = point[0]
    y = point[1]
    a = line[0]
    b = -1
    c = line[1]
    return (abs(a * x + b * y + c) / np.sqrt(a * a + b * b))
def point2point(point1, point2):
    (x1, y1) = point1
    (x2, y2) = point2
    return np.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
def src2image2(src, channel, result, index):
    if channel == 3:
        image = cv2.imread(src, cv2.IMREAD_GRAYSCALE)
    else:
        image = cv2.imread(src, cv2.IMREAD_COLOR)
    image = cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)
    result[index] = image
    print(src)
def src2image(src, channel, name):
    '''
    this function take src list in each image to return image list.

    src : def its images src list.
    channel : integer type. it define image's channel. if 3 -> RGB color, 1 -> Grayscale color.
    '''
    imagelist = []
    tickrecord("", "start_read_img2" + name)
    for i in range(len(src)):
        image = 0
        if channel == 1:
            image = cv2.imread(src[i], cv2.IMREAD_GRAYSCALE)
        else:
            image = cv2.imread(src[i], cv2.IMREAD_COLOR)
        imagelist.append(image)
        # per = str(round(i/len(src)*100,1))
        # print("\r",per,"%",end="")
    # print("\r")

    print(tickrecord("start_read_img2" + name, "end_read_img"), '\t sec read image list')
    return imagelist
def fit_circle(data):
    # data [[x1,y],[x2,y2]...]
    # data is contour[0]

    xs = []
    ys = []
    for i in range(len(data)):
        xs.append(data[i][0])
        ys.append(data[i][1])
    xs = np.array(xs, dtype=np.float64)
    ys = np.array(ys, dtype=np.float64)
    J = np.mat(np.vstack((-2 * xs, -2 * ys, np.ones_like(xs, dtype=np.float64))))
    J = J.T
    Jp = np.linalg.pinv(J)
    Y = np.mat(-xs ** 2 - ys ** 2)
    X = Jp * Y.T
    # X = (J.T * J).I * J.T * Y.T

    cx = X[0, 0]
    cy = X[1, 0]
    c = X[2, 0]
    r = np.sqrt(cx ** 2 + cy ** 2 - c)
    return (cx, cy, r)
def contour2data(contour):
    _xy = []
    for b in range(len(contour)):
        _tempx = contour[b][0][0]
        _tempy = contour[b][0][1]
        _xy.append([_tempx, _tempy])
    return _xy
def detect_ContactAngle(ref):
    Image = ref[0]
    bin_Image = cv2.cvtColor(Image, cv2.COLOR_BGR2GRAY)
    a1 = ref[1]
    b1 = ref[2]

    pointL = (ref[3][0], ref[3][1])
    pointR = (ref[4][0], ref[4][1])
    mpointL = [ref[3][0], ref[3][1]]
    mpointR = [ref[4][0], ref[4][1]]
    maxspreadingTime = ref[5]
    current_i = ref[6]
    ImpactDeg = ref[7]
    _scalenumber = ref[8]
    w, h, c = Image.shape
    horizonline = get_horizonline(a1, b1, w)

    contactNumber = 80
    badLR = 0
    contour, _ = cv2.findContours(bin_Image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    memcL = []
    memcR = []
    if len(contour) == 0:
        print("zero contour")
        return [0, 0]
    maL, mbL = 0, 0
    maR, mbR = 0, 0
    md = 99999999
    memPoints = []
    for a in range(len(contour)):
        if len(contour[a]) < contactNumber:
            continue
        for b in range(len(contour[a])):
            ax = contour[a][b][0][0]
            ay = contour[a][b][0][1]
            d = point2point(pointL, (ax, ay))
            if d <= md:
                maL = a
                mbL = b
                md = d
    md = 99999999
    for a in range(len(contour)):
        if len(contour[a]) < contactNumber:
            continue
        for b in range(len(contour[a])):
            ax = contour[a][b][0][0]
            ay = contour[a][b][0][1]
            d = point2point(pointR, (ax, ay))
            if d <= md:
                maR = a
                mbR = b
                md = d
    if maL == maR:
        a = maL
        for b in range(len(contour[maL])):
            ax = contour[a][b][0][0]
            ay = contour[a][b][0][1]
            memPoints.append([ax, ay])
    else:
        a = maL
        for b in range(len(contour[maL])):
            ax = contour[a][b][0][0]
            ay = contour[a][b][0][1]
            memPoints.append([ax, ay])
        a = maR
        for b in range(len(contour[maR])):
            ax = contour[a][b][0][0]
            ay = contour[a][b][0][1]
            memPoints.append([ax, ay])

    th = ImpactDeg * np.pi / 180
    _Diameter = np.sqrt((pointL[0] - pointR[0]) ** 2 + (pointL[1] - pointR[1]) ** 2) * _scalenumber
    # print(_Diameter)
    badLR = 0

    contactL = []
    contactR = []
    for k in range(contactNumber):
        tempk = mbL - k
        if mbL - k < 0:
            tempk = mbL - k + len(contour[maL])
        if len(contour[maL]) < contactNumber:
            print("low contactnumber L", len(contour[maL]), current_i)
            return [0, 0, 1, memPoints]
        tempy = contour[maL][tempk][0][1]
        tempx = contour[maL][tempk][0][0]
        contactL.append([tempx, tempy])
        cv2.line(Image, (int(tempx), int(tempy)), (int(tempx), int(tempy)), (0, 255, 0), 1)
    for k in range(contactNumber):
        tempk = mbR + k
        if tempk >= len(contour[maR]):
            tempk = tempk - len(contour[maR])
        if len(contour[maR]) < contactNumber:
            print("low contactnumber R", len(contour[maR]), current_i)
            return [0, 0, 1, memPoints]
        tempy = contour[maR][tempk][0][1]
        tempx = contour[maR][tempk][0][0]
        contactR.append([tempx, tempy])
        cv2.line(Image, (int(tempx), int(tempy)), (int(tempx), int(tempy)), (0, 255, 0), 1)
    txL = []
    tyL = []
    txR = []
    tyR = []
    for k in range(len(contactL)):
        txL.append(contactL[k][0])
        tyL.append(contactL[k][1])
        txR.append(contactR[k][0])
        tyR.append(contactR[k][1])
    fit3L = np.polyfit(txL, tyL, 3)
    fit3R = np.polyfit(txR, tyR, 3)
    fitPLx = []
    fitPRx = []
    fitPLy = []
    fitPRy = []
    cv2.circle(Image, (pointL[0], pointL[1]), 10, (255, 255, 0), 5)
    cv2.circle(Image, (pointR[0], pointR[1]), 10, (255, 255, 0), 5)
    for z in range(0, 512):
        dx = z
        dy = fit3L[0] * pow(dx, 3) + fit3L[1] * pow(dx, 2) + fit3L[2] * dx + fit3L[3]
        fitPLx.append(dx)
        fitPLy.append(dy)
        cv2.line(Image, (int(dx), int(dy)), (int(dx), int(dy)), (255, 0, 255), 1)
    for z in range(512, 1024):
        dx = z
        dy = fit3R[0] * pow(dx, 3) + fit3R[1] * pow(dx, 2) + fit3R[2] * dx + fit3R[3]
        fitPRx.append(dx)
        fitPRy.append(dy)
        cv2.line(Image, (int(dx), int(dy)), (int(dx), int(dy)), (255, 0, 255), 1)
    cL, CR = 0, 0
    if current_i < maxspreadingTime:
        dx = pointL[0]
        dyL1 = fit3L[0] * pow(dx, 3) + fit3L[1] * pow(dx, 2) + fit3L[2] * dx + fit3L[3]
        dx = pointL[0] + 3
        dyL2 = fit3L[0] * pow(dx, 3) + fit3L[1] * pow(dx, 2) + fit3L[2] * dx + fit3L[3]

        cL = -np.arctan((dyL2 - dyL1) / 3)
        dx = pointR[0]
        dyR1 = fit3R[0] * pow(dx, 3) + fit3R[1] * pow(dx, 2) + fit3R[2] * dx + fit3R[3]
        dx = pointR[0] - 3
        dyR2 = fit3R[0] * pow(dx, 3) + fit3R[1] * pow(dx, 2) + fit3R[2] * dx + fit3R[3]
        cR = np.arctan((-dyR2 + dyR1) / 3)

        dxsL = -30 * np.cos(cL) + pointL[0]
        dysL = +30 * np.sin(cL) + pointL[1]
        dxeL = +30 * np.cos(cL) + pointL[0]
        dyeL = -30 * np.sin(cL) + pointL[1]
        dxsR = -30 * np.cos(cR) + pointR[0]
        dysR = -30 * np.sin(cR) + pointR[1]
        dxeR = +30 * np.cos(cR) + pointR[0]
        dyeR = +30 * np.sin(cR) + pointR[1]
        cL = cL * 180 / np.pi + 90
        cR = cR * 180 / np.pi + 90
    else:
        cLNum = 15
        cRNum = 15
        if pointL[0] == contactL[cLNum][0]:
            for i in range(10, 30):
                if pointL[0] != contactL[i][0]:
                    cLNum = i
                    break
        if pointR[0] == contactR[cRNum][0]:
            for i in range(10, 30):
                if pointR[0] != contactR[i][0]:
                    cRNum = i
                    break

        tanL = (pointL[1] - contactL[cLNum][1]) / (pointL[0] - contactL[cLNum][0])
        tanR = (pointR[1] - contactR[cRNum][1]) / (pointR[0] - contactR[cRNum][0])

        # cv2.line(Image,(int(pointL[0]),int(pointL[1])),(int(contactL[15][0]),int(contactL[15][1])),(255,0,0),5)
        # cv2.line(Image,(int(pointR[0]),int(pointR[1])),(int(contactR[15][0]),int(contactR[15][1])),(255,0,0),5)

        cL = -np.arctan((pointL[1] - contactL[cLNum][1]) / (pointL[0] - contactL[cLNum][0]))
        cR = +np.arctan((pointR[1] - contactR[cRNum][1]) / (pointR[0] - contactR[cRNum][0]))

        dxsL = -30 * np.cos(cL) + pointL[0]
        dysL = +30 * np.sin(cL) + pointL[1]
        dxeL = +30 * np.cos(cL) + pointL[0]
        dyeL = -30 * np.sin(cL) + pointL[1]
        dxsR = -30 * np.cos(cR) + pointR[0]
        dysR = -30 * np.sin(cR) + pointR[1]
        dxeR = +30 * np.cos(cR) + pointR[0]
        dyeR = +30 * np.sin(cR) + pointR[1]
        cL = cL * 180 / np.pi
        cR = cR * 180 / np.pi

        # cv2.line(Image,(int(dxsL),int(dysL)),(int(dxsL),int(dysL)),(128,128,0),5)
        # cv2.line(Image,(int(dxeL),int(dyeL)),(int(dxeL),int(dyeL)),(128,0,128),5)
        # cv2.line(Image,(int(dxsR),int(dysR)),(int(dxsR),int(dysR)),(255,0,0),5)
        # cv2.line(Image,(int(dxeR),int(dyeR)),(int(dxeR),int(dyeR)),(255,0,0),5)

    cv2.line(Image, (int(dxsL), int(dysL)), (int(dxeL), int(dyeL)), (0, 0, 255), 1)
    cv2.line(Image, (int(dxsR), int(dysR)), (int(dxeR), int(dyeR)), (0, 0, 255), 1)
    # cv2.imshow("aa",Image)
    # cv2.waitKey(1)
    # print(cL,cR)
    sw1 = 0
    if cL < 0:
        cL = abs(cL)
        sw1 = 1
    if cR < 0:
        cR = abs(cR)
        sw1 = 1
    if sw1 == 1:
        return [cL, cR, 1, memPoints]
    return [cL, cR, 0, memPoints]
    _xy = []
    for b in range(len(contour)):
        _tempx = contour[b][0][0]
        _tempy = contour[b][0][1]
        _xy.append([_tempx, _tempy])
    return _xy
def makedirs(path):
    if not os.path.exists(path):
        os.makedirs(path)
def tickrecord(start_name, tick_name):
    end_time = time.time()
    ticktime.append(end_time)
    tickname.append(tick_name)
    if start_name == "":
        return
    else:
        temp = tickname.index(start_name)
        val = end_time - ticktime[temp]
        return round(val, 1)
def findendofpoints(pts,angle):
    maxi = len(pts)
    mems = 99999999
    memi = 0
    result = []
    for i in range(0,maxi):
        temp = np.sqrt(pow(pts[i][0] * np.cos(np.pi/180*angle),2) + pow(pts[i][1] * np.sin(np.pi/180*angle),2))
        if mems > temp:
            mems = temp
            memi = i
    result.append([pts[memi][0], pts[memi][1]])
    mems = 0
    memi = 0
    for i in range(0,maxi):
        temp = np.sqrt(pow(pts[i][0] * np.cos(np.pi/180*angle),2) + pow(pts[i][1] * np.sin(np.pi/180*angle),2))
        if mems < temp:
            mems = temp
            memi = i
    result.append([pts[memi][0], pts[memi][1]])
    return result
def findendofpoints2(pts,angle):
    maxi = len(pts)
    mems = 99999999
    memi = 0
    result = []
    for i in range(0,maxi):
        temp = pts[i][0]*np.cos(np.pi/180*angle)-pts[i][1]*np.sin(np.pi/180*angle)
        if mems > temp:
            mems = temp
            memi = i
    result.append([pts[memi][0], pts[memi][1]])
    mems = 0
    memi = 0
    for i in range(0,maxi):
        temp = pts[i][0]*np.cos(np.pi/180*angle)-pts[i][1]*np.sin(np.pi/180*angle)
        if mems < temp:
            mems = temp
            memi = i
    result.append([pts[memi][0], pts[memi][1]])
    return result
def points2linefunction(points):
    px1 = points[0][0]
    py1 = points[0][1]
    px2 = points[1][0]
    py2 = points[1][1]
    dx = (px2 - px1)
    dy = (py2 - py1)
    a,b = 0,0
    if dx == 0:
        a = 0
        b = py1
    else:
        a = dy/dx
        b = py1-a*px1
    return a,b
def memorycapture():
    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics('lineno')
    print("[ Top 10 ]")
    for stat in top_stats[:10]:
        print(stat)

class HighSpeedImage:
    Contrastnumber = 0

    def __init__(self, Image):
        self._image = Image
        self._image_con = []
        self._imageno = len(self._image)
        self._alpha = 0
        self._alpha2 = 0
        self._val2 = 0
        self._horizonLine_A = 0
        self._horizonLine_B = 0
        self._sx0 = 0
        self._sx1 = 0
        self._sy0 = 0
        self._sy1 = 0
        self.circlefit = []
        self.circlefit2 = []
        self._time_startfall = 0
        self._time_impact = 0
        self._time_maxspreading = 0
        self._impactDeg = 0
        self._Diameter = 0
        self._Velocity = 0
        self._onDiameter = []
        self._onDiameterL = []
        self._onDiameterR = []
        self._maxDiameter = 0
        self._impactpoint_x = 0
        self._impactpoint_y = 0
        self._Errornum = 0
        self._name = ""
        self._savepath = ""
        self._LeftAngle = []
        self._RightAngle = []
        self._onVelocityL = []
        self._onVelocityR = []
        self._ondVL = []
        self._ondVR = []
        self._onRim = []
        self._imagepoints = []
        self._scalenumber = 0
        self._sw_quick = False
        self._path2 = []
        self._path3 = []
        self._reflect1 = 0
        self._reflect2 = 0
        self._kernelsize = 0
        self._thresholdvalue = 0
        self._startframe = 0
        self._endframe = 0
        self._date = 0
        self._height = 0
        self._size = 0
        self._surface = 0
        self._degree = 0
        self._viscosity = 0
        self._number = 0
        self._groundA = 0
        self._groundB = 0
        self._contours = []
    def loadto(self,src,height,surface,degree,viscosity,number):
        savepath = src + str(height) + "CM_" + surface + "_" + str(degree) + "_"+str(viscosity)+"_" + number + "/_DATA.csv"
        Data = pd.read_csv(savepath)
        self._alpha = int(Data['alpha'].iloc[0])
        self._alpha2 = float(Data['alpha2'].iloc[0])
        self._val2 = int(Data['val2'].iloc[0])
        self._sx0 = int(Data['sx0'].iloc[0])
        self._sx1 = int(Data['sx1'].iloc[0])
        self._sy0 = int(Data['sy0'].iloc[0])
        self._sy1 = int(Data['sy1'].iloc[0])
        self._time_startfall = int(Data['timestartfall'].iloc[0])
        self._time_impact = int(Data['timeimpact'].iloc[0])
        self._time_maxspreading = int(Data['timemaxspreading'].iloc[0])
        self._impactDeg = float(Data['impactDeg'].iloc[0])
        self._Diameter = int(Data['Diameter'].iloc[0])
        self._Velocity = int(Data['Velocity'].iloc[0])
        self._maxDiameter = int(Data['maxDiameter'].iloc[0])
        self._impactpoint_x = int(Data['impactpoint_x'].iloc[0])
        self._impactpoint_y = int(Data['impactpoint_y'].iloc[0])
        self._Errornum = int(Data['Errornum'].iloc[0])
        self._name = Data['name'].iloc[0]
        self._scalenumber = float(Data['scalenumber'].iloc[0])
        self._sw_quick = bool(Data['sw_quick'].iloc[0])
        self._reflect1 = int(Data['reflect1'].iloc[0])
        self._reflect2 = int(Data['reflect2'].iloc[0])
        self._kernelsize = int(Data['kernelsize'].iloc[0])
        self._startframe = int(Data['startframe'].iloc[0])
        self._endframe = int(Data['endframe'].iloc[0])
        self._date = int(Data['date'].iloc[0])
        self._height = int(Data['height'].iloc[0])
        self._size = int(Data['size'].iloc[0])
        self._surface = Data['surface'].iloc[0]
        self._degree = int(Data['degree'].iloc[0])
        self._viscosity = int(Data['viscosity'].iloc[0])
        self._number = int(Data['number'].iloc[0])
        self._groundA = float(Data['groundA'].iloc[0])
        self._groundB = float(Data['groundB'].iloc[0])

        self._horizonLine_A = self._groundA
        self._horizonLine_B = self._groundB
        self._sx0 = 0
        self._sx1 = int(1024)
        self._sy0 = int(self._groundB + 3)
        self._sy1 = int(self._groundA * 1024 + self._groundB + 3)
        self._impactDeg = 90 - np.arctan2(1, self._groundA) * 180 / np.pi


        print(Data)
        print("load complete!")
    def saveto(self,savepathto):
        data = pd.DataFrame([self._alpha], columns=['alpha'])
        data['alpha2'] = [self._alpha2]
        data['val2'] = [self._val2]
        data['horizonLineA'] = [self._horizonLine_A]
        data['horizonLineB'] = [self._horizonLine_B]
        data['sx0'] = [self._sx0]
        data['sx1'] = [self._sx1]
        data['sy0'] = [self._sy0]
        data['sy1'] = [self._sy1]
        data['timestartfall'] = [self._time_startfall]
        data['timeimpact'] = [self._time_impact]
        data['timemaxspreading'] = [self._time_maxspreading]
        data['impactDeg'] = [self._impactDeg]
        data['Diameter'] = [self._Diameter]
        data['Velocity'] = [self._Velocity]
        data['maxDiameter'] = [self._maxDiameter]
        data['impactpoint_x'] = [self._impactpoint_x]
        data['impactpoint_y'] = [self._impactpoint_y]
        data['Errornum'] = [self._Errornum]
        data['name'] = [self._name]
        data['imagepoints'] = [self._imagepoints]
        data['scalenumber'] = [self._scalenumber]
        data['sw_quick'] = [self._sw_quick]
        data['reflect1'] = [self._reflect1]
        data['reflect2'] = [self._reflect2]
        data['kernelsize'] = [self._kernelsize]
        data['thresholdvalue'] = [self._thresholdvalue]
        data['startframe'] = [self._startframe]
        data['endframe'] = [self._endframe]
        data['date'] = [self._date]
        data['height'] = [self._height]
        data['size'] = [self._size]
        data['surface'] = [self._surface]
        data['degree'] = [self._degree]
        data['viscosity'] = [self._viscosity]
        data['number'] = [self._number]
        data['groundA'] = [self._groundA]
        data['groundB'] = [self._groundB]


        temppath = savepathto + str(self._height) + "CM_" + str(self._surface) + "_" + str(self._degree) + "_"+ str(self._viscosity)  +"_00" + str(int(self._number))
        makedirs(temppath)
        data.to_csv(temppath + "/_DATA.csv", index=False)
    def savebinimages(self,savepath2):
        for i in range(self._imageno):
            img_bac = self._image[i].copy()
            _img2_blured = cv2.GaussianBlur(img_bac, (self._kernelsize, self._kernelsize), sigmaX=0, sigmaY=0)
            _img2_blured = cv2.cvtColor(_img2_blured, cv2.COLOR_RGB2GRAY)
            x1, y1 = 0, int(self._groundB)
            x2, y2 = 1023, int(self._groundA * 1023 + self._groundB)
            points = np.array([[0, 1023], [1023, 1023], [x2, y2], [x1, y1],
                               [0, 1023]], dtype=np.int32)
            cv2.fillConvexPoly(_img2_blured, points, (255, 255, 255))
            b_img = np.clip((1 + self._alpha2) * _img2_blured - 128 - self._alpha2, 0, 255).astype(np.uint8)
            _, bin_img = cv2.threshold(b_img, 20, 255, cv2.THRESH_BINARY_INV)

            temppath = savepath2 + self._height + "CM_" + self._surface + "_" + self._degree + "_" + self._number
            makedirs(temppath)
    def saveContours(self,savepath2):
        temppath = savepath2 + str(self._height) + "CM_" + str(self._surface) + "_" + str(self._degree) + "_" + str(self._viscosity) + "_00" + str(int(self._number))
        temppath = temppath +"/Binary Images/"
        makedirs(temppath)
        for i in range(self._imageno):
            img_bac = self._image[i].copy()
            _img2_blured = cv2.GaussianBlur(img_bac, (self._kernelsize, self._kernelsize), sigmaX=0, sigmaY=0)
            _img2_blured = cv2.cvtColor(_img2_blured, cv2.COLOR_RGB2GRAY)
            pointa,pointb = self._groundA,self._groundB
            _alpha = self._alpha2
            x1, y1 = 0, int(pointb)
            x2, y2 = 1023, int(pointa * 1023 + pointb)
            h,w = 1023,1023
            points = np.array([[0, h], [w, h], [x2, y2], [x1, y1],
                               [0, h]], dtype=np.int32)
            cv2.fillConvexPoly(_img2_blured, points, 255)
            b_img = np.clip((1 + _alpha) * _img2_blured - 128 - _alpha, 0, 255).astype(np.uint8)
            _, bin_img = cv2.threshold(b_img, self._thresholdvalue, 255, cv2.THRESH_BINARY_INV)
            contour2, _ = cv2.findContours(bin_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            #print(i,len(contour2))
            try:
                temppath = savepath2 + str(self._height) + "CM_" + str(self._surface) + "_" + str(self._degree) + "_" + str(self._viscosity) + "_00" + str(int(self._number))
                temppath = temppath +"/Contour Files/Imagenumber_" + str(i) + "/"
                makedirs(temppath)
                if len(contour2) == 1:
                    np.save(temppath + "/DATA_0", contour2[0])
                else:
                    for k in range(len(contour2)):
                        np.save(temppath + "/DATA_" + str(k), contour2[k])
            except Exception as e:
                print("Error at",i)
                print(e)
                print(contour2)
            
            cv2.imwrite(savepath2 + str(self._height) + "CM_" + str(self._surface) + "_" + str(self._degree) + "_" + str(self._viscosity) + "_00" + str(int(self._number))+'/Binary Images/' + str(i) + ".png",bin_img)

    def loadContours(self,src,height,surface,degree,viscosity,number):
        temppath = src + str(height) + "CM_" + surface + "_" + str(degree) + "_" + str(viscosity) + "_" + number + "/Contour Files/"
        file_lst = os.listdir(temppath)
        contours = []
        self._imageno = len(file_lst)-1
        for i in range(len(file_lst)):
            src = temppath + 'Imagenumber_' + str(i) + '/'
            file_list2 = os.listdir(src)
            temp = []
            for k in range(len(file_list2)):
                path = temppath + 'Imagenumber_' +  str(i) + "/" + file_list2[k]
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
        self._contours = contours

        #for i in range (len(self._contours)):
        #    contour2binimage(self._contours[i])
        print("End loading Contours")
    def getbinaryImage(self):
        for i in range(len(self._image)):
            _, self._binary_image[i] = cv2.threshold(self._image, 20, 255, cv2.THRESH_BINARY_INV)
    def findvalues(self):
        name = self._name
    def setvelContrast3(self, shutdown_Key, savepath2):
        print("------Set Contrast & Ground Reflection2------")
        for i in range(len(self._image)):
            img_bac = self._image[i].copy()
            _alpha = np.tan(600 * 0.1 * np.pi / 180)
            _img2_blured = cv2.GaussianBlur(img_bac, (10 * 2 + 1, 10 * 2 + 1), sigmaX=0, sigmaY=0)
            _img2_blured = cv2.cvtColor(_img2_blured, cv2.COLOR_RGB2GRAY)
            b_img = np.clip((1 + _alpha) * _img2_blured - 128 - _alpha, 0, 255).astype(np.uint8)
            _, bin_img = cv2.threshold(b_img, 20, 255, cv2.THRESH_BINARY_INV)
            #cv2.imshow("aa",bin_img)
            #cv2.waitKey(1)
            temppath = savepath2 + self._date + "/"
            makedirs(temppath)
            cv2.imwrite(temppath + str(i) + ".png",bin_img)
    def setvelContrast2(self, shutdown_Key,savepath2):
        print("------Set Contrast & Ground Reflection2------")
        print("Press", shutdown_Key, "Key to set Contrast value and Reflection value")
        global img_num, C_num, kernelsize, Val2, YLocation, StartFrame, EndFrame, kernelsize2
        cv2.destroyAllWindows()
        cv2.namedWindow("TRIM")
        cv2.createTrackbar("frame", "TRIM", 0, len(self._image) - 1, self._onChange)
        cv2.createTrackbar("Contrast", "TRIM", 600, 899, self._onChange3)
        cv2.createTrackbar("Ksize", "TRIM", 1, 50, self._onChange_8)
        cv2.createTrackbar("Ksize2","TRIM", 1, 50, self._onChange9)
        cv2.createTrackbar("Val2", "TRIM", 0, 500, self._onChange4)
        cv2.createTrackbar("YLocation", "TRIM", 0, 700, self._onChange5)
        _alpha = 0
        h, w = 1024, 1024
        endx, endy = 1024, 1024
        while cv2.waitKey(1) != ord(shutdown_Key):
            _alpha = np.tan(C_num * 0.1 * np.pi / 180)
            img_bac = self._image[img_num].copy()
            _img2_blured = cv2.GaussianBlur(img_bac, (kernelsize * 2 + 1, kernelsize * 2 + 1), sigmaX=0, sigmaY=0)
            _img2_blured = cv2.cvtColor(_img2_blured, cv2.COLOR_RGB2GRAY)
            b_img = np.clip((1 + _alpha) * _img2_blured - 128 - _alpha, 0, 255).astype(np.uint8)
            _, bin_img = cv2.threshold(b_img, 20, 255, cv2.THRESH_BINARY_INV)
            mask = np.repeat(bin_img[:, :, np.newaxis], 3, -1)
            mask = cv2.dilate(mask,cv2.getStructuringElement(cv2.MORPH_RECT, (kernelsize2,kernelsize2)))
            mask2 = cv2.bitwise_not(mask)
            #img_bac2 = cv2.cvtColor(img_bac,cv2.COLOR_GRAY2BGR)
            img3 = cv2.bitwise_and(img_bac,mask)
            img3 = cv2.bitwise_or(img3,mask2)
            b_img = cv2.cvtColor(b_img, cv2.COLOR_GRAY2BGR)

            b_img2 = cv2.line(b_img,(0,int(YLocation)),(1024,int(YLocation)),(0,0,255),5)

            img4 = cv2.bitwise_and(b_img,mask)
            img4 = cv2.bitwise_or(img4,mask2)
            b_img_re = cv2.resize(b_img2, dsize=(512, 512), interpolation=cv2.INTER_AREA)
            bin_img_re = cv2.resize(mask2, dsize=(512, 512), interpolation=cv2.INTER_AREA)
            mask_re = cv2.resize(img4,dsize=(512,512),interpolation=cv2.INTER_AREA)
            addh = np.hstack((b_img_re, bin_img_re))
            addh = np.hstack((addh,mask_re))
            cv2.imshow("TRIM", addh)
        print(YLocation)
        memY = YLocation
        cv2.destroyAllWindows()
        temppath = savepath2 + self._date+ "/"
        makedirs(temppath)
        print("image overlay ...")
        img0 = np.full((1024, 1024, 3), (0,0,0), np.uint8)
        img00 = np.full((1024, 1024, 3), (0, 0, 0), np.float64)
        img01 = np.full((1024, 1024, 3), (0, 0, 0), np.float64)
        for i in range(self._imageno):
            _alpha = np.tan(C_num * 0.1 * np.pi / 180)
            img_bac = self._image[i].copy()
            _img2_blured = cv2.GaussianBlur(img_bac, (kernelsize * 2 + 1, kernelsize * 2 + 1), sigmaX=0, sigmaY=0)
            _img2_blured = cv2.cvtColor(_img2_blured, cv2.COLOR_RGB2GRAY)
            b_img = np.clip((1 + _alpha) * _img2_blured - 128 - _alpha, 0, 255).astype(np.uint8)
            _, bin_img = cv2.threshold(b_img, 20, 255, cv2.THRESH_BINARY_INV)

            #cv2.imwrite(temppath + str(i) + ".png",bin_img)

            mask = np.repeat(bin_img[:, :, np.newaxis], 3, -1)
            mask = cv2.dilate(mask,cv2.getStructuringElement(cv2.MORPH_RECT, (kernelsize2,kernelsize2)))
            mask2 = cv2.bitwise_not(mask)
            b_img = cv2.cvtColor(b_img, cv2.COLOR_GRAY2BGR)
            img4 = cv2.bitwise_and(b_img,mask)
            img4 = cv2.bitwise_or(img4,mask2)


            img00 = img00*(i/(i+1))+mask*(1/(i+1))
            img00 = np.clip(img00,0,255)

            img01 = img01*(i/(i+1))+img_bac*(1/(i+1))
            img01 = np.clip(img01,0,255)

            img0 = img00.astype(np.uint8)
            b1 = cv2.resize(img0, dsize=(512, 512), interpolation=cv2.INTER_AREA)
            b2 = cv2.resize(mask, dsize=(512, 512), interpolation=cv2.INTER_AREA)
            addh = np.hstack((b1, b2))
            if i%100 == 0:
                print(i, "/", self._imageno)
            #cv2.imshow("aa",addh)
            #cv2.waitKey(1)
        img00 = img00.astype(np.uint8)
        img01 = img01.astype(np.uint8)
        #cv2.imwrite(temppath + "bin_average.png",img00)
        #cv2.imwrite(temppath + "gray_average.png", img01)

        cv2.destroyAllWindows()
        cv2.namedWindow("TRIM")
        cv2.createTrackbar("YLocation", "TRIM", 0, 255, self._onChange5)
        cv2.createTrackbar("Ksize", "TRIM", 1, 50, self._onChange_8)
        cv2.createTrackbar("frame", "TRIM", 0,1023 ,self._onChange)
        cv2.createTrackbar("Contrast", "TRIM", 1023,1023 , self._onChange3)
        img00_bac = img00.copy()
        resultimg = 0
        YLocation = 128
        while cv2.waitKey(1) != ord(shutdown_Key):
            img00 = cv2.GaussianBlur(img00_bac, (kernelsize * 2 + 1, kernelsize * 2 + 1), sigmaX=0, sigmaY=0)
            img00_bin = cv2.cvtColor(img00, cv2.COLOR_BGR2GRAY)
            x_Trim_start = img_num
            x_Trim_end = C_num
            y_Trim_start = memY

            if x_Trim_start < 0:
                x_Trim_start = 0
            if x_Trim_end > 1024:
                x_Trim_end = 1023
            if x_Trim_start > x_Trim_end:
                x_Trim_end = x_Trim_start
            if y_Trim_start < 0:
                y_Trim_start = 0
            if y_Trim_start > 1024:
                y_Trim_start = 1023

            img00_bin = img00_bin[y_Trim_start:,x_Trim_start:x_Trim_end]
            imgblack = np.full((1024, 1024), 0 , np.uint8)
            imgblack[y_Trim_start:,x_Trim_start:x_Trim_end] = img00_bin
            img00_bin = imgblack

            _, img2 = cv2.threshold(img00_bin,YLocation,255,cv2.THRESH_BINARY)
            img2 = cv2.cvtColor(img2, cv2.COLOR_GRAY2BGR)
            resultimg = img2

            img00_bac2 = cv2.line(img00, (0, int(memY)), (1024, int(memY)), (0, 0, 255), 5)
            img00_bac2 = cv2.line(img00_bac2, (int(img_num), 0), (int(img_num), 1024), (0, 0, 255), 5)
            img00_bac2 = cv2.line(img00_bac2, (int(C_num), 0), (int(C_num), 1024), (0, 0, 255), 5)

            b_img_re = cv2.resize(img00_bac2, dsize=(512, 512), interpolation=cv2.INTER_AREA)
            bin_img_re = cv2.resize(img2, dsize=(512, 512), interpolation=cv2.INTER_AREA)
            addh = np.hstack((b_img_re, bin_img_re))
            addh = np.hstack((addh,bin_img_re))
            cv2.imshow("TRIM", addh)
        cv2.destroyAllWindows()

        cv2.imshow("aa",resultimg)
        cv2.waitKey(0)


    def setvelContrast(self, shutdown_Key):
        print("------Set Contrast & Ground Reflection------")
        print("Press",shutdown_Key,"Key to set Contrast value and Reflection value")
        global img_num, C_num,kernelsize,Val2,YLocation,StartFrame,EndFrame
        cv2.destroyAllWindows()
        cv2.namedWindow("TRIM")
        cv2.createTrackbar("frame", "TRIM", img_num, len(self._image) - 1, self._onChange)
        cv2.createTrackbar("Contrast", "TRIM", C_num, 899, self._onChange3)
        cv2.createTrackbar("Ksize","TRIM",1,50,self._onChange_8)
        cv2.createTrackbar("Val2", "TRIM", Val2, 1100, self._onChange4)
        cv2.createTrackbar("YLocation","TRIM",YLocation,3000, self._onChange5)
        #YLocation = 350
        _alpha = 0
        h, w = 1024, 1024
        endx,endy = 1024,1024
        while cv2.waitKey(1) != ord(shutdown_Key):
            _alpha = np.tan(C_num * 0.1 * np.pi / 180)
            img_bac = self._image[img_num].copy()
            _img2_blured = cv2.GaussianBlur(img_bac, (kernelsize*2+1,kernelsize*2+1),sigmaX=0,sigmaY=0)
            _img2_blured = cv2.cvtColor(_img2_blured, cv2.COLOR_RGB2GRAY)
            points = np.array([[self._sx0, endy - Val2 - (YLocation-1500)], [0, h], [w, h], [endx, endy - Val2],
                               [self._sx0, endy - Val2 - (YLocation-1500)]], dtype=np.int32)
            cv2.fillConvexPoly(_img2_blured, points, (255, 255, 255))
            b_img = np.clip((1 + _alpha) * _img2_blured - 128 - _alpha, 0, 255).astype(np.uint8)
            _, bin_img = cv2.threshold(b_img, 20, 255, cv2.THRESH_BINARY_INV)
            b_img_re = cv2.resize(b_img, dsize=(512, 512), interpolation=cv2.INTER_AREA)
            bin_img_re = cv2.resize(bin_img, dsize=(512, 512), interpolation=cv2.INTER_AREA)
            addh = np.hstack((b_img_re, bin_img_re))
            cv2.imshow("TRIM", addh)
        cv2.destroyAllWindows()
        self._alpha2 = _alpha
        self._val2 = Val2
        self._reflect1 = Val2
        self._reflect2 = YLocation
        self._kernelsize = kernelsize*2+1
        print("------Set ground function------")
        print("Press", shutdown_Key, "Key to set ground function")
        cv2.destroyAllWindows()
        cv2.namedWindow("TRIM")
        cv2.createTrackbar("frame", "TRIM", img_num, len(self._image) - 1, self._onChange)
        cv2.createTrackbar("StartFrame", "TRIM", 0, 2000, self._onChange6)
        cv2.createTrackbar("EndFrame", "TRIM", 1, 2000, self._onChange7)
        while cv2.waitKey(1) != ord(shutdown_Key):
            img_bac = self._image[img_num].copy()
            _img2_blured = cv2.GaussianBlur(img_bac, (self._kernelsize,self._kernelsize),sigmaX=0,sigmaY=0)
            _img2_blured = cv2.cvtColor(_img2_blured, cv2.COLOR_RGB2GRAY)
            points = np.array([[self._sx0, endy - Val2 - (YLocation-1500)], [0, h], [w, h], [endx, endy - Val2],
                               [self._sx0, endy - Val2 - (YLocation-1500)]], dtype=np.int32)
            cv2.fillConvexPoly(_img2_blured, points, (255, 255, 255))
            b_img = np.clip((1 + _alpha) * _img2_blured - 128 - _alpha, 0, 255).astype(np.uint8)
            _, bin_img = cv2.threshold(b_img, 20, 255, cv2.THRESH_BINARY_INV)
            b_img_re = cv2.resize(b_img, dsize=(512, 512), interpolation=cv2.INTER_AREA)
            bin_img_re = cv2.resize(bin_img, dsize=(512, 512), interpolation=cv2.INTER_AREA)
            addh = np.hstack((b_img_re, bin_img_re))
            cv2.imshow("TRIM", addh)
        cv2.destroyAllWindows()
        print("Please input Impact Degree")
        ID = np.arctan2(int(YLocation-1500),1024)
        ID = ID*180/np.pi*-1
        print("Impact Degree :",ID)
        ImpactDegree = ID
        #ImpactDegree = 0
        print("Impact Degree :",ImpactDegree)


        pointa = []
        pointb = []
        mempoints = []
        self._startframe = StartFrame
        self._endframe = EndFrame
        print(self._startframe,self._endframe)
        print("Calculating...")

        for i in range(self._startframe,self._endframe):
            img_bac = self._image[i].copy()
            _img2_blured = cv2.GaussianBlur(img_bac, (self._kernelsize,self._kernelsize),sigmaX=0,sigmaY=0)
            _img2_blured = cv2.cvtColor(_img2_blured, cv2.COLOR_RGB2GRAY)
            points = np.array([[self._sx0, endy - Val2 - (YLocation-1500)], [0, h], [w, h], [endx, endy - Val2],
                               [self._sx0, endy - Val2 - (YLocation-1500)]], dtype=np.int32)
            cv2.fillConvexPoly(_img2_blured, points, (255, 255, 255))
            b_img = np.clip((1 + _alpha) * _img2_blured - 128 - _alpha, 0, 255).astype(np.uint8)
            _, bin_img = cv2.threshold(b_img, 20, 255, cv2.THRESH_BINARY_INV)
            contour2, _ = cv2.findContours(bin_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            if len(contour2) == 0:
                continue
            marea = 0
            ma = 0
            for a in range(len(contour2)):
                if len(contour2[a]) < 5:
                    continue
                _area = cv2.contourArea(contour2[a])
                if marea < _area:
                    marea = _area
                    ma = a
            pts = contour2data(contour2[ma])
            endpoints = findendofpoints2(pts,ImpactDegree)

            #ep1 = (int(endpoints[0][0]), int(endpoints[0][1]))
            #ep2 = (int(endpoints[1][0]), int(endpoints[1][1]))
            #bin_img2 = bin_img.copy()
            #bin_img2 = cv2.circle(bin_img2,ep1,3,128,5)
            #bin_img2 = cv2.circle(bin_img2, ep2, 3, 128, 5)
            #cv2.imshow("aa",bin_img2)
            #cv2.waitKey(1)

            tpa,tpb = points2linefunction(endpoints)
            pointa.append(tpa)
            pointb.append(tpb)
            mempoints.append([i,endpoints])
            # calculate point end of right & left
        pointa = np.mean(pointa)
        pointb = np.mean(pointb)
        print("Press", shutdown_Key, "Key to set ground function")
        cv2.destroyAllWindows()
        self._groundA = pointa
        self._groundB = pointb
    def setthresholdvalue(self,shutdown_Key):
        print("------Set Threshold Value & Contrast Value------")
        print("Press",shutdown_Key,"Key to set value")
        global img_num, C_num,kernelsize,thresholdvalue
        cv2.destroyAllWindows()
        cv2.namedWindow("TRIM")
        cv2.createTrackbar("frame", "TRIM", img_num, len(self._image) - 1, self._onChange)
        cv2.createTrackbar("Contrast", "TRIM", C_num, 899, self._onChange3)
        cv2.createTrackbar("Threshold","TRIM",thresholdvalue,255,self._onChange8)
        cv2.createTrackbar("Ksize","TRIM",kernelsize,50,self._onChange_8)
        _alpha = 0
        h, w = 1024, 1024
        endx,endy = 1024,1024
        pointa = self._groundA
        pointb = self._groundB

        while cv2.waitKey(1) != ord(shutdown_Key):
            _alpha = np.tan(C_num * 0.1 * np.pi / 180)
            img_bac = self._image[img_num].copy()
            _img2_blured = cv2.GaussianBlur(img_bac, (kernelsize*2+1,kernelsize*2+1),sigmaX=0,sigmaY=0)
            _img2_blured = cv2.cvtColor(_img2_blured, cv2.COLOR_RGB2GRAY)
            x1, y1 = 0, int(pointb)
            x2, y2 = 1023, int(pointa * 1023 + pointb)
            points = np.array([[0, h], [w, h], [x2, y2], [x1, y1],
                               [0, h]], dtype=np.int32)
            _img2_filled = cv2.fillConvexPoly(_img2_blured, points, (255, 255, 255))
            b_img = np.clip((1 + _alpha) * _img2_filled - 128 - _alpha, 0, 255).astype(np.uint8)
            b_img2 = np.clip((1 + _alpha) * _img2_blured - 128 - _alpha, 0, 255).astype(np.uint8)
            b_img2 = cv2.line(b_img2,(x2,y2),(x1,y1),(255,0,0),1)
            _, bin_img = cv2.threshold(b_img, thresholdvalue, 255, cv2.THRESH_BINARY_INV)
            ctr,_ = cv2.findContours(bin_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            b_img = cv2.cvtColor(b_img,cv2.COLOR_GRAY2BGR)
            bin_img = cv2.cvtColor(bin_img,cv2.COLOR_GRAY2BGR)
            try:
                b_img = cv2.drawContours(b_img, ctr[0], -1, (0, 255, 0), 10)
                _c,_r = cv2.minEnclosingCircle(ctr[0])
                b_img = cv2.putText(b_img, "Diameter" + str(round(_r*2*self._scalenumber,2)) + "um", (20, 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            except:
                pass
            b_img_re = cv2.resize(b_img, dsize=(512, 512), interpolation=cv2.INTER_AREA)
            bin_img_re = cv2.resize(bin_img, dsize=(512, 512), interpolation=cv2.INTER_AREA)
            addh = np.hstack((b_img_re, bin_img_re))
            cv2.imshow("TRIM", addh)
        cv2.destroyAllWindows()
        self._alpha2 = _alpha
        self._kernelsize = kernelsize*2+1
        self._thresholdvalue = thresholdvalue
        
    def picture_Horizon(self, shutdown_Key, Reset_Key, ds):
        '''
        this function help set Horizon line of Images.
        Images : list of Images, it can be 3 channel
        shutdown_Key : def shutdown Key value. it must be char
        Reset_Key : def reset Key value. it also must be char
        ds : integer value of def max window size of Images.
        '''
        global img_num, img0_draw, mousestate, img, TRIM_START_X2, TRIM_START_Y2, TRIM_END_X2, TRIM_END_Y2
        global TRIM_START_X1, TRIM_START_Y1, TRIM_END_X1, TRIM_END_Y1, C_num, alpha, Framenumber
        if self._sw_quick:
            return self._image
        img_num = 0
        mousestate = 0
        cv2.destroyAllWindows()
        cv2.namedWindow("TRIM")
        cv2.createTrackbar("frame", "TRIM", 0, self._imageno - 1, self._onChange)
        cv2.createTrackbar("Contrast", "TRIM", 600, 899, self._onChange3)
        cv2.imshow("TRIM", np.hstack((self._image[0], self._image[0])))
        h, w, c = self._image[0].shape
        s = (0, 0)
        state = 0
        p = 0
        if h > w:
            p = int(h / w * ds)
            s = (ds, p)
            state = 1
        else:
            p = int(w / h * ds)
            s = (p, ds)
            state = 2
        img0_draw = cv2.resize(img0_draw, dsize=s)
        _alpha = 0
        while cv2.waitKey(1) != ord(shutdown_Key):
            # print("alpha", alpha)
            if cv2.waitKey(1) == ord(Reset_Key) and mousestate == 1:
                print("re-loaded")
                mousestate = 0
                img0_draw = self._image[img_num].copy()
                img0_draw = cv2.resize(img0_draw, dsize=s)
                _alpha = np.tan(C_num * 0.1 * np.pi / 180)
                img0_draw = np.clip((1 + _alpha) * img0_draw - 128 - _alpha, 0, 255).astype(np.uint8)
                _, imgb_draw = cv2.threshold(img0_draw, 20, 255, cv2.THRESH_BINARY_INV)
                addh = np.hstack((img0_draw, imgb_draw))
                cv2.imshow("TRIM", addh)
            img = self._image[img_num]
            img = cv2.resize(img, dsize=s)
            _alpha = np.tan(C_num * 0.1 * np.pi / 180)
            img = np.clip((1 + _alpha) * img - 128 - _alpha, 0, 255).astype(np.uint8)

            if mousestate == 1:
                img0_draw = img.copy()
                h, w, c = img.shape
                if (TRIM_END_X2 - TRIM_START_X2 == 0):
                    a = 0
                else:
                    a = (TRIM_END_Y2 - TRIM_START_Y2) / (TRIM_END_X2 - TRIM_START_X2)
                b = TRIM_START_X2 * -a + TRIM_START_Y2
                sx0 = 0
                sx1 = int(w)
                sy0 = int(b)
                sy1 = int(a * w + b)

                cv2.line(img0_draw, (sx0, sy0), (sx1, sy1), (255, 0, 0), 1)
                _, imgb_draw = cv2.threshold(img0_draw, 20, 255, cv2.THRESH_BINARY_INV)
                addh = np.hstack((img0_draw, imgb_draw))

                cv2.imshow("TRIM", addh)
            cv2.setMouseCallback("TRIM", self._onMouse2)
        cv2.destroyAllWindows()
        alpha = _alpha
        self._alpha = alpha
        h, w, c = self._image[0].shape
        TRIM_START_X2 = int(TRIM_START_X2 * h / ds)
        TRIM_START_Y2 = int(TRIM_START_Y2 * h / ds)
        TRIM_END_X2 = int(TRIM_END_X2 * h / ds)
        TRIM_END_Y2 = int(TRIM_END_Y2 * h / ds)
        print("----------------------------------------------------------------")
        if (TRIM_END_X2 - TRIM_START_X2 == 0):
            a1 = 99999999
        else:
            a1 = (TRIM_END_Y2 - TRIM_START_Y2) / (TRIM_END_X2 - TRIM_START_X2)
        b1 = TRIM_START_X2 * -a1 + TRIM_START_Y2
        self._horizonLine_A = a1
        self._horizonLine_B = b1

        self._sx0 = 0
        self._sx1 = int(w)
        self._sy0 = int(b1 + 3)
        self._sy1 = int(a1 * w + b1 + 3)

        self._impactDeg = 90 - np.arctan2(1, a1) * 180 / np.pi
        print("Impact Degree  :", round(self._impactDeg, 3))
        print("Alpha          :", round(self._alpha, 3))
        print("----------------------------------------------------------------")
        cv2.destroyAllWindows()
        # print(tickrecord('starthorizon','endhorizon2'),"horizon2 image list")
        return
    def spreading(self):
        pool = Pool()
        inputs = []
        pL = []
        pR = []
        dL = []
        dR = []
        D = []
        aL = []
        aR = []
        VL = []
        VR = []
        dVL = []
        dVR = []
        E = []
        Rim = []
        points = []
        # Calculate Diameter

        tickrecord('', 'startdiameter' + self._name)
        for i in range(self._time_impact, self._imageno):
            _, _bin_image = cv2.threshold(self._image_con[i], 20, 255, cv2.THRESH_BINARY_INV)
            _ref = [_bin_image, self._horizonLine_A, self._horizonLine_B, self._impactpoint_x, self._impactpoint_y]
            # a = detect_Diameter(_ref)
            inputs.append(_ref)
        val = pool.map(detect_Diameter, inputs)
        for i in range(len(val)):
            pL.append(val[i][0])
            pR.append(val[i][1])
            dL.append(val[i][2] * self._scalenumber)
            dR.append(val[i][3] * self._scalenumber)
            D.append((val[i][2] + val[i][3]) * self._scalenumber)
            Rim.append(val[i][4] * self._scalenumber)

        self._onDiameter = D
        self._onDiameterL = dL
        self._onDiameterR = dR
        self._onRim = Rim
        VL.append(0)
        VR.append(0)
        dVL.append(0)
        dVR.append(0)
        for i in range(1, len(dR)):
            d_dL = dL[i - 1] - dL[i]
            d_dR = dR[i - 1] - dR[i]
            VL.append(-d_dL * Framenumber * 10 ** -6)
            VR.append(-d_dR * Framenumber * 10 ** -6)
            dVL.append(VL[i] - VL[i - 1])
            dVR.append(VR[i] - VR[i - 1])
            if dVL[i] < -4:
                VL[i] = VL[i - 1]
            if dVR[i] < -4:
                VR[i] = VR[i - 1]
        self.cal_time()
        self._onVelocityL = VL
        self._onVelocityR = VR
        self._ondVL = dVL
        self._ondVR = dVR
        # Calculate Contact Angle
        inputs = []
        print(tickrecord('startdiameter' + self._name, 'enddiameter'), "\t sec diameter Calculate")
        tickrecord('', 'startContactAngle' + self._name)
        for i in range(self._time_impact, self._imageno):
            _, _bin_image = cv2.threshold(self._image_con[i], 20, 255, cv2.THRESH_BINARY_INV)
            _ref = [_bin_image, self._horizonLine_A, self._horizonLine_B, pL[i - self._time_impact],
                    pR[i - self._time_impact], self._time_maxspreading, i, self._impactDeg, self._scalenumber]
            inputs.append(_ref)
            # detect_ContactAngle(_ref)
        val = pool.map(detect_ContactAngle, inputs)
        for i in range(len(val)):
            if val[i][0] == 0 and val[i][1] == 0:
                aL.append(val[i - 1][0] + self._impactDeg)
                aR.append(val[i - 1][1] - self._impactDeg)
            else:
                aL.append(val[i][0] + self._impactDeg)
                aR.append(val[i][1] - self._impactDeg)
                E.append(val[i][2])
                points.append([val[i][3]])
        print(tickrecord('startContactAngle' + self._name, 'endContactAngle'), "\t sec contactAngle")

        self._LeftAngle = aL
        self._RightAngle = aR
        self._imagepoints = points
        self._Errornum = sum(E)
        print("Error count", self._Errornum)
    def spreading_contour(self,savepathto):
        pool = Pool()
        inputs = []
        pL = []
        pR = []
        dL = []
        dR = []
        D = []
        aL = []
        aR = []
        VL = []
        VR = []
        dVL = []
        dVR = []
        E = []
        Rim = []
        points = []
        # Calculate Diameter

        tickrecord('', 'startdiameter' + self._name)
        for i in range(self._time_impact, self._imageno):
            _ref = [self._contours[i], self._horizonLine_A, self._horizonLine_B, self._impactpoint_x, self._impactpoint_y,i]
            a = detect_Diameter_contour(_ref)
            pL.append(a[0])
            pR.append(a[1])
            dL.append(a[2] * self._scalenumber)
            dR.append(a[3] * self._scalenumber)
            D.append((a[2] + a[3]) * self._scalenumber)
            Rim.append(a[4] * self._scalenumber)

        #     inputs.append(_ref)
        # val = pool.map(detect_Diameter_contour, inputs)
        # for i in range(len(val)):
        #     pL.append(val[i][0])
        #     pR.append(val[i][1])
        #     dL.append(val[i][2] * self._scalenumber)
        #     dR.append(val[i][3] * self._scalenumber)
        #     D.append((val[i][2] + val[i][3]) * self._scalenumber)
        #     Rim.append(val[i][4] * self._scalenumber)

        self._onDiameter = D
        self._onDiameterL = dL
        self._onDiameterR = dR
        self._onRim = Rim
        maxt = len(self._onDiameter) * (1000 / 20000)
        t = np.arange(0, maxt, 1000 / 20000)
        t = t[:len(self._onDiameter)]
        df = pd.DataFrame(t,columns=["time"])
        df['Diameter'] = D
        df['Diameter_L'] = dL
        df['Diameter_R'] = dR
        temppath = savepathto + str(self._height) + "CM_" + str(self._surface) + "_" + str(self._degree) + "_"+ str(self._viscosity)  +"_00" + str(int(self._number))
        makedirs(temppath)
        df.to_csv(temppath + "/_SpreadFactorData.csv", index=False)
        #plt.plot(D)
        #plt.show()

        VL.append(0)
        VR.append(0)
        dVL.append(0)
        dVR.append(0)
        for i in range(1, len(dR)):
            d_dL = dL[i - 1] - dL[i]
            d_dR = dR[i - 1] - dR[i]
            VL.append(-d_dL * 20000 * 10 ** -6)
            VR.append(-d_dR * 20000 * 10 ** -6)
            dVL.append(VL[i] - VL[i - 1])
            dVR.append(VR[i] - VR[i - 1])
            if dVL[i] < -4:
                VL[i] = VL[i - 1]
            if dVR[i] < -4:
                VR[i] = VR[i - 1]
        self.cal_time()
        self._onVelocityL = VL
        self._onVelocityR = VR
        self._ondVL = dVL
        self._ondVR = dVR
        # Calculate Contact Angle
        inputs = []
        print(tickrecord('startdiameter' + self._name, 'enddiameter'), "\t sec diameter Calculate")




        # tickrecord('', 'startContactAngle' + self._name)
        # for i in range(self._time_impact, self._imageno):
        #     _, _bin_image = cv2.threshold(self._image_con[i], 20, 255, cv2.THRESH_BINARY_INV)
        #     _ref = [_bin_image, self._horizonLine_A, self._horizonLine_B, pL[i - self._time_impact],
        #             pR[i - self._time_impact], self._time_maxspreading, i, self._impactDeg, self._scalenumber]
        #     inputs.append(_ref)
        #     ##### detect_ContactAngle(_ref)
        # val = pool.map(detect_ContactAngle, inputs)
        # for i in range(len(val)):
        #     if val[i][0] == 0 and val[i][1] == 0:
        #         aL.append(val[i - 1][0] + self._impactDeg)
        #         aR.append(val[i - 1][1] - self._impactDeg)
        #     else:
        #         aL.append(val[i][0] + self._impactDeg)
        #         aR.append(val[i][1] - self._impactDeg)
        #         E.append(val[i][2])
        #         points.append([val[i][3]])
        # print(tickrecord('startContactAngle' + self._name, 'endContactAngle'), "\t sec contactAngle")
        #
        # self._LeftAngle = aL
        # self._RightAngle = aR
        # self._imagepoints = points
        # self._Errornum = sum(E)
        # print("Error count", self._Errornum)
    def setStandard(self,shutdown_Key):
        print("------Set Impact Frame------")
        print("Press", shutdown_Key, "Key to set Impact Frame when hit droplet onto surface")
        global img_num,thresholdvalue
        cv2.destroyAllWindows()
        cv2.namedWindow("TRIM")
        cv2.createTrackbar("frame", "TRIM", img_num, 500, self._onChange)
        _alpha = 0
        h, w = 1024, 1024
        endx, endy = 1024, 1024
        while cv2.waitKey(1) != ord(shutdown_Key):
            _alpha = np.tan(450 * 0.1 * np.pi / 180)
            img_bac = self._image[img_num].copy()
            img_re = cv2.resize(img_bac, dsize=(512, 512), interpolation=cv2.INTER_AREA)
            cv2.imshow("TRIM", img_re)
        print("Impact Frame :",img_num)

        print("------Set Contrast & Threshold value------")
        print("Press", shutdown_Key, "Key to set Contrast and threshold value")
        cv2.destroyAllWindows()
        cv2.namedWindow("TRIM")
        cv2.createTrackbar("frame", "TRIM", img_num, len(self._image) - 1, self._onChange)
        cv2.createTrackbar("Contrast", "TRIM", C_num, 899, self._onChange3)
        cv2.createTrackbar("Threshold","TRIM",0,255,self._onChange8)
        _alpha = 0
        h, w = 1024, 1024
        endx,endy = 1024,1024
        while cv2.waitKey(1) != ord(shutdown_Key):
            _alpha = np.tan(C_num * 0.1 * np.pi / 180)
            img_bac = self._image[img_num].copy()
            _img2_blured = cv2.cvtColor(img_bac, cv2.COLOR_RGB2GRAY)

            points = np.array([[self._sx0, endy - Val2 - (YLocation-1500)], [0, h], [w, h], [endx, endy - Val2],
                               [self._sx0, endy - Val2 - (YLocation-1500)]], dtype=np.int32)
            cv2.fillConvexPoly(_img2_blured, points, (255, 255, 255))

            b_img = np.clip((1 + _alpha) * _img2_blured - 128 - _alpha, 0, 255).astype(np.uint8)

            # draw fit circle to 2000um

            _, bin_img = cv2.threshold(b_img, thresholdvalue, 255, cv2.THRESH_BINARY_INV)
            b_img_re = cv2.resize(b_img, dsize=(512, 512), interpolation=cv2.INTER_AREA)
            bin_img_re = cv2.resize(bin_img, dsize=(512, 512), interpolation=cv2.INTER_AREA)
            addh = np.hstack((b_img_re, bin_img_re))
            cv2.imshow("TRIM", addh)
    def getpoints_onlycontour(self, shutdown_Key):
        print("------test------")
        global img_num
        cv2.destroyAllWindows()
        cv2.namedWindow("TRIM")
        starthitFrame = self._startframe
        starthitFrame = 0
        cv2.createTrackbar("frame", "TRIM", starthitFrame, len(self._image) - 1, self._onChange)
        cv2.setTrackbarMin("frame", "TRIM", starthitFrame)
        cv2.setTrackbarMax("frame", "TRIM", self._imageno)
        print(starthitFrame,self._imageno)
        while cv2.waitKey(1) != ord(shutdown_Key):
            _img = contour2binimage(self._contours[img_num])
            cv2.imshow("TRIM", _img)
    def ploting(self):
        maxt = len(self._onDiameter) * (1000 / Framenumber)
        t = np.arange(0, maxt, 1000 / Framenumber)

        t = t[:len(self._onDiameter)]
        plt.figure(figsize=(10, 6))
        plt.subplot(311)
        plt.plot(t, self._onDiameter, label="Diameter", color="blue")
        plt.plot(t, self._onDiameterL, label="DiameterL", color="green")
        plt.plot(t, self._onDiameterR, label="DiameterR", color="red")

        minval = min(self._onDiameterL)
        if minval > 0:
            minval = 0
        minval = -5000
        plt.legend()
        # plt.xlabel("Time (ms)")
        plt.ylabel("Diameter (µm)")
        plt.title("Diameter")
        plt.xlim([0, 80])
        plt.ylim([minval, self._maxDiameter + 1000])
        plt.vlines((self._time_maxspreading - self._time_impact) * 1000 / Framenumber, -10000, 100000, colors='green',
                   linestyles='--', label="maxspreading Time")
        plt.subplot(312)
        plt.vlines((self._time_maxspreading - self._time_impact) * 1000 / Framenumber, -10000, 100000, colors='green',
                   linestyles='--', label="maxspreading Time")
        plt.plot(t, self._LeftAngle, label="Left", color="red")
        plt.plot(t, self._RightAngle, label="Right", color="blue")
        plt.xlabel("Time (ms)")
        plt.ylabel("Angle (deg)")
        plt.title("Contact Angle")
        plt.xlim([0, 80])
        plt.ylim([0, 180])
        plt.legend()
        plt.subplot(313)
        plt.plot(t, self._onRim, label="Rim_height", color="red")
        plt.xlim([0, 80])
        plt.ylim([0, 2500])
        plt.xlabel("Time (ms)")
        plt.ylabel("height (µm)")
        plt.legend()
        # plt.show()
        plt.savefig(self._savepath + "_plot.png", dpi=600)
    def save_Horizon(self):
        Data = pd.DataFrame([self._alpha], columns=['alpha'])
        Data['alpha2'] = [self._alpha2]
        Data['val2'] = [self._val2]
        Data['sx0'] = [self._sx0]
        Data['sx1'] = [self._sx1]
        Data['sy0'] = [self._sy0]
        Data['sy1'] = [self._sy1]
        Data['A'] = [self._horizonLine_A]
        Data['B'] = [self._horizonLine_B]
        Data.to_csv(self._savepath + "_horizondata.txt", index=False)
        print(self._name)
        print("save Complete!")
    def save_Data(self):
        Data = pd.DataFrame([self._time_startfall], columns=['time_startfall'])
        Data['time_impact'] = [self._time_impact]
        Data['time_maxspreading'] = [self._time_maxspreading]
        Data['impact_deg'] = [self._impactDeg]
        Data['diameter'] = [self._Diameter]
        Data['velocity'] = [self._Velocity]
        Data['maxdiameter'] = [self._maxDiameter]
        Data['impactx'] = [self._impactpoint_x]
        Data['impacty'] = [self._impactpoint_y]
        Data.to_csv(self._savepath + "_Data.txt", index=False)

        Data2 = pd.DataFrame(self._onDiameter, columns=['Diameter'])
        Data2['Diameter_L'] = self._onDiameterL
        Data2['Diameter_R'] = self._onDiameterR
        Data2['L_Angle'] = self._LeftAngle
        Data2['R_Angle'] = self._RightAngle
        Data2['L_Velocity'] = self._onVelocityL
        Data2['R_Velocity'] = self._onVelocityR
        Data2.to_csv(self._savepath + "_Data2.csv", index=False)

        for z in range(1, len(self._imagepoints)):
            tempx, tempy = contour2points(self._imagepoints[z])
            Data3 = pd.DataFrame(tempx, columns=['testx'])
            Data3['testy'] = tempy
            Data3.to_csv(self._path3 + "Data_" + str(z + self._time_impact) + ".csv", index=False)

        print(self._name)
        print("save Complete")
    def load_Horizon_only(self):
        Data = pd.read_csv(self._savepath + "_horizondata.txt")
        self._alpha = Data['alpha'][0]
        self._sx0 = Data['sx0'][0]
        self._sx1 = Data['sx1'][0]
        self._sy0 = Data['sy0'][0]
        self._sy1 = Data['sy1'][0]
        self._horizonLine_A = Data['A'][0]
        self._horizonLine_B = Data['B'][0]
        print("Load Complete")
    def load_Horizon(self):
        Data = pd.read_csv(self._savepath + "_horizondata.txt")

        self._alpha = Data['alpha'][0]
        self._alpha2 = Data['alpha2'][0]
        self._val2 = Data['val2'][0]
        self._sx0 = Data['sx0'][0]
        self._sx1 = Data['sx1'][0]
        self._sy0 = Data['sy0'][0]
        self._sy1 = Data['sy1'][0]
        self._horizonLine_A = Data['A'][0]
        self._horizonLine_B = Data['B'][0]
        print("Load Complete")
        tickrecord('', 'starthorizonS' + self._name)
        '''
        _a = []
        for i in range(self._imageno):
            _temp = np.core.umath.maximum(np.core.umath.minimum((1+self._alpha)*self._image[i]-128-self._alpha,255),0).astype(np.uint8)
            _a.append(_temp)
        '''

        inputs = []
        pool = Pool()
        for i in range(self._imageno):
            inputs.append([self._image[i], self._alpha])
        _a = pool.starmap(heavywork, inputs)

        self._image_con = _a
        a1 = self._horizonLine_A
        self._impactDeg = 90 - np.arctan2(1, a1) * 180 / np.pi
        print(tickrecord('starthorizonS' + self._name, 'endhorizonS'), "\t sec horizon line image")
        print("----------------------------------------------------------------")
        print("Impact Degree  :", round(self._impactDeg, 3))
        print("Alpha          :", round(self._alpha, 3))
        print("----------------------------------------------------------------")
    def bulktest(self):
        bin_image = []
        bin_image2 = []
        bulk = []
        mcX = []
        mcY = []
        mcX2 = []
        mcY2 = []
        pool = Pool()
        inputs = []
        h, w, c = self._image[0].shape
        tickrecord('', 'startstaindiameter' + self._name)
        for i in range(self._imageno):
            img2 = np.core.umath.maximum(
                np.core.umath.minimum((1 + self._alpha2) * self._image[i] - 128 - self._alpha2, 255), 0).astype(
                np.uint8)
            points1 = np.array([[self._sx0, self._sy0], [0, h], [w, h], [self._sx1, self._sy1], [self._sx0, self._sy0]],
                               dtype=np.int32)
            points2 = np.array(
                [[self._sx0, self._sy0 - self._val2], [0, h], [w, h], [self._sx1, self._sy1 - self._val2],
                 [self._sx0, self._sy0 - self._val2]], dtype=np.int32)
            ref = [img2, points2]

            # val3 = detect_Diameter_Velocity(ref)
            # self.circlefit2.append(val3[0])
            inputs.append(ref)
        val = pool.map(detect_Diameter_Velocity, inputs)
        for i in range(len(val)):
            self.circlefit2.append(val[i][0])
        print(tickrecord('startstaindiameter' + self._name, 'endstaindiameter' + self._name),
              "\t sec stain diameter Calculate")
        tickrecord('', 'startcaldiameter' + self._name)
        for i in range(self._imageno):
            [(cx, cy, r)] = self.circlefit2[i]
            mr = r * self._scalenumber
            if mr > 800 and mr < 1400:
                self._time_startfall = i
                break
        for i in range(self._time_startfall, self._imageno):
            [(cx, cy, r)] = self.circlefit2[i]
            mr = r * self._scalenumber
            _, temp = cv2.threshold(self._image_con[i], 20, 255, cv2.THRESH_BINARY_INV)
            if detect_lineonpoint(temp, self._horizonLine_A, self._horizonLine_B, w, h) and self._time_startfall < i:
                self._time_impact = i
                break
        _, _temp = cv2.threshold(self._image_con[self._time_impact], 20, 255, cv2.THRESH_BINARY_INV)
        (self._impactpoint_x, self._impactpoint_y) = detect_impactpoint(_temp, self._horizonLine_A, self._horizonLine_B,
                                                                        w)
        print(tickrecord('startcaldiameter' + self._name, 'endstaindiameter' + self._name),
              "\t sec cal diameter Calculate")
        print("impact point :\t", int(self._impactpoint_x), int(self._impactpoint_y), "(x,y), pixel")
        print("time_startfall:\t", self._time_startfall, "\tframe")
        print("time_impact   :\t", self._time_impact, "\tframe")
        mcx, mcy = 0, 0
        mD = []
        mD2 = []
        mV = []
        for i in range(self._time_startfall, self._time_impact):
            [(cx, cy, r)] = self.circlefit2[i]
            D = r * self._scalenumber * 2
            mD.append(D)
            if mcx == 0 and mcy == 0:
                mcx = cx
                mcy = cy
                mV.append(0)
                continue
            else:
                dx = abs(mcx - cx)
                dy = abs(mcy - cy)
                dV = np.sqrt(dx ** 2 + dy ** 2) * Framenumber * self._scalenumber * 10 ** -6
                mcx = cx
                mcy = cy
                mV.append(dV)
        for i in range(1, len(mD)):
            if (mD[i] - mD[i - 1]) < 100:
                mD2.append(mD[i])
        self._Diameter = int(np.mean(mD2))
        self._Velocity = round(np.mean(mV), 3)

        print("Diameter :\t", self._Diameter, "\tµm")
        print("Velocity :\t", self._Velocity, "\tm/s")
        # plt.subplot(211)
        # plt.plot(mD)
        # plt.subplot(212)
        # plt.plot(mD2)
        # plt.show()
    def bulktest_onlycontour(self):
        bin_image = []
        bin_image2 = []
        bulk = []
        mcX = []
        mcY = []
        mcX2 = []
        mcY2 = []
        pool = Pool()
        inputs = []
        h, w = 1023,1023
        tickrecord('', 'startstaindiameter' + self._name)
        for i in range(self._imageno):
            img2 = self._contours[i]
            points2 = np.array(
                [[self._sx0, self._sy0 - self._val2], [0, h], [w, h], [self._sx1, self._sy1 - self._val2],
                 [self._sx0, self._sy0 - self._val2]], dtype=np.int32)
            ref = [img2, points2]

            # val3 = detect_Diameter_Velocity(ref)
            # self.circlefit2.append(val3[0])
            inputs.append(ref)
        val = pool.map(detect_Diameter_Velocity_onlycontour, inputs)
        for i in range(len(val)):
            self.circlefit2.append(val[i][0])
        print(tickrecord('startstaindiameter' + self._name, 'endstaindiameter' + self._name),
              "\t sec stain diameter Calculate")
        tickrecord('', 'startcaldiameter' + self._name)
        for i in range(self._imageno):
            [(cx, cy, r)] = self.circlefit2[i]
            mr = r * self._scalenumber
            if mr > 800 and mr < 1400:
                self._time_startfall = i
                break
        for i in range(self._time_startfall, self._imageno):
            [(cx, cy, r)] = self.circlefit2[i]
            mr = r * self._scalenumber
            #contour2binimage(self._contours[i])
            (_x,_y) = contour2linepoint(self._contours[i], self._horizonLine_A, self._horizonLine_B,3)
            #print(_x,_y,i)
            if _x != -1:
                self._impactpoint_x = _x
                self._impactpoint_y = _y
                self._time_impact = i
                break
            '''
            if detect_lineonpoint(contour2binimage(self._contours[i]), self._horizonLine_A, self._horizonLine_B, w, h) and self._time_startfall < i:
                self._time_impact = i
                print(i)
                break
            '''
        # test1 = contour2binimage(self._contours[i])
        # test1 = cv2.cvtColor(test1, cv2.COLOR_GRAY2BGR)
        # test1 = cv2.line(test1,(int(0),int(self._horizonLine_B)),(int(1024),int(1024*self._horizonLine_A+self._horizonLine_B)),(255,0,0),5)
        # test1 = cv2.circle(test1,(int(self._impactpoint_x),int(self._impactpoint_y)),3,(0,0,255),3)
        # cv2.imshow("aa",test1)
        # cv2.waitKey(0)
        #(self._impactpoint_x, self._impactpoint_y) = detect_impactpoint(contour2binimage(self._contours[self._time_impact]), self._horizonLine_A, self._horizonLine_B,w)
        print(tickrecord('startcaldiameter' + self._name, 'endstaindiameter' + self._name),
              "\t sec cal diameter Calculate")
        print("impact point :\t", int(self._impactpoint_x), int(self._impactpoint_y), "(x,y), pixel")
        print("time_startfall:\t", self._time_startfall, "\tframe")
        print("time_impact   :\t", self._time_impact, "\tframe")
        mcx, mcy = 0, 0
        mD = []
        mD2 = []
        mV = []
        for i in range(self._time_startfall, self._time_impact):
            [(cx, cy, r)] = self.circlefit2[i]
            D = r * self._scalenumber * 2
            mD.append(D)
            if mcx == 0 and mcy == 0:
                mcx = cx
                mcy = cy
                mV.append(0)
                continue
            else:
                dx = abs(mcx - cx)
                dy = abs(mcy - cy)
                dV = np.sqrt(dx ** 2 + dy ** 2) * 20000 * self._scalenumber * 10 ** -6
                mcx = cx
                mcy = cy
                mV.append(dV)
        for i in range(1, len(mD)):
            if (mD[i] - mD[i - 1]) < 100:
                mD2.append(mD[i])
        self._Diameter = int(np.mean(mD2))
        self._Velocity = round(np.mean(mV), 3)

        print("Diameter :\t", self._Diameter, "\tµm")
        print("Velocity :\t", self._Velocity, "\tm/s")
        # plt.subplot(211)
        # plt.plot(mD)
        # plt.subplot(212)
        # plt.plot(mD2)
        # plt.show()
    def saveheight(self):
        tempx = []
        tempy = []
        tempb = []
        for i in range(1024):
            tempx.append(i)
            tempy.append(self._groundA * i + self._groundB)
        a1 = 0
        if self._groundA == 0:
            a1 = 999999999
        else:
            a1 = -1/self._groundA
        for i in range(len(tempx)):
            tempb.append(a1*tempx[i]+tempy[i])

        for i in range(self._time_impact,self._imageno-1):
            tempheight = []
            temp = contour2binimage(self._contours[i])

            radian = np.pi/180*self._impactDeg
            testy = np.zeros(1024)
            for g in range(len(self._contours[i])):
                #for k in range(len(self._contours[i][g])):
                k = len(self._contours[i][g])
                points = contour2data(self._contours[i][g])
                for m in range(len(points)):
                    xp = np.cos(radian)*points[m][0]-np.sin(radian)*points[m][1]
                    yp = np.sin(radian)*points[m][0]+np.cos(radian)*points[m][1]
                    xp = points[m][0]
                    yp = points[m][1]

                    #print(i,g,k,int(xp),int(yp))
                    if testy[int(xp)] < abs(int(self._horizonLine_B)-int(yp)):
                        testy[int(xp)] = abs(int(self._horizonLine_B)-int(yp))

            # plt.plot(testy)
            # plt.ylim(0,500)
            # plt.show()
            # cv2.imshow('aa',temp)
            # cv2.waitKey(0)

            print("Frame :",i,"\t",tempheight)
    def detect_endofrim(self, shutdown_Key):
        global img_num, C_num
        cv2.destroyAllWindows()
        cv2.namedWindow("TRIM")
        cv2.createTrackbar("frame", "TRIM", 0, len(self._image) - 1, self._onChange)
        cv2.createTrackbar("Contrast", "TRIM", 600, 899, self._onChange3)
        cv2.createTrackbar("Val2", "TRIM", 0, 900, self._onChange4)
        _alpha = 0
        h, w = 1024, 1024
        while cv2.waitKey(1) != ord(shutdown_Key):
            _alpha = np.tan(C_num * 0.1 * np.pi / 180)
            img_bac = self._image[img_num].copy()
            points = np.array([[self._sx0, self._sy0 - Val2], [0, h], [w, h], [self._sx1, self._sy1 - Val2],
                               [self._sx0, self._sy0 - Val2]], dtype=np.int32)
            cv2.fillConvexPoly(img_bac, points, (255, 255, 255))
            # img_bac = cv2.cvtColor(img_bac,cv2.COLOR_RGB2GRAY)
            b_img = np.clip((1 + _alpha) * img_bac - 128 - _alpha, 0, 255).astype(np.uint8)
            _, bin_img = cv2.threshold(b_img, 20, 255, cv2.THRESH_BINARY_INV)
            _img2 = cv2.GaussianBlur(b_img, (33, 33), sigmaX=0, sigmaY=0)
            _img2 = cv2.cvtColor(_img2, cv2.COLOR_RGB2GRAY)
            _, temp2 = cv2.threshold(_img2, 20, 255, cv2.THRESH_BINARY_INV)
            contour2, _ = cv2.findContours(temp2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            if len(contour2) == 0:
                continue
            marea = 0
            ma = 0
            for a in range(len(contour2)):
                if len(contour2[a]) < 5:
                    continue
                _area = cv2.contourArea(contour2[a])
                if marea < _area:
                    marea = _area
                    ma = a
                    M = cv2.moments(contour2[a])
            (cx, cy, r) = fit_circle(contour2data(contour2[ma]))
            b_img = cv2.circle(b_img, (int(cx), int(cy)), int(r), (255, 0, 255), 10)
            text = str((r * self._scalenumber * 2)) + "um"
            cv2.putText(b_img, text, (0, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 5)
            b_img_re = cv2.resize(b_img, dsize=(300, 300), interpolation=cv2.INTER_AREA)
            bin_img_re = cv2.resize(bin_img, dsize=(300, 300), interpolation=cv2.INTER_AREA)
            addh = np.hstack((b_img_re, bin_img_re))
            cv2.imshow("TRIM", addh)
        cv2.destroyAllWindows()
    def cal_time(self):
        maxD = 0
        maxT = 0
        for i in range(200):
            if maxD < self._onDiameter[i]:
                maxD = self._onDiameter[i]
                maxT = i
        self._time_maxspreading = maxT + self._time_impact
        self._maxDiameter = maxD
    def _onChange(self, x):
        global img_num, changed
        img_num = cv2.getTrackbarPos('frame', "TRIM")
        changed = True
    def _onChange2(self, x):
        global YLocation
        YLocation = cv2.getTrackbarPos('Xpos', "TRIM")
    def _onChange3(self, x):
        global C_num, changed
        C_num = cv2.getTrackbarPos('Contrast', "TRIM")
        changed = True
    def _onChange4(self, x):
        global Val2
        Val2 = cv2.getTrackbarPos('Val2', "TRIM")
    def _onChange5(self, x):
        global YLocation
        YLocation = cv2.getTrackbarPos('YLocation', "TRIM")
    def _onChange6(self, x):
        global StartFrame, EndFrame
        StartFrame = cv2.getTrackbarPos('StartFrame', "TRIM")
    def _onChange7(self, x):
        global StartFrame, EndFrame
        EndFrame = cv2.getTrackbarPos('EndFrame', "TRIM")
    def _onChange_8(self, x):
        global kernelsize,changed
        kernelsize = cv2.getTrackbarPos('Ksize', "TRIM")
        changed = True
    def _onChange8(self, x):
        global thresholdvalue,changed
        thresholdvalue = cv2.getTrackbarPos('Threshold', "TRIM")
        changed = True
    def _onChange9(self, x):
        global kernelsize2,changed
        kernelsize2 = cv2.getTrackbarPos('Ksize2', "TRIM")
        changed = True
    def setName(self,path2,ref,scalenumber):
        date = ref.split('-')[0]
        height = ref.split('-')[1].split('cm')[0]
        size = ref.split('-')[2].split('um')[0]
        surface = ref.split('-')[3]
        degree = ref.split('-')[4].split('deg')[0]
        viscosity = ref.split('-')[5].split('cp')[0]
        number = ref.split('-')[6]
        print("date\t\theight\t\tsize\t\tsurface\t\tdegree\t\tviscosity\t\tnumber")
        temp = str(date)+'\t\t'+str(height)+'\t\t\t'+str(size)+'\t\t'+str(surface)+'\t\t\t'+str(degree)+'\t\t'+str(viscosity)+'\t\t'+str(int(number))
        print(temp)
        self._date = date
        self._height = height
        self._size = size
        self._surface = surface
        self._degree = degree
        self._viscosity = viscosity
        self._number = number

        self._name = ref
        self._scalenumber = scalenumber
        self._savepath = path2 + "/" + self._name
    def _onMouse1(event, x, y, flags, param):
        global mousestate, img0_draw, x1, y1, click, img, TRIM_END_X1, TRIM_END_Y1, TRIM_START_X1, TRIM_START_Y1, img0_draw
        if mousestate == 1:
            return
        if event == cv2.EVENT_LBUTTONDOWN:
            click = True
            x1, y1 = x, y
            TRIM_START_X1, TRIM_START_Y1 = x, y

        elif event == cv2.EVENT_MOUSEMOVE:
            if click == True:
                img0_draw = img.copy()
                img0_draw = cv2.rectangle(img0_draw, (x1, y1), (x, y), (255, 0, 0), 2)
                cv2.imshow("TRIM", img0_draw)

        elif event == cv2.EVENT_LBUTTONUP:
            if click == True:
                click = False
                img0_draw = img.copy()
                TRIM_END_X1, TRIM_END_Y1 = x, y
                img0_draw = cv2.rectangle(img0_draw, (x1, y1), (x, y), (255, 0, 0), 2)
                cv2.imshow("TRIM", img0_draw)
                mousestate = 1
    def _onMouse2(self, event, x, y, flags, param):
        global mousestate, img0_draw, x1, y1, click, img, TRIM_END_X2, TRIM_END_Y2, TRIM_START_X2, TRIM_START_Y2
        if mousestate == 1:
            return
        if event == cv2.EVENT_LBUTTONDOWN:
            click = True
            x1, y1 = x, y
            TRIM_START_X2, TRIM_START_Y2 = x, y

        elif event == cv2.EVENT_MOUSEMOVE:
            if click == True:
                img0_draw = img.copy()
                cv2.line(img0_draw, (x1, y1), (x, y), (255, 0, 0), 1)
                cv2.imshow("TRIM", img0_draw)
        elif event == cv2.EVENT_LBUTTONUP:
            if click == True:
                click = False
                img0_draw = img.copy()
                TRIM_END_X2, TRIM_END_Y2 = x, y
                cv2.line(img0_draw, (x1, y1), (x, y), (255, 0, 0), 1)
                cv2.imshow("TRIM", img0_draw)
                mousestate = 1
