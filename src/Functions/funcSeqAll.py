import numpy as np
from funcPeakAlign import DPeakList,myPeakAlignment,DPeakAlignParams, fPeakList
from copy import  deepcopy
from funcGeneral import averQ, normSimple, smoothRect, fitLinear
from scipy.optimize import fmin

        ### SEQEUENCE ALIGNMENT ###
def changeNucToN(seqRNA,dSeq):
    seqRNAN=''
    for i in range(len(seqRNA)):
        if seqRNA[i]==dSeq['nuc1']:
            seqRNAN+=dSeq['nuc1']
        elif dSeq['isSeq2'] and seqRNA[i]==dSeq['nuc2']:
            seqRNAN+=dSeq['nuc2']
        else:
            seqRNAN+='N'
    return seqRNAN

def shapeSeqAlign(dProject,seqRNA):
    seq=dProject['seq0']
    seqX=dProject['seqX0']
    scoreNuc=dProject['scrNuc']
    costMSeq=shapeCostM(seqRNA,seq,scoreNuc)
    seqWid=seqX[1:]-seqX[:-1]
    seqWid=normStat(seqWid)
    seqWid=np.append(seqWid,0)
    scormat, arrow=shapeScoreM(seq,seqRNA,costMSeq,seqWid)
    alignedSeqRNA,alignedSeq,newSeqX,start,end= shapeBackTrace(scormat, arrow,seqRNA,seq,seqX)
   
    return  alignedSeqRNA,alignedSeq,newSeqX,start,end

def shapeCostM(seqRNA,seq,score=None,match=2,misMatch=-1):
    n=len(seqRNA)
    m=len(seq)
    costMSeq=np.zeros([n,m])
    if score==None:
        score=np.ones(m)
    for i in range(n):
        for j in np.arange(m):
            if seqRNA[i]==seq[j]:
                if seq[j]=='N':
                    costMSeq[i,j]=match/2
                else:
                    costMSeq[i,j]=match*score[j]
            else:
                costMSeq[i,j]=misMatch
    return costMSeq


def shapeScoreM(seq,seqRNA3to5N,costMSeq,seqWid,gap=-5.0):
    NSeq=len(seq)
    NRNA=len(seqRNA3to5N)
     
    scormat = np.zeros( [NRNA+1,NSeq+1], dtype='f4')
    arrow = np.zeros( [NRNA+1,NSeq+1], int)
    arrow[0,:] = 2 # np.ones(NSeq+1)
    arrow[:,0] = 1 #np.ones(NSeq+1)
    
    for i in range( 1,NRNA+1 ):
        for j in range(1,NSeq+1):
            gap1=gap
            gap2=gap 
            if seqWid[j-1]<1 and seqWid[j-1]>-1:  
                gap2+=gap
                gap1+=gap
            if arrow[i-1,j]==1:
                gap1+=gap
            elif arrow[i,j-1]==2:
                gap2+=gap
            s0= scormat[i-1,j-1]+ costMSeq[i-1,j-1]  # Matched
            s1= scormat[i-1,j] + gap1  # put gap to Seq, a peak should be added
            s2= scormat[i,j-1] + gap2  # put gap to RNA, a peak should be deleted
          
            scormat[i,j],arrow[i,j] = maxArg4(s0,s1,s2,0)
                  
    return scormat, arrow

def maxArg4(s0,s1,s2,s3):
    max=s0
    arg=0
    if s1>max:
        max=s1
        arg=1
    if s2>max:
        max=s2
        arg=2
    if s3>max:
        max=s3
        arg=3
    return max, arg  

def shapeBackTrace(scormat, arrow,seq1,seq2,seqX):
    newSeq1=''
    newSeq2=''
    newSeqX=np.array([])
    N1=len(seq1)
    N2=len(seq2)
    ok = 1
    v,h = divmod( scormat.argmax(), N2+1)
    end=v
    if h<N2:
        diff=N2-h
        end=end+diff
        for i in range(diff):
            if (v+i)<N1:
                newSeq1+=seq1[v+i]
                newSeq2+=seq2[h+i]
                newSeqX=np.append(newSeqX,seqX[h+i])
            else:
                break
        newSeq1=newSeq1[::-1]
        newSeq2=newSeq2[::-1]
        newSeqX=newSeqX[::-1]   
    v2,h2=v,h         
    while ok:
        if arrow[v,h] == 0:
            newSeq1+=seq1[v-1]
            newSeq2+=seq2[h-1]
            newSeqX=np.append(newSeqX,seqX[h-1])
            v -= 1
            h -= 1
        elif arrow[v,h] == 1:
            newSeq1+=seq1[v-1]
            newSeq2+='-'
            newSeqX=np.append(newSeqX,0)
            v -= 1
        elif arrow[v,h] == 2:
            newSeq1+='-'
            newSeq2+=seq2[h-1]
            newSeqX=np.append(newSeqX,seqX[h-1])
            h -= 1
        elif arrow[v,h] == 3:
            ok = 0
        if (v==0 and h==0) or scormat[v,h]==0:
            ok = 0
    
    if h>0:
        for i in range(h,0,-1):
            if v>0:
                newSeq1+=seq1[v-1]
                newSeq2+=seq2[h-1]
                newSeqX=np.append(newSeqX,seqX[h-1])
                v -= 1
                h -= 1
    v1,h1=v,h
   
    newSeq1=newSeq1[::-1]
    newSeq2=newSeq2[::-1]
    newSeqX=newSeqX[::-1]
    # reverse the strings
    start=v1# (v1-h1) 
    
    return newSeq1,newSeq2,newSeqX,start,end

def applySeqAlign(dProjOut,seqRNA3to5N,start,end):
    alignedSeqRNA,alignedSeq,newSeqX,startNucI,endNucI=shapeSeqAlign(dProjOut,seqRNA3to5N[start:end])
    newSeqX,newSeq=nucAddDelete(alignedSeqRNA,alignedSeq,newSeqX)
    
    startNucI=startNucI+start   
    endNucI=startNucI+len(newSeqX) 
    NSeqRNA=len(dProjOut['RNA'])   
    dProjOut['start']=NSeqRNA-startNucI
    dProjOut['end']=dProjOut['start']-len(newSeqX)
    dProjOut['seqX']=np.array(newSeqX,int)
    dProjOut['seqRNA']=dProjOut['RNA'][::-1][startNucI:endNucI]
    dProjOut['seqNum']=np.arange(dProjOut['start'],dProjOut['end'],-1)    
    return dProjOut


def nucAddDelete(seqRNA,seq,seqX):
    NSeq=len(seq)
    seq0=list(seq)
#    for i in range(NSeq):
#        if seq[i]=='-':
#            seqX=np.insert(seqX,i,0)  
#                  
# Find the match points
    matchI=np.array([0],dtype='i4')
    i=0
    while i<NSeq-1:
        if seq[i]==seqRNA[i] and seq[i]!='N':
            matchI=np.append(matchI,i)
        i+=1
    
    matchI=np.append(matchI,NSeq-1)
   
# check the width
    newSeqX=np.array([],int)
    newSeq=[]
    for i in range(len(matchI)-1):
        NGapRNA=0
        NGapSeq=0
        appendX=np.array([])
        for j in range(matchI[i],matchI[i+1]):
            if seqRNA[j]=='-': 
                NGapRNA+=1 
            if seq[j]=='-': 
                NGapSeq+=1     
        if  int(matchI[i+1]-matchI[i]-NGapRNA)==1:
            newSeqX=np.append(newSeqX,seqX[matchI[i]])
            newSeq.append(seq[matchI[i]])
        elif NGapRNA==0 and NGapSeq==0:
            appendX=seqX[matchI[i]:matchI[i+1]]
            newSeqX=np.append(newSeqX,appendX)
            newSeq.append(seq[matchI[i]:matchI[i+1]])
        elif NGapRNA==NGapSeq:
            for k in (matchI[i],matchI[i+1],1):
                if seqX[k]!=0:
                    newSeqX=np.append(newSeqX,seqX[k]) 
                    newSeq.append(seq[k])   
        elif NGapRNA>NGapSeq:
            # delete a peak
            xx=np.array([])
            ss=[]
            for m in range(matchI[i],matchI[i+1]+1,1):
                if seqX[m]!=0:
                    xx=np.append(xx,seqX[m])
                    ss.append(seq[m])
            diffGap=NGapRNA-NGapSeq
            while diffGap>0:
                widXX=xx[1:]-xx[:-1]
                argmin0=np.argmin(widXX)
                if argmin0==0:
                    argmin0+=1
                xx=np.delete(xx,argmin0)
                del ss[argmin0]
                diffGap-=1
            newSeqX=np.append(newSeqX,xx[:-1]) 
            newSeq.append(''.join(ss[:-1]))         
        elif NGapRNA<NGapSeq:
            xx=np.array([])
            ss=[]
            for m in range(matchI[i],matchI[i+1]+1,1):
                if seqX[m]!=0:
                    xx=np.append(xx,seqX[m])
                    ss.append(seq[m])
            diffGap=NGapSeq-NGapRNA
            while diffGap>0:
                widXX=xx[1:]-xx[:-1]
                argmax0=np.argmax(widXX)
                ind=argmax0+1
                x=int((xx[ind-1]+xx[ind])/2)
                xx=np.insert(xx,ind,x)
                ss.insert(ind,'N')
                diffGap-=1
            newSeqX=np.append(newSeqX,xx[:-1])
            newSeq.append(''.join(ss[:-1])) 
         
    newSeqX=np.append(newSeqX,seqX[matchI[-1]])
    newSeq.append(seq[matchI[-1]])
    newSeq=''.join(newSeq)
    newSeq=list(newSeq)
    return newSeqX,newSeq


def peakLinking(seqX,dPeakList1,data1,isOptPos=False,minScore=0.5): 
    dPeakList0=DPeakList()
    dPeakList0['pos']=np.array(seqX,dtype='i4')
    dPeakList0['NPeak']=len(seqX)
    dParams=DPeakAlignParams()
    dParams['simFunc']='Position'
    dParams['minScore']=minScore
    dParams['timeT'] = 0.0
    aligned0,aligned1 = myPeakAlignment(dPeakList0,dPeakList1,dParams)
    dPeakList11,controlA = findLinkedPeaks(aligned0,aligned1,dPeakList1,data1,isOptPos)
    return dPeakList11, controlA

    
def findLinkedPeaks(aligned0,aligned1,dPeakList1,data1,isOptPos):
    controlA=np.array([],int)
    newPeakX1=np.array([],int)
   
    NAligned=len(aligned0)
    if aligned0[0]!=-1 and aligned1[0]!=-1:
        newPeakX1=np.append(newPeakX1,aligned1[0])
        controlA=np.append(controlA,1)
    elif aligned0[0]!=-1 and aligned1[0]==-1:
        newPeakX1=np.append(newPeakX1,aligned0[0])
        controlA=np.append(controlA,0)
    i=1   
    while i<NAligned-1:
        if aligned0[i]!=-1 and aligned1[i]!=-1:
            newPeakX1=np.append(newPeakX1,aligned1[i])
            controlA=np.append(controlA,1)
        elif aligned0[i]!=-1 and aligned1[i]==-1:
            newPeakX1=np.append(newPeakX1,aligned0[i])
            controlA=np.append(controlA,0)
        i+=1
    if aligned0[-1]!=-1 and aligned1[-1]!=-1:
        newPeakX1=np.append(newPeakX1,aligned1[-1])
        controlA=np.append(controlA,1)
    elif aligned0[-1]!=-1 and aligned1[-1]==-1:
        newPeakX1=np.append(newPeakX1,aligned0[-1])
        controlA=np.append(controlA,0)
        
    newPeakX1=np.array(newPeakX1,dtype='i4')
    dPeakList11={}
    dPeakList11['NPeak']=len(newPeakX1)
    dPeakList11['pos']=newPeakX1
    dPeakList11['amp']=data1[newPeakX1]
    if isOptPos:
        sigma=optimizeOneSigma(data1,dPeakList11['pos'],dPeakList11['amp'])
        if isOptPos:                
            dPeakList11=optimizePosition(data1,dPeakList11,sigma,controlA)
    return dPeakList11,controlA

  
def seqFindFinal0(dProject,keyS1='BGS1',keyS2='BGS2'):
    dataS1=dProject['dData'][keyS1]
    peakListBG = fPeakList(dProject['dData']['BG'])
    peakListS1 = fPeakList(dProject['dData'][keyS1], isDel=True, isAdd=True)
    seqX = findSeqX(peakListBG,peakListS1)
    peakListS1['NPeak']=len(seqX)
    peakListS1['pos']=seqX
    peakListS1['amp']=dataS1[seqX]
    peakListBG,controlBG=peakLinking(seqX,peakListBG,dProject['dData']['BG'],True)
    if dProject['isSeq2']:
        peakListS2=fPeakList(dProject['dData'][keyS2])
        peakListS2,controlS2=peakLinking(seqX,peakListS2,dProject['dData'][keyS2],True)
    else:
        peakListS2=None
        
    NSeq=len(seqX)
    seq=['N']*NSeq
    scoreNuc=np.ones(NSeq)
    if NSeq>160:
        K=80
    else:
        K=NSeq
    kat=int(NSeq/K)
    for i in range(kat):
        s=i*K
        if i==kat-1:
            e=NSeq
        else:
            e=(i+1)*K
        seq0,scoreNuc0 = findSeqPart(dProject,peakListS1,peakListS2,peakListBG,s,e)
        seq[s:e]=seq0
        scoreNuc[s:e]=scoreNuc0
    
    dProject['seq0']=seq
    dProject['seqX0']=seqX
    dProject['scrNuc']=scoreNuc
    
    return dProject


def findSeqX(peakListBG,peakListS1):
    dParams=DPeakAlignParams()
    dParams['simFunc']='Position'
    aligned0,aligned1=myPeakAlignment(peakListBG,peakListS1,dParams)
    seqX=np.array([],int)
    for i in range(2,len(aligned0)-1,1):
        if aligned1[i]==-1:
            if aligned0[i-1]!=-1 and aligned1[i-1]!=-1:
                if aligned0[i+1]!=-1 and aligned1[i+1]!=-1:
                    pos0=aligned1[i-1]
                    pos1=aligned1[i+1]
                    if (pos1-pos0)>1.2*peakListS1['averW']:
                        newPos=int((pos1+pos0)/2)
                        seqX=np.append(seqX,newPos)
        else:
            seqX=np.append(seqX,aligned1[i])
    return  seqX

def findSeqPart(dProject,peakListS1,peakListS2,peakListBG,s,e):
    thres=1.3
    factor=scaleShapeData(peakListS1['amp'][s:e],peakListBG['amp'][s:e],rate=0.5)
    newSeqY1=peakListS1['amp'][s:e]/factor
    NSeq1=len(newSeqY1)
    seq0=['N']*NSeq1
    scoreNuc0=np.ones(NSeq1)
    averY1=np.average(newSeqY1)
    for i in range(NSeq1):
        kat0=newSeqY1[i]/averY1
        if kat0>2:
            kat0=2
        scoreNuc0[i]=kat0
        if kat0>0.8:
            kat1=newSeqY1[i]/peakListBG['amp'][s+i]
            if  kat1>thres:
                seq0[i]=dProject['nuc1']
                
    if dProject['isSeq2']:
        factor=scaleShapeData(peakListBG['amp'][s:e],peakListS2['amp'][s:e],rate=0.5)
        newSeqY2=peakListS2['amp'][s:e]/factor
        averY2=np.average(newSeqY2)
        for i in range(NSeq1):
            if newSeqY2[i]>averY2 and newSeqY2[i]>newSeqY1[i]:
                kat0=newSeqY2[i]/averY2
                kat1=newSeqY2[i]/peakListBG['amp'][s+i]
                if kat1>2:
                    kat1=2
                scoreNuc0[i]=kat0
                if  kat1>thres:
                    seq0[i]=dProject['nuc2']
                   
    return seq0,scoreNuc0


### FAST SEQUENCE ALIGNMENT  
def seqAlignFast(seqR,seq):
    NSeq=len(seq)
    NSeqR=len(seqR)
    fark=NSeqR-NSeq
    if fark<1:
        start=0
        return start
    scr=np.zeros(fark)
    for i in range(fark):
        scr[i]=findScoreFast(seqR[i:i+NSeq],seq)
    start=np.argmax(scr)
    return start
        
def findScoreFast(seqR,seq):
    scr=0
    for i in range(len(seqR)):
        if seqR[i]==seq[i] and seq[i]!='N':
            scr+=1
    return scr    
              
                ### GAUSSIAN FIT ##3
def fitFuncG(x,pos,amp,wid):
    return  amp * np.exp(-2*(x-pos)**2/wid**2)

def fitShapeData(dPeakList,dataIn,controlA=None,isOptPos=True):
    NPeak=dPeakList['NPeak']
    sigma=optimizeOneSigma(dataIn,dPeakList['pos'],dPeakList['amp'])
    if isOptPos:                
        dPeakList=optimizePosition(dataIn,dPeakList,sigma,controlA)
    dPeakList['wid']=optimizeAllSigma(dataIn,dPeakList,sigma)
    dPeakList['amp']=optimizeAmp(dataIn,dPeakList)
    dPeakList['area']=np.abs(dPeakList['amp']*dPeakList['wid'])
   
    return dPeakList

def optimizeOneSigma(inputA,peakX,peakY):
    peakX=np.array(peakX)
    peakY=np.array(peakY)
    averW1=peakX[1:]-peakX[:-1]
    averW=np.average(averW1[int(len(averW1)*0.1):int(len(averW1)*0.9)])
    wid=averW*0.45
    controlWid=np.arange(wid*0.8,wid*1.2,0.1)
    errorWid=np.ones(len(controlWid))
    NPeak=len(peakX)
    NData=len(inputA)
    x=np.arange(NData)
    for j in range(len(controlWid)):
        A=np.zeros(NData)
        for i in range(NPeak):
            y=fitFuncG(x,peakX[i],peakY[i],controlWid[j])
            A=A+y
        errorWid[j]=np.sum(np.abs(A-inputA)) #/np.sum(inputA)
    return controlWid[np.argmin(errorWid)]


def optimizeAllSigma(dataA,peakList,wid=5):
    newSig=np.ones(peakList['NPeak'])*wid
    for i  in range(1,peakList['NPeak']-1):
        controlSig=np.arange(wid*0.9,wid*1.1,0.1)
        errorPos=np.ones(len(controlSig))*9999
        x=np.arange(peakList['pos'][i-1],peakList['pos'][i+1]+1,1,dtype='i4')
        y=dataA[x]  
        for j in range(len(controlSig)):
            sig=controlSig[j]
            y1=fitFuncG(x,peakList['pos'][i-1],peakList['amp'][i-1],newSig[i-1])
            y2=fitFuncG(x,peakList['pos'][i],peakList['amp'][i],sig)
            y3=fitFuncG(x,peakList['pos'][i+1],peakList['amp'][i+1],newSig[i+1])
            y4=y1+y2+y3
            errorPos[j]=np.sum(np.abs(y4-y)) #/np.sum(y)

        newSig[i]=controlSig[np.argmin(errorPos)]   
    return newSig


def optimizePosition(dataA,peakList,sigma,controlA=None):
    NPeak=peakList['NPeak']
    if controlA==None:
        controlA=np.zeros(NPeak)
        
    for i in range(1,NPeak-1):
        if controlA[i]==0:
            controlX=peakList['pos'][i]  
            start=controlX-3
            end=controlX+4
    
            controlPos=np.arange(start,end,1)
            errorPos=np.ones(len(controlPos))*9999
            x=np.arange(peakList['pos'][i-1],peakList['pos'][i+1]+1,1,dtype='i4')
            y=dataA[x]  
            for j in range(len(controlPos)):
                pos=controlPos[j]
                amp=dataA[pos]
                y1=fitFuncG(x,peakList['pos'][i-1],peakList['amp'][i-1],sigma)
                y2=fitFuncG(x,peakList['pos'][i+1],peakList['amp'][i+1],sigma)
                y3=fitFuncG(x,pos,amp,sigma)
                y4=y1+y2+y3
                errorPos[j]=np.sum(np.abs(y4-y)) #/np.sum(y)
            peakList['pos'][i]=controlPos[np.argmin(errorPos)]
            peakList['amp'][i]=dataA[peakList['pos'][i]]    
    return peakList


def optimizeAmp(dataA,peakList,wid=5):
    newAmp=np.zeros(len(peakList['pos']),dtype='f4')
    newAmp=peakList['amp'].copy()
    newAmpUp=newAmp.copy()
    newAmpUp*=1.2
    newAmpDown=newAmp.copy()
    newAmpDown*=0.8
   
    for k in range(5):  
        for i in range(1,len(peakList['pos'])-1):
            x=peakList['pos'][i]
            y1=fitFuncG(x,peakList['pos'][i-1],newAmp[i-1],peakList['wid'][i-1])
            y2=fitFuncG(x,peakList['pos'][i+1],newAmp[i+1],peakList['wid'][i+1])
            newY=dataA[x]-y1-y2
            if newY>newAmpUp[i]:
                newY=newAmpUp[i]
            elif newY<newAmpDown[i]:
                newY=newAmpDown[i]
            newAmp[i]=newY       
    return newAmp

            ### SCALE###

def scaleShapeData(data0,data1,rate=0.25):
    """   Scale Shape Data
    """
    # Data1 is scaled to Data1. 
    # Data0 is sorted and then the lower ones are used using the ratio. Data0[:N*rate] 
    N=len(data0) #100
    if rate>=1:
        A=data0.copy()
        B=data1.copy()
    else:
        A,B=selectDataForScale1(data0,data1,rate)
    
    A,B=removeDifferenceOutlier(A,B)
  
  #  newFactor=findScaleFactor0(A,B)
  #  print 'scale factor', newFactor
    newFactor= optimizeScaleFactor(A,B)
      
    return newFactor


def selectDataForScale1(data0,data1,rate=0.25):
    """ Select the lowest RX  area with corresponding BG area
    """
    NData=len(data0)
    argSorted0=np.argsort(data0)
    NSelect=int(NData*rate)
    #s=int(NData*0.5)
    #e=int(NData*rate)
    selectedArgSortAreaRX=argSorted0[:NSelect]
    A=np.zeros(NSelect)
    B=np.zeros(NSelect)
    for i in range(len(selectedArgSortAreaRX)):
        ind=selectedArgSortAreaRX[i]
        A[i]=data0[ind]
        B[i]=data1[ind]
    return A,B


def removeDifferenceOutlier(A,B):
    diff=A-B
    sortedDiff=np.argsort(diff)
    N=len(diff)
    newA, newB = np.array([]), np.array([])
    q1=int(N*0.2)
    q3=int(N*0.8)+1
    for i in range(q1,q3):
        newA=np.append(newA,A[sortedDiff[i]])
        newB=np.append(newB,B[sortedDiff[i]])
        
    return newA,newB


def optimizeScaleFactor(A,B,func='Data'):
    factor=1.0
    if func=='Data':
        resultList= fmin(scaleFactorFuncData, factor, args=(A,B),full_output=1,disp=0)
    elif func=='Median':
        resultList= fmin(scaleFactorFuncMedian, factor, args=(A,B),full_output=1,disp=0)
    else:
        resultList= fmin(scaleFactorFuncAver, factor, args=(A,B),full_output=1,disp=0)
    
    if resultList[4]==0:
        scaleFactor=resultList[0]
    else:
        scaleFactor=1
    return float(scaleFactor)

def scaleFactorFuncData(factor,A,B):
    err=np.sum(np.abs(A-factor*B))
    return err

def scaleFactorFuncMedian(factor,A,B):
    err=np.abs(np.median(A)-factor*np.median(B))
    return err

def scaleFactorFuncAver(factor,A,B):
    err=np.abs(averQ(A)-factor*averQ(B))
    return err

def scaleShapeDataWindow(data0,data1,deg=40,rate=1,step=10,fit=None,ref=None):
    N=len(data0)
    win=2*deg+1
    if N<win+step:
        scaleFactor=scaleShapeData(data0,data1,rate)
        return scaleFactor
    
    aScaleFactor=np.array([])
    aX=np.array([])
    for i in range(0,N,step):
        if i<deg:
            s=0
            e=win
        elif i>N-deg:
            e=N
            s=N-win
        else:
            s=i-deg
            e=i+deg+1      
        partData0=data0[s:e]
        partData1=data1[s:e]
        scaleFactor=scaleShapeData(partData0,partData1,rate)
        aScaleFactor=np.append(aScaleFactor,scaleFactor)
        aX=np.append(aX,i)
  
    #aY=scipy.signal.medfilt(aScaleFactor,5) 
    aY = smoothRect(aScaleFactor,degree=2)
    aX=aX[1:-1]
    aY=aY[1:-1]
    fittedSig = fitLinear(aX,aY,len(data1))
    # data11=data1*fittedSig
    if fit=='linear':
        newX=np.arange(len(fittedSig))
        coeff=np.polyfit(newX,fittedSig,1)
        poly=np.poly1d(coeff)
        fittedSig=np.polyval(poly, newX)
    if fit=='exp':
        newX=np.arange(len(fittedSig))
    if ref==0:
        data11=data1*fittedSig
        return data11
    if ref==1:
        data00=data0/fittedSig
        return data00
    
    return fittedSig

            ### NORMALIZATION 
            
def findPOutlierBox(dataIn):
#Order the SHAPE reactivities from largest to smallest  take the top 10% of the data - excluding outliers - this is your normalization factor - divide all the data by this number.
#Outliers are defined either by --- anything higher than - 1.5*(Quartile3-Quartile1)+Quartile3 or the top 10% of the data - whichever is less.
#Note - The quartiles come from the traditional box plot calculation (this can be done in Excel by doing =QUARTILE(B:B,1) if the reactivities are in column B)  

    NData=len(dataIn)
    if NData<50:
        return 2.0,10.0
    dataSorted=np.sort(dataIn)
    a1=int(NData*0.25) 
    a2=int(NData*0.5)
    a3=int(NData*0.75)
    Q1=dataSorted[a1]
    Q2=dataSorted[a2]
    Q3=dataSorted[a3]
    QThres=1.5*(Q3-Q1)+Q3
   
    NOutlier=0
    for i in range(NData-1,0,-1):
        if dataSorted[i]>QThres:
            NOutlier+=1
        else:
            break
        
    POutlier=float(NOutlier)/float(NData)*100
   # if POutlier>8.0:
   #     POutlier=8.0    
    PAver=10.0 
    if NData<100:
        PAver = (10.0/ float(NData)) * 100
    
    return POutlier, PAver

def normBox(dataIn, scale=1):
    dataNormed=deepcopy(dataIn)
    POutlier,PAver=findPOutlierBox(dataNormed)
    dataNormed , aver= normSimple(dataNormed,POutlier,PAver)
    dataNormed = dataNormed * scale
    return dataNormed

def normSimple(dataIn,POutlier=2.0, PAver=10.0):
    NData=len(dataIn)
    NOutlier=int(float(NData)*float(POutlier)/100.0)
    if NOutlier<1:
        NOutlier=1 
    NAver=int(float(NData)*float(PAver)/100.0) + NOutlier
    
    dataSorted=np.sort(dataIn)
    aver=np.average(dataSorted[-NAver:-NOutlier])
    dataNormed=dataIn/aver
    return dataNormed, aver

def normStat(data):
    normalized=np.zeros(len(data))
    mean=np.mean(data)
    std=np.std(data)
    normalized=(data-(mean))/std
    #normalized=normalized+1
    return normalized
            ### REPORT   
reportKeys=['seqNum','seqRNA','posSeq','posRX','areaRX','posBG','areaBG','areaDiff','normDiff']
def DReport():
    dReport={}
    dReport['seqNum']=np.array([],dtype='i4')
    dReport['seqRNA']=''
    dReport['posSeq']=np.array([],dtype='i4')
    dReport['posRX']=np.array([],dtype='i4')
    dReport['areaRX']=np.array([],dtype='i4')
    dReport['posBG']=np.array([],dtype='i4')
    dReport['areaBG']=np.array([],dtype='i4')
    dReport['areaDiff']=np.array([],dtype='i4')
    dReport['normDiff']=np.array([],dtype='i4')
    
    return dReport
 
def createDReport(dProject):
    dReport=DReport()
    dReport['seqNum']=np.array(dProject['seqNum'][1:],int)
    dReport['seqRNA']=dProject['seqRNA'][1:]
    dReport['posSeq']=np.array(dProject['seqX'][1:],int)
    dReport['posRX']=np.array(dProject['dPeakRX']['pos'][:-1],int)
    dReport['areaRX']=np.round(dProject['dPeakRX']['area'][:-1],decimals=2)
    dReport['posBG']=np.array(dProject['dPeakBG']['pos'][:-1],int)
    dReport['areaBG']=np.round(dProject['dPeakBG']['area'][:-1],decimals=2)
    dReport['areaDiff']=np.round(dProject['areaDiff'][:-1],decimals=2)
    dReport['normDiff']=np.round(dProject['normDiff'][:-1],decimals=2)
    
    return dReport

def writeReportFile(dReport,fName):
    myfile=open(fName,'w')    
    for key in reportKeys:
        myfile.write(str(key)+'\t')
    myfile.write('\n')
    for i in range(len(dReport['seqRNA'])):
        for key in reportKeys:
            myfile.write(str(dReport[key][i])+'\t')
        myfile.write('\n')
 