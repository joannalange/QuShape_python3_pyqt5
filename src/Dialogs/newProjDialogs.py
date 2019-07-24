from imports import QtGui,QtCore

from Functions import readShapeData,readBaseFile,DProjectNew
from myWidgets import DlgSelectFile, DlgSelectDir,hintLabel
import shelve
from copy import deepcopy

class ButtonWizard(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        
        # self.cancelButton = QtGui.QPushButton(self.tr("Cancel"))
        self.backButton = QtGui.QPushButton(self.tr("< &Back"))
        self.nextButton = QtGui.QPushButton(self.tr("Next >"))
        self.doneButton = QtGui.QPushButton(self.tr("&Done"))
     
        buttonLayout = QtGui.QHBoxLayout()
        buttonLayout.addStretch(1)
        
        # buttonLayout.addWidget(self.cancelButton)
        buttonLayout.addWidget(self.backButton)
        buttonLayout.addWidget(self.nextButton)
        buttonLayout.addWidget(self.doneButton)
    
        self.mainLayout = QtGui.QVBoxLayout()
        
        self.mainLayout.addLayout(buttonLayout)
        self.setLayout(self.mainLayout)

class DlgNewProject0(QtGui.QDialog):
    def __init__(self, dProject,parent=None):
        QtGui.QDialog.__init__(self, parent)
        
        self.dProject=dProject
        self.isApplied=False
        self.title = QtGui.QLabel(self.tr("<center><b>CREATE NEW PROJECT - STEP 1 OF 3</b></center>"))
        self.name='New Project'
    
        label0=QtGui.QLabel('Project Name')
        self.lineEdit0=QtGui.QLineEdit()
        self.lineEdit0.setText(self.dProject['name'])
        
        self.selectDir0=DlgSelectDir('Directory')
        self.selectDir0.lineEdit0.setText(self.dProject['dir'])
        
        self.radioButton0=QtGui.QRadioButton('One Sequencing Channel')
        self.radioButton1=QtGui.QRadioButton('Two Sequencing Channels ')
        
        if self.dProject['isSeq2']:
            self.radioButton1.setChecked(True)
        else:
            self.radioButton0.setChecked(True)    
        
        self.groupBox = QtGui.QGroupBox(self.tr("Choose the Project Type"))
        layout0=QtGui.QVBoxLayout()
        layout0.addWidget(self.radioButton0)
        layout0.addWidget(self.radioButton1)
        self.groupBox.setLayout(layout0)
    
        layout0=QtGui.QGridLayout() 
        layout0.addWidget(label0,1,0)
        layout0.addWidget(self.lineEdit0,1,1)
        layout0.addWidget(self.selectDir0,2,0,1,2)
        layout0.addWidget(self.groupBox,3,0,1,2)
        
        self.buttonBox=ButtonWizard() 
        self.buttonBox.backButton.setEnabled(False)
        self.buttonBox.doneButton.setEnabled(False)
        self.buttonBox.nextButton.setDefault(True)
       
        self.connect(self.buttonBox.nextButton,QtCore.SIGNAL("clicked()"),self.clickNext0)
       
        mainLayout=QtGui.QVBoxLayout()
        mainLayout.addWidget(self.title)
        mainLayout.addLayout(layout0)
        mainLayout.addStretch()
        mainLayout.addWidget(self.buttonBox)
        self.setLayout(mainLayout)
       
    def clickNext0(self):
        if self.lineEdit0.text()=='':
            QtGui.QMessageBox.warning(self,'Warning', 'Write a project Name')
        elif self.selectDir0.lineEdit0.text()=='':
            QtGui.QMessageBox.warning(self,'Warning', 'Select Project Directory')  
        else: 
            self.dProject['name']=str(self.lineEdit0.text())
            self.dProject['dir']=str(self.selectDir0.lineEdit0.text())
            self.dProject['fName']=self.dProject['dir']+'/'+self.dProject['name']+'.qushape'
            
            if self.radioButton1.isChecked():
                self.dProject['isSeq2']=True
                self.dProject['chKeyRS']=['RX', 'BG', 'RXS1', 'BGS1','RXS2','BGS2']
                self.dProject['chKeyCC']=['RX', 'RXS1','RXS2','BG', 'BGS1','BGS2']
                self.dProject['chKeyRX']=['RX', 'RXS1','RXS2']
                self.dProject['chKeyBG']=['BG', 'BGS1','BGS2']
            else:
                self.dProject['isSeq2']=False
                self.dProject['chKeyRS']=['RX', 'BG', 'RXS1', 'BGS1']
                self.dProject['chKeyCC']=['RX', 'RXS1','BG', 'BGS1']
                self.dProject['chKeyRX']=['RX', 'RXS1']
                self.dProject['chKeyBG']=['BG', 'BGS1']
            
            if QtCore.QFile(self.dProject['fName']).exists():
                reply=QtGui.QMessageBox.question(self,"QuShape",
                                                 "Saving the file will overwrite the original file on the disk.\n"
                                                "Do you really want to save?",
                                           QtGui.QMessageBox.Yes| QtGui.QMessageBox.Cancel)
                if reply==QtGui.QMessageBox.Cancel:
                    return False
                elif reply==QtGui.QMessageBox.Yes:
                    QtCore.QFile(self.dProject['fName']).remove()
            self.isApplied=True
            
 
class DlgNewProject1(QtGui.QDialog):
    def __init__(self, dProject,parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.name='New Project'
        self.title = QtGui.QLabel(self.tr("<center><b>CREATE NEW PROJECT - STEP 2 OF 3</b></center>"))
       
        self.dProject=dProject
        self.isApplied=False
      
        self.fileRead0=DlgSelectFile('(+) Reaction',"ABIF or Text File (*.ab1 *.fsa *.txt)",self.dProject['dir'])
        self.fileRead1=DlgSelectFile('(-) Reaction',"ABIF or Text File (*.ab1 *.fsa *.txt)",self.dProject['dir'])
        self.fileRead2=DlgSelectFile('Sequence',"Base Files (*.txt *.fasta *.gbk *.seq )",self.dProject['dir'])
        self.fileRead3=DlgSelectFile('Ref. Proj.',"Reference Project (*.pyshape *.qushape)",self.dProject['dir'])
        
        self.fileRead0.lineEdit0.setText(self.dProject['fNameRX'])
        self.fileRead1.lineEdit0.setText(self.dProject['fNameBG'])
        self.fileRead2.lineEdit0.setText(self.dProject['fNameSeq'])
        self.fileRead3.lineEdit0.setText(self.dProject['fNameRef'])
        
        text="HINT: Select either Sequence or Reference Project"
        self.hint = hintLabel(text)
        
        layout0 = QtGui.QVBoxLayout()
        layout0.addWidget(self.fileRead0)
        layout0.addWidget(self.fileRead1)
        layout0.addWidget(self.fileRead2)
        layout0.addWidget(self.fileRead3)
        layout0.addWidget(self.hint)
        
        self.buttonBox=ButtonWizard() 
        self.buttonBox.doneButton.setEnabled(False)
        self.buttonBox.nextButton.setDefault(True)
       
        self.connect(self.buttonBox.backButton,QtCore.SIGNAL("clicked()"),self.clickBack1)
        self.connect(self.buttonBox.nextButton,QtCore.SIGNAL("clicked()"),self.clickNext1)
        
        mainLayout=QtGui.QVBoxLayout()
        mainLayout.addWidget(self.title)
        mainLayout.addLayout(layout0)
        mainLayout.addStretch()
        mainLayout.addWidget(self.buttonBox)
        self.setLayout(mainLayout)
    
    def clickBack1(self):
        self.readFileNames()
        
    def clickNext1(self):
        if self.fileRead0.lineEdit0.text()=='':
            QtGui.QMessageBox.warning(self,'Warning', 'Select (+) Reaction File')
        elif self.fileRead1.lineEdit0.text()=='':
            QtGui.QMessageBox.warning(self,'Warning','Select (+) Reaction File')
        elif self.fileRead2.lineEdit0.text()=='' and self.fileRead3.lineEdit0.text()=='':
            QtGui.QMessageBox.warning(self,'Warning','Select Sequence or Reference File')
        else:
            self.readFileNames()
            
    def readFileNames(self):
            self.dProject['fNameRX']=str(self.fileRead0.lineEdit0.text())
            self.dProject['fNameBG']=str(self.fileRead1.lineEdit0.text())
            self.dProject['fNameSeq']=str(self.fileRead2.lineEdit0.text())
            if self.fileRead3.lineEdit0.text()!='':
                self.dProject['isRef']=True
                self.dProject['fNameRef']=str(self.fileRead3.lineEdit0.text())
            
            self.isApplied=True
    
class DlgNewProject2(QtGui.QDialog):
    def __init__(self, dProject,parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.name='New Project'
        self.title = QtGui.QLabel(self.tr("<center><b>CREATE NEW PROJECT - STEP 3 OF 3</b></center>"))
        self.dProject=dProject
        self.isApplied=False 
            
        self.label0={}
        self.comboBox0={}
        choices0=['Channel 1','Channel 2', 'Channel 3','Channel 4']
        for key in self.dProject['chKeyRS']:
            self.label0[key]=QtGui.QLabel(key)
            self.comboBox0[key]=QtGui.QComboBox()
            self.comboBox0[key].addItems(choices0)
            self.comboBox0[key].setCurrentIndex(self.dProject['chIndex'][key])
            
        choices2=['ddC','ddG', 'ddA', 'ddT']
        self.comboBox1={}
        self.comboBox1['RXS1']=QtGui.QComboBox()
        self.comboBox1['RXS1'].addItems(choices2)
        self.comboBox1['BGS1']=QtGui.QComboBox()
        self.comboBox1['BGS1'].addItems(choices2)
        
        if self.dProject['isSeq2']:
            self.comboBox1['RXS2']=QtGui.QComboBox()
            self.comboBox1['RXS2'].addItems(choices2) 
            self.comboBox1['BGS2']=QtGui.QComboBox()
            self.comboBox1['BGS2'].addItems(choices2) 
            self.comboBox1['RXS2'].setCurrentIndex(1)
            self.comboBox1['BGS2'].setCurrentIndex(1)
        
        layout1 = QtGui.QGridLayout()
        layout1.addWidget(self.label0['RX'], 0, 0)
        layout1.addWidget(self.comboBox0['RX'], 0, 1)
        layout1.addWidget(self.label0['RXS1'], 1, 0)
        layout1.addWidget(self.comboBox0['RXS1'], 1, 1)
        layout1.addWidget(self.comboBox1['RXS1'], 1, 2)
        if self.dProject['isSeq2']:
            layout1.addWidget(self.label0['RXS2'], 2, 0)
            layout1.addWidget(self.comboBox0['RXS2'], 2, 1)
            layout1.addWidget(self.comboBox1['RXS2'], 2, 2)
        
        groupBox1=QtGui.QGroupBox('Select (+) Reaction Channels')
        groupBox1.setLayout(layout1)
        
        layout2 = QtGui.QGridLayout()
        layout2.addWidget(self.label0['BG'], 0, 0)
        layout2.addWidget(self.comboBox0['BG'], 0, 1)
        layout2.addWidget(self.label0['BGS1'], 1, 0)
        layout2.addWidget(self.comboBox0['BGS1'], 1, 1)
        layout2.addWidget(self.comboBox1['BGS1'], 1, 2)
        if self.dProject['isSeq2']:
            layout2.addWidget(self.label0['BGS2'], 2, 0)
            layout2.addWidget(self.comboBox0['BGS2'], 2, 1)
            layout2.addWidget(self.comboBox1['BGS2'], 2, 2)
        
        groupBox2=QtGui.QGroupBox('Select (-) Reaction Channels')
        groupBox2.setLayout(layout2)
        
        self.buttonBox=ButtonWizard() 
        self.buttonBox.nextButton.setText('Apply')
        self.buttonBox.doneButton.setEnabled(False)
        self.buttonBox.nextButton.setDefault(True)
         
        self.connect(self.buttonBox.backButton,QtCore.SIGNAL("clicked()"),self.clickBack2)
        self.connect(self.buttonBox.nextButton,QtCore.SIGNAL("clicked()"),self.clickNext2)
        
        mainLayout=QtGui.QVBoxLayout()
        mainLayout.addWidget(self.title)
        mainLayout.addWidget(groupBox1)
        mainLayout.addWidget(groupBox2)
        mainLayout.addStretch()
        mainLayout.addWidget(self.buttonBox)
        
        self.setLayout(mainLayout)
        
        self.connect(self.comboBox0['RX'],QtCore.SIGNAL("currentIndexChanged(int)"),self.changeCombo00)
        self.connect(self.comboBox0['RXS1'],QtCore.SIGNAL("currentIndexChanged(int)"),self.changeCombo01)
        self.connect(self.comboBox1['RXS1'],QtCore.SIGNAL("currentIndexChanged(int)"),self.changeCombo10)
        if self.dProject['isSeq2']:
            self.connect(self.comboBox0['RXS2'],QtCore.SIGNAL("currentIndexChanged(int)"),self.changeCombo02)
            self.connect(self.comboBox1['RXS2'],QtCore.SIGNAL("currentIndexChanged(int)"),self.changeCombo11)
    
    def changeCombo00(self):
        self.comboBox0['BG'].setCurrentIndex(self.comboBox0['RX'].currentIndex())
    def changeCombo01(self):
        self.comboBox0['BGS1'].setCurrentIndex(self.comboBox0['RXS1'].currentIndex())
    def changeCombo02(self):
        self.comboBox0['BGS2'].setCurrentIndex(self.comboBox0['RXS2'].currentIndex())
    def changeCombo10(self):
        self.comboBox1['BGS1'].setCurrentIndex(self.comboBox1['RXS1'].currentIndex())
    def changeCombo11(self):
        self.comboBox1['BGS2'].setCurrentIndex(self.comboBox1['RXS2'].currentIndex())
        
    def clickBack2(self):
        self.isApplied=True     
           
    def clickNext2(self):
        dataRX,self.dProject['Satd']['RX'],dyesRX=readShapeData(self.dProject['fNameRX'])
        dataBG,self.dProject['Satd']['BG'],dyesBG=readShapeData(self.dProject['fNameBG'])
        if self.dProject['fNameSeq']!='':
            self.dProject['RNA']=readBaseFile(self.dProject['fNameSeq'])
        if self.dProject['fNameRef']=='':
            self.dProjRef=DProjectNew()
        else:   
            self.dBase=shelve.open(self.dProject['fNameRef'])
            self.dProjRef=self.dBase['dProject'] 
            self.dProject['RNA']= self.dProjRef['RNA']
            self.dProject['isRef']=True
            self.dBase.close()  
        for key in self.comboBox0.keys():
            ind=self.comboBox0[key].currentIndex()
            self.dProject['chIndex'][key]=ind
            if key=='RX' or key=='RXS1' or key=='RXS2':
                self.dProject['dData'][key]=dataRX[:,ind]
                self.dProject['dyeN'][key]=dyesRX[ind] #str(readerRX.getData('DyeN',ind+1)).replace(' ','')
            else: 
                self.dProject['dData'][key]=dataBG[:,ind]
                self.dProject['dyeN'][key]=dyesBG[ind] #str(readerBG.getData('DyeN',ind+1)).replace(' ','')
    
        self.dProject['ddNTP1']=str(self.comboBox1['RXS1'].currentText())
        nucs=['G','C','U','A']
        self.dProject['nuc1']=nucs[self.comboBox1['RXS1'].currentIndex()]
        if self.dProject['isSeq2']:
            self.dProject['ddNTP2']=str(self.comboBox1['RXS2'].currentText())
            self.dProject['nuc2']=nucs[self.comboBox1['RXS2'].currentIndex()]
        self.dProjOut=deepcopy(self.dProject)  
        self.isApplied=True
        
class DlgProjInfo(QtGui.QWidget):
    def __init__(self, dProject,parent=None):
        QtGui.QWidget.__init__(self, parent)
        
        self.labelTitle = QtGui.QLabel(self.tr("<center><b>PROJECT INFORMATION</b></center>"))
        self.name="ProjInfo"
        self.toolID=1
        
        self.dProject=dProject
        self.projInfo=''
        self.projInfo+='<h3 align=center>QUSHAPE PROJECT INFORMATION</h3>'
        self.projInfo+='<p><b> Project Name : </b>'+str(dProject['name'])
        self.projInfo+='<p><b> Working Directory : </b>'+str(dProject['dir'])
        self.projInfo+='<p><b> RX File: </b>'+ str(self.dProject['fNameRX'])+'</p>'
        self.projInfo+='<p><b> BG File: </b>'+ str(self.dProject['fNameBG'])+'</p>'
        self.projInfo+='<p><b> RNA File: </b>'+ str(self.dProject['fNameSeq'])+'</p>'
        self.projInfo+='<p><b> Reference File: </b>'+ str(self.dProject['fNameRef'])+'</p>'
        
        self.projInfo+='<p><b> ddNTP: </b>'+str(self.dProject['ddNTP1'])
        
        self.projInfo+='<p><b> Used Dyes: RX: </b>'+str(self.dProject['dyeN']['RX'])
        self.projInfo+='<b> BG: </b>'+str(self.dProject['dyeN']['BG'])
        self.projInfo+='<b> RXS1: </b>'+str(self.dProject['dyeN']['RXS1'])
        self.projInfo+='<b> BGS1: </b>'+str(self.dProject['dyeN']['BGS1'])
        
        self.projInfo+='<p><b> Channel Index: RX: </b>'+str(self.dProject['chIndex']['RX']+1)
        self.projInfo+='<b> BG: </b>'+str(self.dProject['chIndex']['BG']+1)
        self.projInfo+='<b> RXS1: </b>'+str(self.dProject['chIndex']['RXS1']+1)
        self.projInfo+='<b> BGS1: </b>'+str(self.dProject['chIndex']['BGS1']+1)
        
        
        self.textBrowser = QtGui.QTextBrowser()
        self.textBrowser.setHtml(self.projInfo)
        
        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(self.textBrowser)
        self.setLayout(mainLayout)
    