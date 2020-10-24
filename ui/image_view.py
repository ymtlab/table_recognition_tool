# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets, QtCore, QtGui
from .image_view_ui import Ui_Form
from model import Model
from item import Item
from delegate import Delegate
from column import Column
from image_process import ImageProcess

class ImageView(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.model = Model( self, Item(), Column(['column']) )

        self.ui.listView.setModel(self.model)
        self.ui.listView.setItemDelegate( Delegate() )
        self.ui.listView.clicked.connect(self.listview_clicked)
        self.ui.listView.customContextMenuRequested.connect(self.context_menu)
        self.ui.listView.keyReleaseEvent = self.lsitview_keyReleaseEvent
        
        self.ui.graphicsView.setScene( QtWidgets.QGraphicsScene(self.ui.graphicsView) )

    def context_menu(self, point):
        menu = QtWidgets.QMenu(self)
        menu.addAction('Delete', self.delete_selected_item)
        menu.exec( self.focusWidget().mapToGlobal(point) )

    def delete_selected_item(self):
        mainwindow = self.mainwindow(self)
        if mainwindow is None:
            tableview_item = None
        else:
            tableview_items = mainwindow.tableview_selected_items()
            if len(tableview_items) == 0:
                tableview_item = None
            else:
                tableview_item = tableview_items[0]
        
        selected_indexes = self.ui.listView.selectedIndexes()
        for index in selected_indexes[::-1]:
            row = index.row()
            self.model.removeRow(row)
            
            if tableview_item is None:
                continue
            
            for key in ['rects', 'crops']:
                del tableview_item.data(key)[row]
        
        if len(selected_indexes) > 0:
            tableview_item.data('rects_indexs', [0])

        mainwindow.graphics_view_update()
        
    def listview_clicked(self, index):
        mainwindow = self.mainwindow(self)
        if mainwindow is None:
            return
        
        tableview_items = mainwindow.tableview_selected_items()
        if len(tableview_items) == 0:
            return
        else:
            tableview_item = tableview_items[0]
        
        rows = [ i.row() for i in self.ui.listView.selectedIndexes() ]
        tableview_item.data('rects_indexs', rows)
        mainwindow.graphics_view_update()

    def lsitview_keyReleaseEvent(self, event):
        if event.key() == QtCore.Qt.Key_Delete:
            self.delete_selected_item()
        if event.key() == QtCore.Qt.Key_Down:
            self.listview_clicked( self.ui.listView.selectedIndexes()[0] )
        if event.key() == QtCore.Qt.Key_Up:
            self.listview_clicked( self.ui.listView.selectedIndexes()[0] )
        super(QtWidgets.QListView, self.ui.listView).keyReleaseEvent(event)

    def mainwindow(self, widget):
        if widget is None:
            return None
        if widget.inherits('QMainWindow'):
            return widget
        return self.mainwindow( widget.parent() )

    def graphics_view_fit(self):
        self.ui.graphicsView.fitInView(self.ui.graphicsView.scene().sceneRect(), QtCore.Qt.KeepAspectRatio)

    def rect_item(self, rect, r, g, b, a, pen_width):
        color = QtGui.QColor(r, g, b, a)
        rect_item = QtWidgets.QGraphicsRectItem()
        rect_item.setRect( rect[0], rect[1], rect[2], rect[3] )
        pen = QtGui.QPen(color)
        pen.setWidth(pen_width)
        rect_item.setPen(pen)
        return rect_item

    def draw_pixmap(self, pixmap):
        scene = self.ui.graphicsView.scene()

        for item in scene.items():
            scene.removeItem(item)

        scene.setSceneRect( QtCore.QRectF(pixmap.rect()) )
        scene.addPixmap(pixmap)

    def draw_rect(self, rect, r, g, b, a, pen_width):
        color = QtGui.QColor(r, g, b, a)
        rect_item = QtWidgets.QGraphicsRectItem()
        rect_item.setRect( rect[0], rect[1], rect[2], rect[3] )
        pen = QtGui.QPen(color)
        pen.setWidth(pen_width)
        rect_item.setPen(pen)
        self.ui.graphicsView.scene().addItem(rect_item)

    def set_current_index(self, row):
        if self.model.rowCount() == 0:
            return
        index = self.model.createIndex( row, 0, self.model.root().child(row) )
        self.ui.listView.setCurrentIndex(index)
        
    def update_rows(self, rects):
        if self.model.rowCount() > 0:
            self.model.removeRows(0, self.model.rowCount())

        if rects is None:
            return
        self.model.insertRows( 0, len(rects) )
        children = self.model.root().children()
        for r, list_item in enumerate(children):
            list_item.data('column', 'Rect'+str(r))
