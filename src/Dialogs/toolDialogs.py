from imports import QtGui,QtCore

import numpy as np
from myWidgets import * #GroupBoxROI,ApplyChannel,ToolButton
from Functions import * # smoothRect, smoothTriangle, smoothGaussian,DData,chKeysRS,enhance,baselineAdjust
import shelve

class DlgToolsAll(QtGui.QWidget):
    def __init__(self,dProject,dProjRef,parent=None):
        QtGui.QWidget.__init__(self, parent)
        
        self.labelTitle = QtGui.QLabel(self.tr("<center><b>APPLY ALL TOOLS</b></center>"))
        self.name="Apply All Tools"
        self.toolID=1
        
        self.dProject=dProject
        self.dProjOut=deepcopy(dProject)
        self.dProjRef=deepcopy(dProjRef)
        
        label0 = QtGui.QLabel("Start Point")
        label1 = QtGui.QLabel("End Point")
        start,end=0,len(self.dProject['dData']['RX']) # findRoi(self.dCurData['RXS'])
        
        self.spinBox0 = QtGui.QSpinBox()
        self.spinBox0.setRange(0, len(self.dProject['dData']['RX']))
        self.spinBox0.setValue(start)
        self.spinBox0.setSingleStep(1)
        
        self.spinBox1 = QtGui.QSpinBox()
        self.spinBox1.setRange(0, len(self.dProject['dData']['RX']))
        self.spinBox1.setValue(end)
        self.spinBox1.setSingleStep(1)
        
        layout0=QtGui.QHBoxLayout()
        layout0.addWidget(label0)
        layout0.addWidget(self.spinBox0)
        layout0.addWidget(label1)
        layout0.addWidget(self.spinBox1)
        
        groupBox0=QtGui.QGroupBox('Select Region of Interest')
        groupBox0.setLayout(layout0)
        
        self.checkBox01=QtGui.QCheckBox("Saturation Correction") 
        self.checkBox0=QtGui.QCheckBox("Smoothing Windows Size")
        self.checkBox1=QtGui.QCheckBox("Mobility Shift")
        self.checkBox2=QtGui.QCheckBox("Baseline Adjustment Window")
        self.checkBox3=QtGui.QCheckBox("Signal Decay Correction")
        self.checkBox4=QtGui.QCheckBox("Signal Alignment")
        
        self.checkBox01.setChecked(True)
        self.checkBox0.setChecked(True)
        self.checkBox1.setChecked(True)
        self.checkBox2.setChecked(True)
        self.checkBox3.setChecked(True)
        self.checkBox4.setChecked(True)
         
        self.spinBox2 = QtGui.QSpinBox()
        self.spinBox2.setRange(0, 10)
        self.spinBox2.setValue(1)
        self.spinBox2.setSingleStep(1)
        
        self.spinBox4 = QtGui.QSpinBox()
        self.spinBox4.setRange(0, 500)
        self.spinBox4.setValue(60)
        self.spinBox4.setSingleStep(1)  
        
        layout1=QtGui.QGridLayout()
        layout1.addWidget(self.checkBox01,0,0)
        layout1.addWidget(self.checkBox0,1,0)
        layout1.addWidget(self.spinBox2,1,1)
        layout1.addWidget(self.checkBox1,2,0)
        layout1.addWidget(self.checkBox2,3,0)
        layout1.addWidget(self.spinBox4,3,1)
        layout1.addWidget(self.checkBox3,4,0)
        layout1.addWidget(self.checkBox4,5,0)
        groupBox1=QtGui.QGroupBox('Select Tools')
        groupBox1.setLayout(layout1)
        
 ### Button Box
        self.buttonBox = ToolButton() 
        
        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(self.labelTitle)
        mainLayout.addWidget(groupBox0)
        mainLayout.addWidget(groupBox1)
        mainLayout.addStretch()
        mainLayout.addWidget(self.buttonBox)
        self.setLayout(mainLayout)
        self.isToolApplied=False 
    
    def apply1(self):
        self.dProjOut=applyAllToolsAuto1(self.dProject, self.dProjRef)
        
#        self.dProjOut=deepcopy(self.dProject)
#        self.dOutput=self.dProjOut['dData']
#        
#        key='BG'
#        self.dProjOut['dData'][key], dataR = applyAllToolsAuto0(self.dProjOut['dData'][key], self.dProjRef['dData'][key],self.dProjOut['Satd'][key])
#    
#        key='RX'
#        self.dProjOut['dData'][key], dataR = applyAllToolsAuto0(self.dProjOut['dData'][key], self.dProjRef['dData'][key],self.dProjOut['Satd'][key])
        self.isToolApplied=True
        
    def apply(self):
        self.dProjOut=deepcopy(self.dProject)
        self.dOutput=self.dProjOut['dData']
        
### Select Region of Interest
        roiStart=self.spinBox0.value() #1700
        roiEnd=self.spinBox1.value() #7500
        
        for key in self.dProject['dData'].keys():
            if len(self.dProject['dData'][key])>0:
                self.dOutput[key]=self.dProject['dData'][key][roiStart:roiEnd]
                
### SATURATION CORRECTION
        if self.checkBox01.isChecked():
                for key in self.dProject['chKeyRX']:
                    self.dOutput[key]=correctSatd(self.dOutput[key],self.dProject['Satd']['RX'])
                for key in self.dProject['chKeyBG']:
                    self.dOutput[key]=correctSatd(self.dOutput[key],self.dProject['Satd']['BG'])
                self.dProject['isSatd']=True
    
### SMOOTHING  
        if self.checkBox0.isChecked():
            self.smoothWindow=self.spinBox2.value()
            for key in self.dProject['dData'].keys():
                if len(self.dProject['dData'][key])>0:
                    self.dOutput[key]=smoothTriangle(self.dOutput[key],self.smoothWindow)
                     
### MOBILITY SHIFT         
        if self.checkBox1.isChecked():
            dyeNR=self.dProject['dyeN']['RX']
            dyeNS=self.dProject['dyeN']['RXS1']
            self.dOutput['RXS1']=fMobilityShift(self.dOutput['RX'],self.dOutput['RXS1'],dyeNR,dyeNS)
            if 'RXS2' in self.dProject['dData'].keys():
                dyeWS=dDyesWL[self.dProject['dyeN']['RXS2']]
                self.dOutput['RXS2']=fMobilityShift(self.dOutput['RX'],self.dOutput['RXS2'],dyeNR,dyeNS)
           
            dyeNR=self.dProject['dyeN']['BG']
            dyeNS=self.dProject['dyeN']['BGS1']
            self.dOutput['BGS1']=fMobilityShift(self.dOutput['BG'],self.dOutput['BGS1'],dyeNR,dyeNS)
            if 'BGS2' in self.dProject['dData'].keys():
                dyeWS=dDyesWL[self.dProject['dyeN']['BGS2']]
                self.dOutput['BGS2']=fMobilityShift(self.dOutput['BG'],self.dOutput['BGS2'],dyeNR,dyeNS) 
### BASELINE ADJUSTMENT
        if self.checkBox2.isChecked():
            self.baselineWindow=self.spinBox4.value()
            for key in self.dProject['dData'].keys():
                if len(self.dProject['dData'][key])>0:
                    self.dOutput[key]=baselineAdjust(self.dOutput[key],self.baselineWindow)
### SIGNAL DECAY        
        if self.checkBox3.isChecked():
            for key in self.dProject['dData'].keys():
                self.dOutput[key]=autoDecaySum(self.dOutput[key])
### SIGNAL ALIGNMENT
        if self.checkBox4.isChecked():
            self.dProjOut['dData']=self.dOutput.copy()
            usedSeq=['RXS1','BGS1','RXS2','BGS2'] 
            linkX0,linkX1=dtwAlign2Cap(self.dProjOut,usedSeq)
            self.dProjOut=splineCap(self.dProjOut,usedSeq,linkX0,linkX1)
   
        self.isToolApplied=True
        
        
class DlgRegionOfInterest(QtGui.QWidget):
    def __init__(self, dProject,dProjRef,parent=None):
        QtGui.QWidget.__init__(self, parent)
        
        self.labelTitle = QtGui.QLabel(self.tr("<center><b>REGION OF INTEREST</b></center>"))
        self.name="Region of Interest"
        self.toolID=1
        self.hint = QtGui.QLabel(self.tr("HINT: Press Key 'F' button and click the axes to set From. "
                                         "Press Key 'T' button and click the axes  to set To" 
                                                                    ))
        self.hint.setWordWrap(True)
        self.font = QtGui.QFont() 
        self.font.setPointSize(10)
        self.hint.setFont(self.font)
        self.dProject=dProject
        self.dProjRef=dProjRef 
        self.dProjOut=deepcopy(dProject) 
        self.isToolApplied=False
        
        self.roi={}
        for key in self.dProject['chKeyRS']:
            self.roi[key]=[0,len(self.dProject['dData'][key])]
         
        labelFrom = QtGui.QLabel("From ")
        labelTo = QtGui.QLabel("To   ")
        
        labelPlus=QtGui.QLabel('(+) Reaction')
        self.spinBoxPlusFrom=QtGui.QSpinBox()
        self.spinBoxPlusTo=QtGui.QSpinBox()
        self.spinBoxPlusFrom.setRange(0,len(self.dProject['dData']['RX']))
        self.spinBoxPlusTo.setRange(0,len(self.dProject['dData']['RX']))
        self.spinBoxPlusTo.setValue(len(self.dProject['dData']['RX']))
        
        labelMinus=QtGui.QLabel('(-) Reaction')
        self.spinBoxMinusFrom=QtGui.QSpinBox()
        self.spinBoxMinusTo=QtGui.QSpinBox()
        self.spinBoxMinusFrom.setRange(0,len(self.dProject['dData']['BG']))
        self.spinBoxMinusTo.setRange(0,len(self.dProject['dData']['BG']))
        self.spinBoxMinusTo.setValue(len(self.dProject['dData']['BG']))

        layout0=myGridLayout()
        layout0.addWidget(labelFrom,0,1)
        layout0.addWidget(labelTo,0,2)
        layout0.addWidget(labelPlus,1,0)
        layout0.addWidget( self.spinBoxPlusFrom,1,1)
        layout0.addWidget( self.spinBoxPlusTo,1,2)
        layout0.addWidget(labelMinus,2,0)
        layout0.addWidget( self.spinBoxMinusFrom,2,1)
        layout0.addWidget( self.spinBoxMinusTo,2,2)
        
        self.groupBox0=QtGui.QGroupBox()
        self.groupBox0.setLayout(layout0)
        
        self.buttunAuto=QtGui.QPushButton('Auto ROI by Reference')
        self.connect(self.buttunAuto,QtCore.SIGNAL("clicked()"),self.autoFindROI)
        
        if not self.dProject['isRef']:
            self.buttunAuto.setEnabled(False)
        self.buttonBox = ToolButton()
        
        mainLayout=QtGui.QVBoxLayout()
        mainLayout.addWidget(self.labelTitle)
        mainLayout.addWidget(self.groupBox0)
        mainLayout.addWidget(self.buttunAuto)
        
        mainLayout.addWidget(self.hint)
        mainLayout.addStretch()
        mainLayout.addWidget(self.buttonBox)
        self.setLayout(mainLayout)
        
    def autoFindROI(self):      
        data0=self.dProject['dData']['RXS1']
        data1=self.dProjRef['dData']['RXS1']
        startRX,endRX=autoROIwDTW(data0,data1)
        self.spinBoxPlusFrom.setValue(startRX)   
        self.spinBoxPlusTo.setValue(endRX)
           
        data0=self.dProject['dData']['BGS1']
        data1=self.dProjRef['dData']['BGS1']
        startBG,endBG=autoROIwDTW(data0,data1)
        self.spinBoxMinusFrom.setValue(startBG)   
        self.spinBoxMinusTo.setValue(endBG)   
        
    def apply(self):
        for key in ['RX','BG']:
            if key=='RX':# in self.dProject['chKeyRX']:
                start=self.spinBoxPlusFrom.value()
                end=self.spinBoxPlusTo.value()
            else:
                start=self.spinBoxMinusFrom.value()
                end=self.spinBoxMinusTo.value()    
            if end<start:
                message="Start should be lower than End"
                QtGui.QMessageBox.warning(self,'Warning', message)
            else:    
                self.roi[key]=[start,end] 
        self.isToolApplied=True
    
    def done(self):
        for key in self.dProject['chKeyRX']:
            self.dProjOut['dData'][key]=self.dProject['dData'][key][self.roi['RX'][0]:self.roi['RX'][1]]
        for key in self.dProject['chKeyBG']:
                self.dProjOut['dData'][key]=self.dProject['dData'][key][self.roi['BG'][0]:self.roi['BG'][1]]  
        self.dProjOut['Satd']['RX'] = fNewSatd(self.dProject['Satd']['RX'],self.roi['RX'][0],self.roi['RX'][1])
        self.dProjOut['Satd']['BG'] = fNewSatd(self.dProject['Satd']['BG'],self.roi['BG'][0],self.roi['BG'][1])

class DlgSmooth(QtGui.QWidget):
    def __init__(self, dProject,parent=None):
        QtGui.QWidget.__init__(self, parent)
        
        self.labelTitle = QtGui.QLabel(self.tr("<center><b>SMOOTHING</b></center>"))
        self.name="Smooth"
        self.toolID=2

        
        self.dProject=dProject 
        self.dProjOut=deepcopy(dProject)  
        self.isToolApplied=False   
#Saturation Correction: Analysis of saturated data points by creating a synthetic peak based upon the peak shape before and after saturation.
        self.checkBoxSatd=QtGui.QCheckBox('Saturation Correction')  
        self.checkBoxSatd.setChecked(True)
####  Group  Box Radio
        self.radioButton0 = QtGui.QRadioButton(self.tr("Triangular Moving Aver."))
        self.radioButton1 = QtGui.QRadioButton(self.tr("Rectangular Moving Aver."))
        self.radioButton2 = QtGui.QRadioButton(self.tr("Gaussian"))
        self.radioButton0.setChecked(True)
        
 #### Window Size
        windowSizeLabel = QtGui.QLabel("Window Size:")
        self.spinBox1 = QtGui.QSpinBox()
        self.spinBox1.setRange(1, 10)
        self.spinBox1.setValue(1)
        self.spinBox1.setSingleStep(1)
        
        layout1 = myGridLayout()
        layout1.addWidget(self.radioButton0,0,0,1,2)
        layout1.addWidget(self.radioButton1,1,0,1,2)
        layout1.addWidget(self.radioButton2,2,0,1,2)
        layout1.addWidget(windowSizeLabel,3,0)
        layout1.addWidget(self.spinBox1,3,1)
        
        self.groupBox0 = QtGui.QGroupBox(self.tr("Smoothing"))
        self.groupBox0.setCheckable(True)
        self.groupBox0.setLayout(layout1)
 
### Button Box
 
        self.buttonBox =ToolButton()
        
        self.groupBoxROI=GroupBoxROI(self.dProject)
        self.applyChannel=ApplyChannel(self.dProject)
        
        mainLayout=QtGui.QVBoxLayout()
        mainLayout.addWidget(self.labelTitle)
        mainLayout.addWidget(self.checkBoxSatd)
        mainLayout.addWidget(self.groupBox0)       
        mainLayout.addWidget(self.groupBoxROI.groupBox)
        mainLayout.addWidget(self.applyChannel.groupBox)
        mainLayout.addStretch()
        mainLayout.addWidget(self.buttonBox)
      
        self.setLayout(mainLayout)
    
    def apply(self):
        self.dProjOut=deepcopy(self.dProject)
        winSize=self.spinBox1.value()
        try:
            if self.checkBoxSatd.isChecked():
                for key in self.dProject['chKeyRX']:
                    self.dProjOut['dData'][key]=correctSatd(self.dProject['dData'][key],self.dProject['Satd']['RX'])
                for key in self.dProject['chKeyBG']:
                    self.dProjOut['dData'][key]=correctSatd(self.dProject['dData'][key],self.dProject['Satd']['BG'])
                self.dProject['isSatd']=True
        except:
            self.dOutput=self.dProject['dData'].copy()      
                    
        if self.groupBox0.isChecked():
            for key in self.dProject['chKeyRS']: 
                if self.applyChannel.checkBox0[key].isChecked():
                    if self.groupBoxROI.groupBox.isChecked():
                        fromP=self.groupBoxROI.fromSpinBox.value()
                        toP=self.groupBoxROI.toSpinBox.value()
                    else:
                        fromP=0
                        toP=len(self.dProjOut['dData'][key])
                    if self.radioButton0.isChecked():
                        method='triangle'
                    elif self.radioButton1.isChecked():
                        method='rectangle'
                    elif self.radioButton2.isChecked():
                        method='gaussian'
                        
                    self.dProjOut['dData'][key][fromP:toP]=fSmooth(self.dProjOut['dData'][key][fromP:toP],winSize,method)
        self.isToolApplied=True          
                               
class DlgBaseline(QtGui.QWidget):
    def __init__(self, dProject,parent=None):
        QtGui.QWidget.__init__(self, parent)
        
        self.labelTitle = QtGui.QLabel(self.tr("<center><b>BASELINE ADJUSTMENT</b></center>"))
        self.name="Baseline Adjustment"
        self.toolID=3
        
        self.dProject=dProject
        self.isToolApplied=False
#### Window Size
        windowLabel = QtGui.QLabel("Baseline Window:")
        self.spinBox0 = QtGui.QSpinBox()
        self.spinBox0.setRange(0,200)
        self.spinBox0.setValue(60)
        self.spinBox0.setSingleStep(1)
        
        self.smoothCheckBox = QtGui.QCheckBox("Smooth the Baseline Drift")
        #self.smoothCheckBox.setChecked(True)
          
        layout2=myGridLayout()
        layout2.addWidget(windowLabel,0,0)
        layout2.addWidget(self.spinBox0,0,1)
        layout2.addWidget(self.smoothCheckBox,1,0)
        groupBoxParameter = QtGui.QGroupBox()
        groupBoxParameter.setLayout(layout2)

### Button Box
        self.buttonBox = ToolButton() 
  
        self.groupBoxROI=GroupBoxROI(self.dProject)
        self.applyChannel=ApplyChannel(self.dProject)
        
        mainLayout=QtGui.QVBoxLayout()
        mainLayout.addWidget(self.labelTitle)
        mainLayout.addWidget(groupBoxParameter)
        mainLayout.addWidget(self.groupBoxROI.groupBox) 
        mainLayout.addWidget(self.applyChannel.groupBox)
        mainLayout.addStretch()
        mainLayout.addWidget(self.buttonBox)
        self.setLayout(mainLayout)
        
    def apply(self):
        self.dProjOut=deepcopy(self.dProject)
        windowSize=self.spinBox0.value()
        isSmooth=self.smoothCheckBox.isChecked()
        for key in self.dProject['dData'].keys(): 
            if self.applyChannel.checkBox0[key].isChecked():
                if self.groupBoxROI.groupBox.isChecked():
                    fromP=self.groupBoxROI.fromSpinBox.value()
                    toP=self.groupBoxROI.toSpinBox.value()
                else:
                    fromP=0
                    toP=len(self.dProjOut['dData'][key])
             
           
                self.dProjOut['dData'][key][fromP:toP]=baselineAdjust(self.dProject['dData'][key][fromP:toP],windowSize,isSmooth)
        self.isToolApplied=True

      
class DlgSignalDecay(QtGui.QWidget):
    def __init__(self, dProject,parent=None):
        QtGui.QWidget.__init__(self, parent)
        
        self.labelTitle = QtGui.QLabel(self.tr("<center><b>SIGNAL DECAY CORRECTION</b></center>"))
        self.name="Signal Decay Correction"
        self.toolID=4
        
        self.dProject=dProject
        self.dOutput=dProject['dData'].copy()
        self.dProjOut=deepcopy(dProject)
        self.isToolApplied=False
        
        
        self.spinBox0=QtGui.QDoubleSpinBox()    
        self.spinBox0.setRange(0,2.0)
        self.spinBox0.setValue(0.2)
        self.spinBox0.setSingleStep(0.1)
          
        ####  Group  Box Radio
        self.radioButton0 = QtGui.QRadioButton(self.tr(" Automatic Summation "))
        self.radioButton1 = QtGui.QRadioButton(self.tr("Exponential"))
        self.radioButton2 = QtGui.QRadioButton(self.tr("Summation       - Factor"))
        
        self.radioButton0.setChecked(True)

        layout0 = myGridLayout()
        layout0.addWidget(self.radioButton0,0,0)
        layout0.addWidget(self.radioButton1,1,0)
        layout0.addWidget(self.radioButton2,2,0)
        layout0.addWidget(self.spinBox0,2,1)
        groupBox0 = QtGui.QGroupBox(self.tr("Select a method"))
        groupBox0.setLayout(layout0)    
        
 ### Button Box
        self.buttonBox = ToolButton()
        self.groupBoxROI=GroupBoxROI(self.dProject)
        self.applyChannel=ApplyChannel(self.dProject)
### Main Layout
        mainLayout=QtGui.QVBoxLayout()
        mainLayout.addWidget(self.labelTitle)
        mainLayout.addWidget(groupBox0) 
        mainLayout.addWidget(self.groupBoxROI.groupBox)
        mainLayout.addWidget(self.applyChannel.groupBox)
        
        mainLayout.addStretch()
        mainLayout.addWidget(self.buttonBox)
        self.setLayout(mainLayout)
    
    def apply(self):
        self.dProjOut=deepcopy(self.dProject)
        self.expF={}
        for key in self.dProject['dData'].keys(): 
            if self.applyChannel.checkBox0[key].isChecked():
                if self.groupBoxROI.groupBox.isChecked():
                    fromP=self.groupBoxROI.fromSpinBox.value()
                    toP=self.groupBoxROI.toSpinBox.value()
                else:
                    fromP=0
                    toP=len(self.dProjOut['dData'][key])
                if self.radioButton0.isChecked():
                    self.dProjOut['dData'][key][fromP:toP]=autoDecaySum(self.dProject['dData'][key][fromP:toP]) 
                elif self.radioButton1.isChecked():
                    self.dProjOut['dData'][key][fromP:toP],self.expF[key]=decayCorrectionExp(self.dProject['dData'][key][fromP:toP])       
                elif self.radioButton2.isChecked():
                    self.dProjOut['dData'][key][fromP:toP]=decaySum(self.dProject['dData'][key][fromP:toP],self.spinBox0.value())             
        self.isToolApplied=True   
class DlgMobilityShift(QtGui.QWidget):
    def __init__(self,dProject,parent=None):
        QtGui.QWidget.__init__(self, parent)
        
        self.labelTitle = QtGui.QLabel(self.tr("<center><b>MOBILITY SHIFT</b></center>"))
        self.name="Mobility Shift"
        self.toolID=4
        
        self.dProject=dProject
        self.dProjOut=deepcopy(dProject)    
        self.dProject=dProject.copy()
        self.isToolApplied=False
        
        self.radioButton0=QtGui.QRadioButton('Position Similarity')
        self.radioButton1=QtGui.QRadioButton('Dynamic Programming')
        self.radioButton0.setChecked(True)
        
        layoutMethod=myVBoxLayout()
        layoutMethod.addWidget((self.radioButton0))
        layoutMethod.addWidget(self.radioButton1)
        self.groupBoxMethod=QtGui.QGroupBox('Select a method')
        self.groupBoxMethod.setLayout(layoutMethod)
        
        self.comboBox0={}
        self.label0={}
        for key in dProject['chKeyRS']:
            self.label0[key] = QtGui.QLabel(key)
            self.comboBox0[key]=QtGui.QComboBox()
            self.comboBox0[key].addItems(dyesName)
            try:
                self.comboBox0[key].setCurrentIndex(dyesName.index(dProject['dyeN'][key]))
            except:
                pass
            if len(self.dProject['dData'][key])==0:
                self.comboBox0[key].setEnabled(False)
        
        self.groupBoxRX=QtGui.QGroupBox(self.tr('(+) Reagent'))
        self.groupBoxRX.setCheckable(True)
        self.groupBoxRX.setChecked(True)
        layoutRX = myGridLayout()
        layoutRX.addWidget(self.label0['RX'], 0, 0)
        layoutRX.addWidget(self.comboBox0['RX'], 0, 1)
        layoutRX.addWidget(self.label0['RXS1'], 1, 0)
        layoutRX.addWidget(self.comboBox0['RXS1'], 1, 1)
        if self.dProject['isSeq2']:
            layoutRX.addWidget(self.label0['RXS2'], 2, 0)
            layoutRX.addWidget(self.comboBox0['RXS2'], 2, 1)
        
        self.groupBoxRX.setLayout(layoutRX)
         
        self.groupBoxBG=QtGui.QGroupBox(self.tr('(-) Reagent)'))
        self.groupBoxBG.setCheckable(True)
        self.groupBoxBG.setChecked(True)
        
        layoutBG = myGridLayout()
        layoutBG.addWidget(self.label0['BG'], 0, 0)
        layoutBG.addWidget(self.comboBox0['BG'], 0, 1)
        layoutBG.addWidget(self.label0['BGS1'], 1, 0)
        layoutBG.addWidget(self.comboBox0['BGS1'], 1, 1)
        if self.dProject['isSeq2']:
            layoutBG.addWidget(self.label0['BGS2'], 2, 0)
            layoutBG.addWidget(self.comboBox0['BGS2'], 2, 1)
        
        self.groupBoxBG.setLayout(layoutBG)
 ### Button Box
        self.buttonBox = ToolButton()
        
        mainLayout=QtGui.QVBoxLayout()
        mainLayout.addWidget(self.labelTitle)
        mainLayout.addWidget(self.groupBoxMethod)
        mainLayout.addWidget(self.groupBoxRX)
        mainLayout.addWidget(self.groupBoxBG)
        mainLayout.addStretch()     
        mainLayout.addWidget(self.buttonBox)
        self.setLayout(mainLayout)
    
    def apply(self):
        self.dOutput=self.dProject['dData'].copy()   
        if self.groupBoxRX.isChecked(): 
            dyeNR=str(self.comboBox0['RX'].currentText())
            dyeNS=str(self.comboBox0['RXS1'].currentText())
            method0='posSim'
            if self.radioButton1.isChecked():
                method0='peakSim'   
            self.dOutput['RXS1']=fMobilityShift(self.dProject['dData']['RX'],self.dProject['dData']['RXS1'],dyeNR,dyeNS,method=method0)
            if self.dProject['isSeq2']:
                dyeNS=str(self.comboBox0['RXS2'].currentText())
                self.dOutput['RXS2']=fMobilityShift(self.dProject['dData']['RX'],self.dProject['dData']['RXS2'],dyeNR,dyeNS,method=method0)   
        if self.groupBoxBG.isChecked():
            dyeNR=str(self.comboBox0['BG'].currentText())
            dyeNS=str(self.comboBox0['BGS1'].currentText())
            self.dOutput['BGS1']=fMobilityShift(self.dProject['dData']['BG'],self.dProject['dData']['BGS1'],dyeNR,dyeNS,method=method0)
            if self.dProject['isSeq2']:
                dyeNS=str(self.comboBox0['BGS2'].currentText())
                self.dOutput['BGS2']=fMobilityShift(self.dProject['dData']['BG'],self.dProject['dData']['BGS2'],dyeNR,dyeNS,method=method0)
        self.dProjOut['dData']=self.dOutput.copy()
        self.isToolApplied=True
                     
class DlgSignalAlign(QtGui.QWidget):
    def __init__(self, dProject,parent=None):
        QtGui.QWidget.__init__(self, parent)
        
        self.title = QtGui.QLabel(self.tr("<center><b>SIGNAL ALIGNMENT</b></center>"))
        self.name="Signal Alignment"
        self.toolID=4
        
        self.dProject=dProject
        self.dOutput=dProject['dData'].copy()    
        self.dProjOut=deepcopy(dProject)
        self.linkXR,self.linkXS=np.array([]),np.array([])
        self.dataR,self.dataS=np.array([]),np.array([])
        self.isToolApplied=False
### Group of ComboBoxes
        label1=QtGui.QLabel("Seq. Channels")
        
        self.comboBox0=QtGui.QComboBox() 
        self.comboBox0.setCurrentIndex(0)
        if self.dProject['isSeq2']: 
            choices0= ['RXS1 - BGS1','RXS2 - BGS2']
        else:
            choices0= ['RXS1 - BGS1']
        self.comboBox0.addItems(choices0)
        
        gridLayout0 = QtGui.QGridLayout()
        gridLayout0.addWidget(label1, 0, 0)
        gridLayout0.addWidget(self.comboBox0, 0, 1)  
        
        groupBox1=QtGui.QGroupBox('Select Channels to be aligned')
        groupBox1.setLayout(gridLayout0)
      
        self.button0=peakMatchModifyButton()
        
        text=self.tr("HINT: When the matched peaks are modified; Key 'A'  to add a Peak. Key 'D'  to delete a Peak. Key 'Shift' to change position. ")                                     
        self.hint = hintLabel(text)
        
#        self.button0=QtGui.QPushButton('Modify Matched Peaks')
#        self.button0.setEnabled(False)
#        
#        self.hint = QtGui.QLabel(self.tr("HINT: When the matched peaks are modified,"
#                                         "Press Key 'A' button and click both plots to add a Peak. "
#                                         "Press Key 'D' button and click to delete a Peak. "
#                                         "Press Key 'Shift' button and select a peak in BGS to change position. "
#                                                                ))
        
#        self.font = QtGui.QFont() 
#        self.font.setPointSize(9)
#        self.hint.setFont(self.font)
#        self.hint.setWordWrap(True)
        
### Button Box
        self.buttonBox = ToolButton()
## Main Layout  
        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget( self.title)
        mainLayout.addWidget(groupBox1)
        mainLayout.addWidget(self.button0)
        mainLayout.addWidget(self.hint)

        mainLayout.addStretch()  
        mainLayout.addWidget(self.buttonBox) 
        self.setLayout(mainLayout)
        
        self.isToolAppliedSigAlign=False
        self.connect(self.comboBox0,QtCore.SIGNAL('currentIndexChanged(int)'), self.comboChanged)
        
    def comboChanged(self):
        self.isToolAppliedSigAlign=False
    def apply(self):
        self.dProjOut=deepcopy(self.dProject) 
        if self.isToolAppliedSigAlign==False:
            if self.comboBox0.currentIndex()==0:
                self.usedSeq=['RXS1','BGS1','RXS2','BGS2'] 
            else:
                self.usedSeq=['RXS2','BGS2','RXS1','BGS1'] 
            self.linkXR,self.linkXS=dtwAlign2Cap(self.dProjOut,self.usedSeq)
            self.isToolAppliedSigAlign=True
            self.button0.setEnabled(True)
        
        self.dataR=self.dProjOut['dData'][self.usedSeq[0]]
        self.dataS=self.dProjOut['dData'][self.usedSeq[1]]
        
        self.linkYR=self.dataR[self.linkXR]
        self.linkYS=self.dataS[self.linkXS]
    
        self.dProjOut=splineCap(self.dProjOut,self.usedSeq,self.linkXR,self.linkXS)
        self.isToolApplied=True
  
        
        
        