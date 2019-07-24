import numpy as np
from imports import QtGui,QtCore
from copy import deepcopy

#chKeysCC=['RX','RXS1','RXS2','BG','BGS1','BGS2']
chKeysRS=['RX','BG','RXS1','BGS1','RXS2','BGS2']
#chKeysRX=['RX','RXS1','RXS2']
#chKeysBG=['BG','BGS1','BGS2']

def DData(isSeq2=False):
    if isSeq2:
        keys=['RX','BG','RXS1','BGS1','RXS2','BGS2']
    else:
        keys=['RX','BG','RXS1','BGS1']
    dData={}
    for key in keys:
        dData[key]=np.array([],dtype='f4')
    return dData

def DProjectNew():
    dProjectNew={}
## NEW PROJECT RESULTS
    dProjectNew['dData']=DData() #DData(dChKeys['RS'])# {'RX':np.array([0]),'BG':np.array([0]),'RXS':np.array([0]),'BGS':np.array([0])}
    dProjectNew['dir']= QtCore.QDir.homePath()# '' # Working directory "/Users/fethullah/example4"
    dProjectNew['name']='' #''  # Project Name
    dProjectNew['fName']='' # Project file name
    dProjectNew['fNameRX']='' # Project file name
    dProjectNew['fNameBG']='' # Project file name
    dProjectNew['fNameSeq']='' # Project file name
    dProjectNew['chIndex']={'RX':0, 'RXS1':1,'RXS2':2,'BG':0, 'BGS1':1,'BGS2':2 }
    dProjectNew['isRef']=False
    dProjectNew['fNameRef']='' # Project file name
    dProjectNew['Satd']={'RX':[],'BG':[]}
    dProjectNew['dyeN']=DData() #dict(zip(chKeys,['6-FAM','VIC','NED','6-FAM','VIC','NED']))
    dProjectNew['isSeq2']=False
    dProjectNew['RNA']=''  # Official RNA sequence
    dProjectNew['ddNTP1']='ddC' # ddNTP type of the sequences, RX BG
    dProjectNew['ddNTP2']='ddT' # ddNTP type of the sequences, RX BG
    dProjectNew['nuc1']='G'  # Nucleotide type of sequences
    dProjectNew['nuc2']='A'  # Nucleotide type of sequence
    dProjectNew['chKeyRS']=['RX', 'BG', 'RXS1', 'BGS1']
    dProjectNew['chKeyCC']=['RX', 'RXS1','BG', 'BGS1']
    dProjectNew['chKeyRX']=['RX', 'RXS1']
    dProjectNew['chKeyBG']=['BG', 'BGS1']
    dProjectNew['scriptList']=[]
    
    
## SEQUENCE ALIGNMENT RESULTS
    dProjectNew['seqRNA']=''
    dProjectNew['seqX0']=np.array([],dtype='i4') # X value of nuc, above threshold 
    dProjectNew['seq0']='' #Detected sequence
    dProjectNew['seqX']=np.array([],dtype='i4') # X value of completed seq
    dProjectNew['usedCh1']='BGS1' # used channel RXS1 or BGS1
    dProjectNew['usedCh2']='BGS2' # used channel RXS1 or BGS1
    dProjectNew['start']=0  # start point in RNA, roi 
    dProjectNew['end']=0# end point in RNA, roi 
    dProjectNew['seqNum']=np.array([],int)# end point in RNA, roi 
    dProjectNew['scrNuc']=np.array([],dtype='f4')
    
## REACTIVITY RESULTS 
    dProjectNew['dPeakRX']=DPeakList()
    dProjectNew['dPeakBG']=DPeakList()
 #   dProjectNew['dPeakBG']=DPeakList()
    
    dProjectNew['scaleFactor']=np.array([1])
    dProjectNew['areaDiff']=np.array([],dtype='f4')
    dProjectNew['normDiff']=np.array([],dtype='f4')
    
  
    return dProjectNew

def DPeakList():
    dPeakList={}
    dPeakList['NPeak']=0
    dPeakList['pos']=np.array([],dtype='i4')
    dPeakList['amp']=np.array([],dtype='f4')
    dPeakList['wid']=np.array([],dtype='f4')
    dPeakList['area']=np.array([],dtype='f4')
    dPeakList['averW']=np.array([],dtype='f4')
    dPeakList['minW']=np.array([],dtype='f4')
    dPeakList['maxW']=np.array([],dtype='f4')
    
    return dPeakList

def DVar(chKeyRS):
    colors=[QtGui.QColor('red').name(),QtGui.QColor('blue').name(),QtGui.QColor('green').name(),
            QtGui.QColor('magenta').name(),QtGui.QColor('orange').name(),QtGui.QColor('cyan').name()]
    dVar={}
    dVar
    dVar['lineVisible']={}
    dVar['lineColor']={}
    dVar['lineStyle']={}
    dVar['lineMarker']={}
    dVar['lineWidth']={}
    
    for i in range(len(chKeyRS)):
        key=chKeyRS[i]
        dVar['lineColor'][key]=colors[i]  
        dVar['lineVisible'][key]=True
        dVar['lineStyle'][key]='-'
        dVar['lineMarker'][key]=''
        dVar['lineWidth'][key]=1
    
    dVar['widthP']=100
    dVar['heightP']=100
    dVar['zoomP']=100
    dVar['left']=0.01
    dVar['right']=0.99
    dVar['top']=0.99
    dVar['bottom']=0.05
    
    dVar['maxLength']=0

#
    dVar['isDoneSeqAlign']=False
    dVar['isDoneSeqAlignRef']=False
    dVar['isDoneReactivity']=False
    
## CONTROL FLAGS
    dVar['flag']={}
    dVar['flag']['isDrawStad']=False
    dVar['flag']['isSeqAlign']=False
    dVar['flag']['isDrawLine']=False
    dVar['flag']['isDrawGauss']=False
    
    dVar['flag']['isSatd']=False
    dVar['flag']['isScale']=False
    dVar['flag']['isPeakMatchModify']=False
    dVar['flag']['isPeakLinkRefModify']=False
    dVar['flag']['isDrawRef']=False
    
    
    return dVar
    
def globalVars():
    dGlobalVars={}
    dGlobalVars['dye']={'5-FAM':517,'6-FAM':522,'TET':538,'HEX':553,'JOE':554,'VIC':555,'NED':575,'TAMRA':583,'PET':595,'ROX':607,'LIZ':655}
    return dGlobalVars
       
def maxLenF(dData):
    maxLen=len(dData['RX'])
    for key in dData.keys():
        try:
            len1=len(dData[key])
        except:
            len1=0
        if len1>maxLen:
            maxLen=len1
    return maxLen

def minLenF(dData):
    minLen=len(dData['RX'])
    for key in dData.keys():
        if len(dData[key])>0:
            len1=len(dData[key])
            if len1<minLen:
                minLen=len1
    return minLen

def setNucColor(nuc):
    clr='k'
    if nuc=='G':
        clr='r'
    elif nuc=='C':
        clr='g'
    elif nuc=='A':
        clr='b'
    elif nuc=='U':
        clr='m'
    return clr
        
def clickedSeqAlign(x,dProject,eventKey,conFromBGToRX,conFromSeqToBG,chAxes):
    diff=np.abs(dProject['seqX0']-x)
    peakInd= int(np.argmin(diff))
    if eventKey== QtCore.Qt.Key_A:
        if x>dProject['seqX0'][peakInd]:
            peakInd=peakInd+1
        dProject['seq0'].insert(peakInd,'N')
        dProject['seqX0']=np.insert(dProject['seqX0'],peakInd,x)
        
        argmax=argmax3(dProject['dData']['RX'][x-1],dProject['dData']['RX'][x],dProject['dData']['RX'][x+1])
        x=x-1+argmax
        dProject['dPeakRX']['pos']=np.insert(dProject['dPeakRX']['pos'],peakInd,x)
        dProject['dPeakRX']['amp']=np.insert(dProject['dPeakRX']['amp'],peakInd,dProject['dData']['RX'][x])
        dProject['dPeakRX']['NPeak']=dProject['dPeakRX']['NPeak']+1
        
        argmax=argmax3(dProject['dData']['BG'][x-1],dProject['dData']['BG'][x],dProject['dData']['BG'][x+1])
        x=x-1+argmax
        dProject['dPeakBG']['pos']=np.insert(dProject['dPeakBG']['pos'],peakInd,x)
        dProject['dPeakBG']['amp']=np.insert(dProject['dPeakBG']['amp'],peakInd,dProject['dData']['BG'][x])
        dProject['dPeakBG']['NPeak']=dProject['dPeakBG']['NPeak']+1 
    elif eventKey== QtCore.Qt.Key_D:
        del dProject['seq0'][peakInd]
        dProject['seqX0']=np.delete(dProject['seqX0'],peakInd)  
        dProject['dPeakRX']['pos']=np.delete(dProject['dPeakRX']['pos'],peakInd)
        dProject['dPeakRX']['amp']=np.delete(dProject['dPeakRX']['amp'],peakInd)
        dProject['dPeakRX']['NPeak']=dProject['dPeakRX']['NPeak']-1
        dProject['dPeakBG']['pos']=np.delete(dProject['dPeakBG']['pos'],peakInd)
        dProject['dPeakBG']['amp']=np.delete(dProject['dPeakBG']['amp'],peakInd)
        dProject['dPeakBG']['NPeak']=dProject['dPeakBG']['NPeak']-1      
    else:
        if dProject['seq0'][peakInd]=='N':
            dProject['seq0'][peakInd]=dProject['nuc1']
        elif dProject['seq0'][peakInd]==dProject['nuc1']:
            if dProject['isSeq2']:
                dProject['seq0'][peakInd]=dProject['nuc2']
            else:
                dProject['seq0'][peakInd]='N'
        elif dProject['isSeq2'] and dProject['seq0'][peakInd]==dProject['nuc2']:
            dProject['seq0'][peakInd]='N'
 
    from matplotlib.patches import ConnectionPatch
    
    if eventKey== QtCore.Qt.Key_A:
        xyA=(dProject['dPeakBG']['pos'][peakInd], dProject['dPeakBG']['amp'][peakInd])
        xyB=(dProject['dPeakRX']['pos'][peakInd], dProject['dPeakRX']['amp'][peakInd])
        con0 = ConnectionPatch(xyA,xyB,coordsA="data",coordsB="data",axesA=chAxes['BG'], axesB=chAxes['RX'],
                                  arrowstyle="<|-|>",ec='0.3')
        chAxes['BG'].add_artist(con0)
        conFromBGToRX.insert(peakInd,con0)
                    
        xyA=(dProject['seqX0'][peakInd], dProject['dData']['BGS1'][dProject['seqX0'][peakInd]])
        xyB=(dProject['dPeakBG']['pos'][peakInd], dProject['dPeakBG']['amp'][peakInd])
        con1 = ConnectionPatch(xyA,xyB,coordsA="data",coordsB="data",axesA=chAxes['BGS1'], axesB=chAxes['BG'],
                      arrowstyle="<|-|>",ec='0.3')
        chAxes['BGS1'].add_artist(con1)
        conFromSeqToBG.insert(peakInd,con1)  
#      canvas.draw()
    if eventKey== QtCore.Qt.Key_D:
        conFromBGToRX[peakInd].remove()
        conFromSeqToBG[peakInd].remove()
        del  conFromBGToRX[peakInd]
        del  conFromSeqToBG[peakInd]
                    
    return dProject,peakInd,conFromBGToRX,conFromSeqToBG


def clickLines(x,chAxes,eventAxes,dPeakM,conFromBGToRX,isArrowSelectedRX, isArrowSelectedBG):
    if eventAxes==chAxes['RX']:
        if isArrowSelectedRX==False:
            diff=np.abs(dPeakM['RX'][:,0]-x)
            clickedPeakInd= np.argmin(diff)
            conFromBGToRX[clickedPeakInd].set_ec('c')
            conFromBGToRX[clickedPeakInd].set_fc('c')
            isArrowSelectedRX=True
    elif eventAxes==chAxes['BG']:
        if isArrowSelectedBG==False:
            diff=np.abs(dPeakM['BG'][:,0]-x)
            clickedPeakInd= np.argmin(diff)
            conFromBGToRX[clickedPeakInd].set_ec('c')
            conFromBGToRX[clickedPeakInd].set_fc('c')
            isArrowSelectedBG=True
    return  conFromBGToRX,isArrowSelectedRX,isArrowSelectedBG

def findAxesYLim(dData,drawType):
    minData={}
    maxData={}
    dAxesYLim={}
    for key in dData.keys():
        minData[key]=np.min(dData[key])
        maxData[key]=np.max(dData[key])
        dAxesYLim[key]=[minData[key],maxData[key]]
    if 'RXS2' in dData.keys():
        if minData['RXS2']<minData['RXS1']:
            minData['RXS1']=minData['RXS2']
        if maxData['RXS2']>maxData['RXS1']:
            maxData['RXS1']=maxData['RXS2']
    if 'BGS2' in dData.keys():
        if minData['BGS2']<minData['BGS1']:
            minData['BGS1']=minData['BGS2']
        if maxData['BGS2']>maxData['BGS1']:
            maxData['BGS1']=maxData['BGS2']       
    if drawType==1:
        dAxesYLim['RX'][0]=np.min(np.array([minData['RX'],minData['BG']]))
        dAxesYLim['RX'][1]=np.max(np.array([maxData['RX'],maxData['BG']]))
        dAxesYLim['BG']=dAxesYLim['RX']
        dAxesYLim['RXS1'][0]=np.min(np.array([minData['RXS1'],minData['BGS1']]))
        dAxesYLim['RXS1'][1]=np.max(np.array([maxData['RXS1'],maxData['BGS1']]))
        dAxesYLim['BGS1']=dAxesYLim['RXS1']
    if drawType==2:
        dAxesYLim['RX'][0]=np.min(np.array([minData['RX'],minData['BG'],minData['RXS1'],minData['BGS1']]))
        dAxesYLim['RX'][1]=np.max(np.array([maxData['RX'],maxData['BG'],maxData['RXS1'],maxData['BGS1']]))
        dAxesYLim['BG']=dAxesYLim['RX']
        dAxesYLim['RXS1']=dAxesYLim['RX']
        dAxesYLim['RXS1']=dAxesYLim['RX']
    if drawType==3:
        dAxesYLim['RX'][0]=np.min(np.array([minData['RX'],minData['RXS1']]))
        dAxesYLim['RX'][1]=np.max(np.array([maxData['RX'],maxData['RXS1']]))
        dAxesYLim['RXS1']=dAxesYLim['RX']
        dAxesYLim['BG'][0]=np.min(np.array([minData['BG'],minData['BGS1']]))
        dAxesYLim['BG'][1]=np.max(np.array([maxData['BG'],maxData['BGS1']]))
        dAxesYLim['BGS1']=dAxesYLim['BG']    
    return dAxesYLim


def setRcParams(rcParams):
    rcParams['font.size'] = 9
    rcParams['lines.markersize']=4
    rcParams['legend.fontsize']=10
    rcParams['xtick.labelsize']='small'
    rcParams['ytick.labelsize']='small'
    rcParams['xtick.color']='k'
    rcParams['ytick.color']='k'
    rcParams['figure.dpi']=100
    return True
 
dyesName=['5-FAM','6-FAM','TET','HEX','JOE','NED','VIC','TAMRA','PET','ROX']#,'LIZ']
dyesWL=[517,522,538,553,554,555,575,583,595,607]#,655]
dDyesWL=dict(zip(dyesName,dyesWL))#  {'5-FAM':517,'6-FAM':522,'TET':538,'HEX':553,'JOE':554,'VIC':555,'NED':575,'TAMRA':583,'PET':595,'ROX':607}#,'LIZ':655}
#print dDyesWL

def deriv2(array):
    n=len(array)
    d=np.zeros(n)
    d[0]=d[1]
    d[n-1]=d[n-2]
    for j in np.arange(1,n-1):
        d[j]=array[j+1]-2*array[j]+array[j-1]
    return d

##### DERIVATIVE ########
def deriv1(array):
    n=len(array)
    d=np.zeros(n)
    d[0]=array[1]-array[0]
    d[n-1]=array[n-1]-array[n-2]
    for j in np.arange(1,n-1):
        d[j]=(array[j+1]-array[j-1])/2
    return d

def min3(a,b,c):
    minvalue = a
    if b < minvalue:
        minvalue = b
    if c < minvalue:
        minvalue = c
    return minvalue

def argmin3(a,b,c):
    minvalue = a
    argmin=0
    if b < minvalue:
        minvalue = b
        argmin=1
    if c < minvalue:
        argmin=2
    return argmin


def max3(a,b,c):
    maxvalue = a
    if b > maxvalue:
        maxvalue = b
    if c > maxvalue:
        maxvalue = c
    return maxvalue

def argmax3(a,b,c):
    maxvalue = a
    argmax=0
    if b > maxvalue:
        maxvalue = b
        argmax=1
    if c > maxvalue:
        argmax=2
    return argmax



def max2(a,b):
    maxvalue = a
    if b > maxvalue:
        maxvalue = b
    return maxvalue

def argmax2(a,b):
    maxvalue = a
    argmax=0
    if b > maxvalue:
        maxvalue = b
        argmax=1
    return argmax

def setNegToZero(dataIn):
    NData=len(dataIn)
    dataOut=dataIn.copy()
    for i in range(NData):
        if dataIn[i]<0:
            dataOut[i]=0
    return dataOut

def averQ(dataIn):
    NData=len(dataIn)
    dataSorted=np.sort(dataIn)
    a1=int(NData*0.25) 
    a3=int(NData*0.75)
    aver=np.average(dataSorted[a1:a3])
    
    return aver

def findClickedInd(x,array):
    diff=np.abs(array-x)
    clickedInd=int(np.argmin(diff))
    return clickedInd

def fitLinear(x,y,NData):
    fittedData=np.zeros(NData)
    fittedData[0:x[0]]=y[0]
    fittedData[x[-1]:]=y[-1]
    NPoint=len(x)
    
    for i in range(NPoint-1):
        x1=np.array([x[i],x[i+1]])
        y1=np.array([y[i],y[i+1]])
        coeff=np.polyfit(x1,y1,1)
        poly=np.poly1d(coeff)
        xNew=np.arange(x[i],x[i+1])
        xNew=np.array(xNew,int)
        yNew=np.polyval(poly, xNew)
        fittedData[xNew]=yNew
    
    return fittedData

def equalLen(dDataIn):
    dDataOut=deepcopy(dDataIn)
    minLen=minLenF(dDataIn)#  np.min(np.array([len(dData['RX']),len(dData['BG']),len(dData['RXS']),len(dData['BGS'])]))
    for key in dDataIn.keys():
        dDataOut[key]=dDataIn[key][:minLen]
    return dDataOut

def normSimple(dataIn, POutlier=2.0, PAver=10.0):
    NData=len(dataIn)
    NOutlier=int(float(NData)*float(POutlier)/100.0)
    if NOutlier<1:
        NOutlier=1
    NAver=int(float(NData)*float(PAver)/100.0)
    dataSorted=np.sort(dataIn)
    aver=np.average(dataSorted[-NAver:-NOutlier])
    dataNormed=dataIn/aver
    return dataNormed, aver 

def smoothRect(dataIn,degree=1):
    NData=len(dataIn)  
    dataOut=np.zeros(NData)
    window=degree*2+1
    for i in range(degree):
        dataOut[i]=np.average(dataIn[:i+degree+1])
    for i in range(1,degree+1):
        dataOut[-i]=np.average(dataIn[-(i+degree):])
    for i in range(degree,NData-degree):
        dataOut[i]=np.average(dataIn[i-degree:i+degree+1])
    return dataOut  

            ### RESOLUTION ENHANCEMENT
def enhance(array,factor=1):
    enhanced=array.copy()
    secderiv=deriv2(array)
    secderiv=smoothRect(secderiv,1)
    enhanced=array-(factor*secderiv)
    return enhanced

               