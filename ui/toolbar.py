# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets, QtCore, QtGui
from .toolbar_ui import Ui_Form

class ToolBar(QtWidgets.QWidget):

    slider_changed = QtCore.pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)

        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.ui.horizontalSlider.valueChanged.connect(self.slider_changed_event)
        self.ui.horizontalSlider_2.valueChanged.connect(self.slider_changed_event)
        self.ui.horizontalSlider_3.valueChanged.connect(self.slider_changed_event)

        self.ui.lineEdit.returnPressed.connect(self.lineedit_changed)
        self.ui.lineEdit_2.returnPressed.connect(self.lineedit_changed)
        self.ui.lineEdit_3.returnPressed.connect(self.lineedit_changed)
        
    def slider_changed_event(self):
        widget = self.sender()
        if widget is self.ui.horizontalSlider:
            self.ui.lineEdit.setText( str(self.ui.horizontalSlider.value()) )
            self.slider_changed.emit()
        if widget is self.ui.horizontalSlider_2:
            self.ui.lineEdit_2.setText( str(self.ui.horizontalSlider_2.value()) )
            self.slider_changed.emit()
        if widget is self.ui.horizontalSlider_3:
            self.ui.lineEdit_3.setText( str(self.ui.horizontalSlider_3.value()) )
            self.slider_changed.emit()

    def lineedit_changed(self):
        widget = self.sender()
        if widget is self.ui.lineEdit:
            self.ui.horizontalSlider.setValue( int(self.ui.lineEdit.text()) ) 
        if widget is self.ui.lineEdit_2:
            self.ui.horizontalSlider_2.setValue( int(self.ui.lineEdit_2.text()) ) 
        if widget is self.ui.lineEdit_3:
            self.ui.horizontalSlider_3.setValue( int(self.ui.lineEdit_3.text()) ) 
