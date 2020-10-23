# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets, QtCore, QtGui

class GraphicsView(QtWidgets.QGraphicsView):

    mouse_left_released = QtCore.pyqtSignal(list)

    def __init__(self, *argv, **keywords):
        super(GraphicsView, self).__init__(*argv, **keywords)
        self._numScheduledScalings = 0
        self.coordinates = []

    def animation_finished(self):
        if self._numScheduledScalings > 0:
            self._numScheduledScalings -= 1
        else:
            self._numScheduledScalings += 1
        
    def wheelEvent(self, event):
        numDegrees = event.angleDelta().y() / 8
        numSteps = numDegrees / 15
        self._numScheduledScalings += numSteps
        if self._numScheduledScalings * numSteps < 0:
            self._numScheduledScalings = numSteps
        anim = QtCore.QTimeLine(350, self)
        anim.setUpdateInterval(20)
        anim.valueChanged.connect(self.scaling_time)
        anim.finished.connect(self.animation_finished)
        anim.start()

    def mainwindow(self, parent):
        if parent is None:
            return None
        if parent.inherits('QMainWindow'):
            return parent
        return self.mainwindow(parent.parent())

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MidButton:
            self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)

            event = QtGui.QMouseEvent(
                QtCore.QEvent.GraphicsSceneDragMove, 
                event.pos(), 
                QtCore.Qt.MouseButton.LeftButton, 
                QtCore.Qt.MouseButton.LeftButton, 
                QtCore.Qt.KeyboardModifier.NoModifier
            )

        elif event.button() == QtCore.Qt.LeftButton:
            self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)
            pos = self.mapToScene(event.pos())
            self.coordinates = [pos]

        QtWidgets.QGraphicsView.mousePressEvent(self, event)
        
    def mouseReleaseEvent(self, event):
        QtWidgets.QGraphicsView.mouseReleaseEvent(self, event)
        self.setDragMode(QtWidgets.QGraphicsView.NoDrag)

        if event.button() == QtCore.Qt.LeftButton:
            pos = self.mapToScene(event.pos())
            self.coordinates.append(pos)

        self.mouse_left_released.emit( self.coordinates )

    def scaling_time(self, x):
        factor = 1.0 + float(self._numScheduledScalings) / 300.0
        self.scale(factor, factor)
