from imports import QtGui,QtCore

from myWidgets import myGridLayout

class DlgLineProps(QtGui.QDialog):

    def __init__(self,dVar,chKeyRS,parent=None):
        super(DlgLineProps, self).__init__(parent)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setModal(False)
        
        self.labelTitle = QtGui.QLabel(self.tr("<center><b>CHANNEL ATTRIBUTES</b></center>"))
        self.name="Channel Attributes"
        self.toolID=3
        
        self.dVar=dVar.copy()
        self.chKeyRS=chKeyRS
        
        labels=["Channel", "Color", "Line", "Marker", "Width"]
        self.label={}
        self.checkBox0={}
        self.pushButton0={}
        self.comboBoxLineStyle={}
        lineStyles=["solid","dashed","dash_dot","dotted"]
        self.lineStyles=['-','--','-.',':']
        self.comboBoxMarkerStyle={}
        markerStyles=["none","point","circle","star", "square","plus","X","diamond"]
        self.markerStyles1=['','.','o','*','s','+','x','D']
        self.doubleSpinBoxLW={}
        for key in chKeyRS:
            self.checkBox0[key]=QtGui.QCheckBox(key)
            self.checkBox0[key].setChecked(self.dVar['lineVisible'][key])
            self.pushButton0[key]=QtGui.QPushButton()
            self.pushButton0[key].setStyleSheet("QWidget { background-color: %s }" % self.dVar['lineColor'][key])
            self.comboBoxLineStyle[key]=QtGui.QComboBox()
            self.comboBoxLineStyle[key].addItems(lineStyles)
            self.comboBoxMarkerStyle[key]=QtGui.QComboBox()
            self.comboBoxMarkerStyle[key].addItems(markerStyles)
            self.doubleSpinBoxLW[key]=QtGui.QDoubleSpinBox()
            self.doubleSpinBoxLW[key].setValue(1.0)
            self.doubleSpinBoxLW[key].setSingleStep(0.1)
            
            
        layout0=myGridLayout()
        for i in range(len(labels)):
            self.label[i]=QtGui.QLabel(labels[i])
            layout0.addWidget(self.label[i],0,i)
                              
        for key in chKeyRS: #self.dChKeys['RS']:
            index=chKeyRS.index(key)+1
            layout0.addWidget(self.checkBox0[key],index,0)
            layout0.addWidget(self.pushButton0[key],index,1)
            layout0.addWidget(self.comboBoxLineStyle[key],index,2)
            layout0.addWidget(self.comboBoxMarkerStyle[key],index,3)
            layout0.addWidget(self.doubleSpinBoxLW[key],index,4)
            
            
    
        self.buttonBox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Apply| QtGui.QDialogButtonBox.Close)
        
        self.connect(self.pushButton0['RX'], QtCore.SIGNAL("clicked()"), self.changeColorRX)
        self.connect(self.pushButton0['RXS1'], QtCore.SIGNAL("clicked()"), self.changeColorRXS1)
        self.connect(self.pushButton0['BG'], QtCore.SIGNAL("clicked()"), self.changeColorBG)
        self.connect(self.pushButton0['BGS1'], QtCore.SIGNAL("clicked()"), self.changeColorBGS1)
        if 'RXS2' in chKeyRS:
            self.connect(self.pushButton0['RXS2'], QtCore.SIGNAL("clicked()"), self.changeColorRXS2)
        if 'BGS2' in chKeyRS:
            self.connect(self.pushButton0['BGS2'], QtCore.SIGNAL("clicked()"), self.changeColorBGS2)
                        
        self.connect(self.buttonBox.button(QtGui.QDialogButtonBox.Apply),QtCore.SIGNAL("clicked()"),self.apply)
        self.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), self.reject)
       
       
        mainLayout=QtGui.QVBoxLayout()
        mainLayout.addLayout(layout0)
        mainLayout.addWidget(self.buttonBox)
        self.setLayout(mainLayout)
 
        self.title="Channel Attributes"
        self.setWindowTitle(self.title)
        
    def changeColorRX(self):
        self.color0 = QtGui.QColorDialog.getColor()
        if self.color0.isValid():
            self.pushButton0['RX'].setStyleSheet("QWidget { background-color: %s }"% self.color0.name())
            self.dVar['lineColor']['RX']= str(self.color0.name())   
    def changeColorRXS1(self):
        self.color1 = QtGui.QColorDialog.getColor()
        if self.color1.isValid():
            self.pushButton0['RXS1'].setStyleSheet("QWidget { background-color: %s }"% self.color1.name())
            self.dVar['lineColor']['RXS1']= str(self.color1.name())   
    def changeColorRXS2(self):
        self.color2 = QtGui.QColorDialog.getColor()
        if self.color2.isValid():
            self.pushButton0['RXS2'].setStyleSheet("QWidget { background-color: %s }"% self.color2.name())
            self.dVar['lineColor']['RXS2']= str(self.color2.name())   
    def changeColorBG(self):
        self.color0 = QtGui.QColorDialog.getColor()
        if self.color0.isValid():
            self.pushButton0['BG'].setStyleSheet("QWidget { background-color: %s }"% self.color0.name())
            self.dVar['lineColor']['BG']= str(self.color0.name()) 
    def changeColorBGS1(self):
        self.color1 = QtGui.QColorDialog.getColor()
        if self.color1.isValid():
            self.pushButton0['BGS1'].setStyleSheet("QWidget { background-color: %s }"% self.color1.name())
            self.dVar['lineColor']['BGS1']= str(self.color1.name())   
    def changeColorBGS2(self):
        self.color2 = QtGui.QColorDialog.getColor()
        if self.color2.isValid():
            self.pushButton0['BGS2'].setStyleSheet("QWidget { background-color: %s }"% self.color2.name())
            self.dVar['lineColor']['BGS2']= str(self.color2.name())   
         
    def apply(self):
        for key in self.chKeyRS:
            self.dVar['lineVisible'][key]=self.checkBox0[key].isChecked()
            self.dVar['lineStyle'][key]=self.lineStyles[self.comboBoxLineStyle[key].currentIndex()]
            self.dVar['lineMarker'][key]=self.markerStyles1[self.comboBoxMarkerStyle[key].currentIndex()]
            self.dVar['lineWidth'][key]=self.doubleSpinBoxLW[key].value()


class DlgFigureSet(QtGui.QDialog):

    def __init__(self,dVar,chKeyRS,parent=None):
        super(DlgFigureSet, self).__init__(parent)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setModal(False)
        
        self.labelTitle = QtGui.QLabel(self.tr("<center><b>FIGURE SETTING</b></center>"))
        self.name="Figure Setting"
        self.toolID=3
        
        self.dVar=dVar.copy()
        self.chKeyRS=chKeyRS
        
        # Size, width, height, resolution, 
        
        labelT=QtGui.QLabel('Size style')
        self.comboBox0=QtGui.QComboBox()
        self.comboBox0.addItems(['Percentage','Inches'])
        
        labelW = QtGui.QLabel("Width")
        self.spinBoxWidth=QtGui.QSpinBox()
        self.spinBoxWidth.setRange(10, 200)
        self.spinBoxWidth.setValue(100)
        self.spinBoxWidth.setSingleStep(10)
        self.spinBoxWidth.setSuffix(" %")
        
        labelH = QtGui.QLabel("Height")
        self.spinBoxHeight=QtGui.QSpinBox()
        self.spinBoxHeight.setRange(10, 200)
        self.spinBoxHeight.setValue(100)
        self.spinBoxHeight.setSingleStep(10)
        self.spinBoxHeight.setSuffix(" %")
        
        self.checkBoxFitWindow=QtGui.QCheckBox("Fit into Window")
         
        labelR = QtGui.QLabel("Zoom")
        self.spinBoxR=QtGui.QSpinBox()
        self.spinBoxR.setRange(10, 1000)
        self.spinBoxR.setValue(100)
        self.spinBoxR.setSingleStep(50)
       
        layout0=myGridLayout()
        layout0.addWidget(self.checkBoxFitWindow,0,0,1,2)
        layout0.addWidget(labelT,1,0)
        layout0.addWidget(self.comboBox0,1,1)
        layout0.addWidget(labelW,2,0)
        layout0.addWidget(self.spinBoxWidth,2,1)
        layout0.addWidget(labelH,3,0)
        layout0.addWidget(self.spinBoxHeight,3,1)
        layout0.addWidget(labelR,4,0)
        layout0.addWidget(self.spinBoxR,4,1)
      
        groupBox0=QtGui.QGroupBox(self.tr('Figure Options'))
        groupBox0.setLayout(layout0)
         
        
        labelSubs={}
        self.spinBoxSubs={}
        self.keySubs=['top', 'bottom', 'left','right'] #,'wspace','hspace']
        for key in self.keySubs:
            labelSubs[key]=QtGui.QLabel(key)
            self.spinBoxSubs[key]=QtGui.QDoubleSpinBox()
            self.spinBoxSubs[key].setRange(0, 1)
            self.spinBoxSubs[key].setValue(self.dVar[key])
            self.spinBoxSubs[key].setSingleStep(0.01)
           
        layout1=myGridLayout()
        i=0
        while i<len(self.keySubs):
            key=self.keySubs[i]
            layout1.addWidget(labelSubs[key],i,0)
            layout1.addWidget(self.spinBoxSubs[key],i,1)
            i+=1
            key=self.keySubs[i]
            layout1.addWidget(labelSubs[key],i-1,2)
            layout1.addWidget(self.spinBoxSubs[key],i-1,3)
            i+=1
            
        groupBox1=QtGui.QGroupBox(self.tr('Subplot Configuration'))
        groupBox1.setLayout(layout1)
        
        self.checkBoxSatd=QtGui.QCheckBox('Draw Saturated Points')
        self.lanelXLim=QtGui.QLabel('Set Xlim')
        self.fromSpinBox=QtGui.QSpinBox()    
        self.toSpinBox=QtGui.QSpinBox()    
        fromLabel=QtGui.QLabel('From')
        toLabel=QtGui.QLabel('To')
      
        
        self.buttonBox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Apply| QtGui.QDialogButtonBox.Close)
        
        mainLayout=QtGui.QVBoxLayout()
        mainLayout.addWidget(groupBox0)
        mainLayout.addWidget(groupBox1)
        mainLayout.addWidget(self.buttonBox)
        self.setLayout(mainLayout)
 
        self.title="Channel Attributes"
        self.setWindowTitle(self.title)
    def apply(self):
        self.dVar['isFit']=self.checkBoxFitWindow.isChecked()
        self.dVar['widthP']=self.spinBoxWidth.value()
        self.dVar['heightP']=self.spinBoxHeight.value()
        self.dVar['zoomP']=self.spinBoxR.value() 
        self.dVar['isDrawSatd']=self.checkBoxSatd.isChecked()
        for key in self.keySubs:
            self.dVar[key]=self.spinBoxSubs[key].value()
        
     
if __name__ == "__main__":
    import sys
    dLineVisible={'RX':True,'BG':True,'RXS1':True, 'BGS1':True,'RXS2':False, 'BGS2':False}
    dLineColor={'RX':(QtGui.QColor('red').name()),
                            'BG':(QtGui.QColor('blue').name()),
                            'RXS1':str(QtGui.QColor('green').name()),
                            'BGS1':str(QtGui.QColor('magenta').name()),
                            'RXS2':str(QtGui.QColor('yellow').name()),
                            'BGS2':str(QtGui.QColor('cyan').name())}
    app = QtGui.QApplication(sys.argv)
    from Functions import DVar
    form = DlgFigureSet(DVar(dLineVisible.keys()),dLineVisible.keys())
    form.show()
    app.exec_()
        