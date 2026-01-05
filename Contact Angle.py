import functions as Ca
import gc
import tracemalloc
# Global val

path = "./dynamic2/50cm/WSP-30deg/"
path2 = "./Complete/ContactAngle2"
imgtype = '.png'
scalenumber = 11.4155
font2 = {'family': 'Arial','color': 'yellow','weight': 'bold','size': 12,'alpha': 1}
ticktime = []
tickname = []
PLT = False
PLT2 = True
CON = True
USETRIMNUM = False
SHOWFRAME = True
TURNONPLOT = True
tD = 1900
quick = False
Xpos_num = 0
alpha = 0
Framenumber = 20000
YLocation = 0

def tt(i):
    _img_list = Ca.src2image(_src_list[i],3,_file_lst[i])
    Test = Ca.HighSpeedImage(_img_list)
    Test.setName(path2,_file_lst[i])
    Test.load_Horizon()
    Test.bulktest()
    Test.spreading()
    Test.ploting()
    Test.save_Data()

def tt3(i):
    _img_list = Ca.src2image(_src_list[i],3,_file_lst[i])
    Test = Ca.HighSpeedImage(_img_list)
    Test.setName(path2,_file_lst[i])
    Test.detect_endofrim('r')
def tt2(i):
    _img_list = Ca.src2image(_src_list[i],3,_file_lst[i])
    Test = Ca.HighSpeedImage(_img_list)
    Test.setName(path2,_file_lst[i])
    Test.load_Horizon_only()
    Test.setvelContrast('a')
    Test.save_Horizon()

def Image2BinImage(i,savepath):
    #set ground value
    Test = Ca.HighSpeedImage(Ca.src2image(_src_list[i],3,_file_lst[i]))
    Test.setName(path2,_file_lst[i],scalenumber)
    Test._savepath = ""
    Test.setvelContrast('a')
    Test.saveto(savepath)
    Test.saveContours(savepath)

def Image2BinImage2(i,savepath):
    #set threhosld value & contrast value
    # save contours
    Test = Ca.HighSpeedImage(Ca.src2image(_src_list[i],3,_file_lst[i]))
    Test.setName(path2,_file_lst[i],scalenumber)
    Test._savepath = ""
    Test.setvelContrast('p')
    Test.setthresholdvalue('p')
    Test.saveto(savepath)
    Test.saveContours(savepath)

def getspreadfactor(src,height,surface,degree,viscosity,number):
    print("height :",height,"\tsurface :",surface,"\tdegree :",degree,"\tviscosity",viscosity,"\tnumber :",number)
    Test = Ca.HighSpeedImage([0])
    num = '00'+str(number)
    Test.loadto(src,height,surface,degree,viscosity,num)
    Test.loadContours(src,height,surface,degree,viscosity,num)
    Test.bulktest_onlycontour()
    #Test.saveheight()
    Test.spreading_contour('./tempsave/')
    Test.saveto('./tempsave/')
def getcontactangle(src,height,surface,degree,viscosity,number):
    Test = Ca.HighSpeedImage([0])
    num = '00'+str(number)
    Test.loadto(src,height,surface,degree,viscosity,num)
    Test.loadContours(src,height,surface,degree,viscosity,num)
    Test.getpoints_onlycontour('a')

if __name__ == '__main__':
    tracemalloc.start()
    # readcontour(path4)
    """
    scalenumber = 11.4155
    path = "./re/"
    path0 = path
    _src_list,_file_lst = src_list(path,imgtype)
    for i in range(len(_src_list)):
        tt(i)
    """
    scalenumber = 11.4155
    # scalenumber = 10.6359
    path = "../../High speed cam images/dynamic2/25cm/AL-15deg/"
    # path = "../../High speed cam images/0718/75cm/"
    path0 = path
    _src_list, _file_lst = Ca.src_list(path, imgtype)
    
    # for i in range(len(_src_list)):
    #     Image2BinImage2(i,'./tempsave0904/')
    # exit(0)
    src = './tempsave0904/'
    getcontactangle(src,20,'AL',0,5,5)
    # getspreadfactor(src, 25, 'AL', 45, 1, 1)
    # getspreadfactor(src, 25, 'AL', 45, 1, 2)
    # getspreadfactor(src, 25, 'AL', 45, 1, 3)
    # getspreadfactor(src, 25, 'AL', 45, 1, 4)
    # getspreadfactor(src, 25, 'AL', 45, 1, 5)

    # getspreadfactor(src, 50, 'AL', 30, 1, 1)
    # getspreadfactor(src, 50, 'AL', 30, 1, 2)
    # getspreadfactor(src, 50, 'AL', 30, 1, 3)
    # getspreadfactor(src, 50, 'AL', 30, 1, 4)
    # getspreadfactor(src, 50, 'AL', 30, 1, 5)

    # getspreadfactor(src, 75, 'WSP', 45, 1, 1)
    # getspreadfactor(src, 75, 'WSP', 45, 1, 2)
    # getspreadfactor(src, 75, 'WSP', 45, 1, 3)
    # getspreadfactor(src, 75, 'WSP', 45, 1, 4)
    # getspreadfactor(src, 75, 'WSP', 45, 1, 5)

    getspreadfactor(src, 20, 'AL', 0, 5, 1)
    getspreadfactor(src, 20, 'AL', 0, 5, 2)
    getspreadfactor(src, 20, 'AL', 0, 5, 3)
    getspreadfactor(src, 20, 'AL', 0, 5, 4)
    getspreadfactor(src, 20, 'AL', 0, 5, 5)

    getspreadfactor(src, 20, 'AL', 0, 10, 1)
    getspreadfactor(src, 20, 'AL', 0, 10, 2)
    getspreadfactor(src, 20, 'AL', 0, 10, 3)
    getspreadfactor(src, 20, 'AL', 0, 10, 4)
    getspreadfactor(src, 20, 'AL', 0, 10, 5)

    getspreadfactor(src, 20, 'AL', 0, 15, 1)
    getspreadfactor(src, 20, 'AL', 0, 15, 2)
    getspreadfactor(src, 20, 'AL', 0, 15, 3)
    getspreadfactor(src, 20, 'AL', 0, 15, 4)
    getspreadfactor(src, 20, 'AL', 0, 15, 5)

    getspreadfactor(src, 20, 'AL', 15, 5, 1)
    getspreadfactor(src, 20, 'AL', 15, 5, 2)
    getspreadfactor(src, 20, 'AL', 15, 5, 3)
    getspreadfactor(src, 20, 'AL', 15, 5, 4)
    getspreadfactor(src, 20, 'AL', 15, 5, 5)

    getspreadfactor(src, 20, 'AL', 15, 10, 1)
    getspreadfactor(src, 20, 'AL', 15, 10, 2)
    getspreadfactor(src, 20, 'AL', 15, 10, 3)
    getspreadfactor(src, 20, 'AL', 15, 10, 4)
    getspreadfactor(src, 20, 'AL', 15, 10, 5)

    getspreadfactor(src, 20, 'AL', 15, 15, 1)
    getspreadfactor(src, 20, 'AL', 15, 15, 2)
    getspreadfactor(src, 20, 'AL', 15, 15, 3)
    getspreadfactor(src, 20, 'AL', 15, 15, 4)
    getspreadfactor(src, 20, 'AL', 15, 15, 5)

    getspreadfactor(src, 20, 'AL', 30, 5, 1)
    getspreadfactor(src, 20, 'AL', 30, 5, 2)
    getspreadfactor(src, 20, 'AL', 30, 5, 3)
    getspreadfactor(src, 20, 'AL', 30, 5, 4)
    getspreadfactor(src, 20, 'AL', 30, 5, 5)

    getspreadfactor(src, 20, 'AL', 30, 10, 1)
    getspreadfactor(src, 20, 'AL', 30, 10, 2)
    getspreadfactor(src, 20, 'AL', 30, 10, 3)
    getspreadfactor(src, 20, 'AL', 30, 10, 4)
    getspreadfactor(src, 20, 'AL', 30, 10, 5)

    getspreadfactor(src, 20, 'AL', 30, 15, 1)
    getspreadfactor(src, 20, 'AL', 30, 15, 2)
    getspreadfactor(src, 20, 'AL', 30, 15, 3)
    getspreadfactor(src, 20, 'AL', 30, 15, 4)
    getspreadfactor(src, 20, 'AL', 30, 15, 5)

    getspreadfactor(src, 20, 'AL', 45, 5, 1)
    getspreadfactor(src, 20, 'AL', 45, 5, 2)
    getspreadfactor(src, 20, 'AL', 45, 5, 3)
    getspreadfactor(src, 20, 'AL', 45, 5, 4)
    getspreadfactor(src, 20, 'AL', 45, 5, 5)

    getspreadfactor(src, 20, 'AL', 45, 10, 1)
    getspreadfactor(src, 20, 'AL', 45, 10, 2)
    getspreadfactor(src, 20, 'AL', 45, 10, 3)
    getspreadfactor(src, 20, 'AL', 45, 10, 4)
    getspreadfactor(src, 20, 'AL', 45, 10, 5)

    getspreadfactor(src, 20, 'AL', 45, 15, 1)
    getspreadfactor(src, 20, 'AL', 45, 15, 2)
    getspreadfactor(src, 20, 'AL', 45, 15, 3)
    getspreadfactor(src, 20, 'AL', 45, 15, 4)
    getspreadfactor(src, 20, 'AL', 45, 15, 5)
    
    getspreadfactor(src, 20, 'WSP', 0, 5, 1)
    getspreadfactor(src, 20, 'WSP', 0, 5, 2)
    getspreadfactor(src, 20, 'WSP', 0, 5, 3)
    getspreadfactor(src, 20, 'WSP', 0, 5, 4)
    getspreadfactor(src, 20, 'WSP', 0, 5, 5)

    getspreadfactor(src, 20, 'WSP', 0, 10, 1)
    getspreadfactor(src, 20, 'WSP', 0, 10, 2)
    getspreadfactor(src, 20, 'WSP', 0, 10, 3)
    getspreadfactor(src, 20, 'WSP', 0, 10, 4)
    getspreadfactor(src, 20, 'WSP', 0, 10, 5)

    getspreadfactor(src, 20, 'WSP', 0, 15, 1)
    getspreadfactor(src, 20, 'WSP', 0, 15, 2)
    getspreadfactor(src, 20, 'WSP', 0, 15, 3)
    getspreadfactor(src, 20, 'WSP', 0, 15, 4)
    # getspreadfactor(src, 20, 'WSP', 0, 15, 5)
    


    # getspreadfactor(src, 50, 'AL', 0, 5, 1)
    getspreadfactor(src, 50, 'AL', 0, 5, 2)
    getspreadfactor(src, 50, 'AL', 0, 5, 3)
    getspreadfactor(src, 50, 'AL', 0, 5, 4)
    getspreadfactor(src, 50, 'AL', 0, 5, 5)

    getspreadfactor(src, 50, 'AL', 0, 10, 1)
    getspreadfactor(src, 50, 'AL', 0, 10, 2)
    getspreadfactor(src, 50, 'AL', 0, 10, 3)
    getspreadfactor(src, 50, 'AL', 0, 10, 4)
    getspreadfactor(src, 50, 'AL', 0, 10, 5)

    getspreadfactor(src, 50, 'AL', 0, 15, 1)
    getspreadfactor(src, 50, 'AL', 0, 15, 2)
    getspreadfactor(src, 50, 'AL', 0, 15, 3)
    getspreadfactor(src, 50, 'AL', 0, 15, 4)
    getspreadfactor(src, 50, 'AL', 0, 15, 5)

    getspreadfactor(src, 50, 'AL', 15, 15, 1)
    getspreadfactor(src, 50, 'AL', 15, 15, 2)
    getspreadfactor(src, 50, 'AL', 15, 15, 3)
    getspreadfactor(src, 50, 'AL', 15, 15, 4)
    getspreadfactor(src, 50, 'AL', 15, 15, 5)

    getspreadfactor(src, 50, 'AL', 30, 15, 1)
    getspreadfactor(src, 50, 'AL', 30, 15, 2)
    # getspreadfactor(src, 50, 'AL', 30, 15, 3)
    # getspreadfactor(src, 50, 'AL', 30, 15, 4)
    # getspreadfactor(src, 50, 'AL', 30, 15, 5)

    # getspreadfactor(src, 50, 'AL', 45, 15, 1)
    getspreadfactor(src, 50, 'AL', 45, 15, 2)
    # getspreadfactor(src, 50, 'AL', 45, 15, 3)
    # getspreadfactor(src, 50, 'AL', 45, 15, 4)
    getspreadfactor(src, 50, 'AL', 45, 15, 5)
    
    getspreadfactor(src, 50, 'WSP', 0, 5, 1)
    getspreadfactor(src, 50, 'WSP', 0, 5, 2)
    getspreadfactor(src, 50, 'WSP', 0, 5, 3)
    getspreadfactor(src, 50, 'WSP', 0, 5, 4)
    getspreadfactor(src, 50, 'WSP', 0, 5, 5)

    getspreadfactor(src, 50, 'WSP', 0, 10, 1)
    getspreadfactor(src, 50, 'WSP', 0, 10, 2)
    getspreadfactor(src, 50, 'WSP', 0, 10, 3)
    getspreadfactor(src, 50, 'WSP', 0, 10, 4)
    getspreadfactor(src, 50, 'WSP', 0, 10, 5)

    getspreadfactor(src, 50, 'WSP', 0, 15, 1)
    getspreadfactor(src, 50, 'WSP', 0, 15, 2)
    getspreadfactor(src, 50, 'WSP', 0, 15, 3)
    getspreadfactor(src, 50, 'WSP', 0, 15, 4)
    getspreadfactor(src, 50, 'WSP', 0, 15, 5)
    
    getspreadfactor(src, 75, 'AL', 0, 5, 1)
    getspreadfactor(src, 75, 'AL', 0, 5, 2)
    getspreadfactor(src, 75, 'AL', 0, 5, 3)
    getspreadfactor(src, 75, 'AL', 0, 5, 4)
    getspreadfactor(src, 75, 'AL', 0, 5, 5)

    getspreadfactor(src, 75, 'AL', 0, 10, 1)
    getspreadfactor(src, 75, 'AL', 0, 10, 2)
    getspreadfactor(src, 75, 'AL', 0, 10, 3)
    getspreadfactor(src, 75, 'AL', 0, 10, 4)
    getspreadfactor(src, 75, 'AL', 0, 10, 5)

    getspreadfactor(src, 75, 'AL', 0, 15, 1)
    getspreadfactor(src, 75, 'AL', 0, 15, 2)
    getspreadfactor(src, 75, 'AL', 0, 15, 3)
    # getspreadfactor(src, 75, 'AL', 0, 15, 4)
    getspreadfactor(src, 75, 'AL', 0, 15, 5)

    # getspreadfactor(src, 75, 'WSP', 0, 5, 1)
    # getspreadfactor(src, 75, 'WSP', 0, 5, 2)
    getspreadfactor(src, 75, 'WSP', 0, 5, 3)
    # getspreadfactor(src, 75, 'WSP', 0, 5, 4)
    # getspreadfactor(src, 75, 'WSP', 0, 5, 5)

    getspreadfactor(src, 75, 'WSP', 0, 10, 1)
    getspreadfactor(src, 75, 'WSP', 0, 10, 2)
    # getspreadfactor(src, 75, 'WSP', 0, 10, 3)
    # getspreadfactor(src, 75, 'WSP', 0, 10, 4)
    getspreadfactor(src, 75, 'WSP', 0, 10, 5)

    getspreadfactor(src, 75, 'WSP', 0, 15, 1)
    getspreadfactor(src, 75, 'WSP', 0, 15, 2)
    getspreadfactor(src, 75, 'WSP', 0, 15, 3)
    getspreadfactor(src, 75, 'WSP', 0, 15, 4)
    getspreadfactor(src, 75, 'WSP', 0, 15, 5)

    getspreadfactor(src, 75, 'WSP', 15, 15, 1)
    getspreadfactor(src, 75, 'WSP', 15, 15, 2)
    getspreadfactor(src, 75, 'WSP', 15, 15, 3)
    getspreadfactor(src, 75, 'WSP', 15, 15, 4)
    getspreadfactor(src, 75, 'WSP', 15, 15, 5)

    getspreadfactor(src, 75, 'WSP', 30, 15, 1)
    getspreadfactor(src, 75, 'WSP', 30, 15, 2)
    getspreadfactor(src, 75, 'WSP', 30, 15, 3)
    getspreadfactor(src, 75, 'WSP', 30, 15, 4)
    getspreadfactor(src, 75, 'WSP', 30, 15, 5)

    # getspreadfactor(src, 75, 'WSP', 45, 15, 1)
    # getspreadfactor(src, 75, 'WSP', 45, 15, 2)
    getspreadfactor(src, 75, 'WSP', 45, 15, 3)
    getspreadfactor(src, 75, 'WSP', 45, 15, 4)
    getspreadfactor(src, 75, 'WSP', 45, 15, 5)


    

