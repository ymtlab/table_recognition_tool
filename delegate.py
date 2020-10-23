# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets, QtCore, QtGui

class Delegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent=None, setModelDataEvent=None):
        super(Delegate, self).__init__(parent)
        self.setModelDataEvent = setModelDataEvent
 
    def createEditor(self, parent, option, index):
        return QtWidgets.QLineEdit(parent)
 
    def setEditorData(self, editor, index):
        value = index.model().data(index, QtCore.Qt.DisplayRole)
        editor.setText(str(value))
 
    def setModelData(self, editor, model, index):
        model.setData(index, editor.text())
        if not self.setModelDataEvent is None:
            self.setModelDataEvent()

    def paint(self, painter, option, index):
        data = index.model().data(index)
        
        if type(data) is QtGui.QPixmap:
            # cell size
            r = option.rect
            x, y, w, h = r.x(), r.y(), r.width(), r.height()
            # image size
            w2, h2 = data.size().width(), data.size().height()
            # aspect rasio
            r1, r2 = w / h, w2 / h2
            if r1 < r2:
                h = w / r2
            else:
                w = h * r2
            
            pixmap2 = data.scaled(w, h, QtCore.Qt.KeepAspectRatio)
            rect = QtCore.QRect(x, y, w, h)
            painter.drawPixmap(rect, pixmap2)
        
        super(Delegate, self).paint(painter, option, index)
