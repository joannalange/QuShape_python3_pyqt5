from mainWindow import *

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app.setOrganizationName("Week Lab")
    app.setOrganizationDomain("http://www.chem.unc.edu/rna/")
    app.setApplicationName("QuShape")
    app.setStyle(QtWidgets.QStyleFactory.create('Cleanlooks'))
    iconFileName = os.getcwd() + "/Icons/QuShapeIcon.png"
    app.setWindowIcon(QtGui.QIcon(iconFileName))
    form = MainWindow()
    form.show()
    app.exec_()
