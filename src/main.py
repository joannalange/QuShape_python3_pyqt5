
from PyQt4 import QtGui, QtCore
import sys, os
from mainWindow import *
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    app.setOrganizationName("Week Lab")
    app.setOrganizationDomain("http://www.chem.unc.edu/rna/")
    app.setApplicationName("QuShape")
    app.setStyle(QtGui.QStyleFactory.create('Cleanlooks'))  
    iconFileName=os.getcwd()+"/Icons/QuShapeIcon.png"
    app.setWindowIcon(QtGui.QIcon(iconFileName))
    form = MainWindow()
    form.show()
  #  form.loadInitialFile()
    app.exec_()
