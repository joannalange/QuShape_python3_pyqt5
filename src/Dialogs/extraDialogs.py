from imports import QtGui,QtCore

import numpy as np
from myWidgets import *
from Functions import *

class DlgVariousTools(QtGui.QWidget):
    def __init__(self, dProject,parent=None):
        QtGui.QWidget.__init__(self, parent)
        
        self.labelTitle = QtGui.QLabel(self.tr("<center><b>SOME FUNCTIONS</b></center>"))
        self.name="Various Tools"
        self.toolID=1
        
        self.dProject=dProject
        self.isToolApplied=False
####  Group  Box Radio
        groupBoxRadio = QtGui.QGroupBox(self.tr("Select a Tool"))
        self.radioButton0 = QtGui.QRadioButton(self.tr("Resolution Enhancement"))
        self.radioButton1 = QtGui.QRadioButton(self.tr("First Derivative"))
        self.radioButton2 = QtGui.QRadioButton(self.tr("Stat Normalization"))
        self.radioButton3 = QtGui.QRadioButton(self.tr("Fourier Transform"))
        
        self.radioButton0.setChecked(True)

        vbox = myVBoxLayout()
        vbox.addWidget(self.radioButton0)
        vbox.addWidget(self.radioButton1)
        vbox.addWidget(self.radioButton2)  
        vbox.addWidget(self.radioButton3)       
        groupBoxRadio.setLayout(vbox)

### Button Box
        self.buttonBox =ToolButton()
  
        self.groupBoxROI=GroupBoxROI(self.dProject)
        self.applyChannel=ApplyChannel(self.dProject)
        
        mainLayout=QtGui.QVBoxLayout()
        mainLayout.addWidget(self.labelTitle)
        mainLayout.addWidget(groupBoxRadio)
        mainLayout.addWidget(self.groupBoxROI.groupBox) 
        mainLayout.addWidget(self.applyChannel.groupBox)
        mainLayout.addStretch()
        mainLayout.addWidget(self.buttonBox)
        self.setLayout(mainLayout)
        
        
    def apply(self):
        self.dProjOut=deepcopy(self.dProject)
        self.dOutput=self.dProjOut['dData']
      
        for key in self.dProject['dData'].keys(): 
            if self.applyChannel.checkBox0[key].isChecked():
                if self.groupBoxROI.groupBox.isChecked():
                    fromP=self.groupBoxROI.fromSpinBox.value()
                    toP=self.groupBoxROI.toSpinBox.value()
                else:
                    fromP=0
                    toP=len(self.dProjOut['dData'][key])
                if self.radioButton0.isChecked():
                    self.dProjOut['dData'][key][fromP:toP]=enhance(self.dProject['dData'][key][fromP:toP]) 
                elif self.radioButton1.isChecked():
                    self.dProjOut['dData'][key][fromP:toP]=deriv1(self.dProject['dData'][key][fromP:toP])       
                elif self.radioButton2.isChecked():
                    self.dProjOut['dData'][key][fromP:toP]=normSimple(self.dProject['dData'][key][fromP:toP] )             
                elif self.radioButton3.isChecked():            
                    self.dProjOut['dData'][key][fromP:toP]=np.fft.fftshift(np.fft.fft(self.dProject['dData'][key][fromP:toP])).real
        self.isToolApplied=True
       
        
class DlgSwap(QtGui.QWidget):
    def __init__(self, dProject,parent=None):
        QtGui.QWidget.__init__(self, parent)
        
        self.labelTitle = QtGui.QLabel(self.tr("<center><b>CHANNEL SWAP</b></center>"))
        self.name="Swap"
        self.toolID=1
        
        self.dProject=dProject
        self.dProjOut=dProject.copy()
            
        self.label0={}
        self.comboBox0={}
        for key in self.dProject['chKeyRS']:
            self.label0[key]=QtGui.QLabel(key)
            self.comboBox0[key]=QtGui.QComboBox()
            self.comboBox0[key].addItems(self.dProject['chKeyRS'])
            self.comboBox0[key].setCurrentIndex(self.dProject['chKeyRS'].index(key))
         
        vbox=myGridLayout()
        vbox.addWidget(self.label0['RX'],0,0)
        vbox.addWidget(self.comboBox0['RX'],0,1)
        vbox.addWidget(self.label0['BG'],1,0)
        vbox.addWidget(self.comboBox0['BG'],1,1)
        vbox.addWidget(self.label0['RXS1'],2,0)
        vbox.addWidget(self.comboBox0['RXS1'],2,1)
        vbox.addWidget(self.label0['BGS1'],3,0)
        vbox.addWidget(self.comboBox0['BGS1'],3,1)
        if self.dProject['isSeq2']:
            vbox.addWidget(self.label0['RXS2'],4,0)
            vbox.addWidget(self.comboBox0['RXS2'],4,1)
            vbox.addWidget(self.label0['BGS2'],5,0)
            vbox.addWidget(self.comboBox0['BGS2'],5,1)
        
        self.groupBox0=QtGui.QGroupBox()
        self.groupBox0.setLayout(vbox)
        
        
### Button Box
        self.buttonBox = ToolButton()
## Main Layout  
        mainLayout=QtGui.QVBoxLayout()
        mainLayout.addWidget(self.labelTitle)
        mainLayout.addWidget(self.groupBox0)
        mainLayout.addStretch()
        mainLayout.addWidget(self.buttonBox)
        self.setLayout(mainLayout)
        self.isToolApplied=False 
       
    def apply(self):
        self.dOutput=self.dProject['dData'].copy()
        for key in self.dProject['chKeyRS']:
            self.dOutput[key]=self.dProject['dData'][str(self.comboBox0[key].currentText())]
        self.dProjOut['dData']=self.dOutput.copy()
        self.isToolApplied=True 
       
class DlgScale(QtGui.QWidget):
    def __init__(self, dProject,parent=None):
        QtGui.QWidget.__init__(self, parent)
        
        self.title = QtGui.QLabel(self.tr("<center><b>SCALE</b></center>"))
        self.name="Scale"
        self.toolID=1
        
        self.dProject=dProject
        self.dOutput=dProject['dData'].copy()
         
        self.label0={}
        self.doubleSpinBox0={}
        for key in self.dProject['chKeyRS']:
            self.label0[key]=QtGui.QLabel(key)
            self.doubleSpinBox0[key]=QtGui.QDoubleSpinBox()
            self.doubleSpinBox0[key].setRange(0.01,100.00) 
            self.doubleSpinBox0[key].setValue(1.00)
            self.doubleSpinBox0[key].setSingleStep(0.01)
        
        self.groupBox1=QtGui.QGroupBox(self.tr('Enter Scale Factor'))
       
        vbox=QtGui.QGridLayout()
        vbox.addWidget(self.label0['RX'],0,0)
        vbox.addWidget(self.doubleSpinBox0['RX'],0,1)
        vbox.addWidget(self.label0['BG'],1,0)
        vbox.addWidget(self.doubleSpinBox0['BG'],1,1)
        vbox.addWidget(self.label0['RXS1'],2,0)
        vbox.addWidget(self.doubleSpinBox0['RXS1'],2,1)
        vbox.addWidget(self.label0['BGS1'],3,0)
        vbox.addWidget(self.doubleSpinBox0['BGS1'],3,1)
        if self.dProject['isSeq2']:
            vbox.addWidget(self.label0['RXS2'],4,0)
            vbox.addWidget(self.doubleSpinBox0['RXS2'],4,1)
            vbox.addWidget(self.label0['BGS2'],5,0)
            vbox.addWidget(self.doubleSpinBox0['BGS2'],5,1)
        

        vbox.setContentsMargins(0,0,0,0)
        self.groupBox1.setLayout(vbox)
   
        self.pushButton0=QtGui.QPushButton('Scale All to BG')
        self.connect(self.pushButton0,QtCore.SIGNAL("clicked()"),self.autoScale)
        
### Button Box
        self.buttonBox = ToolButton()
## Main Layout  
        self.groupBoxROI=GroupBoxROI(self.dProject)
              
        mainLayout=QtGui.QVBoxLayout()
        mainLayout.addWidget(self.title)
        mainLayout.addWidget(self.groupBox1)
        mainLayout.addWidget(self.pushButton0)
        mainLayout.addWidget(self.groupBoxROI.groupBox)
        mainLayout.addStretch()
        mainLayout.addWidget(self.buttonBox)
       
        self.setLayout(mainLayout)
        self.isToolApplied=False
        
    def apply(self):
        self.dOutput=self.dProject['dData'].copy()
        if self.groupBoxROI.groupBox.isChecked():
            fromP=self.groupBoxROI.fromSpinBox.value()
            toP=self.groupBoxROI.toSpinBox.value()
            if toP<fromP:
                QtGui.QMessageBox.warning(self,'Warning', ' FROM  should be higher than TO')
                self.isApplied=False
                return
        for key in self.dProject['chKeyRS']:
            if self.groupBoxROI.groupBox.isChecked():
                self.dOutput[key][fromP:toP]=self.dProject['dData'][key][fromP:toP] * self.doubleSpinBox0[key].value() 
            else:
                self.dOutput[key]=self.dProject['dData'][key] * self.doubleSpinBox0[key].value()       
        self.dProjOut=deepcopy(self.dProject)
        self.dProjOut['dData']=self.dOutput
        self.isToolApplied=True 
        
    def autoScale(self):
        dScaleFactor=scaleAllShapeData(self.dProject['dData'])
        for key in self.dProject['chKeyRS']:
            self.doubleSpinBox0[key].setValue(dScaleFactor[key]) 
          
class DlgOpenABIFFile(QtGui.QWidget):
    def __init__(self,parent=None):
        QtGui.QWidget.__init__(self, parent)
        
        self.title = QtGui.QLabel(self.tr("<center><b>OPEN ABIF FILE</b></center>"))
        self.name="Open ABIF File"
        self.toolID=1
            
        self.fileRead0=DlgSelectFile('ABIF File',"ABIF or Text File (*.ab1 *.fsa *.txt)")
        self.listWidget0 = myListWidget()       
        self.buttonBox = ToolButton()
        
        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(self.title)
        mainLayout.addWidget(self.fileRead0)
        mainLayout.addWidget(self.listWidget0)
        mainLayout.addWidget(self.buttonBox)
        self.setLayout(mainLayout)
        self.isToolApplied=False 
        
    def apply(self):
        self.fName=str(self.fileRead0.lineEdit0.text())
        if self.fName=='':
            QtGui.QMessageBox.warning(self,'Warning', 'Select a file')
        else:
            self.listWidget0.clear()
            self.reader=ABIFReader(self.fName)
            entry=self.reader.entries
            for e in entry:
                if str(e.name)!='DATA':
                    item=''
                    item=str(e.name)+' '+str(e.number)+' '+str(self.reader.getData(e.name,e.number))
                    self.listWidget0.addItem(item)
                    
            self.Satd={}
            try:
                self.Satd['RX']=self.reader.getData('Satd',1) #readOfSc(self.reader)
                self.Satd['BG']=self.reader.getData('Satd',1)
            except:
                self.Satd['RX']=np.array([])
                self.Satd['BG']=np.array([])
            self.dOutput={}
            self.dOutput['RX']=self.reader.getData('DATA',1)
            self.dOutput['BG']=self.reader.getData('DATA',2)
            self.dOutput['RXS1']=self.reader.getData('DATA',3)
            self.dOutput['BGS1']=self.reader.getData('DATA',4)
        
        self.dProjOut=DProjectNew()
        self.dProjOut['dData']=self.dOutput
        self.dProjOut['Satd']=self.Satd
        self.isToolApplied=True

class DlgOpenSeqFile(QtGui.QWidget):
    def __init__(self,parent=None):
        QtGui.QWidget.__init__(self, parent)
        
        self.labelTitle = QtGui.QLabel(self.tr("<center><b>OPEN SEQUENCE FILE</b></center>"))
        self.name="Read Sequence File"
        self.toolID=1
         
        self.fileRead0=DlgSelectFile('Seq. File',"Base Files (*.txt *.fasta *.gbk *.seq )")
        self.listWidget0 = QtGui.QListWidget()
         
### Button Box
        self.buttonBox = ToolButton()
        
        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(self.labelTitle)
        mainLayout.addWidget(self.fileRead0)
        mainLayout.addWidget(self.listWidget0)
        mainLayout.addWidget(self.buttonBox)         
        self.setLayout(mainLayout)
        self.isToolApplied=False 
        
    def apply(self):
        self.fileSeqRNA=str(self.fileRead0.lineEdit0.text())
        self.seqRNA5to3=readBaseFile(str(self.fileSeqRNA))
        self.seqRNA3to5=self.seqRNA5to3[::-1]
        NSeqRNA=len(self.seqRNA5to3)
        self.listWidget0.addItem('Length of RNA : '+str(NSeqRNA))
        NofNuc=[self.seqRNA5to3.count('G'),self.seqRNA5to3.count('C'),self.seqRNA5to3.count('A'),self.seqRNA5to3.count('U')]
        
        self.listWidget0.addItem('Number of nucleotides: G:'+str(NofNuc[0])+', C:'+str(NofNuc[1])+', A: '+str(NofNuc[2])+', U: '+str(NofNuc[3]))
        self.listWidget0.addItem("Nucleotides from 5' to 3': ")
        nn=50
        for i in range(0,NSeqRNA,nn):
            line='-'*67
            self.listWidget0.addItem(line) 
            line=str(NSeqRNA-i)
            line+='   '
            line+=str(self.seqRNA3to5[i:i+10])
            line+='   '
            line+=str(self.seqRNA3to5[i+10:i+20])
            line+='   '
            line+=str(self.seqRNA3to5[i+20:i+30])
            line+='   '
            line+=str(self.seqRNA3to5[i+30:i+40])
            line+='   '
            line+=str(self.seqRNA3to5[i+40:i+50])
            self.listWidget0.addItem(line) 
        self.isToolApplied=True 
            
class DlgOpenShapeFinder(QtGui.QWidget):
    def __init__(self,parent=None):
        QtGui.QWidget.__init__(self, parent)
        
        self.labelTitle = QtGui.QLabel(self.tr("<center><b>OPEN SHAPEFINDER FILES</b></center>"))
        self.name="Read ShapeFinder File"
        self.toolID=1
        
        self.fileRead0=DlgSelectFile('Data File',"Text File (*.txt)")
        self.fileRead1=DlgSelectFile('Report File',"Text File (*.txt)")
         
### Button Box
        self.buttonBox = ToolButton()
        
        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(self.labelTitle)
        mainLayout.addWidget(self.fileRead0)
        mainLayout.addWidget(self.fileRead1)
        mainLayout.addStretch()
        mainLayout.addWidget(self.buttonBox)         
        self.setLayout(mainLayout)
        self.isToolApplied=False 
    def apply(self):
        self.dProjOut=DProjectNew()
        self.dataFile=str(self.fileRead0.lineEdit0.text())
     #   self.dataFile='/Users/fethullah/Shape Data/TPP files 2/KS_1M7_DMSO_-TPP_060809_int.txt'
        dataA=readDataTxt(self.dataFile)
       
        self.dProjOut['dData']['RX']=dataA[:,0]
        self.dProjOut['dData']['BG']=dataA[:,1]
        self.dProjOut['dData']['RXS1']=dataA[:,2]
        self.dProjOut['dData']['BGS1']=dataA[:,3]
        
        self.integratedFile=str(self.fileRead1.lineEdit0.text())
     #   self.integratedFile="/Users/fethullah/Shape Data/TPP files 2/KS_1M7_DMSO_-TPP_060809_areasb.txt"
        fl=open(self.integratedFile, "r")
        a,data=[],[]
        lines=fl.readlines()
        for i in range(len(lines)-1,0,-1):
            a= lines[i].split('\t')
            self.dProjOut['seqNum']=np.append(self.dProjOut['seqNum'],int(a[0]))
            self.dProjOut['seqRNA']+=str(a[1])
            self.dProjOut['dPeakRX']['pos']=np.append(self.dProjOut['dPeakRX']['pos'],int(a[2]))
            self.dProjOut['dPeakRX']['wid']=np.append(self.dProjOut['dPeakRX']['wid'],float(a[3]))
            self.dProjOut['dPeakRX']['area']=np.append(self.dProjOut['dPeakRX']['area'],float(a[4]))
            self.dProjOut['dPeakBG']['pos']=np.append(self.dProjOut['dPeakBG']['pos'],int(a[6]))
            self.dProjOut['dPeakBG']['wid']=np.append(self.dProjOut['dPeakBG']['wid'],float(a[7]))
            self.dProjOut['dPeakBG']['area']=np.append(self.dProjOut['dPeakBG']['area'],float(a[8]))
            self.dProjOut['areaDiff']=np.append(self.dProjOut['areaDiff'],float(a[10]))
            self.dProjOut['normDiff']=np.append(self.dProjOut['normDiff'],float(a[11]))
        
        fl.close()
          
        self.dProjOut['dPeakRX']['amp']=self.dProjOut['dData']['RX'][self.dProjOut['dPeakRX']['pos']]
        self.dProjOut['dPeakBG']['amp']=self.dProjOut['dData']['RX'][self.dProjOut['dPeakBG']['pos']]
     
        self.dProjOut['seqX']=self.dProjOut['dPeakRX']['pos']
        self.dProjOut['seqNum']=self.dProjOut['seqNum'][:-1]
        self.dProjOut['seqNum']=np.insert(self.dProjOut['seqNum'],0,self.dProjOut['seqNum'][0]+1)
        self.dProjOut['seqRNA']=self.dProjOut['seqRNA'][:-1]
        self.dProjOut['seqRNA']= 'N'+self.dProjOut['seqRNA']
        
        self.dProjOut['dPeakRX']['NPeak']=len(self.dProjOut['dPeakRX'])
        self.dProjOut['dPeakBG']['NPeak']=len(self.dProjOut['dPeakBG'])
        
        if self.dProjOut['dPeakRX']['pos'][0]>10:
            s=self.dProjOut['seqX'][0]-10
            e=self.dProjOut['seqX'][-1]+10
            self.dProjOut['seqX']=self.dProjOut['seqX']-s
            self.dProjOut['dPeakRX']['pos']=self.dProjOut['dPeakRX']['pos']-s
            self.dProjOut['dPeakBG']['pos']=self.dProjOut['dPeakBG']['pos']-s  
            
            self.dProjOut['dData']['RX']=self.dProjOut['dData']['RX'][s:e]
            self.dProjOut['dData']['BG']=self.dProjOut['dData']['BG'][s:e]
            self.dProjOut['dData']['RXS1']=self.dProjOut['dData']['RXS1'][s:e]
            self.dProjOut['dData']['BGS1']=self.dProjOut['dData']['BGS1'][s:e]
            
            self.dProjOut['dPeakRX']['amp']=self.dProjOut['dData']['RX'][self.dProjOut['dPeakRX']['pos']]
            self.dProjOut['dPeakBG']['amp']=self.dProjOut['dData']['BG'][self.dProjOut['dPeakRX']['pos']]
                  
        self.dProjOut['start']=self.dProjOut['seqNum'][0]
        self.dProjOut['end']=self.dProjOut['seqNum'][-1]+1
        
        self.isToolApplied=True
        
def readShapeFinderReport(dProject,fName):
    fl=open(fName, "r")
    a,data=[],[]
    lines=fl.readlines()
    for i in range(len(lines)-1,0,-1):
        a= lines[i].split('\t')
        dProject['seqNum']=np.append(dProject['seqNum'],int(a[0]))
        dProject['seqRNA']+=str(a[1])
        dProject['dPeakRX']['pos']=np.append(dProject['dPeakRX']['pos'],int(a[2]))
        dProject['dPeakRX']['wid']=np.append(dProject['dPeakRX']['wid'],float(a[3]))
        dProject['dPeakRX']['area']=np.append(dProject['dPeakRX']['area'],float(a[4]))
        dProject['dPeakBG']['pos']=np.append(dProject['dPeakBG']['pos'],int(a[6]))
        dProject['dPeakBG']['wid']=np.append(dProject['dPeakBG']['wid'],float(a[7]))
        dProject['dPeakBG']['area']=np.append(dProject['dPeakBG']['area'],float(a[8]))
        dProject['areaDiff']=np.append(dProject['areaDiff'],float(a[10]))
        dProject['normDiff']=np.append(dProject['normDiff'],float(a[11]))
    
    fl.close()
    
    return dProject


class DlgManualSignalAlign(QtGui.QWidget):
    def __init__(self,dProject,parent=None):
        QtGui.QWidget.__init__(self, parent)
        
        self.labelTitle = QtGui.QLabel(self.tr("<center><b>MANUAL SIGNAL ALGINMENT</b></center>"))
        self.name="Manual Signal Alignment"
        self.toolID=1
        
        self.dProject=dProject
        self.dProjOut=deepcopy(dProject)
        
        self.linkXR,self.linkXS=np.array([]),np.array([])
        self.dataR,self.dataS=np.array([]),np.array([])
        self.isToolApplied=False
        
        label0=QtGui.QLabel('Reference Channel')
        self.comboBox0=QtGui.QComboBox()
        self.comboBox0.addItems(dProject['chKeyRS'])
        label1=QtGui.QLabel('Sample Channel')
        self.comboBox1=QtGui.QComboBox()
        self.comboBox1.addItems(dProject['chKeyRS'])
        self.comboBox1.setCurrentIndex(1)
        
        layout0=myGridLayout()
        layout0.addWidget(label0,0,0)
        layout0.addWidget(self.comboBox0,0,1)
        layout0.addWidget(label1,1,0)
        layout0.addWidget(self.comboBox1,1,1)
        
        self.groupBox0=QtGui.QGroupBox("Select Channels")
        self.groupBox0.setLayout(layout0)
        self.groupBox0.setCheckable(True)
        
        self.button0=QtGui.QPushButton('Modify Matched Peaks')
        self.button0.setEnabled(False)
        
        self.buttonBox = ToolButton()
       
        self.applyChannel=ApplyChannel(self.dProject)
       
        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(self.labelTitle)
        mainLayout.addWidget(self.groupBox0)
        mainLayout.addWidget(self.button0)
        mainLayout.addStretch()
        mainLayout.addWidget(self.applyChannel.groupBox)
        mainLayout.addWidget(self.buttonBox)         
        self.setLayout(mainLayout)
        
        self.refKey='RXS1'
        self.sampleKey='BGS1'
       
    def apply(self):
        if self.groupBox0.isChecked():
            self.dProjOut=deepcopy(self.dProject)
            self.keyR=str(self.comboBox0.currentText())
            self.keyS=str(self.comboBox1.currentText())
            for key in self.dProject['chKeyRS']:
                if key!=self.keyS:
                    self.applyChannel.checkBox0[key].setChecked(False)
    
            self.dataR=self.dProject['dData'][self.keyR]
            self.dataS=self.dProject['dData'][self.keyS]
            NDataR=len(self.dataR)
            NDataS=len(self.dataS)
            self.linkXR=np.array([int(NDataR/4),int(NDataR/2),int(3*NDataR/4)],int) #np.linspace(NDataR/4, NDataR, 3, endpoint=False)
            self.linkXS=np.array([int(NDataS/4),int(NDataS/2),int(3*NDataS/4)],int) #np.linspace(NDataS/4, NDataR, 3, endpoint=False)
            self.button0.setEnabled(True)
            self.groupBox0.setChecked(False)
         
        for key in self.dProject['chKeyRS']:  
            if key!=self.keyR and self.applyChannel.checkBox0[key].isChecked():
                self.dProjOut['dData'][key]=splineSampleData(self.dProject['dData'][key],self.linkXR,self.linkXS,len(self.dataR))
        self.isToolApplied=True      