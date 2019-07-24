import numpy as np
from funcGeneral import max2,argmax2, max3,argmax3, deriv1,enhance
from scipy import interpolate

    ### PEAK DETECTION ###
def peakListAll(dProject,keys):
    for key in keys:
        key1=str('dPeak'+key)
        dProject[key1]=fPeakList(dProject['dData'][key],False,False)
    return dProject
    
def fPeakList(dataIn,isDel=False,isAdd=False,repType=None):
 ## RepTpes: "Cubic", "Poly2"
    peakX,peakY=peakDetection(dataIn)
    if peakX[0]<3:
        peakX=np.delete(peakX,0)
        peakY=np.delete(peakY,0)
    if peakX[-1]>len(dataIn)-4:
        peakX=np.delete(peakX,-1)
        peakY=np.delete(peakY,-1)
        
    dPeakList=DPeakList()
    dPeakList['NPeak']=len(peakX)
    dPeakList['pos']=peakX
    dPeakList['amp']=peakY
    dPeakList['score']=np.ones(dPeakList['NPeak'])
    dPeakList['averW'],dPeakList['minW'],dPeakList['maxW']=findAverPeakW(peakX,rate=0.33,minR=0.4,maxR=1.8) 
    if isDel:
        dPeakList=delPeaks(dPeakList, dataIn)
    if isAdd:
        dPeakList=addPeaks(dPeakList, dataIn)
    if repType!=None:
        dPeakList['X']=[]
        dPeakList['Y']=[]
        for i in range(dPeakList['NPeak']):
            if repType=="Cubic":
                newX,newY,newPos,newAmp=fitSplineToPeak(dataIn,dPeakList['pos'][i],wid=3)
            elif repType=="Poly2":    
                newX,newY,newPos,newAmp=fitPolyToPeak(dataIn,dPeakList['pos'][i],wid=3)
            elif repType=="Amp":
                newX,newY,newPos,newAmp=peakX[i],peakY[i],dPeakList['pos'][i],peakY[i]
                
            dPeakList['pos'][i]=newPos
            dPeakList['amp'][i]=newAmp
            dPeakList['X'].append(newX)
            dPeakList['Y'].append(newY)
          
    return dPeakList


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
      
def peakDetection(dataIn,isY=True):           
    if len(dataIn)<3:
        peakX=np.array([])
        return  peakX
    derivData=deriv1(dataIn)
    peakX=findPeakX(derivData,dataIn)
    if isY:
        peakY=findPeakY(dataIn,peakX)
        return peakX, peakY
    else:
        return peakX
    
def findPeakX(derivData,dataIn):
    peakX=np.array([],dtype='i4') 
    NData=len(derivData)
    i=0
    while i<NData-1:
        if np.sign(derivData[i]) > np.sign(derivData[i+1]):
            peak=argmax3(dataIn[i-1],dataIn[i],dataIn[i+1])
            peak=i-1+peak
            i=i+1
            peakX=np.append(peakX,peak)
        i+=1
    return peakX

def findPeakY(dataIn,peakX):
    NPeak=len(peakX)
    peakY=np.zeros(NPeak,dtype='f4')
    for i in range(NPeak):
        peakY[i]= dataIn[peakX[i]]
    return peakY


def delPeaks(dPeakList, dataIn):
    newPeakX=np.array([dPeakList['pos'][0]],dtype='i4')
    i=1
    while i<len(dPeakList['pos'])-2:
        fark0=dPeakList['pos'][i+1]-dPeakList['pos'][i]
        if fark0<dPeakList['minW']:
            fark1=dPeakList['pos'][i+2]-dPeakList['pos'][i+1]
            fark2=dPeakList['pos'][i]-dPeakList['pos'][i-1]
            if fark1>fark2:
                newPeakX=np.append(newPeakX,dPeakList['pos'][i+1])
            else:
                newPeakX=np.append(newPeakX,dPeakList['pos'][i])
            i+=1
        else:
            newPeakX=np.append(newPeakX,dPeakList['pos'][i])             
        i+=1
    newPeakX=np.append(newPeakX,dPeakList['pos'][-2])
    newPeakX=np.append(newPeakX,dPeakList['pos'][-1]) 

    dPeakList['NPeak']=len(newPeakX)
    newPeakY=np.zeros(dPeakList['NPeak'])
    for i in range(dPeakList['NPeak']):
        newPeakY[i]=dataIn[newPeakX[i]]
    dPeakList['amp']=newPeakY
    dPeakList['pos']=newPeakX
    dPeakList['score']=np.ones(dPeakList['NPeak'])
    return dPeakList


def addPeaks(dPeakList,dataIn):
    newPeakX=np.array([dPeakList['pos'][0]],dtype='i4')
    newScore=np.array([1],dtype='i4') 
    i=1
    while i<len(dPeakList['pos']):
        firstP=newPeakX[-1]
        secondP=dPeakList['pos'][i]
        fark=secondP-firstP
        if fark>dPeakList['maxW']:  
            s=int(firstP+dPeakList['minW'])
            e=int(s+dPeakList['averW'])
            partData=enhance(dataIn[s:e])
            partX=peakDetection(partData,False)
            if len(partX)>0:
                newPeakX=np.append(newPeakX,int(partX[0]+s))
            else:
                m=int(firstP+dPeakList['averW'])
                argM=m-1+argmax3(dataIn[m-1],dataIn[m],dataIn[m+1])
                newPeakX=np.append(newPeakX,argM) 
            newScore=np.append(newScore,0)     
        elif fark>1.2*dPeakList['averW']:
            s=int(firstP+dPeakList['minW'])
            e=int(secondP-dPeakList['minW']+1)
            partData=enhance(dataIn[s:e])
            partX=peakDetection(partData,False)
            if len(partX)>0:
                newPeakX=np.append(newPeakX,(partX[0]+s))
                newScore=np.append(newScore,0) 
            newPeakX=np.append(newPeakX,secondP)
            newScore=np.append(newScore,1) 
            i+=1
        else:
            newPeakX=np.append(newPeakX,secondP)
            newScore=np.append(newScore,1) 
            i+=1
    
    dPeakList['NPeak']=len(newPeakX)
    dPeakList['pos']=np.array(newPeakX,dtype='i4')
    dPeakList['amp']=dataIn[newPeakX]
    dPeakList['score']=np.array(newScore,dtype='i4')
    
    
    return dPeakList

    
def findAverPeakW(peakX,rate=0.33,minR=0.4,maxR=1.5):
    NPeak=len(peakX)
    diffW=peakX[1:]-peakX[:-1]
    diffW=np.sort(diffW)
    s=int(NPeak*rate)
    e=int(NPeak*(1-rate))
    averW=np.average(diffW[s:e])
    minW=averW*minR
    maxW=averW*maxR
    return averW,minW,maxW


    
def fitSplineToPeak(dataIn,peakPos,wid=3):
    s=int(peakPos-wid)
    e=int(peakPos+wid+1)
    X=np.arange(s,e)
    Y=dataIn[s:e]

    fittedFunc= interpolate.splrep(X,Y,s=0)
    
    newWid=wid*5    
    newX=np.linspace(s,e-1,newWid)
    newY=interpolate.splev(newX,fittedFunc,der=0)
    
    argMax=np.argmax(newY)
    newAmp=newY[argMax]
    newPos=newX[argMax]
    
    s=newPos-wid
    e=newPos+wid+1
      
    newX=np.linspace(s,e-1,newWid)
    newY=interpolate.splev(newX,fittedFunc,der=0)
    
    return newX,newY,newPos,newAmp


def fitPolyToPeak(dataIn,peakPos,wid=3):
    s=int(peakPos-wid)
    e=int(peakPos+wid+1)
    X=np.arange(s,e)
    Y=dataIn[s:e]

    fittedFunc= np.poly1d(np.polyfit(X,Y,2))
    
    newWid=wid*5    
    newX=np.linspace(s,e-1,newWid)
    
    newY=fittedFunc(newX)#,fittedFunc,der=)
    
    argMax=np.argmax(newY)
    newAmp=newY[argMax]
    newPos=newX[argMax]
    
    s=newPos-wid
    e=newPos+wid+1
      
    newX=np.linspace(s,e-1,newWid)
    newY=fittedFunc(newX)#,fittedFunc,der=)
    
    #newY=interpolate.splev(newX,fittedFunc,der=0)
    
    return newX,newY,newPos,newAmp


def noBand(n,m):
    band=np.zeros([2,n],dtype='i4')
    for i in range(n):
        band[0,i] = 0
        band[1,i] = m
    return band

def SakoeChibaBand(n,m,r):
    band=np.zeros([2,n],dtype='i4')
    mnf=float(m)/float(n)
    
    for i in range(n):
        band[0,i]=np.ceil(mnf*i-r) # int(np.max(np.array([ceil(i * mnf - r), 0.0 ])));
        band[1,i]=np.floor(mnf*i+r) #int(np.min(np.array([ceil(i * mnf - r), 0.0 ])));
        if  band[0,i]<0:
            band[0,i]=0
        if  band[1,i]>m:
            band[1,i]=m   
    return band

## SIMILARITY FUNCTIONS

# Similarity between two numbers, a and b
def simAandB(a,b):
    a=float(a)
    b=float(b)
    sim=1.0-(np.abs(a-b)/(2*max2(np.abs(a),np.abs(b))))
    sim=sim*2.0-1.0
    return sim
 
# Mean similarity between two time series, a1,a2,...,aN, and b1,...,bN
def simMean(A,B):
    if len(A)!=len(B):
        return False
    sum=0
    for i in range(len(A)):
        sum+=simAandB(A[i],B[i])
    sim=sum/len(A)
    return sim

def simMeanDeriv(A,B):
    A0=deriv1(A)
    B0=deriv1(B)
    sim=simMean(A0,B0)
    return sim
  
# The root mean square similarity
def simRootMean(A,B):
    if len(A)!=len(B):
        return False
    sum=0
    for i in range(len(A)):
        sum+=(simAandB(A[i],B[i]))**2
    sim=np.sqrt(sum/len(A))
    return sim
    

def simCorr(A,B):
    if len(A)!=len(B):
        return 0
    sim=np.corrcoef(A,B)[0,1]
    return sim
 
def simPeakCorr(A,B,i,j,D=0.02):
    corr=simCorr(A,B)
    posSim=np.exp(np.abs(i-j)*D)
    sim=corr/posSim
    return sim

def simCosAngle(A,B):
    top = np.dot(A, B)
    bot =  np.sqrt(np.sum(A**2)*np.sum(B**2)) #mass_spect1_sum*mass_spect2_sum)
    if bot > 0:
        sim = top/bot
    else:
        sim = 0
    sim=sim*2-1
    return sim
   
def posSim(t1,t2,D=0.03):
    posSim0=np.exp(-np.abs(t1-t2)*D)
    posSim0=posSim0*2-1
    return posSim0
#a=10
#b=np.arange(5,150)
#for i in b:
#    print a,i,posSim(a,i)

def simPosAmp(a0,a1,t0,t1,kA=0.1,kT=0.9):
    simPos=posSim(t0,t1)
    simAmp=simAandB(a0,a1)
    sim=simPos*kT+simAmp*kA
    sim=sim*2-1
    return sim
    
    
def timeTol(t1,t2,D=0.05):
    rtime = np.exp(-np.abs(t1-t2)*D)
    return rtime
    
simFuncs=['Amplitude','Mean','Derivative','Correlation','Cosine','Gaussian','Position']

def DPeakAlignParams():
    dParams={}
    dParams['method']='Global'
    dParams['simFunc']='Amplitude'
    dParams['peakRep']=None  
    dParams['gap']=-0.20  
    dParams['timeT']=0.00 
    dParams['band']=0.20
    dParams['minScore']=0.0
    dParams['seqType']='pos'  # 'pos', 'index'
    dParams['isBackTrace']=True
    dParams['repType']=None
     
    return dParams
              
def obtainCostM(dPeakList0,dPeakList1,bandM,dParams):
    n=dPeakList0['NPeak']
    m=dPeakList1['NPeak']
    costM=np.array(np.ones([n,m])*(-9999), dtype='f4')
    if dParams['simFunc']=='Amplitude':  
        for i in range(n):
            for j in np.arange(bandM[0,i],bandM[1,i]): 
                costM[i,j]=simAandB(dPeakList0['amp'][i],dPeakList1['amp'][j])
    elif dParams['simFunc']=='Position':  
        for i in range(n):
            for j in np.arange(bandM[0,i],bandM[1,i]): 
                costM[i,j]=posSim(dPeakList0['pos'][i],dPeakList1['pos'][j])
    elif dParams['simFunc']=='Mean':  
        for i in range(n):
            for j in np.arange(bandM[0,i],bandM[1,i]):  
                costM[i,j]=simMean(dPeakList0['Y'][i],dPeakList1['Y'][j])
    elif dParams['simFunc']=='Derivative':  
        for i in range(n):
            for j in np.arange(bandM[0,i],bandM[1,i]):  
                costM[i,j]=simMeanDeriv(dPeakList0['Y'][i],dPeakList1['Y'][j])
    elif dParams['simFunc']=='Correlation':  
        for i in range(n):
            for j in np.arange(bandM[0,i],bandM[1,i]):  
                costM[i,j]=simCorr(dPeakList0['Y'][i],dPeakList1['Y'][j])
    elif dParams['simFunc']=='Gaussian':  
        for i in range(n):
            for j in np.arange(bandM[0,i],bandM[1,i]):  
                costM[i,j]=simCorr(dPeakList0['Y'][i],dPeakList1['Y'][j])
    elif dParams['simFunc']=='Cosine':  
        for i in range(n):
            for j in np.arange(bandM[0,i],bandM[1,i]):  
                costM[i,j]=simCosAngle(dPeakList0['Y'][i],dPeakList1['Y'][j])
                
#    # Apply time tolerace
#    if dParams['method']=='Global' and dParams['timeT']>0:
#        for i in range(n):
#            for j in np.arange(bandM[0,i],bandM[1,i]):  
#                costM[i,j]=costM[i,j]*timeTol(dPeakList0['pos'][i],dPeakList1['pos'][j],dParams['timeT'])
#                       
    return costM
 
def peakScoringGlobal(dPeakList0,dPeakList1,costM,bandM, gap=-1.0, minScr=0.5):
    l1, l2 = dPeakList0['NPeak'], dPeakList1['NPeak']
    scormat = np.zeros( (l1+1,l2+1), dtype='f4')
    arrow = np.zeros( [l1+1,l2+1], int)
    arrow[0,:] = 2 # np.ones(NSeq+1)
    arrow[:,0] = 1 #np.ones(NSeq+1)
    scormat[0,:] = np.arange(l2+1)* gap
    scormat[:,0] = np.arange(l1+1)* gap
  #  arrow[0] = np.ones(l2+1)
    for i in range( 1,l1+1 ):
        for j in range(bandM[0,i-1]+1,bandM[1,i-1]+1,1): # for j in range( 1, l2+1 ):
            s0= scormat[i-1,j-1]+ costM[i-1,j-1]
            s1= scormat[i-1,j] + gap
            s2= scormat[i,j-1] + gap
            scormat[i,j] = max3(s0,s1,s2)
            arrow[i,j] = argmax3(s0,s1,s2)
            if costM[i-1,j-1]<minScr:     
                scormat[i,j] = max2(s1,s2)
                arrow[i,j] = 1+argmax2(s1,s2)
 
    return scormat, arrow

def peakBacktraceGlobal(seq0,seq1,scormat,arrow,costM,minScr=0.5):
    NPeak0=len(seq0)
    NPeak1=len(seq1)
    
    st0, st1 = [],[]
    v,h = arrow.shape
    v-=1
    h-=1
    ok = 1 
    while ok:
        if arrow[v,h] == 0:
            st0.append(seq0[v-1])# += seq1[v-1]
            st1.append(seq1[h-1])# += seq2[h-1]
            v -= 1
            h -= 1
        elif arrow[v,h] == 1:
            st0.append(seq0[v-1]) #+= seq1[v-1]
            st1.append(-1)
            v -= 1
        elif arrow[v,h] == 2:
            st0.append(-1)
            st1.append(seq1[h-1])
            h -= 1
        if v==0 and h==0:
            ok = 0
        
    # reverse the strings
    st0.reverse()
    st1.reverse()
    
    return st0, st1

def peakScoringLocal(dPeakList0,dPeakList1,costM, gap=-1.0, minScr=0.0):
    l1, l2 = dPeakList0['NPeak'], dPeakList1['NPeak']
    scormat = np.zeros( (l1+1,l2+1), dtype='f4')
    arrow = np.ones( (l1+1,l2+1), int)
    # create first row and first column
      
    arrow[0,:] = 1 # np.ones(NSeq+1)
    arrow[:,0] = 2 #np.ones(NSeq+1)
    
    for i in range( 1,l1+1 ):
        for j in range(1,l2+1): # for j in range( 1, l2+1 ):
            s0= scormat[i-1,j-1]+ costM[i-1,j-1]
            s1= scormat[i-1,j] + gap
            s2= scormat[i,j-1] + gap
            if costM[i-1,j-1]>minScr:  
                scormat[i,j],arrow[i,j] = maxArg4(s0,s1,s2,0)
            else:
                scormat[i,j] = max3(s1,s2,0)
                arrow[i,j] = 1+argmax3(s1,s2,0)
    return scormat, arrow

    
def peakBackTraceLocal(seq0,seq1,scormat,arrow):
    NPeak0=len(seq0)
    NPeak1=len(seq1)
  
    st0, st1 = [],[]
    ok = 1 
    v,h = divmod(scormat.argmax(), NPeak1+1)
    
    while ok:
        if arrow[v,h] == 0:
            st0.append(seq0[v-1])# += seq1[v-1]
            st1.append(seq1[h-1])# += seq2[h-1]
            v -= 1
            h -= 1
        elif arrow[v,h] == 1:
            st0.append(seq0[v-1]) #+= seq1[v-1]
            st1.append(-1)
            v -= 1
        elif arrow[v,h] == 2:
            st0.append(-1)
            st1.append(seq1[h-1])
            h -= 1
        if (v==0 and h==0) or scormat[v,h]==0:
            ok = 0
    # reverse the strings
    st0.reverse()
    st1.reverse()
    
    return st0, st1


def peakScoreM(peakXA, peakXB,costM, G=0.1): 
    l1, l2 = len( peakXA), len(peakXB)
    scormat = np.zeros([l1+1,l2+1])
    arrow = np.zeros([l1+1,l2+1], int )
    # create first row and first column
    scormat[0] = np.arange(l2+1)* G
    scormat[:,0] = np.arange( l1+1)* G
    arrow[0] = np.ones(l2+1)
    # fill in the matrix 
    for i in range(1,l1+1):
        for j in range(1,l2+1):
            f = np.zeros(3, float )
            f[0] = scormat[i-1,j] + G
            f[1] = scormat[i,j-1] + G
            f[2] = scormat[i-1,j-1] + costM[i-1,j-1] #subvals[i]
            scormat[i,j] = np.max(f)
            arrow[i,j] = np.argmax(f)
    return scormat, arrow

def myPeakAlignment(dPeakList0,dPeakList1,dParams):
    if dParams['method']=='Global':
        bandM=SakoeChibaBand(dPeakList0["NPeak"],dPeakList1["NPeak"],dPeakList0["NPeak"]*dParams['band'])
    if dParams['method']=='Local':
        bandM=noBand(dPeakList0["NPeak"],dPeakList1["NPeak"])
     
    costM=obtainCostM(dPeakList0,dPeakList1,bandM,dParams)
    if dParams['method']=='Global':
        scormat, arrow=peakScoringGlobal(dPeakList0,dPeakList1,costM,bandM, gap=dParams['gap'],minScr=dParams['minScore'])
        if dParams['isBackTrace']==False:
            return scormat[-1,-1]
    if dParams['method']=='Local':
        scormat, arrow=peakScoringLocal(dPeakList0,dPeakList1,costM, gap=dParams['gap'],minScr=dParams['minScore'])
  
    seq0=dPeakList0['pos']
    seq1=dPeakList1['pos']
    if dParams['seqType']=='index':
        seq0=np.arange(dPeakList0['NPeak'],dtype='i4')
        seq1=np.arange(dPeakList1['NPeak'],dtype='i4')
    if dParams['method']=='Global':
        aligned0, aligned1=peakBacktraceGlobal(seq0,seq1,scormat,arrow,costM,dParams['minScore'])       
    if dParams['method']=='Local':
        aligned0, aligned1=peakBackTraceLocal(seq0,seq1,scormat,arrow)
        
    return aligned0, aligned1
        
  
def multiShapeAlignment(dataRX,dataBG,dataBGS):
    peakListRX=fPeakList(dataRX)
    peakListBG=fPeakList(dataBG)
    peakListBGS=fPeakList(dataBGS)
    
    dParams= DPeakAlignParams()
    dParams['simFunc'] = 'Position'
    dParams['minScore'] = 0.75
    alRX0,alBG0=myPeakAlignment(peakListRX,peakListBG,dParams)
    alRX1,alBGS0=myPeakAlignment(peakListRX,peakListBGS,dParams) 
    alBG1,alBGS1=myPeakAlignment(peakListBG,peakListBGS,dParams) 
    
    mulAlign=[]
    for i in range(len(alRX0)):
        if alRX0[i]!=-1:
            ind=alRX1.index(alRX0[i])
            mulAlign.append([alRX0[i],alBG0[i],alBGS0[ind]])
        else:
            ind=alBG1.index(alBG0[i])
            mulAlign.append([alRX0[i],alBG0[i],alBGS1[ind]])
    
    return np.array(mulAlign)


def fMultiPeakAlign(peakList0,peakList1,peakList2):
    dParams= DPeakAlignParams()
    dParams['simFunc'] = 'Position'
    dParams['minScore'] = 0.5
    dParams['seqType']='pos'
    al01,al10=myPeakAlignment(peakList0,peakList1,dParams)
    al02,al20=myPeakAlignment(peakList0,peakList2,dParams) 
     
    mulAlign=[]
    for i in range(len(al01)):
        if al01[i]!=-1 and al10[i]!=-1:
            ind=al02.index(al01[i])
            if al20[ind]!=-1:
                mulAlign.append([al01[i],al10[i],al20[ind]])
    
    return np.array(mulAlign)

def fMultiPeakAlign0(peakList0,peakList1,peakList2):
    mulAlign=[]
    for i in range(peakList0['NPeak']):
        diff1=peakList1['pos']-peakList0['pos'][i]
        diff1=np.abs(diff1)
        argMin1=np.argmin(diff1) 
        diff2=peakList2['pos']-peakList0['pos'][i]
        diff2=np.abs(diff2)
        argMin2=np.argmin(diff2)         
        if diff1[argMin1]<4 and diff2[argMin2]<4:
            mulAlign.append([i,argMin1,argMin2])
    return np.array(mulAlign)

def splineSampleData(dataS,dataR, linkXR,linkXS, isCorr=True):
    NDataR=len(dataR)
    if len(linkXR)==0:
        return  dataS
    if linkXR[0]<linkXS[0]:
        diff=int(linkXS[0]-linkXR[0])
        newS=dataS[diff:linkXS[0]]
    elif linkXR[0]>linkXS[0]:
        diff=int(linkXR[0]-linkXS[0])
        newS=np.ones(diff)*dataS[0]
        newS=np.append(newS,dataS[:linkXS[0]])
    else:
        newS=dataS[:linkXS[0]]
        
    #newS=dataS[peakMatchX[0,0]] #np.array([])
    for i in range(1,len(linkXR)):
        fark2=linkXR[i]-linkXR[i-1]
        fark3=linkXS[i]-linkXS[i-1]
        if fark2!=fark3:
            try:
                x=np.arange(linkXS[i-1],linkXS[i])
                yS=dataS[linkXS[i-1]:linkXS[i]]
                tckS = interpolate.splrep(x,yS,s=0)
                xnew=np.linspace(linkXS[i-1],linkXS[i]-1,fark2)
                ynewS = interpolate.splev(xnew,tckS,der=0)
                if isCorr:
                    corr = np.corrcoef(ynewS,dataR[linkXR[i-1]:linkXR[i]])[0,1]
                    if corr <0.9:
                        linkXR[i]=linkXR[i-1] 
                        linkXS[i]=linkXS[i-1]
                    else:
                        newS=np.append(newS,ynewS)
                else:
                    newS=np.append(newS,ynewS)
                    
            except:
                linkXR[i]=linkXR[i-1] 
                linkXS[i]=linkXS[i-1]
        else:
            if isCorr:
                corr = np.corrcoef(dataS[linkXS[i-1]:linkXS[i]],dataR[linkXR[i-1]:linkXR[i]])[0,1]
                if corr<0.9:
                    linkXR[i]=linkXR[i-1] 
                    linkXS[i]=linkXS[i-1]
                else:
                    newS=np.append(newS,dataS[linkXS[i-1]:linkXS[i]])
            else:
                newS=np.append(newS,dataS[linkXS[i-1]:linkXS[i]])
                  
    #newS=np.append(newS,dataS[peakMatchX[-1,1]])
    newS=np.append(newS,dataS[linkXS[-1]:])

# Control the end Data length should be same 
    if NDataR>len(newS):
        addD=np.ones((NDataR-len(newS)))*newS[-1]
        newS=np.append(newS,addD)
    else:
        newS=newS[:NDataR]
        
    return newS
           

           
if __name__ == "__main__":
    import sys
    import os
    import time
    import numpy as np
    import matplotlib
    import matplotlib.pyplot as plt
    from matplotlib.pyplot import figure, show
    from matplotlib.patches import ConnectionPatch
    #from funcFile import readABI
    from Functions import ABIFReader,readABI,peakDetection
    np.set_printoptions(precision=2)

    currentDir=os.getcwd()
    
    plt.close('all')
    fig = figure(figsize=(14,8))
    axes0 = fig.add_subplot(211)
    axes1 = fig.add_subplot(212)
    
     
    fName=currentDir+'//data//dataTPPforSigAlign.txt'
    data=np.loadtxt(fName)
   

    data0=normShapeData(data[:,2])
    data1=normShapeData(data[:,3])
    
    data0=enhance(data0)
    data1=enhance(data1)
    
    data0=data0[100:200]
    data1=data1[110:210]
    
    peakX0,peakY0=peakDetection(data0)
    peakX1,peakY1=peakDetection(data1)
     
   
    t0= time.clock()
    dPeakList1=fPeakList(data1,True, True,None)
    t1= time.clock()
    print 'peakList', t0,t1,t1-t0
    dPeakList0=fPeakList(data0,True, True,'Cubic')
    dParams=DPeakAlignParams()
    dParams['band']=1
    dParams['simFunc'] ='Amplitude'
 #   print 'pos0 \n', dPeakList0['pos']
 #   print 'pos1\n', dPeakList1['pos']
  
#    print 'amp0\n', dPeakList0['amp']
 #   print 'amp1\n', dPeakList1['amp']
  
    bandM=SakoeChibaBand(dPeakList0["NPeak"],dPeakList1["NPeak"],dPeakList0["NPeak"]*dParams['band'])
    
    t0= time.clock()
    costM=obtainCostM(dPeakList0,dPeakList1,bandM,dParams)
    t1= time.clock()
    print 'costTime', t0,t1,t1-t0
   # print 'costM\n',costM
    scormat, arrow=peakScoringGlobal(dPeakList0,dPeakList1,costM,bandM, gap=dParams['gap'],minScr=dParams['minScore'])
    print 'scormat\n',scormat
   # print 'arrow\n',arrow
   
    score=scormat[-1,-1]
    aligned0, aligned1=peakBacktraceGlobal(dPeakList0['pos'],dPeakList1['pos'],scormat,arrow,costM)
    print 'aligned0\n', aligned0
    print 'aligned1\n', aligned1
    
    axes0.plot(data0,'r',dPeakList0['pos'],dPeakList0['amp'],'rs')
    axes1.plot(data1,'b',dPeakList1['pos'],dPeakList1['amp'],'bs')
    
    for i in range(len(aligned0)):
        if aligned0[i]!=-1 and aligned1[i]!=-1:
            xy0=(aligned0[i], data0[aligned0[i]])
            xy1=(aligned1[i], data1[aligned1[i]])
            con = ConnectionPatch(xy1, xy0, "data", "data",axesA=axes1, axesB=axes0,
                          arrowstyle="<|-|>",ec='0.3',fc='0.3',picker=3)
            axes1.add_artist(con)
     
    print dPeakList0['pos'], dPeakList0["NPeak"]
    print dPeakList1['pos'],dPeakList1["NPeak"]
    
 
    show()
    
    
 
    
                   
            
                    


    
 