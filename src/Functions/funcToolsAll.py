import numpy as np
from funcGeneral import deriv2,setNegToZero, fitLinear, smoothRect
from copy import deepcopy
import scipy.signal
from funcPeakAlign import myPeakAlignment,DPeakAlignParams, splineSampleData, fPeakList, peakDetection
from scipy.optimize.minpack import leastsq
from funcSeqAll import normBox
from funcTimeWarp import myDTW


            # SATURATION CORRECTION 
def correctSatd(dataIn,Satd):
    NData=len(dataIn)
    NSatd=len(Satd)
    x0=np.arange(NData)
    dataOut=dataIn.copy()
    j=0
    for i in Satd:
        dataOut=np.delete(dataOut,(i-j))
        x0=np.delete(x0,(i-j))
        j+=1
        
    from scipy import interpolate
    tckS = interpolate.splrep(x0,dataOut,s=0)
    xnew=np.arange(NData)
    newData = interpolate.splev(xnew,tckS,der=0)
    
    return newData    
  
def fNewSatd(Satd,s,e):
    NSatd=len(Satd)
    newSatd=np.array([])
    for i in range(NSatd):
        if Satd[i]>=s and Satd[i]<e:
            newSatd=np.append(newSatd,(Satd[i]-s))
    return newSatd
                ### SMOOTHING  ###
def fSmooth(dataIn,degree=1,method='triangle'):
    NData=len(dataIn) 
    dataOut = np.zeros(NData)
    window = 2*degree+1
    if len(dataIn) < window:
        return dataOut
    if method == 'triangle':
        dataOut = smoothTriangle(dataIn,degree)
    elif method == 'rectangle':
        dataOut = smoothRect(dataIn,degree)
    elif method == 'gaussian':
        dataOut = smoothGaussian(dataIn,degree)
    return dataOut


 
def smoothTriangle(dataIn,degree=1):
    NData=len(dataIn)  
    dataOut=np.zeros(NData)
    window=degree*2+1  
    weight=np.arange(1,window+1) 
    #smoothed=array 
    for x in range(degree+1):
        weight[-(x+1)]=weight[x] # x+degree-1 #-abs(degree-(x+1))  
    for i in range(degree):
        dataOut[i]=sum(weight[degree-i:]*dataIn[:i+degree+1])/float(sum(weight[degree-i:]))
    for i in range(1,degree+1):
        dataOut[-i]=sum(weight[:degree+i]*dataIn[-(i+degree):])/float(sum(weight[:degree+i]))
    for i in range(degree,NData-degree):  
        dataOut[i]=sum(dataIn[i-degree:i+degree+1]*weight) / float(sum(weight))
    return dataOut  

def smoothGaussian(dataIn,degree=1):
    NData=len(dataIn)  
    dataOut=np.zeros(NData)
    window=degree*2-1  
    weight=np.ones(window)  
    weightGauss=[]  
    for i in range(window):  
        i=i-degree+1  
        frac=i/float(window)  
        gauss=1/(np.exp((4*(frac))**2))  
        weightGauss.append(gauss)  
    weight=np.array(weightGauss)*weight  
     
    for i in range(degree):
        dataOut[i]=dataIn[i]
    for i in range(1,degree+1):
        dataOut[-i]=dataIn[-i]
    for i in range(degree,(NData-degree)):  
        dataOut[i]=sum(dataIn[i-int(window/2):i+1+int(window/2)]*weight)/sum(weight)  
    return dataOut  

                ### BASELINE ADJUSTMENT  ###
def baselineAdjust(dataIn,window=80, isSmooth=False):
    dataOut=baselineAdjust0(dataIn,window,isSmooth)
    dataOut=baselineAdjust0(dataOut,window,isSmooth)
    dataOut=setNegToZero(dataOut)
    #min=np.min(dataOut)
    #bas=np.ones(len(dataOut))*min
    #dataOut=dataOut-bas
    return dataOut

def baselineAdjust0(dataIn,window=80, isSmooth=False):
    NData=len(dataIn)
    basAdjusted=deepcopy(dataIn)
    if NData<window:
        return basAdjusted
    minX,minY=findMinPoints(dataIn,window=window)
    if isSmooth:
        minY=scipy.signal.medfilt(minY,3) 
    fittedSig=fitLinear(minX,minY,NData=len(dataIn))
    basAdjusted=dataIn-fittedSig
    return basAdjusted

def findMinPoints(array,window=50):
    minX=np.array([])
    minY=np.array([])
    halfW=int(window/2)
    lastP=len(array)-halfW
      
    minX=np.append(minX,np.argmin(array[:halfW]))
    minY=np.append(minY,np.min(array[:halfW]))
    
    for i in range(halfW,lastP,window):
        minX=np.append(minX,i+np.argmin(array[i:i+window]))
        minY=np.append(minY,np.min(array[i:i+window]))
    
    minX=np.append(minX,lastP+np.argmin(array[lastP:]))
    minY=np.append(minY,np.min(array[lastP:]))
    
    return minX,minY

        ### SIGNAL DECAY CORRECTION ####
        
def autoDecaySum(dataIn, N1=200):
    N=len(dataIn)
    N0=int(N/2)     
    S=np.sum(dataIn)
    step=np.linspace(0,2*S,N1)
    scores=np.zeros(N1)
    for i in range(N1):
        S1=step[i]
        outA=decaySum1(dataIn,S1)
        aver0=np.average(outA[:N0])
        aver1=np.average(outA[N0:])
        scores[i]=np.abs(aver0-aver1)/aver0
   # np.savetxt('\decayreasult500.txt', scores)
    argmin0=np.argmin(scores)
    S1=step[argmin0]
    dataOut=decaySum1(dataIn,S1)
    averIn=np.average(dataIn[:N0])
    averOut=np.average(dataOut)
    dataOut=dataOut*averIn/averOut
    return dataOut

def decaySum1(inputA,S1):
    N=len(inputA)
    outA=inputA.copy()
    S=np.sum(inputA)
    S0=S.copy()
    inputA[0]=inputA[0]/(S0+S1)
    for i in np.arange(1,N):
        S0=S0-inputA[i-1]
        outA[i]=inputA[i]/(S0+S1) #np.sum(inputA[i:])
    return outA

def decaySum(inputA,factor=0.2):
    N=len(inputA)
    outA=inputA.copy()
    scale=np.sum(inputA)
    scale1=scale+scale*factor
    inputA[0]=(inputA[0]/scale1)*scale
    for i in np.arange(1,N):
        scale1=scale1-inputA[i-1]
        outA[i]=(inputA[i]/scale1)*scale #np.sum(inputA[i:])
        #outA[i]=inputA[i]/np.sum(inputA[i:])
    return outA
### EXPONENTIAL DECAY CORRECTION
def decayFunc(x,A):
    """Calculate the values y[i] of a single exponential function 
        y = a * power(b,x)+c """
    y=A[0] * np.power(A[1],x) + A[2]
    return y

def objective(A,x,y0,func):
    """Calculate residual deviation of simulated data and experimental data."""
    err=y0 - func(x,A)
    return err

def fitDecayFunc(x,y): 
    isFitted=False   
    function=decayFunc
    A0 = [y[0], 0.9, y[-1]]
    param = (x, y, function)
    A1, cov_x, infodict, mesg, ier = leastsq(objective, A0, args=param, full_output=True)
    if ier in [1,2,3,4]:
        isFitted=True
    return A1,isFitted

def decayCorrectionExp(data):
    expF=np.zeros(len(data))
    x,y=findDataToFit(data)
    A1,isFitted=fitDecayFunc(x,y)
    if isFitted:
        expF=decayFunc(x,A1)
        yNew=expF/expF[0]
        dataOut=data/yNew
    else:
        dataOut=decaySum(data)
    return dataOut,expF

def findDataToFit(data,deg=250,step=5):
    win=2*deg+1
    N=len(data)
    if N<win+step:
        win=int(N/2) 
    
    aX= np.arange(0,N,step)
    averY=np.array([])
    for i in aX:
        if i<(N-win):
            partData=data[i:i+win]
        else:
            partData=data[i-win:i]
        averY=np.append(averY,np.average(partData))
        
    aY=smoothRect(averY,degree=2)
    yNew=fitLinear(aX[1:-1],aY[1:-1],NData=len(data))
    xNew=np.arange(N)
    return xNew,yNew

                ### MOBILITY SHIFT  ###

dyesName=['5-FAM','6-FAM','TET','HEX','JOE','NED','VIC','TAMRA','PET','ROX']#,'LIZ']
dyesWL=[517,522,538,553,554,555,575,583,595,607]#,655]
dDyesWL=dict(zip(dyesName,dyesWL))#  {'5-FAM':517,'6-FAM':522,'TET':538,'HEX':553,'JOE':554,'VIC':555,'NED':575,'TAMRA':583,'PET':595,'ROX':607}#,'LIZ':655}

def fMobilityShift(dataR,dataS,dyeNR,dyeNS,method='posSim'):
    # method  --> peakSim, posSim,corr
    diff=dyesName.index(dyeNR)-dyesName.index(dyeNS)
    shiftNum=5+np.abs(diff)
    NDataR=len(dataR)
    NDataS=len(dataS)
    K=500
    if NDataR>(K+shiftNum) and NDataS>(K+shiftNum):
        corrWindow=K
    else:
        if NDataR>NDataS:
            corrWindow=NDataS-20
        else:
            corrWindow=NDataR-20          
            
    if diff<0:
        direction=1
    else:
        direction=-1
    
    linkX0=np.array([],int)
    linkX1=np.array([],int)
    k=int(NDataR/corrWindow)
    for i in range(k):
        if i==0 and k>2:
            s=i*2*corrWindow+shiftNum
            e=(i+1)*2*corrWindow+shiftNum
        else: 
            s=i*corrWindow+shiftNum
            e=(i+1)*corrWindow+shiftNum
        corrSigR=dataR[s:e]
        corrResult=np.zeros(shiftNum)
        for j in range(shiftNum):
            s1=s+j*direction
            e1=e+j*direction
            corrSigS=dataS[s1:e1]
            if method=='peakSim': 
                dPeakListR=fPeakList(corrSigR,isDel=False, isAdd=False)
                dPeakListS=fPeakList(corrSigS,isDel=False, isAdd=False)
                dParams=DPeakAlignParams()
                dParams['simFunc']='Position'
                dParams['isBackTrace']=False
                corrResult[j]=myPeakAlignment(dPeakListR,dPeakListS,dParams)
            elif method=='posSim': 
                peakXR=peakDetection(corrSigR, isY=False)
                peakXS=peakDetection(corrSigS, isY=False)
                corrResult[j]=fPeakPosComp(peakXR,peakXS)
                
        corrArgMax0=np.argmax(corrResult)
        corrArgMax0=corrArgMax0*direction
        linkX0=np.append(linkX0,s)
        linkX1=np.append(linkX1,s+corrArgMax0)
    newDataS=splineSampleData(dataS,dataR, linkX0,linkX1)
   
    return newDataS

def fPeakPosComp(pos0,pos1):
    N0=len(pos0)
    N1=len(pos1)
    scr=0
    for i in range(N0):
        diff=pos1-pos0[i]
        diff=np.abs(diff)
        min=np.min(diff)
        if min<2:
            scr+=1
    return scr

        ### SIGNAL ALIGNMENT###
 
def dtwAlign2Cap(dProject,usedSeq=['RXS1','BGS1','RXS2','BGS2'], isNormalize=True, isPeakSim=False):
    """
    Method: DTW, peakSim
    """   
### array 0 and array 2 is reference signals, array1 and array 3 is aligned.
### Control the length of the array and 
    keyRXS1=usedSeq[0]
    keyBGS1=usedSeq[1]
    keyRXS2=usedSeq[2]
    keyBGS2=usedSeq[3]
    
    dInput=dProject['dData']
### Step 1: Normalization
    dataRXS=dInput[usedSeq[0]].copy()
    dataBGS=dInput[usedSeq[1]].copy()  
    dataRXS=smoothTriangle(dataRXS)
    dataBGS=smoothTriangle(dataBGS)
    
    linkX0,linkX1=findPeakMatchX(dataRXS,dataBGS,isNormalize)
    return linkX0,linkX1

def splineCap(dProject,usedSeq,linkX0,linkX1):
    keyRXS1=usedSeq[0]
    keyBGS1=usedSeq[1]
    keyRXS2=usedSeq[2]
    keyBGS2=usedSeq[3]
    
    dInput=dProject['dData'].copy()
### Align the signals 
    newBGS1=splineSampleData(dInput[keyBGS1],dInput['RX'],linkX0,linkX1,False)
    newBG=splineSampleData(dInput['BG'],dInput['RX'],linkX0,linkX1,False)
    try:
        if len(dProject['Satd']['BG'])>0:
            NData0=len(dInput['BG'])
            NData1=len(dInput['RX'])
            dProject['Satd']['BG'] = splineSatdData(dProject['Satd']['BG'],linkX0,linkX1,NData0,NData1)
    except:
        pass
    
    dOutput=dInput.copy()   
    dOutput['BG']=newBG
    dOutput[keyBGS1]=newBGS1
    if keyBGS2 in dInput.keys():
        newBGS2=splineSampleData (dInput[keyBGS2],dInput['RX'],linkX0,linkX1,False)
        dOutput[keyBGS2]=newBGS2
    
    dProject['dData']=dOutput
    return dProject

def splineSatdData(Satd0,linkX0,linkX1,NData0,NData1):
    dataStad=np.zeros(NData0)
    dataStad[Satd0]=1
    newDataStad=splineSampleData(dataStad,linkX0,linkX1,NData1)
    newStad=np.array([])
    for i in range(len(newDataStad)):
        if newDataStad[i]>0.5:
            newStad=np.append(newStad,i)
    return newStad
def findMatchX_DTW(dataRXS,dataBGS,isNormalize=True):
    if isNormalize:
        dataRXS=normBox(dataRXS,1000)
        dataBGS=normBox(dataBGS,1000)
    
    r1=len(dataRXS)*0.05
    pathX,pathY= myDTW(dataRXS, dataBGS, derivative=True, costMType='0',D=0.02, bandType = "noband", r=r1, gap=True)
    linkX0,linkX1 = postpeakMatch0(pathX,pathY,step=100)
    
    return linkX0,linkX1

def findPeakMatchX(dataRXS,dataBGS,isNormalize=True):
    if isNormalize:
        dataRXS=normBox(dataRXS,1000)
        dataBGS=normBox(dataBGS,1000)
  
    dParameters= DPeakAlignParams()
    peakList0=fPeakList(dataRXS, isDel=False, isAdd=False,repType="Cubic")
    peakList1=fPeakList(dataBGS, isDel=False, isAdd=False,repType="Cubic")
    dParameters['simFunc']='Derivative'
    aligned0,aligned1=myPeakAlignment(peakList0,peakList1,dParameters)
    linkX0,linkX1=findAlignedPeakX(aligned0,aligned1) 
    linkX0,linkX1=postpeakMatch0(linkX0,linkX1)
    
  #  linkX0,linkX1=postpeakMatch1(peakList0,peakList1,aligned0,aligned1,dataRXS)
    
    return np.array(linkX0,int),np.array(linkX1,int)

def findAlignedPeakX(aligned0,aligned1):
    linkX0=np.array([],dtype='i4')
    linkX1=np.array([],dtype='i4')
    for i in range(len(aligned0)):
        if aligned0[i]!=-1 and aligned1[i]!=-1:
            linkX0=np.append(linkX0,aligned0[i])
            linkX1=np.append(linkX1,aligned1[i])
    return linkX0,linkX1

def postpeakMatch0(linkX0,linkX1, step=8): 
    newlinkX0=np.array([],dtype='i4')
    newlinkX1=np.array([],dtype='i4')
    diffLinkX=linkX0-linkX1
    NLinkX=len(linkX0)
    for i in range(0,NLinkX-step,step):
        diffStep=diffLinkX[i:i+step]
        NDiffStep2=int(len(diffStep)/2)
        diffStepArgSort=np.argsort(diffStep)
        argMedian=diffStepArgSort[NDiffStep2]+i
        newlinkX0=np.append(newlinkX0,linkX0[argMedian])
        newlinkX1=np.append(newlinkX1,linkX1[argMedian])
            
    return newlinkX0, newlinkX1

