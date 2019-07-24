from imports import QtGui,QtCore

class DlgSelectFile(QtGui.QWidget):
    def __init__(self,label,fileType,path=QtCore.QDir.homePath(),parent=None):
        QtGui.QWidget.__init__(self, parent)
       
        self.label=label
        self.fileType=fileType
        self.path=path
        self.label0=QtGui.QLabel(label)
        self.label0.setFixedWidth(80)
        self.lineEdit0=QtGui.QLineEdit()
        self.lineEdit0.setReadOnly(True)
        self.pushButton0=QtGui.QPushButton('Browse')
        
        self.layout0=QtGui.QHBoxLayout()
        self.layout0.addWidget(self.label0)
        self.layout0.addWidget(self.lineEdit0)
        self.layout0.addWidget(self.pushButton0)
        self.layout0.setContentsMargins(0, 0, 0, 0)
        self.layout0.setSpacing(1)
        
        self.setLayout(self.layout0)
        self.connect(self.pushButton0,QtCore.SIGNAL("clicked()"),self.fileBrowse)
        
    def fileBrowse(self):
        self.fName=QtGui.QFileDialog.getOpenFileName(self,"Select a file",self.path,(self.fileType))
        if not self.fName.isEmpty():
            self.lineEdit0.setText(str(self.fName))


class DlgSelectDir(QtGui.QWidget):
    def __init__(self,label,parent=None):
        QtGui.QWidget.__init__(self, parent)
        
        type='file' # dir, save, 
        
        label0=QtGui.QLabel(label)
        self.lineEdit0=QtGui.QLineEdit()
        self.lineEdit0.setReadOnly(True)
        self.pushButton0=QtGui.QPushButton('Browse') 
       
        self.connect(self.pushButton0,QtCore.SIGNAL("clicked()"),self.dirBrowse0)
  
        layout0=myGridLayout() 
        layout0.addWidget(label0,1,0)
        layout0.addWidget(self.lineEdit0,1,1)
        layout0.addWidget(self.pushButton0,1,2)
        
        self.setLayout(layout0)
        
    def dirBrowse0(self):
        self.newDir=QtGui.QFileDialog.getExistingDirectory(self,"Open Directory",QtCore.QDir.homePath())
        if not self.newDir.isEmpty():
            self.lineEdit0.setText(str(self.newDir)) 

                    
class DlgNoTool(QtGui.QWidget):
    def __init__(self,parent=None):
        QtGui.QWidget.__init__(self, parent)
        
        self.labelTitle = QtGui.QLabel(self.tr(
                                               "<p> <center><b>NO TOOL SELECTED </b></center></p>"
                                               "<p> <center>Select a tool from Menu</center> </p> "))
        self.name="No Tool"
        
        self.buttonBox = ToolButton()
        
        mainLayout=QtGui.QVBoxLayout()
        mainLayout.addStretch()
        mainLayout.addWidget(self.labelTitle)
        mainLayout.addStretch()
        mainLayout.addWidget(self.buttonBox)   
        self.setLayout(mainLayout)
        
          
class ToolButton(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        # self.cancelButton = QtGui.QPushButton(self.tr("Cancel"))
        self.applyButton = QtGui.QPushButton(self.tr("Apply"))
        self.skipButton = QtGui.QPushButton(self.tr("Skip"))
        self.doneButton = QtGui.QPushButton(self.tr("Done"))
        self.doneButton.setEnabled(False)
        
        buttonLayout = QtGui.QHBoxLayout()
        buttonLayout.addWidget(self.skipButton)
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(self.applyButton)
        buttonLayout.addWidget(self.doneButton)
      
        self.setLayout(buttonLayout)
        
class GroupBoxROI(QtGui.QWidget):
    def __init__(self, dProject,parent=None):
        QtGui.QWidget.__init__(self, parent)
        
        ## Region of Interest
        self.fromSpinBox=QtGui.QSpinBox()    
        self.fromSpinBox.setRange(0,len(dProject['dData']['RX']))
        self.fromSpinBox.setValue(0)
        self.fromSpinBox.setSingleStep(1)
    
        self.toSpinBox=QtGui.QSpinBox()    
        self.toSpinBox.setRange(0,len(dProject['dData']['RX']))
        self.toSpinBox.setValue(len(dProject['dData']['RX']))
        self.toSpinBox.setSingleStep(1)
      
        fromLabel=QtGui.QLabel('From')
        toLabel=QtGui.QLabel('To')
        
        self.groupBox=QtGui.QGroupBox(self.tr('Region of Interest'))
        self.groupBox.setCheckable(True)
        self.groupBox.setChecked(False)
        layoutRoi=myHBoxLayout()
        layoutRoi.addWidget(fromLabel)
        layoutRoi.addWidget(self.fromSpinBox)
        layoutRoi.addWidget(toLabel)
        layoutRoi.addWidget(self.toSpinBox)
        
        self.groupBox.setLayout(layoutRoi)
       
        
class ApplyChannel(QtGui.QWidget):
    def __init__(self,dProject,parent=None):
        QtGui.QWidget.__init__(self, parent)
        
        self.checkBox0={}    
        self.groupBox=QtGui.QGroupBox(self.tr('Apply to Channels'))
        for key in dProject['chKeyRS']:
            self.checkBox0[key]=QtGui.QCheckBox(key)
            self.checkBox0[key].setChecked(True)
          
        hbox0=myGridLayout()
        hbox0.addWidget(self.checkBox0['RX'],0,0)
        hbox0.addWidget(self.checkBox0['RXS1'],0,1)
        if  dProject['isSeq2']:
            hbox0.addWidget(self.checkBox0['RXS2'],0,2)
        hbox0.addWidget(self.checkBox0['BG'],1,0)
        hbox0.addWidget(self.checkBox0['BGS1'],1,1)
        if dProject['isSeq2']:
            hbox0.addWidget(self.checkBox0['BGS2'],1,2) 
        
        self.groupBox.setLayout(hbox0)

           
class myHBoxLayout(QtGui.QHBoxLayout):
    def __init__(self, parent=None):
        QtGui.QHBoxLayout.__init__(self, parent)
        
        self.setContentsMargins(0, 0, 0, 0) 
        self.setSpacing(1)


class myVBoxLayout(QtGui.QVBoxLayout):
    def __init__(self, parent=None):
        QtGui.QVBoxLayout.__init__(self, parent)
        
        self.setContentsMargins(0, 0, 0, 0) 
        self.setSpacing(1)


class myGridLayout(QtGui.QGridLayout):
    def __init__(self, parent=None):
        QtGui.QGridLayout.__init__(self, parent)
        self.setContentsMargins(0, 0, 0, 0) 
        self.setSpacing(1)

class myListWidget(QtGui.QListWidget):
    def __init__(self, parent=None):
        QtGui.QListWidget.__init__(self, parent)
        
        font = QtGui.QFont("Courier", 11) 
        font.setFixedPitch(True)  
        self.setFont(font)

class peakMatchModifyButton(QtGui.QPushButton):
    def __init__(self, parent=None):
        QtGui.QPushButton.__init__(self, parent)
        
        self.setText('Modify Matched Peaks')
        self.setEnabled(False)
        
        self.setWhatsThis(self.tr("If the signal alignment has glitches, Click to modify the matched peaks. "
                                "Press Key 'A' button and click both plots to add a Peak. "
                                "Press Key 'D' button and click to delete a Peak. "
                                "Press Key 'Shift' button and select a peak to change position. "
                                                                ))


class scaleGroupBox(QtGui.QGroupBox):
    def __init__(self, text, parent=None):
        QtGui.QGroupBox.__init__(self, parent)

        label0=QtGui.QLabel('Scale Factor')
        self.doubleSpinBox0=QtGui.QDoubleSpinBox()
        self.doubleSpinBox0.setRange(0,100.0) 
        self.doubleSpinBox0.setValue(1.00)
        self.doubleSpinBox0.setSingleStep(0.01)
        
        self.checkBoxScale0=QtGui.QCheckBox('Scale by windowing')
        self.checkBoxScale0.setWhatsThis("This option is especially useful for long traces."
                                        " Scaling is applied locally not globally.")
        layout0=myGridLayout()
        layout0.addWidget(self.checkBoxScale0,0,0,1,2)
        layout0.addWidget(label0,1,0)
        layout0.addWidget(self.doubleSpinBox0,1,1)
        self.setTitle(self.tr(text))
        self.setLayout(layout0)
        
class hintLabel(QtGui.QLabel):
    def __init__(self, text, parent=None):
        QtGui.QLabel.__init__(self, parent)
        
        self.setText(text)
        self.setWordWrap(True)
