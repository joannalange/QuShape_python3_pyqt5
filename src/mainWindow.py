from funcMainWin import *

class MainWindow(QtGui.QMainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        
        self.homePath = QtCore.QDir.homePath()
        self.currentDir=os.getcwd()
        self.windowTitle='QuShape'
        self.setWindowTitle(self.windowTitle)
        
        self.variables()
        self.createMainFrame()
        self.createProgressBar() 
     #   self.loadInitialFile()
     #   self.readTestFile()
        
    def readTestFile(self):
        # self.projFileName=self.currentDir+'/data/test0223.pyshape'
        self.projFileName='/Users/fethullah/Shape Data/TPP files 3/test0628.qushape'
        self.openProject(self.projFileName)

    def createMainFrame(self):
        self.mainFrame = QtGui.QWidget()
        self.fig = Figure()
        self.fig.set_facecolor('0.8')
        self.fig.suptitle('Welcome to QuShape',x=0.5,y=0.7, horizontalalignment='center', fontsize=32,color='b')
        self.fig.text(0.5, 0.4, 'Quantification of Nucleic Acid Probing Information', horizontalalignment='center', fontsize=20,color='b')
        
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self.mainFrame)
        setRcParams(rcParams)
        self.scrollArea = QtGui.QScrollArea()
        self.scrollArea.setWidget(self.canvas)
        self.mainTopWidget=MainTopWidget()
        self.setLineColor()  
            
        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(self.scrollArea)
        self.mainFrame.setLayout(mainLayout)
        self.setCentralWidget(self.mainFrame)
        self.setStyleSheet(myStyleSheet)   
        self.createDockWidgets()  
        self.mainWindowConnect()
        self.createMenu()
        
        self.filename = None
        self.qSettings = None
        self.readSettings()
    
        self.updateFileMenu()  
         
    def readSettings(self):
        self.qSettings = QtCore.QSettings()
        try:
            self.recentFiles = self.qSettings.value("RecentFiles").toStringList()
            size = self.qSettings.value("MainWindow/Size",QtCore.QVariant(QtCore.QSize(600, 500))).toSize()
            self.resize(size)
            position = self.qSettings.value("MainWindow/Position",QtCore.QVariant(QtCore.QPoint(0, 0))).toPoint()
            self.move(position)
            self.restoreState(self.qSettings.value("MainWindow/State").toByteArray())
            self.workingDir=self.qSettings.value("workingDir").toString()
        except:
            self.recentFiles=[]
         
    def writeSettings(self):
        self.qSettings = QtCore.QSettings()
        filename = QtCore.QVariant(QtCore.QString(self.projFileName)) \
                if self.projFileName is not None else QtCore.QVariant()
        self.qSettings.setValue("LastFile", filename)
        recentFiles = QtCore.QVariant(self.recentFiles) \
                if self.recentFiles else QtCore.QVariant()
        self.qSettings.setValue("RecentFiles", recentFiles)
        self.qSettings.setValue("MainWindow/Size", QtCore.QVariant(self.size()))
        self.qSettings.setValue("MainWindow/Position",
                QtCore.QVariant(self.pos()))
        self.qSettings.setValue("MainWindow/State", QtCore.QVariant(self.saveState()))
        self.qSettings.setValue("workingDir", QtCore.QVariant(self.workingDir))
            
    def createDockWidgets(self):     
        self.dockTool =ToolDock("Tool Inspector",self) #QtGui.QDockWidget("Tool Inspector",self)  
        self.dockTool.setObjectName("dockToolInspector")
        self.newProject()
        
        self.dockScript=QtGui.QDockWidget("Script Inspector", self)
        self.dockScript.setObjectName("dockScriptInspector") 
        self.dockScript.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea| QtCore.Qt.RightDockWidgetArea)
        self.scriptList=myListWidget()
        self.dockScript.setWidget(self.scriptList) 
        self.dockScript.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea| QtCore.Qt.RightDockWidgetArea)
    
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dockTool)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dockScript)
        
        self.connect(self.scriptList, QtCore.SIGNAL("itemDoubleClicked(QListWidgetItem*)"),self.clickedScriptList)
     
    def createMenu(self):
    ## FILE MENU   
        iconNew= self.currentDir+"/Icons/filenew.png"
        iconOpen= self.currentDir+"/Icons/fileopen.png"
        iconSave= self.currentDir+"/Icons/filesave.png"
        iconSaveAs= self.currentDir+"/Icons/filesaveAs.png"
        iconQuit= self.currentDir+"/Icons/filequit.png"
        
        newProjectAct = self.createAction("&New Project", self.newProject,QtGui.QKeySequence.New,iconNew)
        openProjectAct = self.createAction("&Open Project", self.openProjectDlg,QtGui.QKeySequence.Open,iconOpen)   
        saveProjectAct = self.createAction("Save Project", self.saveProject,QtGui.QKeySequence.Save,iconSave)
        saveProjectAsAct = self.createAction("Save Project As", self.saveProjectAs,QtGui.QKeySequence.SaveAs,iconSaveAs)
        projInfoAct = self.createAction("Project Info", self.projInfo)
        saveFigureAct = self.createAction("Save Figure ", self.saveFigure) 
        saveCurLaneAct= self.createAction("Save Current Lane", self.saveCurLane)  
        quitAct = self.createAction("Close", self.close,"Ctrl+Q", iconQuit)
        self.fileMenuActions= (newProjectAct,openProjectAct,saveProjectAct,saveProjectAsAct,saveCurLaneAct,saveFigureAct,
                                            projInfoAct,None,quitAct)
        
        self.fileMenu = self.menuBar().addMenu("&File")
    #    self.connect(self.fileMenu, QtCore.SIGNAL("aboutToShow()"),self.updateFileMenu)
        self.addActions(self.fileMenu, self.fileMenuActions[:2])
        
        self.recentFilesMenu = self.fileMenu.addMenu("Recent Files")
        self.addActions(self.recentFilesMenu,(None,None))
        self.addActions(self.fileMenu, self.fileMenuActions[2:])
        
    ### EDIT MENU  
        iconUndo= self.currentDir+"/Icons/EditUndo.png"
        editUndo = self.createAction("&Undo", self.undo, "Ctrl+Z", iconUndo)
        #editRedo = self.createAction("&Redo", self.redo,shortcut="Ctrl+Y", tip="Redo")
        editLinePropAct = self.createAction("Line Properties", self.editLineProps)
        editFigSetAct = self.createAction("Figure Setting ", self.editFigSet)
     
        editDrawSatdAction = self.createAction("Draw Saturated Points",self.drawSatd)#, None,None,None, True, "toggled(bool)")
        editDrawSelected = self.createAction("Draw Selected Area", self.drawSelectedArea)#,None,None,None, True, "toggled(bool)")
        editDrawDefault = self.createAction("Draw Default", self.drawFigure)#,None,None,None, True, "toggled(bool)")
          
        editMenuActs=(editUndo,editLinePropAct,editFigSetAct,None,editDrawSatdAction,editDrawSelected,editDrawDefault)    
        self.editMenu = self.menuBar().addMenu("&Edit")
        self.addActions(self.editMenu,editMenuActs)
    #### TOOLS MENU#####
        toolRoiAct = self.createAction("Region of Interest", self.toolActions)
        toolSmoothEnhanceAct = self.createAction("Smoothing", self.toolActions,)
        toolBaselineAct = self.createAction("Baseline Adjustment", self.toolActions)
        toolSignalAlignmentAct = self.createAction("Signal Alignment", self.toolActions)
        toolSignalDecayAct = self.createAction("Signal Decay Correction", self.toolActions)
        toolMobilityShiftAct = self.createAction("Mobility Shift", self.toolActions)
        toolApplyAllAct = self.createAction("Apply All Tools", self.toolActions)
    
        toolsMenuActs=(toolRoiAct, toolSmoothEnhanceAct,toolBaselineAct, toolSignalDecayAct,toolMobilityShiftAct,
                       toolSignalAlignmentAct,None,toolApplyAllAct)
        
        self.toolsMenu = self.menuBar().addMenu("&Tools")
        self.addActions(self.toolsMenu, toolsMenuActs)
   
### SEQUENCE MENU
        seqAlignAct = self.createAction("Sequence Alignment", self.toolActions)
        reactivityAct=self.createAction("Reactivity", self.toolActions)
        viewReportAct = self.createAction("View Report", self.viewReport) 
       
        seqAlignRefAct = self.createAction("Sequence Alignment by Reference", self.toolActions) 
        reactAlignRefAct = self.createAction("Reactivity by Reference", self.toolActions)
        applyAllSeqAct = self.createAction("Automated Analysis by Reference", self.toolActions)
    
        seqMenuActs=(seqAlignAct,reactivityAct,viewReportAct,None,seqAlignRefAct,reactAlignRefAct,applyAllSeqAct)
        self.seqMenu = self.menuBar().addMenu("&Sequence")
        self.addActions(self.seqMenu, seqMenuActs)
         
      #  referenceMenu = self.seqMenu.addMenu("Analyze By Reference")
      #  self.addActions(referenceMenu,(sigAlignRefAct,scaleRefAct,seqAlignRefAct))
     
### EXTRAS        
        toolsScaleAct = self.createAction("Scale", self.toolActions)
        toolsSwapAct = self.createAction("Channel Swap", self.toolActions)
        toolsManualSignalAct = self.createAction("Manual Signal Alignment", self.toolActions)
        toolsVariousToolsAct = self.createAction("Some Useful Functions", self.toolActions)
        
        openShapeFinderAct = self.createAction("Open ShapeFinder File", self.toolActions)
        openAbifFileAct = self.createAction("Open ABIF File", self.toolActions)
        openFileSeqAct = self.createAction("Open Sequence File", self.toolActions)
        
         
        optionaToolMenuActs=(toolsScaleAct,toolsSwapAct,toolsManualSignalAct,toolsVariousToolsAct,None,
                             openShapeFinderAct,openAbifFileAct,openFileSeqAct)
        
        self.optionalToolsMenu = self.menuBar().addMenu("&Extras")
        self.addActions(self.optionalToolsMenu, optionaToolMenuActs) 
        
    ###HELP MENU
        helpAboutAct = self.createAction("&About PyShape",self.helpAbout)
        iconHelp= self.currentDir+"/Icons/HelpIcon.png"
        helpHelpAct = self.createAction("&Help", self.helpHelp,QtGui.QKeySequence.HelpContents,iconHelp)
        helpMenuActs=(helpAboutAct, helpHelpAct)
        
        helpMenu = self.menuBar().addMenu("&Help")
        self.addActions(helpMenu, helpMenuActs)
    #### TOOLBAR
       
        
        fileToolbar = self.addToolBar("File")
        fileToolbar.setObjectName("FileToolBar")
        self.addActions(fileToolbar, (newProjectAct,openProjectAct,saveProjectAct,saveProjectAsAct))
        
        editToolbar = self.addToolBar("Edit")
        editToolbar.setObjectName("EditToolBar")
        self.addActions(editToolbar, (editUndo,))
     
        settingToolbar = self.addToolBar("Setting")
        settingToolbar.setObjectName("SettingToolBar")
        settingToolbar.addWidget(self.mainTopWidget)
        
        helpToolbar = self.addToolBar("Help")
        helpToolbar.setObjectName("HelpToolBar")
        self.addActions(helpToolbar, (helpHelpAct,))
        
        #self.toolBar=Qt.QToolBar(self)
        self.toolBar = self.addToolBar("WhatsThis")
        self.toolBar.setObjectName("WhatsThis")
       # self.toolBar.addAction(Qt.QWhatsThis.createAction(self.toolBar))

    def createAction(self, text, slot=None, shortcut=None, icon=None,
                     tip=None, checkable=False, signal="triggered()"):
        action = QtGui.QAction(text, self)
        if icon is not None:
            action.setIcon(QtGui.QIcon(icon))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            self.connect(action, QtCore.SIGNAL(signal), slot)
        if checkable:
            action.setCheckable(True)
        return action
    def addActions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)
            
    def updateFileMenu(self):
        self.fileMenu.clear()
        self.addActions(self.fileMenu, self.fileMenuActions[:2])
        self.recentFilesMenu = self.fileMenu.addMenu("Open Recent")
        
        if self.recentFiles:
            for i, fname in enumerate(self.recentFiles):
                action = QtGui.QAction(QtGui.QIcon(":/icon.png"), "&%d %s" % (
                        i + 1, QtCore.QFileInfo(fname).fileName()), self)
                action.setData(QtCore.QVariant(fname))
                self.connect(action, QtCore.SIGNAL("triggered()"),self.openProject)
                self.recentFilesMenu.addAction(action)
        self.fileMenu.addSeparator()
        self.addActions(self.fileMenu,self.fileMenuActions[2:])

    def loadInitialFile(self):
        settings = QtCore.QSettings()
        fname = unicode(settings.value("LastFile").toString())
        if fname and QtCore.QFile.exists(fname):
            self.projFileName=fname
            self.openProject(self.projFileName) 
            
    def mainWindowConnect(self):
        self.connect(self.mainTopWidget.spinBoxZoom,QtCore.SIGNAL("valueChanged(int)"),self.setAxesYLim)
        self.connect(self.mainTopWidget.spinBoxWidth,QtCore.SIGNAL("valueChanged(int)"),self.resizeFigure)
        self.connect(self.mainTopWidget.spinBoxHeight,QtCore.SIGNAL("valueChanged(int)"),self.resizeFigure)
        self.connect(self.mainTopWidget.checkBoxFitWindow,QtCore.SIGNAL("toggled(bool)"),self.resizeFigure)
        self.connect(self.mainTopWidget.splitComboBox, QtCore.SIGNAL("currentIndexChanged(int)"),self.applySplitCombo)
               
### MATPLOT EVENT 
        self.canvas.mpl_connect('button_press_event', self.onClick)
        self.canvas.mpl_connect('motion_notify_event', self.onMove)
        self.canvas.mpl_connect('button_release_event', self.onRelease)
        self.canvas.mpl_connect('scroll_event', self.onScrollEvent)
        self.canvas.mpl_connect('draw_event', self.onDrawEvent)
        self.canvas.mpl_connect('figure_leave_event', self.onFigureLeaveEvent)
        self.canvas.mpl_connect('figure_enter_event', self.onFigureEnterEvent)
        self.canvas.mpl_connect('axes_enter_event', self.enter_axes)
        self.canvas.mpl_connect('axes_leave_event', self.leave_axes)
     
    def enter_axes(self,event):
        self.isMouseOnAxes=True  
    def leave_axes(self,event):
        self.isMouseOnAxes=False
    def onFigureEnterEvent(self,event):
        self.isMouseOnFigure=True  
    def onFigureLeaveEvent(self,event):
        self.isMouseOnFigure=False
    def onScrollEvent(self,event):
        self.scrollArea.horizontalScrollBar().setValue(int(self.scrollArea.horizontalScrollBar().value() + event.step*self.scrollArea.horizontalScrollBar().pageStep()/4))   
    def resizeEvent(self, event):
        self.resizeFigure()          
    def variables(self):
        self.workingDir=QtCore.QDir.homePath()
        self.eventKey=None
        self.dDrawData=DData()
        self.dProject=DProjectNew()
        self.dProjRef=DProjectNew()
        self.dVar=DVar(chKeysRS)
        self.dVarDefault=DVar(self.dProject['chKeyRS'])
        self.intervalData=[]
        self.projFileName=None
        self.curScript=''
        self.chAxes={}
        self.dirty=False 
        self.isClickedApply=False
        self.drawReactivityType=0
        self.font = QtGui.QFont("Courier", 11) 
        self.font.setFixedPitch(True)  
        
        self.canvasWidth=1000
        self.canvasHeigth=550
    ### Control Signals      
        self.isArrowSelectedRX=False
        self.isArrowSelectedBG=False
        self.isArrowSelected0=False
        self.isArrowSelected1=False
        self.isArrowSelectedR=False
        self.isArrowSelectedS=False
        self.clickedXR=None
        self.clickedXS=None
        
        self.clickedPeakInd=0
        self.isSequenceAlignment=False
        self.lastScript=''
      
        self.maxLen=0
        self.axesSeq=None
        
        self.mouseClickX=0
        self.mouseMoveX=0
        self.mouseReleaseX=0
        self.mouseDragRight=True
        self.isMouseClick=False
        self.isRectDrawed=False
        
    def createProgressBar(self):
        self.progressBar = QtGui.QProgressBar(self.mainFrame)
        self.progressBar.setMaximum(100)
        self.progressBar.setFixedWidth(200)
        self.labelXY=QtGui.QLabel('X,Y')
        self.statusBar().addPermanentWidget(self.labelXY)
        self.statusBar().addPermanentWidget(self.progressBar)
        self.timer = QtCore.QTimer(self)
       
        self.connect(self.timer, QtCore.SIGNAL('timeout()'), self.advanceProgressBar)
              
    def advanceProgressBar(self):
        if self.progressBar.value()==100:
            self.timer.stop()
            self.progressBar.setValue(0)
        else:
            self.progressBar.setValue(self.progressBar.value()+5)
            if self.progressBar.value()>=80:
                self.progressBar.setValue(80)
   
    def onClick(self, event):
        if event.inaxes is None: return
        x=int(event.xdata)
        self.mouseClickX=x
        self.isMouseClick=True
        
        for ax, rect in zip(self.fig.get_axes(), self.spanRect):
            rect.set_width(0)   
            rect.set_x(self.mouseClickX)   
            ax.draw_artist(rect)
            
        #   if self.isClickedApply==False: return
        
        if  self.dlg.name=="Sequence Alignment": #or self.lastScript=="Align and Integrate":
            if event.inaxes==self.axesSeq:               
                self.dlg.dProjOut,self.peakInd,self.conFromBGToRX,self.conFromSeqToBG=clickedSeqAlign(x,self.dlg.dProjOut,self.eventKey,self.conFromBGToRX,self.conFromSeqToBG,self.chAxes)
                self.dlg.applyFastSeqAlign()   
                self.updateSeqAxes(self.dlg.dProjOut)
                self.dDrawData=deepcopy(self.dlg.dProjOut)      
            elif self.eventKey==QtCore.Qt.Key_Shift and event.inaxes==self.chAxes['RX']:
                self.clickedPeakInd=findClickedInd(x,self.dlg.dProjOut['dPeakRX']['pos'])
                self.isArrowSelectedRX=True
            elif self.eventKey==QtCore.Qt.Key_Shift and event.inaxes==self.chAxes['BG']:
                self.clickedPeakInd=findClickedInd(x,self.dlg.dProjOut['dPeakBG']['pos'])
                self.isArrowSelectedBG=True
                
        elif  self.dVar['flag']['isPeakLinkRefModify']:
            if self.eventKey==QtCore.Qt.Key_Shift and event.inaxes==self.chAxes['BG']:
                self.clickedPeakInd=findClickedInd(x,self.dlg.dProjOut['dPeakRX']['pos'])
                self.isArrowSelectedRX=True
            elif self.eventKey==QtCore.Qt.Key_Shift and event.inaxes==self.chAxes['BGS1']:
                self.clickedPeakInd=findClickedInd(x,self.dlg.dProjOut['dPeakBG']['pos'])
                self.isArrowSelectedBG=True
                
        elif  self.dVar['flag']['isPeakMatchModify']:
            if event.inaxes==self.axesR:
                self.clickedPeakInd=findClickedInd(x,self.dlg.linkXR)
            elif event.inaxes==self.axesS:
                self.clickedPeakInd=findClickedInd(x,self.dlg.linkXS)
            else:
                return True
            if self.eventKey==QtCore.Qt.Key_Shift and event.inaxes==self.axesR:
                self.isArrowSelectedR=True
            if self.eventKey==QtCore.Qt.Key_Shift and event.inaxes==self.axesS:
                self.isArrowSelectedS=True
            if self.eventKey== QtCore.Qt.Key_D:
                self.dlg.linkXR=np.delete(self.dlg.linkXR, self.clickedPeakInd)
                self.dlg.linkXS=np.delete(self.dlg.linkXS, self.clickedPeakInd)
                self.conFromRtoS[self.clickedPeakInd].remove()
                del  self.conFromRtoS[self.clickedPeakInd]
                self.canvas.draw()
            if self.eventKey== QtCore.Qt.Key_A:
                if event.inaxes==self.axesR:
                    self.clickedXR=x
                if event.inaxes==self.axesS:
                    self.clickedXS=x          
                if self.clickedXR!=None and self.clickedXS!=None: 
                    self.clickedPeakIndR=findClickedInd(self.clickedXR,self.dlg.linkXR)
                    self.clickedPeakIndS=findClickedInd(self.clickedXS,self.dlg.linkXS)
                    if self.clickedPeakIndR == self.clickedPeakIndS:
                        self.dlg.linkXR=np.insert(self.dlg.linkXR, self.clickedPeakInd,self.clickedXR)
                        self.dlg.linkXS=np.insert(self.dlg.linkXS, self.clickedPeakInd,self.clickedXS)
                        xyB=(self.clickedXR, self.dlg.dataR[self.clickedXR])
                        xyA=(self.clickedXS, self.dlg.dataS[self.clickedXS])
                        con = ConnectionPatch(xyA,xyB,coordsA="data",coordsB="data",axesA=self.axesS, axesB=self.axesR,
                                              arrowstyle="<|-|>",ec='0.3')
                        self.conFromRtoS.insert(self.clickedPeakInd,con)
                        self.axesS.add_artist(con)
                        self.canvas.draw()
                        self.clickedXR,self.clickedXS=None, None
                    
        elif self.dlg.name=="Region of Interest":
            if event.inaxes==self.chAxes['RX'] or event.inaxes==self.chAxes['RXS1']: 
                if self.eventKey==QtCore.Qt.Key_F: 
                    self.dlg.spinBoxPlusFrom.setValue(x)
                    self.clickedApply()
                if self.eventKey==QtCore.Qt.Key_T:
                    self.dlg.spinBoxPlusTo.setValue(x)
                    self.clickedApply()
            if event.inaxes==self.chAxes['BG'] or event.inaxes==self.chAxes['BGS1']: 
                if self.eventKey==QtCore.Qt.Key_F: 
                    self.dlg.spinBoxMinusFrom.setValue(x)
                    self.clickedApply()
                if self.eventKey==QtCore.Qt.Key_T:
                    self.dlg.spinBoxMinusTo.setValue(x)
                    self.clickedApply()
        elif self.dlg.name=="Report":
            self.clickedPeakInd=findClickedInd(x,self.dlg.dReport['posSeq'])
            self.dlg.table.selectRow(self.clickedPeakInd)
              
    def onMove(self, event):  
        if event.inaxes is None: return
        self.mouseX=int(event.xdata)
        self.mouseMoveX=int(event.xdata)
        text='X:'+str(np.round(event.xdata,2))+', Y:'+str(np.round(event.ydata,2))
        self.labelXY.setText(text)
        
        self.canvas.restore_region(self.background)
            
        for ax, line in zip(self.fig.get_axes(), self.verticalLines):
            line.set_xdata(event.xdata)
            ax.draw_artist(line)
        if self.isMouseClick and self.eventKey!=QtCore.Qt.Key_Shift:
            for ax, rect in zip(self.fig.get_axes(), self.spanRect):
                if self.mouseMoveX<self.mouseClickX:
                    rect.set_x(self.mouseMoveX)
                    self.mouseDragRight=False
                else:
                    self.mouseDragRight=True          
                w=np.abs(self.mouseClickX-self.mouseMoveX)
                rect.set_width(w)   
                ax.draw_artist(rect)
                if event.x<self.scrollArea.horizontalScrollBar().value():
                    self.scrollArea.horizontalScrollBar().setValue(int(self.scrollArea.horizontalScrollBar().value() - 5)) 
                elif event.x>(self.scrollArea.horizontalScrollBar().value()+self.scrollArea.horizontalScrollBar().pageStep()):
                    self.scrollArea.horizontalScrollBar().setValue(int(self.scrollArea.horizontalScrollBar().value() + 5)) 
                    
        if  self.dlg.name=="Sequence Alignment":# "Sequence Alignment":#self.dlg.title=="Align and Integrate" or self.lastScript=="Align and Integrate":
            if self.isArrowSelectedRX and event.inaxes==self.chAxes['RX']:
                self.conFromBGToRX[self.clickedPeakInd].xy2=(event.xdata,self.dlg.dProjOut['dData']['RX'][event.xdata])
                self.chAxes['BG'].draw_artist(self.conFromBGToRX[self.clickedPeakInd])
            if self.isArrowSelectedBG and event.inaxes==self.chAxes['BG']:
                self.conFromBGToRX[self.clickedPeakInd].xy1=(event.xdata,self.dlg.dProjOut['dData']['BG'][event.xdata])
                self.conFromSeqToBG[self.clickedPeakInd].xy2=(event.xdata,self.dlg.dProjOut['dData']['BG'][event.xdata])
                self.chAxes['BG'].draw_artist(self.conFromBGToRX[self.clickedPeakInd])
                self.chAxes['BGS1'].draw_artist(self.conFromSeqToBG[self.clickedPeakInd])
        
        elif  self.dVar['flag']['isPeakLinkRefModify']:
            if self.isArrowSelectedRX and event.inaxes==self.chAxes['BG']:
                self.conRX[self.clickedPeakInd].xy1=(event.xdata,self.dlg.dProjOut['dData']['RX'][event.xdata])
                self.chAxes['BG'].draw_artist(self.conRX[self.clickedPeakInd])
            if self.isArrowSelectedBG and event.inaxes==self.chAxes['BGS1']:
                self.conBG[self.clickedPeakInd].xy1=(event.xdata,self.dlg.dProjOut['dData']['BG'][event.xdata])
                self.chAxes['BGS1'].draw_artist(self.conBG[self.clickedPeakInd])
        
        elif  self.dVar['flag']['isPeakMatchModify']:
            if self.isArrowSelectedR and event.inaxes==self.axesR:
                self.conFromRtoS[self.clickedPeakInd].xy2=(event.xdata,self.dlg.dataR[event.xdata])
                self.axesR.draw_artist(self.conFromRtoS[self.clickedPeakInd])
            if self.isArrowSelectedS and event.inaxes==self.axesS:
                self.conFromRtoS[self.clickedPeakInd].xy1=(event.xdata,self.dlg.dataS[event.xdata])
                self.axesS.draw_artist(self.conFromRtoS[self.clickedPeakInd])
        
        self.canvas.blit(self.canvas.figure.bbox)
       
    def onRelease(self,event):
        self.isMouseClick=False
        if event.inaxes is None: return
        self.eventKey=None
        self.mouseX=int(event.xdata)
        self.mouseReleaseX=int(event.xdata)
        if self.spanRect[0].get_width>3:
            for ax, rect in zip(self.fig.get_axes(), self.spanRect):   
                rect.set_visible(True)
                ax.draw_artist(rect)
            self.canvas.draw()
            
        if self.dlg.name=="Sequence Alignment": #"Sequence Alignment":
            if self.isArrowSelectedRX:
                if event.inaxes==self.chAxes['RX']:
                    argmax=argmax3(self.dlg.dProjOut['dData']['RX'][self.mouseX-1],self.dlg.dProjOut['dData']['RX'][self.mouseX],self.dlg.dProjOut['dData']['RX'][self.mouseX+1])
                    self.mouseX=self.mouseX-1+argmax
                    self.conFromBGToRX[self.clickedPeakInd].xy2=(self.mouseX,self.dlg.dProjOut['dData']['RX'][self.mouseX])
                    self.dlg.dProjOut['dPeakRX']['pos'][self.clickedPeakInd]=self.mouseX
                    self.dlg.dProjOut['dPeakRX']['amp'][self.clickedPeakInd]=self.dlg.dProjOut['dData']['RX'][self.mouseX]
                else:
                    self.conFromBGToRX[self.clickedPeakInd].xy2=(self.dlg.dProjOut['dPeakRX']['pos'][self.clickedPeakInd],self.dlg.dProjOut['dPeakRX']['amp'][self.clickedPeakInd])
                self.dDrawData=deepcopy(self.dlg.dProjOut)
                self.canvas.draw()
                self.isArrowSelectedRX=False
            if self.isArrowSelectedBG:
                if event.inaxes==self.chAxes['BG']:
                    argmax=argmax3(self.dlg.dProjOut['dData']['BG'][self.mouseX-1],self.dlg.dProjOut['dData']['BG'][self.mouseX],self.dlg.dProjOut['dData']['BG'][self.mouseX+1])
                    self.mouseX=self.mouseX-1+argmax
                    self.conFromBGToRX[self.clickedPeakInd].xy1=(self.mouseX,self.dlg.dProjOut['dData']['BG'][self.mouseX])
                    self.conFromSeqToBG[self.clickedPeakInd].xy2=(self.mouseX,self.dlg.dProjOut['dData']['BG'][self.mouseX])
                    self.dlg.dProjOut['dPeakBG']['pos'][self.clickedPeakInd]=self.mouseX
                    self.dlg.dProjOut['dPeakBG']['amp'][self.clickedPeakInd]=self.dlg.dProjOut['dData']['BG'][self.mouseX]  
                else:
                    self.conFromBGToRX[self.clickedPeakInd].xy1=(self.dlg.dProjOut['dPeakBG']['pos'][self.clickedPeakInd],self.dlg.dProjOut['dPeakBG']['amp'][self.clickedPeakInd])        
                self.dDrawData=deepcopy(self.dlg.dProjOut)
                self.canvas.draw()
                self.isArrowSelectedBG=False
        
        if self.dVar['flag']['isPeakLinkRefModify']: #"Sequence Alignment":
            if self.isArrowSelectedRX:
                if event.inaxes==self.chAxes['BG']:
                    self.conRX[self.clickedPeakInd].xy1=(self.mouseX,self.dlg.dProjOut['dData']['RX'][self.mouseX])
                    self.dlg.dProjOut['dPeakRX']['pos'][self.clickedPeakInd]=self.mouseX
                    self.dlg.dProjOut['dPeakRX']['amp'][self.clickedPeakInd]=self.dlg.dProjOut['dData']['RX'][self.mouseX]
                else:
                    self.conRX[self.clickedPeakInd].xy1=(self.dlg.dProjOut['dPeakRX']['pos'][self.clickedPeakInd],self.dlg.dProjOut['dPeakRX']['amp'][self.clickedPeakInd])
                self.dDrawData=deepcopy(self.dlg.dProjOut)
                self.canvas.draw()
                self.isArrowSelectedRX=False
            if self.isArrowSelectedBG:
                if event.inaxes==self.chAxes['BGS1']:
                    self.conBG[self.clickedPeakInd].xy1=(self.mouseX,self.dlg.dProjOut['dData']['BG'][self.mouseX])
                    self.dlg.dProjOut['dPeakBG']['pos'][self.clickedPeakInd]=self.mouseX
                    self.dlg.dProjOut['dPeakBG']['amp'][self.clickedPeakInd]=self.dlg.dProjOut['dData']['BG'][self.mouseX]  
                else:
                    self.conBG[self.clickedPeakInd].xy1=(self.dlg.dProjOut['dPeakBG']['pos'][self.clickedPeakInd],self.dlg.dProjOut['dPeakBG']['amp'][self.clickedPeakInd])
                self.dDrawData=deepcopy(self.dlg.dProjOut)
                self.canvas.draw()
                self.isArrowSelectedBG=False
           
        if  self.dVar['flag']['isPeakMatchModify']:
            if self.isArrowSelectedR and event.inaxes==self.axesR:
                self.conFromRtoS[self.clickedPeakInd].xy2=(self.mouseX,self.dlg.dataR[self.mouseX])
                self.dlg.linkXR[self.clickedPeakInd]=self.mouseX
                self.canvas.draw()
                self.isArrowSelectedR=False
            if self.isArrowSelectedS and event.inaxes==self.axesS:
                self.conFromRtoS[self.clickedPeakInd].xy1=(self.mouseX,self.dlg.dataS[self.mouseX])
                self.dlg.linkXS[self.clickedPeakInd]=self.mouseX
                self.canvas.draw()
                self.isArrowSelectedS=False
                     
    def onDrawEvent(self,event):
        self.background = self.canvas.copy_from_bbox(self.canvas.figure.bbox)
            
    def keyPressEvent(self, event):
        self.eventKey=event.key()
        self.statusBar().showMessage("The key "+ event.text()+" pressed")
        
    def keyReleaseEvent(self, event):
#        if self.eventKey== QtCore.Qt.Key_A and self.dVar['flag']['isPeakMatchModify']:
#            if self.clickedXR!=None and self.clickedXS!=None:   
#                self.dlg.linkXR=np.insert(self.dlg.linkXR, self.clickedPeakInd,self.clickedXR)
#                self.dlg.linkXS=np.insert(self.dlg.linkXS, self.clickedPeakInd,self.clickedXS)
#                xyB=(self.clickedXR, self.dlg.dataR[self.clickedXR])
#                xyA=(self.clickedXS, self.dlg.dataS[self.clickedXS])
#                con = ConnectionPatch(xyA,xyB,coordsA="data",coordsB="data",axesA=self.axesS, axesB=self.axesR,
#                                      arrowstyle="<|-|>",ec='0.3')
#                self.conFromRtoS.insert(self.clickedPeakInd,con)
#                self.axesS.add_artist(con)
#                self.canvas.draw()
#        self.clickedXR,self.clickedXS=None, None
#        self.statusBar().showMessage("The Key Released")

        self.eventKey=None 
            
######  FILE FUNCTIONS #####
    def applyNewProject(self):
        if self.dlg.isApplied:
            self.dVar=DVar(self.dlg.dProject['chKeyRS'])
            self.dDrawData=deepcopy(self.dlg.dProject)
            self.drawFigure()
            self.dlg.buttonBox.doneButton.setEnabled(True)
            self.drawSatd()   
    def doneNewProject(self):
        self.dProject=self.dlg.dProject.copy()
        self.dProjRef=self.dlg.dProjRef.copy()
        self.projFileName=self.dProject['fName']
        self.setOpenProject()
        self.addScriptList()
        self.intervalData=[]
        self.intervalData.append(self.dProject.copy())
        self.saveProject()
        self.nextStep(self.dlg.name)        
                      
    def newProject0(self):
        self.dlg=DlgNewProject0(self.dlg.dProject)
        self.connect(self.dlg.buttonBox.nextButton,QtCore.SIGNAL("clicked()"),self.newProject1)
        self.dockTool.setWidget(self.dlg)  
    def newProject1(self):
        if self.dlg.isApplied:
            self.dlg=DlgNewProject1(self.dlg.dProject)
            self.connect(self.dlg.buttonBox.nextButton,QtCore.SIGNAL("clicked()"),self.newProject2)
            self.connect(self.dlg.buttonBox.backButton,QtCore.SIGNAL("clicked()"),self.newProject0)
            self.dockTool.setWidget(self.dlg) 
    def newProject2(self):
        if self.dlg.isApplied:
            self.dlg=DlgNewProject2(self.dlg.dProject)
            self.connect(self.dlg.buttonBox.nextButton,QtCore.SIGNAL("clicked()"),self.applyNewProject)
            self.connect(self.dlg.buttonBox.backButton,QtCore.SIGNAL("clicked()"),self.newProject1)
            self.connect(self.dlg.buttonBox.doneButton,QtCore.SIGNAL("clicked()"),self.doneNewProject)
            self.dockTool.setWidget(self.dlg) 

    def newProject(self):
        self.checkClickedApply()
        if not self.okToContinue():
            return
        self.dlg=DlgNewProject0(DProjectNew())
        self.newProject0()
  
    def setOpenProject(self):
        self.scriptList.clear()
        self.scriptList.addItems(self.dProject['scriptList']) 
        self.setWindowTitle(self.windowTitle+' - '+self.dProject['name'])
        self.setLineColor()  
        self.addRecentFile(self.projFileName)
        
### OPEN PROJECT
    def openProjectDlg(self):
        self.checkClickedApply()
        if self.okToContinue(): 
            self.projFileName=QtGui.QFileDialog.getOpenFileName(self,"Select a file",self.workingDir,("QuShape project file (*.qushape *.pyshape *.txt *.fsa )"))
            if not self.projFileName.isEmpty():
                self.projFileName=str(self.projFileName)
                try:
                    self.openProject(self.projFileName)
                except: 
                    msg="Selected files is not appropriate to open in QuShape."
                    QtGui.QMessageBox.warning(self,"QuShape - ",msg)
     
    def openProject(self,projFile=None):
        if projFile is None:
            action = self.sender()
            if isinstance(action, QtGui.QAction):
                self.projFileName = unicode(action.data().toString())
                if not self.okToContinue():
                    return
            else:
                return 
        
        self.dProject, self.dVar, self.intervalData, self.dProjRef= openProjFile(self.projFileName)
        self.workingDir=QtCore.QFileInfo(self.projFileName).path()
        
        self.dirty=False
        self.setOpenProject()
        
        self.lastScript=self.dProject['scriptList'][-1]
        if self.lastScript not in ["Reactivity","Reactivity by Reference"]:
            self.checkScriptDraw(self.lastScript,self.intervalData[-1])
        self.nextStep(self.lastScript)
        
    def addRecentFile(self, fname):
        if fname is None:
            return
        if  fname in self.recentFiles:
            self.recentFiles.removeAll(fname)
            self.recentFiles.prepend(QtCore.QString(fname))
        else:
            self.recentFiles.prepend(QtCore.QString(fname))
            while self.recentFiles.count() > 9:
                self.recentFiles.takeLast()
        self.updateFileMenu()
                             
    def clickedScriptList(self):
        row = self.scriptList.currentRow()
        script=self.dProject['scriptList'][row]# str(item.text())
        self.checkScriptDraw(script,self.intervalData[row])
        
    def checkScriptDraw(self,script,interData):
        self.dVar['flag']=deepcopy(self.dVarDefault['flag'])
        if script in ['Sequence Alignment','Sequence Alignment by Reference'] :
            self.dVar['flag']['isSeqAlign']=True
            self.dVar['flag']['isDrawLine']=True  
        elif script in ["Reactivity","Reactivity by Reference"]:
            self.drawReactivityFig(interData)
            return
        self.dDrawData=deepcopy(interData)
        self.drawFigure()

    def saveProject(self):
        if self.dProject['name']=='':
            self.saveProjectAs()
            return
        self.dBase=shelve.open(str(self.projFileName))
        self.dBase['dProject']=deepcopy(self.dProject)
        self.dBase['intervalData']=deepcopy(self.intervalData)
        self.dBase['dProjRef']=deepcopy(self.dProjRef)
        self.dBase['dVar']=deepcopy(self.dVar)
        self.dBase.close()  
        self.dirty = False
        
    def saveProjectAs(self):
        fName= QtGui.QFileDialog.getSaveFileName(self,"Save As", self.dProject['dir'],'')
        if not fName.isEmpty():
            self.projFileName=str(fName)+'.qushape'
            self.dProject['fName']=self.projFileName
            self.dProject['name']=fName.split('/')[-1]
            self.setWindowTitle(self.windowTitle +' - '+self.dProject['name'])
            self.saveProject()
    def saveCurLane(self):
        fileName = QtGui.QFileDialog.getSaveFileName(self,"Save As", self.dProject['dir'], "Text Files (*.txt)")
        if not fileName.isEmpty():
            saveCurLaneAsTxt(fileName,self.dDrawData['dData'],self.dProject['chKeyRS'])
    def saveFigure(self):
        fname = QtGui.QFileDialog.getSaveFileName(self, " ",self.dProject['dir'])
        if fname:
            #self.canvas.print_figure(unicode(fname))
            self.fig.savefig(str(fname))
    def projInfo(self):
        self.dockTool.setWidget(DlgProjInfo(self.dProject))
           
    def closeEvent(self, event):
        if self.okToContinue():
            self.writeSettings()
        else:
            event.ignore()
    def okToContinue(self):
        if self.dirty:
            msg="Do you want to save the changes you made to "+str(self.dProject['name'])+' project?'
            reply = QtGui.QMessageBox.question(self, "PyShape - Unsaved Changes",msg,
                            QtGui.QMessageBox.Yes|QtGui.QMessageBox.No|QtGui.QMessageBox.Cancel)
            if reply == QtGui.QMessageBox.Cancel:
                return False
            elif reply == QtGui.QMessageBox.Yes:
                self.saveProject()
        return True
            
##### EDIT FUNCTIONS####   
    def undo(self):
        row = self.scriptList.count()-1
        if row==0:
            return True 
        else:
            self.scriptList.takeItem(row)
            del self.dProject['scriptList'][-1]
            del self.intervalData[-1]
            self.dProject=deepcopy(self.intervalData[-1])
            self.lastScript=self.dProject['scriptList'][-1]
            self.checkScriptDraw(self.lastScript,self.intervalData[-1])
            self.nextStep(self.lastScript)    
    
##### TOOLS  FUNCTIONS #####
    def checkClickedApply(self):
        if self.isClickedApply:
            msg="You have applied a tool.Do you want to save the changes you made"
            reply = QtGui.QMessageBox.question(self,"QuShape - Unsaved Changes",msg,
                            QtGui.QMessageBox.Yes|QtGui.QMessageBox.No) #|QtGui.QMessageBox.Cancel)
            if reply == QtGui.QMessageBox.No:
                self.isClickedApply=False
                self.dDrawData=deepcopy(self.dProject)
                self.drawFigure()
            elif reply == QtGui.QMessageBox.Yes:
                self.clickedDone(next=False)
 
    def clickedApply(self):
        self.timer.start(1000)
        self.statusBar().showMessage( "Applying...")
        self.dlg.apply()
        if self.dlg.isToolApplied:
            self.dDrawData=deepcopy(self.dlg.dProjOut)
         #   self.defineDrawType(self.dlg)
            self.drawDlgApply()
            self.dlg.buttonBox.doneButton.setEnabled(True)
            self.dlg.buttonBox.doneButton.setDefault(True)
        self.progressBar.setValue(100)
        self.statusBar().showMessage( "Applied")
        self.dVar['flag']['isPeakMatchModify']=False
        self.dVar['flag']['isPeakLinkRefModify']=False
        
    def defineDrawType(self,dlg):
        if dlg.name=='Signal Alignment':
            self.mainTopWidget.splitComboBox.setCurrentIndex(1)
        elif dlg.name=='Mobility Shift':
            self.mainTopWidget.splitComboBox.setCurrentIndex(3)
        else:  
   #     elif dlg.name in ['Sequence Alignment','Sequence Alignment by Reference']:
            self.mainTopWidget.splitComboBox.setCurrentIndex(0)           
#        else:
#            self.mainTopWidget.splitComboBox.setCurrentIndex(0)
   
    def drawDlgApply(self): 
        self.dVar['flag']['isDrawStad']=False
        self.dVar['flag']['isSeqAlign']=False
        self.dVar['flag']['isDrawLine']=False
        self.dVar['flag']['isDrawGauss']=False
        if self.dlg.name=="Reactivity":
            self.drawReactivityFigures()
        elif self.dlg.name=="Reactivity by Reference":
            self.drawReactivityFigures()
        elif self.dlg.name=="Sequence Alignment":
            self.dVar['flag']['isSeqAlign']=True
            self.dVar['flag']['isDrawLine']=True
            self.drawFigure()   
        elif self.dlg.name=="Sequence Alignment by Reference" or self.dlg.name=="Automated by Reference" :
            self.dVar['flag']['isSeqAlign']=True
            self.dVar['flag']['isDrawLine']=True
            self.drawFigure()  
            self.drawRefData(self.dlg.dProjRef)
            
        elif self.dlg.name=="PeakLinkRef":
            self.dVar['flag']['isSeqAlign']=False
            self.dVar['flag']['isDrawLine']=False
            self.drawFigure()   
        elif self.dlg.name=="Read Sequence File":
            return True
        elif self.dlg.name=="Read ShapeFinder Files":
            self.drawFigure()
        elif self.dlg.name=="Region of Interest":
            self.drawROISpan()
        elif self.dlg.name=="Open ABIF File":
            self.dVar['flag']['isDrawStad']=True
            self.drawFigure()
        else:   
            self.drawFigure()
                 
    def clickedDone(self,next=True):
        if self.dlg.name=="Open ABIF File":
            return True
        elif self.dlg.name=="Region of Interest":
            self.dlg.done()
            self.dDrawData=deepcopy(self.dlg.dProjOut)
            self.drawFigure()  
        elif self.dlg.name=="Sequence Alignment by Reference":
            self.dProjRef=deepcopy(self.dlg.dProjRef)
            self.dVar['isDoneSeqAlignRef']=True
            self.dVar['isDoneSeqAlign']=True
        elif self.dlg.name=="Reactivity by Reference" or self.dlg.name=="Reactivity" or self.dlg.name=="Automated by Reference":
            self.dProjRef=deepcopy(self.dlg.dProjRef)
            self.dVar['isDoneReactivity']=True
     
        self.dProject=deepcopy(self.dlg.dProjOut)
        self.intervalData.append(deepcopy(self.dProject))
        self.addScriptList()
        self.isClickedApply=False 
         
        if self.dlg.name=="Sequence Alignment":
            self.dVar['isDoneSeqAlign']=True
        if next:
            self.nextStep(self.dlg.name)
            
    def clickedSkip(self):
        self.drawData=deepcopy(self.dProject)
        self.drawFigure()
        self.isClickedApply=False 
        self.nextStep(self.dlg.name)
         
    def nextStep(self,script):
        if script=='New Project':
            self.curScript='Region of Interest'
        elif script=='Region of Interest':
            self.curScript='Smoothing'
        elif script=='Smooth':
            self.curScript='Mobility Shift'
        elif script=='Mobility Shift':
            self.curScript='Baseline Adjustment'
        elif script=='Baseline Adjustment':
            self.curScript='Signal Decay Correction'
        elif script=='Signal Decay Correction':
            self.curScript='Signal Alignment'
        elif script=='Signal Alignment' or script=='Apply All Tools':
            if self.dProject['fNameRef']=='':
                self.curScript='Sequence Alignment'
            else:
                self.curScript='Sequence Alignment by Reference'
        elif script=='Sequence Alignment':
            self.curScript='Reactivity'
        elif script=="Reactivity" or script=="Reactivity by Reference" or script=="Automated by Reference":
            self.curScript='View Report'
            self.viewReport()
            return
        elif script=="Sequence Alignment by Reference":
            self.curScript='Reactivity by Reference'
        elif script=="Peak Link by Reference":
            self.curScript='Scale by Reference'
        else:
            self.curScript=None
        self.setAction()
        
    def addScriptList(self):
        self.lastScript=str(self.dlg.name)
        self.dProject['scriptList'].append(self.lastScript)
        item=QtGui.QListWidgetItem(self.lastScript)
        self.scriptList.addItem(item)
        self.dirty=True  
                     
    def setToolDlg(self):
        self.connect(self.dlg.buttonBox.applyButton,QtCore.SIGNAL("clicked()"),self.clickedApply)
        self.connect(self.dlg.buttonBox.doneButton,QtCore.SIGNAL("clicked()"),self.clickedDone)
        self.connect(self.dlg.buttonBox.skipButton,QtCore.SIGNAL("clicked()"),self.clickedSkip)
        self.dockTool.setWidget(self.dlg)
    
    def toolActions(self):
        self.checkClickedApply()
        action=self.sender()
        self.curScript=str(action.text())
        self.setAction()
        
    def setAction(self):
        self.dVar['flag']=deepcopy(self.dVarDefault['flag'])
        if self.curScript=='Region of Interest':
            self.dlg=DlgRegionOfInterest(self.dProject,self.dProjRef) 
            self.spanROI={}
            self.rectRX=self.chAxes['RX'].axvspan(self.dlg.roi['RX'][0],self.dlg.roi['RX'][1],visible=True,facecolor='0.8')
            self.rectRXS1=self.chAxes['RXS1'].axvspan(self.dlg.roi['RX'][0],self.dlg.roi['RX'][1],visible=True,facecolor='0.8')
            self.rectBG=self.chAxes['BG'].axvspan(self.dlg.roi['BG'][0],self.dlg.roi['BG'][1],visible=True,facecolor='0.8')
            self.rectBGS1=self.chAxes['BGS1'].axvspan(self.dlg.roi['BG'][0],self.dlg.roi['BG'][1],visible=True,facecolor='0.8')
            self.drawROISpan()
        elif self.curScript=='Smoothing':
            self.dlg = DlgSmooth(self.dProject)
        elif self.curScript=='Baseline Adjustment':
            self.dlg = DlgBaseline(self.dProject)
        elif self.curScript=='Signal Decay Correction':
            self.dlg = DlgSignalDecay(self.dProject)
        elif self.curScript=='Mobility Shift':
            self.dlg =DlgMobilityShift(self.dProject)
        elif self.curScript=='Signal Alignment':
            self.dlg = DlgSignalAlign(self.dProject)
            self.connect(self.dlg.button0, QtCore.SIGNAL("clicked()"), self.drawSignalAlignModify)
        elif  self.curScript=='Apply All Tools':
            self.dlg = DlgToolsAll(self.dProject, self.dProjRef)
        elif  self.curScript=='Sequence Alignment': 
            self.mainTopWidget.spinBoxWidth.setValue(200)
            self.dlg=DlgSeqAlign(self.dProject)
            self.connect(self.dlg.checkBoxLineDraw,QtCore. SIGNAL("toggled(bool)"),self.drawDlgApply)
        elif  self.curScript=='Reactivity': 
            if self.dVar['isDoneSeqAlign']==False:
                msg="You have to apply Sequence Alignment before Reactivity "
                QtGui.QMessageBox.warning(self,"QuShape - ",msg) 
                return
                 
            self.dlg = DlgReactivity(self.dProject,self.dProjRef)
            self.connect(self.dlg.pushButton0,QtCore.SIGNAL("clicked()"),self.drawReactivityPressed)
            self.connect(self.dlg.pushButton1,QtCore.SIGNAL("clicked()"),self.drawReactivityPressed)
            self.connect(self.dlg.pushButton2,QtCore.SIGNAL("clicked()"),self.drawReactivityPressed)
            self.dlg.initialize() 
        elif  self.curScript=='Sequence Alignment by Reference': 
            self.dlg=DlgSeqAlignRef(self.dProject,self.dProjRef)
            self.connect(self.dlg.button0, QtCore.SIGNAL("clicked()"), self.drawSignalAlignModify)  
            self.connect(self.dlg.button1, QtCore.SIGNAL("clicked()"), self.drawPeakLinkRefModify)
        elif  self.curScript=='Reactivity by Reference': 
            if self.dVar['isDoneSeqAlignRef']==False:
                msg="You have to apply Sequence Alignment before Reactivity "
                QtGui.QMessageBox.warning(self,"QuShape - ",msg) 
                return
               
            self.dlg=DlgReactivityRef(self.dProject,self.dProjRef)
            self.connect(self.dlg.pushButton0,QtCore.SIGNAL("clicked()"),self.drawReactivityPressed)
            self.connect(self.dlg.pushButton1,QtCore.SIGNAL("clicked()"),self.drawReactivityPressed)
            self.connect(self.dlg.pushButton2,QtCore.SIGNAL("clicked()"),self.drawReactivityPressed)
            self.drawRefData(self.dProjRef)
            self.dlg.initialize() 
            
        elif  self.curScript=='Automated Analysis by Reference': 
            self.dlg=DlgApplyAutoRef(self.dProject,self.dProjRef)
            self.connect(self.dlg.pushButton0,QtCore.SIGNAL("clicked()"),self.drawReactivityPressed)
            self.connect(self.dlg.pushButton1,QtCore.SIGNAL("clicked()"),self.drawReactivityPressed)
            self.connect(self.dlg.pushButton2,QtCore.SIGNAL("clicked()"),self.drawReactivityPressed)
           
        elif self.curScript=='Scale':
            self.dlg = DlgScale(self.dProject)
        elif self.curScript=='Channel Swap':
            self.dlg = DlgSwap(self.dProject) 
        elif self.curScript=='Manual Signal Alignment':
            self.dlg = DlgManualSignalAlign(self.dProject)       
            self.connect(self.dlg.button0, QtCore.SIGNAL("clicked()"), self.drawSignalAlignModify)
        elif self.curScript=="Some Useful Functions":
            self.dlg = DlgVariousTools(self.dProject)
        elif self.curScript=="Open ShapeFinder File":
            self.dlg = DlgOpenShapeFinder()
        elif self.curScript=="Open ABIF File":
            self.dlg = DlgOpenABIFFile()
        elif self.curScript=="Open Sequence File":
            self.dlg = DlgOpenSeqFile()
            
        else:
            self.dlg=DlgNoTool()
        self.setToolDlg()
        self.defineDrawType(self.dlg)
        
    def viewReport(self):
        if self.dVar['isDoneReactivity']==False:
                msg="You have to apply Reactivity tools"
                QtGui.QMessageBox.warning(self,"QuShape - ",msg) 
                return
           
        self.dlg=DlgReportTable(self.dProject)
        self.dockTool.setWidget(self.dlg)
        self.dDrawData=deepcopy(self.dProject)
        self.dVar['flag']['isSeqAlign']=True
        self.dVar['flag']['isDrawLine']=True
        self.dVar['flag']['isDrawGauss']=False
        self.drawFigure()
        self.connect(self.dlg.table, QtCore.SIGNAL('itemSelectionChanged()'), self.showSelectedNucInReport)
    
    def showSelectedNucInReport(self):
        self.canvas.restore_region(self.background)
        nucPos=self.dlg.dReport['posSeq'][self.dlg.table.currentRow()] #self.dlg.table.item(curRow,1)
        for ax, rect in zip(self.fig.get_axes(), self.spanRect):
            rect.set_width(11)   
            rect.set_x(nucPos-5)   
            ax.draw_artist(rect)
            
        newScrollValue=(nucPos*self.mainTopWidget.spinBoxWidth.value()/100)-(self.scrollArea.horizontalScrollBar().pageStep()/2)
        self.scrollArea.horizontalScrollBar().setValue(newScrollValue)
        self.canvas.blit(self.canvas.figure.bbox)    
        
    def drawROISpan(self):
        self.rectRX.set_visible(False)
        self.rectRXS1.set_visible(False)
        self.rectBG.set_visible(False)
        self.rectBGS1.set_visible(False)
        self.rectRX=self.chAxes['RX'].axvspan(self.dlg.roi['RX'][0],self.dlg.roi['RX'][1],visible=True,facecolor='0.8')
        self.rectRXS1=self.chAxes['RXS1'].axvspan(self.dlg.roi['RX'][0],self.dlg.roi['RX'][1],visible=True,facecolor='0.8')
        self.rectBG=self.chAxes['BG'].axvspan(self.dlg.roi['BG'][0],self.dlg.roi['BG'][1],visible=True,facecolor='0.8')
        self.rectBGS1=self.chAxes['BGS1'].axvspan(self.dlg.roi['BG'][0],self.dlg.roi['BG'][1],visible=True,facecolor='0.8')
        self.canvas.draw()
       
    def drawSignalAlignModify(self):
        self.conFromRtoS,self.axesR,self.axesS=drawPeakLinkModifyFig(self.fig,self.dlg.dataR,self.dlg.dataS,self.dlg.linkXR,self.dlg.linkXS)
        self.dVar['flag']['isPeakMatchModify']=True
      #  self.verticalLines = createVerticalLines(self.fig.get_axes())
        self.dlg.isMatchedPeaksChanged=True
        self.canvas.draw() 
       
    def drawPeakLinkRefModify(self):
        self.mainTopWidget.splitComboBox.setCurrentIndex(0)
        self.dVar['flag']['isPeakLinkRefModify']=True
        self.dDrawData=DProjectNew()
        self.dDrawData['dData']['RX']=self.dlg.dProjRef['dData']['RX']
        self.dDrawData['dData']['BG']=self.dlg.dProjOut['dData']['RX']
        self.dDrawData['dData']['RXS1']=self.dlg.dProjRef['dData']['BG']
        self.dDrawData['dData']['BGS1']=self.dlg.dProjOut['dData']['BG']
        self.dVar['flag']['isSeqAlign']=True
        self.drawFigure()
        self.axesSeq =self.fig.add_axes([self.dFigMargin['L'],0.035,self.dFigMargin['R']-self.dFigMargin['L'],0.035])#,axisbg='#FFFFCC')
        self.updateSeqAxes(self.dlg.dProjRef)
      
        self.chAxes['RX'].legend(['RX Reference'],loc=2)
        self.chAxes['BG'].legend(['RX Sample'],loc=2)
        self.chAxes['RXS1'].legend(['BG Reference'],loc=2)
        self.chAxes['BGS1'].legend(['BG Sample'],loc=2)
        
        pos0=self.dlg.dProjOut['dPeakRX']['pos']
        amp0=self.dlg.dProjOut['dPeakRX']['amp']
        pos1=self.dlg.dProjRef['dPeakRX']['pos']
        amp1=self.dlg.dProjRef['dData']['RX'][pos1]
        ax0=self.chAxes['BG']
        ax1=self.chAxes['RX']
        self.conRX=drawMatchLines0(pos0,amp0,pos1,amp1,ax0,ax1)
        
        pos0=self.dlg.dProjOut['dPeakBG']['pos']
        amp0=self.dlg.dProjOut['dPeakBG']['amp']
        pos1=self.dlg.dProjRef['dPeakBG']['pos']
        amp1=self.dlg.dProjRef['dData']['BG'][pos1]
        ax0=self.chAxes['BGS1']
        ax1=self.chAxes['RXS1']
        self.conBG=drawMatchLines0(pos0,amp0,pos1,amp1,ax0,ax1)
        self.canvas.draw()
        
    def drawGaussFit(self,dProject): 
        keys=['RX','BG'] 
        for key in keys:
            key0=str('dPeak'+key)
            for i in range(len(dProject[key0]['pos'])):
                x=np.arange(dProject[key0]['pos'][i]-2*dProject[key0]['wid'][i],dProject[key0]['pos'][i]+2*dProject[key0]['wid'][i])
                A1=fitFuncG(x,dProject[key0]['pos'][i],dProject[key0]['amp'][i],dProject[key0]['wid'][i])
                self.chAxes[key].plot(x,A1,'k-',lw=1.5)           
        
    def drawMatchLines(self,dProject):
        self.conFromBGToRX=drawMatchLines0(dProject['dPeakBG']['pos'],dProject['dPeakBG']['amp'],dProject['dPeakRX']['pos'],dProject['dPeakRX']['amp'],self.chAxes['BG'],self.chAxes['RX'])
        self.conFromSeqToBG=drawMatchLines0(dProject['seqX'],dProject['dData']['BGS1'][dProject['seqX']],dProject['dPeakBG']['pos'],dProject['dPeakBG']['amp'],self.chAxes['BGS1'],self.chAxes['BG'])
        self.canvas.draw()
     
    def updateSeqAxes(self,dProject): 
        self.axesSeq.clear() 
        self.axesSeqText=[]
        for i in range(len(dProject['seqRNA'])):
            clr=setNucColor(dProject['seqRNA'][i])
            self.axesSeq.text(dProject['seqX'][i],0,dProject['seqRNA'][i],fontsize=8,color=clr, horizontalalignment='center')
        for i in range(len(dProject['seqX0'])):
            clr=setNucColor(dProject['seq0'][i])
            self.axesSeq.text(dProject['seqX0'][i],-1,dProject['seq0'][i],fontsize=8,color=clr, horizontalalignment='center')
       
        xticks, xlabels=[],[]
        for i in range(0,len(dProject['seqX']),10):
            xticks.append(int(dProject['seqX'][i]))
            xlabels.append(int(dProject['seqNum'][i]))
        self.axesSeq.set_xticks((xticks))
        self.axesSeq.set_xticklabels((xlabels)) 
        self.axesSeq.set_xlim(0,self.dVar['maxLen'])
        self.axesSeq.set_ylim(-1,1)
        setp(self.axesSeq.get_yticklabels(),visible=False)  
        self.canvas.draw() 
    
    def drawReactivityPressed(self):
        if str(self.sender().text())=='Data':
            self.drawReactivityType=2
        elif str(self.sender().text())=='Peak Area':
            self.drawReactivityType=1
        else:
            self.drawReactivityType=0
        self.drawReactivityFigures()
    
    def drawReactivityFigures(self):
        if self.dlg.name=='Reactivity':
            if self.drawReactivityType==2:
                self.dDrawData=deepcopy(self.dlg.dProjOut)
                self.dVar['flag']['isSeqAlign']=True
                self.dVar['flag']['isDrawLine']=True
                self.dVar['flag']['isDrawGauss']=True
                self.drawFigure()
            else:
                self.drawReactivityFig(self.dlg.dProjOut,self.dlg.radio5to3.isChecked(),self.drawReactivityType)
        if self.dlg.name=='Reactivity by Reference' or self.dlg.name=='Automated by Reference':
            if self.drawReactivityType==2:
                self.dDrawData=deepcopy(self.dlg.dProjOut)
                self.dVar['flag']['isSeqAlign']=True
                self.dVar['flag']['isDrawLine']=True
                self.drawFigure() 
                self.drawRefData(self.dlg.dProjRef)  
            else:
                self.drawReactivityRef(self.dlg.dProjOut,self.dlg.dProjRef,self.drawReactivityType)
   
    def drawReactivityRef(self,dProject,dProjRef,drawType=0):
        drawReactivityRef(self.fig,dProject,dProjRef,drawType)
        self.verticalLines=createVerticalLines(self.fig.get_axes())
        self.spanRect=createRects(self.fig.get_axes())  
        self.canvas.draw()
               
    def drawReactivityFig(self,dProject,is5to3=False,drawType=0):
        createReactivityFig(self.fig,dProject,is5to3,drawType)
        self.verticalLines=createVerticalLines(self.fig.get_axes())
        self.spanRect=createRects(self.fig.get_axes())  
        self.canvas.draw()
        
#### PLOT  FUNCTIONS            
    def drawPeaks(self,dProject):
        self.dLinePeak={}
        for key in dProject['chKeyRS']:
            key1=str('dPeak'+key)
            self.dLinePeak[key],=self.chAxes[key].plot(dProject[key1]['pos'],dProject[key1]['amp'])
            self.dLinePeak[key].set_color(str(self.dVar['lineColor'][key]))
            self.dLinePeak[key].set_visible(self.dVar['lineVisible'][key])
            self.dLinePeak[key].set_marker('s')
            self.dLinePeak[key].set_linestyle('.')
        self.setAxesXLim()
        self.canvas.draw()
        
    def drawRefData(self,refData):
        try:
            self.mainTopWidget.splitComboBox.setCurrentIndex(0)
            for key in refData['dData'].keys(): 
                factor=np.average(self.dDrawData['dData'][key])/np.average(refData['dData'][key])
                line,=self.chAxes[key].plot(refData['dData'][key]*factor)#,'0.5')
                line.set_color(str(self.dVar['lineColor'][key]))
                line.set_alpha(0.5)
            self.dVar['flag']['isDrawRef']=True
            self.setAxesXLim()
            self.canvas.draw()   
        except:
            pass
        
    def drawFigure(self):
        self.fig.clf()
        self.dFigMargin={'L':0.0,'R':1,'T':1,'B':0.01}
        if self.dVar['flag']['isSeqAlign']:
            self.dFigMargin['B']=0.07
        self.fig.subplots_adjust(self.dFigMargin['L'],self.dFigMargin['B'],self.dFigMargin['R'],self.dFigMargin['T'],0.0,0.0) 
        self.dVar['drawType']=self.mainTopWidget.splitComboBox.currentIndex()
        self.dVar['maxLen']=maxLenF(self.dDrawData['dData'])
        
        self.chAxes=createAxes(self.fig,self.dVar,self.dDrawData['dData'].keys())
        
        self.dLineData={}
        for key in self.dDrawData['dData'].keys(): 
            self.dLineData[key],=self.chAxes[key].plot(self.dDrawData['dData'][key]) 
            setp(self.chAxes[key].get_xticklabels(),visible=False) 
            setp(self.chAxes[key].get_yticklabels(),visible=False)
            
        if self.dVar['flag']['isSeqAlign']:
            self.isSequenceAlignment=True
            self.axesSeq =self.fig.add_axes([self.dFigMargin['L'],0.035,self.dFigMargin['R']-self.dFigMargin['L'],0.035])#,axisbg='#FFFFCC')
            self.updateSeqAxes(self.dDrawData)
            if self.dVar['flag']['isDrawLine']:
                self.drawMatchLines(self.dDrawData)
            if self.dVar['flag']['isDrawGauss']:
                self.drawGaussFit(self.dDrawData)  
        if self.dVar['flag']['isDrawStad']:
            self.drawSatd()
        try:
            self.dAxesYLim=findAxesYLim(self.dDrawData['dData'],self.dVar['drawType'])
        except:
            pass   
        
    ### Draw Vertical Lines  
        self.verticalLines=createVerticalLines(self.fig.get_axes())
        self.setAxesLines()
        self.setAxesYLim() 
        self.setAxesXLim()
    ### Draw  Rectangular for Span  
        self.spanRect=createRects(self.fig.get_axes())  
        self.resizeFigure()
        
    def setAxesLines(self):
        for key in self.dDrawData['dData'].keys():
            self.dLineData[key].set_color(str(self.dVar['lineColor'][key]))
            self.dLineData[key].set_visible(self.dVar['lineVisible'][key])
            self.dLineData[key].set_linewidth(self.dVar['lineWidth'][key])
            self.dLineData[key].set_marker(self.dVar['lineMarker'][key])
            self.dLineData[key].set_linestyle(self.dVar['lineStyle'][key])
    def setAxesXLim(self):
        for key in self.dDrawData['dData'].keys():
            self.chAxes[key].set_xlim(0,self.dVar['maxLen'])                             
    def setAxesYLim(self):
        for key in self.dDrawData['dData'].keys():
            y0=self.dAxesYLim[key][0]
            y1=self.dAxesYLim[key][1]/(self.mainTopWidget.spinBoxZoom.value()*0.01)
            self.chAxes[key].set_ylim(y0,y1) 
        self.canvas.draw()
   
    def drawSatd(self):    
        for i in range(len(self.dDrawData['Satd']['RX'])):
            self.chAxes['RX'].axvline(self.dDrawData['Satd']['RX'][i], alpha=0.3, color='red' )
            self.chAxes['RXS1'].axvline(self.dDrawData['Satd']['RX'][i], alpha=0.3, color='red')
        for i in range(len(self.dDrawData['Satd']['BG'])):
            self.chAxes['BG'].axvline(self.dDrawData['Satd']['BG'][i], alpha=0.3, color='red')
            self.chAxes['BGS1'].axvline(self.dDrawData['Satd']['BG'][i],alpha=0.3, color='red') 
        self.canvas.draw()  
                        
    def drawSelectedArea(self):
        if self.spanRect[0].get_width()<10:
            return
        x0=self.spanRect[0].get_x() # self.dVar['maxLen']/3
        x1=x0+self.spanRect[0].get_width() #elf.dVar['maxLen']/2
        for key in self.dDrawData['dData'].keys():
            self.chAxes[key].set_xlim(x0,x1)
        #    y0=np.min(self.dDrawData['dData'][key][x0:x1])
        #    y1=np.max(self.dDrawData['dData'][key][x0:x1])
        #    self.chAxes[key].set_ylim(y0,y1)
        if self.dVar['flag']['isSeqAlign']:
            self.axesSeq.set_xlim(x0,x1)
        self.canvas.resize(2*self.spanRect[0].get_width(),self.canvas.size().height())
        self.canvas.draw()    
           
### SPLIT CHANNELS
    def applySplitCombo(self):
        if len(self.fig.get_axes())<1:
            return True
        if self.dVar['flag']['isPeakMatchModify'] or self.dVar['flag']['isPeakLinkRefModify'] or self.dVar['flag']['isDrawRef']:
            return True
        if self.dlg.name=='Reactivity':# and self.isSequenceAlignment:
            if self.drawReactivityType==2:
                self.drawFigure()
            else:
                return
        else:
            self.drawFigure()
   
#### RESIZE FIGURE  
    def resizeFigure(self):
        self.dVar['widthP']=self.mainTopWidget.spinBoxWidth.value()
        self.dVar['heightP']=self.mainTopWidget.spinBoxHeight.value()
        h=self.scrollArea.size().height()*0.98
        self.canvasHeigth=h
        if self.mainTopWidget.checkBoxFitWindow.isChecked():
            w=self.scrollArea.size().width()*0.98
        else:
            w=self.dVar['maxLen'] * self.dVar['widthP'] * 0.01
            h=self.canvasHeigth * self.dVar['heightP'] * 0.01
        # width and height must each be below  32768
        if w>16000:
            w=16000
        self.canvas.resize(w,h)
      
### CHANNEL ATTRIBUTES
    def setLineColor(self):
        for key in self.dVar['lineColor'].keys():
            self.mainTopWidget.labelCh[key].setStyleSheet("QWidget { background: %s }" % self.dVar['lineColor'][key])       
            #self.mainTopWidget.lineEditY[key].setStyleSheet("QWidget { background: %s }" % self.dVar['lineColor'][key])
    def applyEditLineProps(self):
        self.setLineColor()
        self.dVar=self.dlgChannel.dVar.copy()
        self.setAxesLines()
        self.canvas.draw() 
        self.dirty=True
    def editLineProps(self):
        self.dlgChannel = DlgLineProps(self.dVar,self.dProject['chKeyRS'])
        self.connect(self.dlgChannel.buttonBox.button(QtGui.QDialogButtonBox.Apply),QtCore.SIGNAL("clicked()"),self.applyEditLineProps)
        self.dlgChannel.show()
    def applyFigSet(self):
        self.dlgChannel.apply()
        self.dVar=self.dlgChannel.dVar.copy()
        self.setFigureProps(self.dVar)
    def setFigureProps(self,dVar):
        self.fig.subplots_adjust(left=dVar['left'],right=dVar['right'],bottom=dVar['bottom'],top=dVar['top'])    
        self.mainTopWidget.spinBoxWidth.setValue(self.dVar['widthP'])
        self.mainTopWidget.spinBoxHeight.setValue(self.dVar['heightP'])
        self.mainTopWidget.checkBoxFitWindow.setChecked(self.dVar['isFit'])
        self.fig.set_dpi(dVar['dpi']) 
        self.resizeFigure()
    def editFigSet(self):
        self.dlgChannel = DlgFigureSet(self.dVar,self.dProject['chKeyRS'])
        self.connect(self.dlgChannel.buttonBox.button(QtGui.QDialogButtonBox.Apply),QtCore.SIGNAL("clicked()"),self.applyFigSet)
        self.dlgChannel.show()
        
##### HELP FUNCTIONS  ######
    def helpAbout(self):
        QtGui.QMessageBox.about(self, "About PyShape",msgAbout)
    def helpHelp(self):
        indexPage=QtCore.QUrl.fromLocalFile(os.getcwd()+'/Help/index.html')
        QtGui.QDesktopServices.openUrl(indexPage)
      
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    app.setOrganizationName("Week Lab")
    app.setOrganizationDomain("http://www.chem.unc.edu/rna/")
    app.setApplicationName("QuShape")
    app.setStyle(QtGui.QStyleFactory.create('Cleanlooks'))  
    iconFileName=os.getcwd()+"/Icons/qushape_logo.png"
    app.setWindowIcon(QtGui.QIcon(iconFileName))
    form = MainWindow()
    form.show()
  #  form.loadInitialFile()
    app.exec_()
