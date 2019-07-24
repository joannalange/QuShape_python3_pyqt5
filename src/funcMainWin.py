from imports import *

msgAbout = """<b>QuShape</b> v %s
            <p>Copyright &copy; 2010 Weeks Lab. 
            <p>University of North Carolina at Chapel Hill 
            <p>All rights reserved.
            <p>This application can be used to extract quantitative 
            nucleic acid reactivity information """
                 
            #<p>Python %s - Qt %s - PyQt %s on %s""" % (
            #    __version__, platform.python_version(),
            #    QtCore.QT_VERSION_STR, QtCore.PYQT_VERSION_STR, platform.system())


def myGetOpenFileName(workingDir):
    getOpenFileName=QtGui.QFileDialog.getOpenFileName(None,"Select a file",workingDir,("QuShape project file (*.qushape *.pyshape *.txt *.fsa )"))
    if isPyQt:
        projFileName=str(getOpenFileName)
    else:
        projFileName=str(getOpenFileName[0])
    return projFileName

def openProjFile(projFileName):
    extFile=QtCore.QFileInfo(projFileName).suffix()
    if extFile=='txt' or extFile=='fsa':
        data,Satd,dyes=readShapeData(str(projFileName))
        dProject=DProjectNew()
        dProject['dData']['RX']=data[:,0]
        dProject['dData']['BG']=data[:,1]
        dProject['dData']['RXS1']=data[:,2]
        dProject['dData']['BGS1']=data[:,3]
        dProject['Satd']['RX']=Satd
        dProject['Satd']['BG']=Satd
        dProject['dyeN']['RX']=dyes[0]
        dProject['dyeN']['BG']=dyes[1]
        dProject['dyeN']['RXS1']=dyes[2]
        dProject['dyeN']['BGS1']=dyes[3]
       
        dProject['scriptList'].append("New Project")
        
        dProjRef=DProjectNew()
        dVar=DVar(dProject['chKeyRS'])
        intervalData=[]
        intervalData.append(deepcopy(dProject))
    else:
        dBase=shelve.open(projFileName)
        dProject=deepcopy(dBase['dProject'])
        intervalData=deepcopy(dBase['intervalData'])
        
        if 'OfSc' in dProject.keys():
            dProject['Satd']={}
            dProject['Satd']=dProject['OfSc']
            del dProject['OfSc']
        
        if 'dProjRef' in dBase.keys():
            dProjRef=deepcopy(dBase['dProjRef'])
        else:
            dProjRef=DProjectNew()
        
        if 'dVar' in dBase.keys():
            dVar=deepcopy(dBase['dVar'])
        else:
            dVar=DVar(dProject['chKeyRS'])
        
        for key in DVar(dProject['chKeyRS']).keys():
            if key not in dVar.keys():
                dVar[key]=DVar(dProject['chKeyRS'])[key]
        dBase.close()
        
    dProject['fName']=str(projFileName)
    
    return dProject, dVar, intervalData, dProjRef
                 

class MainTopWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        
        layoutDataTrack=myHBoxLayout()
        self.labelCh={}
        for key in chKeysRS:
            self.labelCh[key]=QtGui.QLabel(self.tr(key))
            self.labelCh[key].setFixedWidth(30)
            self.labelCh[key].setAlignment(QtCore.Qt.AlignCenter)
           # self.labelCh[key].setFixedSize(30,20)
            
            layoutDataTrack.addWidget(self.labelCh[key])
       
        groupBoxDataTrack=QtGui.QGroupBox(self.tr('Channels'))
        groupBoxDataTrack.setLayout(layoutDataTrack)
        
        self.splitComboBox=QtGui.QComboBox()
        self.splitComboBox.addItems(["Standard","Reaction/Seqencing", "One Panel", "By Capillary"])
        self.splitComboBox.setToolTip("Split the Channels")
        self.splitComboBox.setWhatsThis(
                                        'This combo box is used to draw the data in difference view. '
                                        ' (1) Standard: The channels are plotted separately'
                                        ' (2) Reaction/Sequencing: The Reagent channels (RX and BG) is plotted in one axes,'
                                        'The sequencing channels are drawn in the same axis'
                                        ' (3) By Capillary : (+) Capillary (RX, RXS and RXS1) and (-) Capillary (BG,BGS1,BGS2) is ploteed in seperate axisi'
                                        ' (4) One Panel: All channels are plotted in one axes')
        
        layoutSplitCombo=myHBoxLayout()
        layoutSplitCombo.addWidget(self.splitComboBox)
        groupBox2=QtGui.QGroupBox(self.tr('Split Channels'))
        groupBox2.setLayout(layoutSplitCombo)      
        
        labelWidth = QtGui.QLabel("W")
        self.spinBoxWidth=QtGui.QSpinBox()
        self.spinBoxWidth.setRange(10, 300)
        self.spinBoxWidth.setValue(100)
        self.spinBoxWidth.setSingleStep(10)
        self.spinBoxWidth.setSuffix(" %")
        self.spinBoxWidth.setToolTip("Change the Width")
    
        labelHeight = QtGui.QLabel("H")
        self.spinBoxHeight=QtGui.QSpinBox()
        self.spinBoxHeight.setRange(10, 300)
        self.spinBoxHeight.setValue(100)
        self.spinBoxHeight.setSingleStep(10)
        self.spinBoxHeight.setSuffix(" %")
        self.spinBoxHeight.setToolTip("Change the height")
       
        self.checkBoxFitWindow=QtGui.QCheckBox("Fit")
        self.checkBoxFitWindow.setChecked(True)
        self.checkBoxFitWindow.setToolTip("Fit to Window")
    
        labelZoom = QtGui.QLabel("Z")
        self.spinBoxZoom=QtGui.QSpinBox()
        self.spinBoxZoom.setRange(1,999)
        self.spinBoxZoom.setValue(100)
        self.spinBoxZoom.setSingleStep(25)
        self.spinBoxZoom.setSuffix(" %")
        self.spinBoxZoom.setToolTip("Zoom the image")
       
        layoutResize=myHBoxLayout()
        layoutResize.addWidget(labelWidth)
        layoutResize.addWidget(self.spinBoxWidth)
        layoutResize.addWidget(labelHeight)
        layoutResize.addWidget(self.spinBoxHeight)
        layoutResize.addWidget(labelZoom)
        layoutResize.addWidget(self.spinBoxZoom)
        layoutResize.addWidget(self.checkBoxFitWindow)
        
        groupBoxResize=QtGui.QGroupBox(self.tr('Figure Options'))
        groupBoxResize.setLayout(layoutResize)
        
### TOP LAYOUT     
        layoutTop=QtGui.QHBoxLayout()
        layoutTop.addWidget(groupBoxDataTrack)
        layoutTop.addWidget(groupBoxResize)
        layoutTop.addWidget(groupBox2)
        layoutTop.setContentsMargins(0, 0, 0, 0)
        layoutTop.setSpacing(1)
        layoutTop.addStretch()
        
        self.setLayout(layoutTop)

class ToolDock(QtGui.QDockWidget):
    def __init__(self,label, parent=None):
        QtGui.QDockWidget.__init__(self, parent)
        self.setWindowTitle('Tool Inspector')
     #   self.setFixedSize(250,350) 
        self.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea| QtCore.Qt.RightDockWidgetArea)
        self.connect(self,QtCore.SIGNAL("topLevelChanged(bool)"),self.dockToolLocationChanged)
    
    def  dockToolLocationChanged(self):
        if self.isFloating():
            self.setMinimumSize(300, 400)
            self.setMaximumSize(600, 800)
        else:
            self.setFixedSize(300,400)
      

    
    
        
         