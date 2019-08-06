find src -name "*py" | xargs gsed -i 's/QtGui.QSpinBox/QtWidgets.QSpinBox/g'
