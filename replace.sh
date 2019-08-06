find src -name "*py" | xargs gsed -i 's/QtGui.QRadioButton/QtWidgets.QRadioButton/g'
