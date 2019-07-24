"""
Dynamic Time Warping.
"""

import numpy as np
from funcPeakAlign import deriv1, peakDetection
import time
from funcGeneral import min3,argmin3, normSimple
from copy import deepcopy

def distancePeak(X,Y,band,D=0.02, derivative=True,peakBonus=True):
## New cost calculation. D is used for the time penalty rate. 
# If peakBonus is True, cost of the peak points is reduced.
    n=len(X)
    m=len(Y)
    linfo=np.finfo(dtype='f4')
    maxFloat=linfo.max
    costM=np.ones([n,m])*maxFloat
    for i in range(n):
        for j in np.arange(band[0,i],band[1,i]):
            #D=0.02 #  rate of exponential growth
            posSim=np.exp(-1*np.abs(i-j)*D)
            costM[i,j]=np.abs(X[i]-Y[j])*posSim
    
    if peakBonus:
        if derivative:
            derivX=X
            derivY=Y
        else:
            derivX=deriv1(X)
            derivY=deriv1(Y)
        for i in range(n-1):
            if np.sign(derivX[i]) > np.sign(derivX[i+1]):
                for j in np.arange(band[0,i],band[1,i]-1):
                    if np.sign(derivY[j]) > np.sign(derivY[j+1]):
                        costM[i,j]=costM[i,j]*0.8           
    return costM 

         
def euclideanCostWBand(X,Y,band):
    n=len(X)
    m=len(Y)
    linfo=np.finfo(dtype='f4')
    maxFloat=linfo.max
    costM=np.ones([n,m])*maxFloat
    for i in range(n):
        for j in np.arange(band[0,i],band[1,i]):
            costM[i,j]=(X[i]-Y[j])**2 
    return costM 

def euclideanCost(X,Y):
    n=len(X)
    m=len(Y)
    C=np.ones([n,m],dtype='f4')
    ### 
    for i in range(n):
        for j in range(m):
            C[i,j]=(X[i]-Y[j])**2
    return C 

def accumulatedCostMatrixWBand(X,Y,costM,bandM):
    n=len(X)
    m=len(Y)
    linfo=np.finfo(dtype='f4')
    maxFloat=linfo.max
    dtw=np.ones([n,m])*maxFloat
    dtw[0,0]=2*costM[0,0]
    for i in range(1,bandM[0,0]):
        if bandM[0,i]==0:
            dtw[i,0]=dtw[i-1,0]+costM[i,0]
        else:
            break   
    for i in range(1,bandM[1,0]):  # it means m for noband
        dtw[0,i]=dtw[0,i-1]+costM[0,i]
    for i in range(1,n):
        for j in range(bandM[0,i],bandM[1,i]):
            dtw[i,j]=costM[i,j]+min3(dtw[i-1,j],dtw[i,j-1],dtw[i-1,j-1])
            
    return dtw


def accumulatedCostMatrix(X,Y,costM):
    n=len(X)
    m=len(Y)
    dtw=np.zeros([n,m])
    for i in range(1,n):
        dtw[i,0]=dtw[i-1,0]+costM[i,0]
    for i in range(1,m):
        dtw[0,i]=dtw[0,i-1]+costM[0,i]
    for i in range(1,n):
        for j in range(1,m):
            dtw[i,j]=costM[i,j]+min3(dtw[i-1,j],dtw[i,j-1],dtw[i-1,j-1])
    return dtw
      

                                  
def optimalWarpingPath(dtw):
    pathX,pathY=[],[]
    i=dtw.shape[0]-1
    j=dtw.shape[1]-1
    pathX.append(i)
    pathY.append(j)
    while i>0 or j>0:
        if i==0:
            j=j-1
        elif j==0:
            i=i-1
        else:
            i,j = pathAppend0(dtw,i,j)
        pathX.append(i)
        pathY.append(j)
    pathX=np.array(pathX)
    pathY=np.array(pathY)
    pathX=pathX[::-1]
    pathY=pathY[::-1]
    return pathX, pathY

def pathAppend0(dtw,i,j):
    # classical Path append
    argM=argmin3(dtw[i-1,j-1],dtw[i-1,j],dtw[i,j-1])
    if argM==0:
        i=i-1
        j=j-1
    elif argM==1:
        i=i-1
    else:
        j=j-1
    return i,j

def pathAppend1(dtw,i,j, argM):
    # GAP  Path append
    argM[0]=argM[1]    
    argM[1]=argM[2]
    argM[2]=argmin3(dtw[i-1,j-1],dtw[i-1,j],dtw[i,j-1])
    if argM[2]==1:
        if argM[1]==1 and argM[0]==1:
            if dtw[i-1,j-1] < dtw[i,j-1]:
                i=i-1
                j=j-1
            else:
                j=j-1   
        else:
            i=i-1
    elif argM[2]==2:
        if argM[1]==2 and argM[0]==2:
            if dtw[i-1,j-1] < dtw[i-1,j]:
                i=i-1
                j=j-1
            else:
                i=i-1
        else:
            j=j-1
    else:
        i=i-1
        j=j-1
    
        
    return i,j, argM

                            
def optimalWarpingPath2(dtw):
    pathX,pathY=[],[]
    i=dtw.shape[0]-1
    j=dtw.shape[1]-1
    pathX.append(i)
    pathY.append(j)
    
    argM=np.zeros(3)
    
    while i>0 or j>0:
        if i==0:
            j=j-1
        elif j==0:
            i=i-1
        else:
            i,j, argM = pathAppend1(dtw,i,j, argM)
        
    
        pathX.append(i)
        pathY.append(j)
    pathX=np.array(pathX)
    pathY=np.array(pathY)
    pathX=pathX[::-1]
    pathY=pathY[::-1]
    return pathX, pathY

                                                    
def optimalWarpingPath3(dtw):
    pathX,pathY=[],[]
    N=dtw.shape[0]
    M=dtw.shape[1]
    i=dtw.shape[0]-1
    j=dtw.shape[1]-1
    pathX.append(i)
    pathY.append(j)
    
    while i>N-5 and j>M-5:
        if i==0:
            j=j-1
        elif j==0:
            i=i-1
        else:
            i,j = pathAppend0(dtw,i,j)
        pathX.append(i)
        pathY.append(j)
        print i,j
           
    argM=np.zeros(3)       
    while i>5 or j>5:
        if i==0:
            j=j-1
        elif j==0:
            i=i-1
        else:
            i,j, argM = pathAppend1(dtw,i,j, argM)
        pathX.append(i)
        pathY.append(j)
    
    while i>0 and j>0:
        if i==0:
            j=j-1
        elif j==0:
            i=i-1
        else:
            i,j = pathAppend0(dtw,i,j)  
    
        pathX.append(i)
        pathY.append(j)
    pathX=np.array(pathX)
    pathY=np.array(pathY)
    pathX=pathX[::-1]
    pathY=pathY[::-1]
    return pathX, pathY

def noBand(n,m):
    band=np.zeros([2,n],dtype='i4')
    for i in range(n):
        band[0,i] = 0
        band[1,i] = m
    return band

def SakoeChibaBand(n,m,r):
    # m=len(X), n=len(Y), r=fixed width 
    band=np.zeros([2,n],dtype='i4')
    #mnf=float(m)/float(n)
    mnf=float(m)/float(n)
    
    for i in range(n):
        band[0,i]=np.ceil(mnf*i-r) # int(np.max(np.array([ceil(i * mnf - r), 0.0 ])));
        band[1,i]=np.floor(mnf*i+r) #int(np.min(np.array([ceil(i * mnf - r), 0.0 ])));
        if  band[0,i]<0:
            band[0,i]=0
        if  band[1,i]>m:
            band[1,i]=m   
    return band

                                     
def dtwDer(x):
    n=len(x)
    out=np.zeros(n)
    for i in range(1,n-1):
        out[i] = ((x[i] - x[i-1]) + ((x[i+1] - x[i-1]) / 2.0)) / 2.0
    out[0] = out[1];
    out[n-1] = out[n-2]; 
    return out

def myDTW(X, Y, derivative=False, costMType='0',D=0.02, bandType = "noband", r=3, gap=True):
    """Dynamic Time Warping.
    Input
      * X - [1D numpy array float  first time series
      * *y* - [1D numpy array float] second time series
      * *derivative* - [bool] Derivative DTW (DDTW).
      * costMType='0', '1'  : 0--> Euclidian, 1: distancePeak
      * *wincond* - [string] window condition ('nowindow', 'sakoechiba') 
      * *r* - [float] sakoe-chiba window length
    Output
      * *d* - [float] normalized distance
      * *px* - [1D numpy array int] optimal warping path (for x time series) (for onlydist=False)
      * *py* - [1D numpy array int] optimal warping path (for y time series) (for onlydist=False)
      * *cost* - [2D numpy array float] cost matrix (for onlydist=False)
    """
    if derivative:
        XIn = dtwDer(X)
        YIn = dtwDer(Y)
    else:
        XIn = X
        YIn = Y
        
    if bandType == 'noband':
        bandM=noBand(len(XIn),len(YIn))
    elif bandType == 'sakoechiba':
        bandM=SakoeChibaBand(len(XIn),len(YIn),r)
    else:
        raise ValueError('Band %s is not available' % bandType)
    
   # t1=time.clock()
    if costMType=='0':
        costM=euclideanCostWBand(XIn,YIn,bandM) 
       # costM=euclideanCost(XIn,YIn)  
    elif costMType=='1':
        costM=distancePeak(XIn,YIn,bandM,D,derivative)
    else:
        ValueError('Cost Matrix %s is not available' % costMType)
 #   t2=time.clock()   
 #   print costMType,t1,t2,t2-t1 
    dtwM=accumulatedCostMatrixWBand(XIn,YIn,costM,bandM)
    #dtwM=accumulatedCostMatrix(XIn,YIn,costM)
    if gap:
        pathX,pathY=optimalWarpingPath(dtwM)
    else:
        print gap
        pathX,pathY=optimalWarpingPath3(dtwM)
            
    
    return pathX,pathY


def accumulatedCostMatrixLocal(X,Y,costM):
    n=len(X)
    m=len(Y)
    dtw=np.zeros([n,m])
    for i in range(1,n):
        dtw[i,0]= costM[i,0]
    for j in range(1,m):
        dtw[0,j] = dtw[0,j-1] + costM[0,j]
    for i in range(1,n):
        for j in range(1,m):
            dtw[i,j]=costM[i,j]+min3(dtw[i-1,j],dtw[i,j-1],dtw[i-1,j-1])
    return dtw
      
                                    
def optimalWarpingPathLocal(dtw):
    pathX,pathY=[],[]
    i=dtw.shape[0]-1
    j=dtw.shape[1]-1
    # Modifications for LOCAL
    j=np.argmin(dtw[i,:])
    
    pathX.append(i)
    pathY.append(j)
    while i>0 and j>0:
        i,j = pathAppend0(dtw,i,j)
        
        pathX.append(i)
        pathY.append(j)
    pathX=np.array(pathX)
    pathY=np.array(pathY)
    pathX=pathX[::-1]
    pathY=pathY[::-1]
    return pathX, pathY

                                   
def optimalWarpingPathLocal2(dtw):
    pathX,pathY=np.array([]),np.array([])
    i=dtw.shape[0]-1
    j=dtw.shape[1]-1
    # Modifications for LOCAL
    j=np.argmin(dtw[i,:])
    
    pathX=np.append(pathX,i)
    pathY=np.append(pathY,j)
    while i>0 and j>0:
        i,j = pathAppend1(dtw,i,j)
        
        pathX=np.append(pathX,i)
        pathY=np.append(pathY,j)
    pathX=pathX[::-1]
    pathY=pathY[::-1]
    return pathX, pathY

def myDTWLocal(X, Y, derivative=False, costMType='0',D=0.02, bandType = "noband", r=3, gap=True):
    if derivative:
        XIn = dtwDer(X)
        YIn = dtwDer(Y)
    else:
        XIn = X
        YIn = Y
        
    
    bandM=noBand(len(XIn),len(YIn))
   # t1=time.clock()
    if costMType=='0':
        costM=euclideanCost(XIn,YIn) 
       # costM=euclideanCost(XIn,YIn)  
    elif costMType=='1':
        costM=distancePeak(XIn,YIn,bandM,D,derivative)
    else:
        ValueError('Cost Matrix %s is not available' % costMType)
 #   t2=time.clock()   
 #   print costMType,t1,t2,t2-t1 
    dtwM = accumulatedCostMatrixLocal(XIn,YIn,costM)
    #dtwM=accumulatedCostMatrix(XIn,YIn,costM)
    if gap:
        pathX,pathY=optimalWarpingPathLocal(dtwM)
    else:
        pathX,pathY=optimalWarpingPathLocal2(dtwM)
            
    
    return pathX,pathY


def autoROIwDTW(sampleData,refData):
    dataR=deepcopy(refData)
    if len(dataR)>1000:
        dataR=dataR[:1000]
    dataS = deepcopy(sampleData) 
    
    dataR, aver = normSimple (dataR)
    dataS, aver = normSimple (dataS)
    dataR = dataR*1000
    dataS = dataS*1000 
    
    start0, end0 = 0,len(dataS)
    for i in range(len(dataS)):
        if dataS[i]>100:
            start0 = i
            break  
    for i in range(len(dataS)-1,1,-1):
        if dataS[i]>50:
            end0 = i
            break
    
    dataS= dataS[start0:end0]
    dataS, aver = normSimple (dataS)
    dataS = dataS*1000 
      
    N = len(dataS)
    M = len(dataR)
    
    derivS = dtwDer(dataS)
    derivR = dtwDer(dataR)
     
    bandM=noBand(N,M)
   # costM=euclideanCost(derivS,derivR) 
    costM=distancePeak(derivS,derivR,bandM,D=0.0)
    dtwM = accumulatedCostMatrixLocal(derivS,derivR,costM)
    dtwSort = M + np.argsort(dtwM[M:,M-1]) 
    #print dtwSort[:50]
   # for i in range(50):
   #     k = dtwSort[i]
    #    print i,k-M, k, np.corrcoef(derivS[k-M:k], derivR)[0,1]
    corr=np.zeros(1)
    pathXX=[]
    pathYY=[]
    for k in range(len(corr)):
        i = int(dtwSort[k]) 
        j = int(M-1) #np.argmin(dtw[i,:])
        pathX,pathY=np.array([],int),np.array([],int)
        pathX=np.append(pathX,i)
        pathY=np.append(pathY,j)
        argM=np.zeros(3)
        while i>0 and j>0:
            i,j, argM = pathAppend1(dtwM,i,j,argM)
            pathX=np.append(pathX,i)
            pathY=np.append(pathY,j)
        pathX=pathX[::-1]
        pathY=pathY[::-1]
    
        pathXX.append(pathX)
        pathYY.append(pathY)
        
        dataXX=derivS[pathX]
        dataYY=derivR[pathY]
        corr[k] = np.corrcoef(dataXX, dataYY)[0,1]
    

    bestPathX = pathXX[np.argmax(corr)]
    bestPathY = pathYY[np.argmax(corr)]

    diff=bestPathX-bestPathY
    start=np.median(diff) + start0
#    lenX = bestPathX[-1]- bestPathX[0]
#    lenY = bestPathY[-1]- bestPathY[0]
#    diffLen=float(lenX)/float(lenY)
#    if diffLen>1.2 and diffLen<9.8:
#        diffLen = 1.0    
#    start = bestPathX[0] - bestPathY[0] + start0
#    
    
    end =  start + len(refData)
    
    
    return start, end


if __name__ == "__main__":
    import os
    
    import mlpy
    fname=os.getcwd()+'/data/hyg_applied_tools.txt'
    A=np.loadtxt(fname)
    X=A[:100,0]
    Y=A[:100,1]
    bandM=noBand(len(X),len(Y))
    costM=distancePeak(X,Y,bandM)
 
    pathX0,pathY0=myDTW(X,Y,derivative=True, costMType='0',bandType = "noband", r=3)
    pathX1,pathY1=myDTW(X,Y,derivative=True, costMType='1',bandType = "sakoechiba", r=3)
    
    peakX0,peakY0=peakDetection(X)
    peakX1,peakY1=peakDetection(Y)
    peakM=[]
    for i in peakX0:
        for j in peakX1:
            peakM.append([i,j])
    peakM=np.array(peakM) 
    
    import matplotlib
    import matplotlib.pyplot as plt
    
    plt.close('all')
    fig = plt.figure(1)
    axes0 = fig.add_subplot(111)
    axes0.plot(pathX0,pathY0,'r')
    axes0.plot(pathX1,pathY1,'b')
    axes0.plot(peakM[:,0],peakM[:,1],'k.')
    
    axes1.plot(pathNo[:,0],pathNo[:,1],'r')
#    axes1.plot(dtw2No,dtw3No,'b')
    
    plt.show()
 
#### TESTING MYDTW AND MLPY DTW    
#    t1=time.clock()
#    pathNo=myDTW(X,Y,derivative=True, bandType = "noband", r=3)
#    t2=time.clock()
#    print 'no',t1,t2,t2-t1
#    t1=time.clock()
#    pathSakoe=myDTW(X,Y,derivative=True, bandType = "sakoechiba", r=3)
#    t2=time.clock()
#    print 'sakoe',t1,t2,t2-t1
#    
#    t1=time.clock()
#    mydtw=mlpy.Dtw(derivative=True,onlydist=False, wincond="nowindow", r=0.0)
#    distance=mydtw.compute(X,Y)
#    dtw2No=mydtw.px
#    dtw3No=mydtw.py
#    t2=time.clock()
#    print 'no',t1,t2,t2-t1
#    
#    t1=time.clock()
#    mydtw=mlpy.Dtw(derivative=True,onlydist=False, wincond="sakoechiba", r=3.0)
#    distance=mydtw.compute(X,Y)
#    dtw2Sakoe=mydtw.px
#    dtw3Sakoe=mydtw.py
#    t2=time.clock()
#    print 'sakoe', t1,t2,t2-t1
#    
#    import matplotlib
#    import matplotlib.pyplot as plt
#    
#    plt.close('all')
#    fig = plt.figure(1)
#    axes0 = fig.add_subplot(211)
#    axes1= fig.add_subplot(212)
#    axes0.plot(pathSakoe[:,0],pathSakoe[:,1],'r')
#    axes0.plot(dtw2Sakoe,dtw3Sakoe,'b')
#    
#    axes1.plot(pathNo[:,0],pathNo[:,1],'r')
#    axes1.plot(dtw2No,dtw3No,'b')
#    
#    plt.show()
#
# 


