from copy import deepcopy

from funcSeqAll import findPOutlierBox,normSimple, normBox
from funcTimeWarp import autoROIwDTW
from funcToolsAll import  autoDecaySum
from funcToolsAll import findPeakMatchX, splineSampleData, findMatchX_DTW, dtwAlign2Cap, splineCap
from funcToolsAll import correctSatd,smoothRect,baselineAdjust, smoothTriangle, fitLinear
from imports import QtGui,QtCore
from funcToolsAll import fMobilityShift, dDyesWL
from funcPeakAlign import  fPeakList
from funcSeqAll import peakLinking
from funcSeqAll import fitShapeData
from funcSeqAll import scaleShapeDataWindow, scaleShapeData


def seqAlignRef(dProjRef,dProjOut,keyR,keyS,method='peakSim',isNormalize=True,derivative=True):
### array 0 and array 2 is reference signals, array1 and array 3 is aligned.
### Control the length of the array and    
    dataR=dProjRef['dData'][keyR].copy()
    dataS=dProjOut['dData'][keyS].copy()
    linkX0,linkX1=findPeakMatchX(dataR,dataS,isNormalize)
    
    return linkX0,linkX1

def postSeqAlignRef(dProjRef,dProjOut):  
    dProjOut['seqRNA']=dProjRef['seqRNA']
    dProjOut['seqX0']=dProjRef['seqX0']
    dProjOut['seq0']=dProjRef['seq0']
    dProjOut['seqX']=dProjRef['seqX']
    dProjOut['seqNum']=dProjRef['seqNum']
    try:
        dProjOut['scrNuc']=dProjRef['scrNuc']
    except:
        pass
    dProjOut['start']=dProjRef['start']
    dProjOut['end']=dProjRef['end']
    
    return dProjOut

def applyAllSeq(dProject, dProjRef):
    dProjOut=deepcopy(dProject)

# SIGNAL ALGINMENT   
    linkXR,linkXS = seqAlignRef(dProjRef,dProjOut,'BGS1','BGS1')
    for key in dProjOut['chKeyRS']:
        dProjOut['dData'][key] = splineSampleData(dProjOut['dData'][key],dProjRef['dData'][key],linkXR,linkXS,False)
      
    dProjOut= postSeqAlignRef(dProjRef,dProjOut)
    dProjOut['dPeakRX']=fPeakList(dProjOut['dData']['RX'])
    dProjOut['dPeakBG']=fPeakList(dProjOut['dData']['BG']) 
    dProjOut['dPeakBG'],controlRX=peakLinking(dProjRef['dPeakBG']['pos'],dProjOut['dPeakBG'],dProjOut['dData']['BG'])
    dProjOut['dPeakRX'],controlBG=peakLinking(dProjRef['dPeakRX']['pos'],dProjOut['dPeakRX'],dProjOut['dData']['RX'])

## SCALE RX
    dProjOut['dPeakRX']=fitShapeData(dProjOut['dPeakRX'],dProjOut['dData']['RX'])
    dProjOut['dPeakBG']=fitShapeData(dProjOut['dPeakBG'],dProjOut['dData']['BG'])
    
    if len(dProjOut['dPeakRX']['amp'])>160:
        scaleFactor0 = scaleShapeDataWindow(dProjRef['dPeakRX']['area'],dProjOut['dPeakRX']['area'])
        scaleFactorData0 = fitLinear(dProjOut['dPeakRX']['pos'],scaleFactor0,NData=len(dProjOut['dData']['RX']))
    else:
        scaleFactor0 = scaleShapeData(dProjRef['dPeakRX']['area'],dProjOut['dPeakRX']['area'],rate=1)
        scaleFactorData0 = scaleFactor0
    
    dProjOut['dPeakRX']['area']=dProjOut['dPeakRX']['area']*scaleFactor0
    dProjOut['dPeakRX']['amp']=dProjOut['dPeakRX']['amp']*scaleFactor0
    dProjOut['dData']['RX']=dProjOut['dData']['RX']*scaleFactorData0
         
## SCALE BG   
    if len(dProjOut['dPeakBG']['amp'])>160:
        scaleFactor0 = scaleShapeDataWindow(dProjRef['dPeakBG']['area'],dProjOut['dPeakBG']['area'])
        scaleFactorData0 = fitLinear(dProjOut['dPeakBG']['pos'],scaleFactor0,NData=len(dProjOut['dData']['BG']))
    else:
        scaleFactor0 = scaleShapeData(dProjRef['dPeakBG']['area'],dProjOut['dPeakBG']['area'],rate=1)
        scaleFactorData0 = scaleFactor0
    
    dProjOut['dPeakBG']['area'] = dProjOut['dPeakBG']['area']*scaleFactor0
    dProjOut['dPeakBG']['amp'] = dProjOut['dPeakBG']['amp']*scaleFactor0
    dProjOut['dData']['BG'] = dProjOut['dData']['BG']*scaleFactorData0
    
## NORMALIZATION 

    dProjOut['areaDiff']=dProjOut['dPeakRX']['area']-dProjOut['dPeakBG']['area']
    POutlier,PAver=findPOutlierBox(dProjOut['areaDiff'])
    dProjOut['normDiff'], aver=normSimple(dProjOut['areaDiff'],POutlier,PAver)
    if  len(dProjOut['normDiff']):
        scaleFactor2=scaleShapeDataWindow(dProjRef['normDiff'],dProjOut['normDiff'])
    else:
        scaleFactor2=scaleShapeData(dProjRef['normDiff'],dProjOut['areaDiff'],rate=1) 
    dProjOut['normDiff'] = dProjOut['normDiff']*scaleFactor2
          
    return dProjOut

def applyAllToolsAuto1(dProject, dProjRef):
    dProjOut=deepcopy(dProject)                
### SATURATION CORRECTION
    for key in dProject['chKeyRX']:
        dProjOut['dData'][key]=correctSatd(dProjOut['dData'][key],dProjOut['Satd']['RX'])
    for key in dProject['chKeyBG']:
        dProjOut['dData'][key]=correctSatd(dProjOut['dData'][key],dProjOut['Satd']['BG'])
    dProject['isSatd']=True
    
### SMOOTHING  
    for key in dProjOut['dData'].keys():
        if len(dProjOut['dData'][key])>0:
            dProjOut['dData'][key] = smoothTriangle(dProjOut['dData'][key])
   
### BASELINE ADJUSTMENT
    for key in dProject['dData'].keys():
        dProjOut['dData'][key] = baselineAdjust(dProjOut['dData'][key])
 #   print 'baseline adjusted'   
             
### Select Region of Interest
    startR, endR  = autoROIwDTW(dProjOut['dData']['RXS1'],dProjRef['dData']['RXS1'])
    for key in dProject['chKeyRX']:
        dProjOut['dData'][key]=dProjOut['dData'][key][startR:endR]
     
    startB, endB  = autoROIwDTW(dProjOut['dData']['BGS1'],dProjRef['dData']['BGS1'])
    for key in dProject['chKeyBG']:
        dProjOut['dData'][key]=dProjOut['dData'][key][startB:endB]

                  
### MOBILITY SHIFT         
    dyeNR=dProject['dyeN']['RX']
    dyeNS=dProject['dyeN']['RXS1']
    dProjOut['dData']['RXS1']=fMobilityShift(dProjOut['dData']['RX'],dProjOut['dData']['RXS1'],dyeNR,dyeNS)
    if 'RXS2' in dProject['dData'].keys():
        dyeWS=dDyesWL[dProject['dyeN']['RXS2']]
        dProjOut['dData']['RXS2']=fMobilityShift(dProjOut['dData']['RX'],dProjOut['dData']['RXS2'],dyeNR,dyeNS)
   
    dyeNR=dProject['dyeN']['BG']
    dyeNS=dProject['dyeN']['BGS1']
    dProjOut['dData']['BGS1']=fMobilityShift(dProjOut['dData']['BG'],dProjOut['dData']['BGS1'],dyeNR,dyeNS)
    if 'BGS2' in dProject['dData'].keys():
        dyeWS=dDyesWL[dProject['dyeN']['BGS2']]
        dProjOut['dData']['BGS2']=fMobilityShift(dProjOut['dData']['BG'],dProjOut['dData']['BGS2'],dyeNR,dyeNS)         
 
### BASELINE ADJUSTMENT
    for key in dProject['dData'].keys():
        dProjOut['dData'][key] = baselineAdjust(dProjOut['dData'][key])
        
### SIGNAL DECAY        
    for key in dProject['dData'].keys():
        dProjOut['dData'][key]=autoDecaySum(dProjOut['dData'][key])
### SIGNAL ALIGNMENT
    usedSeq=['RXS1','BGS1','RXS2','BGS2'] 
    linkX0,linkX1=dtwAlign2Cap(dProjOut,usedSeq)
    dProjOut = splineCap(dProjOut,usedSeq,linkX0,linkX1)
            
    return dProjOut
        
def applyAllToolsAuto0(dataIn, dataRef,SatdS):
    dataS=deepcopy(dataIn)
    dataR=deepcopy(dataRef)

#""" Saturation Correction """   
    print 'saturation correction' 
    dataS=correctSatd(dataS,SatdS)
#""" Smoothing """    
    print 'Smoothing'   
    dataS=smoothRect(dataS)
#""" Baseline Adjustment """     
    dataS = baselineAdjust(dataS)
    print 'Baseline' 
#""" Normalization """
    dataR = normBox(dataR, 1000)
    dataS = normBox(dataS, 1000)
#""" Auto Region of Interest """   
    print 'Auto ROI' 
    start, end , dtwM = autoROIwDTW(dataS,dataR)
    print start, end
    dataS=dataS[start-5:end+10]
#""" Signal Decay Correction""" 
    print 'Signal Decay'    
    dataS=autoDecaySum(dataS,100) 
#""" Signal Alignment """
    print 'Signal Alignment'   
   # linkXR,linkXS=findPeakMatchX(dataR,dataS)
    linkXR,linkXS = findMatchX_DTW(dataR,dataS)
    print linkXR
    print linkXS
    dataS=splineSampleData(dataS,dataR,linkXR,linkXS)
    
 #   averS=np.average(dataS)
 #   averR=np.average(dataRef)
 #   scale=averR/averS
 #   dataS = dataS * scale
    
    return dataS, dataR

                  
if __name__ == '__main__':
    import sys
    import numpy as np 
    from pylab import figure,show,savefig,title
    from matplotlib.pyplot import setp
  #  from matplotlib.figure import Figure
    import matplotlib.pyplot as plt
    import shelve
    
  
    fNameR="/Users/fethullah/Sar Data/refHCV1.qushape"
    fNameS="/Users/fethullah/Sar Data/isis11_2.qushape"
    
    dBase=shelve.open(fNameR)
    dProjR=deepcopy(dBase['dProject'])
    dBase.close()
    
    dBase=shelve.open(fNameS)
    dProjS=deepcopy(dBase['dProject'])
    intervalData = deepcopy(dBase['intervalData'])
    dProjRaw=intervalData[0]
    dBase.close()
    
    key='BG'
    dataSOut, dataR=applyAllToolsAuto0(dProjRaw['dData'][key], dProjR['dData'][key],dProjRaw['Satd'][key])
    
    fig0 = plt.figure()
    ax00 = fig0.add_subplot(211)
    ax01 = fig0.add_subplot(212)
  
    ax00.plot(dataR,'r')
    ax00.plot(dataSOut,'b')
    
    ax01.plot(dProjRaw['dData'][key],'k',)
   
  
#    ax00.plot(dProjR['dData']['RX'],'r')
#    ax00.plot(dProjS['dData']['RX'],'b')
    
    
    show()
     
    