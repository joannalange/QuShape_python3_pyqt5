import numpy as np

from matplotlib.patches import ConnectionPatch, Rectangle

def drawMatchLines0(pos0,amp0,pos1,amp1,ax0,ax1):
    conLine=[]
    for i in range(len(pos0)):
        xyA=(pos0[i], amp0[i])
        xyB=(pos1[i], amp1[i])
        con = ConnectionPatch(xyA,xyB,coordsA="data",coordsB="data",axesA=ax0, axesB=ax1,
                              arrowstyle="<|-|>",ec='k')
        conLine.append(con)
        ax0.add_artist(con)
    return conLine
    
def drawPeakLinkModifyFig(fig,dataR,dataS,linkXR,linkXS):
    fig.clf()
  #  dFigMargin={'L':0.05,'R':0.95,'T':1,'B':0.07} 
  #  fig.subplots_adjust(dFigMargin['L'],dFigMargin['B'],dFigMargin['R'],dFigMargin['T'],0.0,0.0) 
    axesR = fig.add_subplot(211)
    axesS = fig.add_subplot(212)
    axesR.plot(dataR,'r')
    axesS.plot(dataS,'b')
    axesR.legend(['Reference Channel'],loc=2)
    axesS.legend(['Sample Channel'],loc=2)
    linkYR=dataR[linkXR]
    linkYS=dataS[linkXS]
    con0=drawMatchLines0(linkXS,linkYS,linkXR,linkYR,axesS,axesR)
    maxLen=len(dataR)
    lenS=len(dataS)
    if lenS>maxLen:
        maxLen=lenS  
    axesR.set_xlim(0,maxLen)
    axesS.set_xlim(0,maxLen)
    
    return con0, axesR,axesS
    
    
   
def drawReactivityRef(fig,dProject,dProjRef,drawType=0):
    fig.clf()
    dFigMargin={'L':0.05,'R':0.95,'T':1,'B':0.07} 
    fig.subplots_adjust(dFigMargin['L'],dFigMargin['B'],dFigMargin['R'],dFigMargin['T'],0.0,0.0) 
    axes0 = fig.add_subplot(211)
    axes1 = fig.add_subplot(212)
    if drawType==1:
        axes0.plot(dProject['dPeakRX']['area'],'r',linestyle='steps')
        axes0.plot(dProjRef['dPeakRX']['area'],'b',linestyle='steps')
        axes1.plot(dProject['dPeakBG']['area'],'r',linestyle='steps')
        axes1.plot(dProjRef['dPeakBG']['area'],'b',linestyle='steps')
        axes0.legend(['Sample Peak Area RX','Reference Peak Area RX'],loc=2)
        axes1.legend(['Sample Peak Area BG','Reference Peak Area BG'],loc=2)
  
    else:
        axes0.plot(dProject['normDiff'],'r',linestyle='steps')
        axes0.plot(dProjRef['normDiff'],'b',linestyle='steps')
        diff=dProjRef['normDiff']-dProject['normDiff']
        error=np.sum(np.abs(diff))
        axes1.plot(diff,'r',linestyle='steps')
        axes1.plot(np.zeros(len(diff)))
        axes0.legend(['Sample Reactivity','Reference Reactivity'],loc=2)
        legError='Reactivity Difference, Error = '+ str(np.round(error,2))
        axes1.legend([legError],loc=2)

    setDiffFigures(dProject,axes0)
    setDiffFigures(dProject,axes1)
    
def createReactivityFig(fig,dProject,is5to3=False,drawType=0):
    fig.clf()
    dFigMargin={'L':0.0,'R':1,'T':1,'B':0.07} 
    fig.subplots_adjust(dFigMargin['L'],dFigMargin['B'],dFigMargin['R'],dFigMargin['T'],0.0,0.0) 
    axesDiff = fig.add_subplot(111)
        
    if drawType==0:
        drawReactivity(dProject,axesDiff,is5to3) 
    else:
        drawPeakArea(dProject,axesDiff,is5to3)
   
def drawReactivity(dProject,axesDiff,is5to3=False):
        i=0
        j=0
        k=1
        if is5to3:
            k=-1 
            i=1       
        while i<(len(dProject['normDiff'])-1):
            ind=k*i
            if dProject['normDiff'][ind]<0.4:
                axesDiff.bar(j,dProject['normDiff'][ind],facecolor='k',edgecolor='k')      
            elif dProject['normDiff'][ind]<0.85:
                axesDiff.bar(j,dProject['normDiff'][ind],facecolor='y',edgecolor='y')
            else:
                axesDiff.bar(j,dProject['normDiff'][ind],facecolor='r',edgecolor='r')
            i+=1
            j+=1
        axesDiff.set_ylim(-0.5,3)
        setDiffFigures(dProject,axesDiff,is5to3)
        
def drawPeakArea(dProject,axesDiff,is5to3=False):
    if is5to3:
        axesDiff.plot(dProject['dPeakRX']['area'][::-1],'r',linestyle='steps')
        axesDiff.plot(dProject['dPeakBG']['area'][::-1],'b',linestyle='steps')
    else:
        axesDiff.plot(dProject['dPeakRX']['area'][:-1],'r',linestyle='steps')
        axesDiff.plot(dProject['dPeakBG']['area'][:-1],'b',linestyle='steps')
    axesDiff.legend(['Peak Area RX','Peak Area BG'],loc=2)
    setDiffFigures(dProject,axesDiff,is5to3)
 
def setDiffFigures(dProject,axesDiff,is5to3=False):
    xtick,xlabel=seqTickLabel(dProject,is5to3)
    axesDiff.set_xticks(xtick)
    axesDiff.set_xticklabels(xlabel)
    axesDiff.grid(True)
    axesDiff.set_xlim(0,len(dProject['seqRNA']))

def seqTickLabel(dProject,is5to3=False):
    xTick=[]#
    xLabel=[] #np.array([]),np.array([],dtype='i4')
    i=1
    j=0
    while i<len(dProject['seqRNA']):
        xTick.append(j)
        label=dProject['seqRNA'][i]+str(dProject['seqNum'][i])
        xLabel.append(label)
        i+=5
        j+=5
    if is5to3:
        xLabel.reverse() 
    return xTick,xLabel     

def createVerticalLines(figAxes):
    verticalLines=[]
    for ax in figAxes: 
        verticalLines.append(ax.axvline(0,visible=True,color='0.5'))
    return verticalLines


def createRects(figAxes):
    spanRect=[]
    for ax in figAxes:
        h = ax.get_ybound()[1]-ax.get_ybound()[0]
        y=ax.get_ybound()[0]
        spanRect.append(Rectangle( (0,y), 0, h, color='0.3',alpha=0.3))# alpha=0.9, facecolor='red'))
        ax.add_patch(spanRect[-1])
    
    return spanRect

def createAxes(fig,dVar,keys):
    chAxes={}
    if  dVar['drawType']==0:
        chAxes['RX'] = fig.add_subplot(411)
        chAxes['RXS1'] = fig.add_subplot(413)
        chAxes['BG'] = fig.add_subplot(412)
        chAxes['BGS1'] = fig.add_subplot(414)
    elif  dVar['drawType']==1:
        chAxes['RX'] = fig.add_subplot(211)
        chAxes['RXS1'] = fig.add_subplot(212)
        chAxes['BG']=chAxes['RX']
        chAxes['BGS1']=chAxes['RXS1']        
    elif  dVar['drawType']==2:
        chAxes['RX'] = fig.add_subplot(111)
        chAxes['RXS1']=chAxes['RX'] 
        chAxes['BG']=chAxes['RX'] 
        chAxes['BGS1']=chAxes['RX'] 
    elif  dVar['drawType']==3:
        chAxes['RX'] = fig.add_subplot(211)
        chAxes['BG'] = fig.add_subplot(212)
        chAxes['RXS1']=chAxes['RX'] 
        chAxes['BGS1']=chAxes['BG'] 
    
    if 'RXS2' in keys:
        chAxes['RXS2']=chAxes['RXS1']
    if 'BGS2' in keys:
        chAxes['BGS2']=chAxes['BGS1'] 
    
    return chAxes
            