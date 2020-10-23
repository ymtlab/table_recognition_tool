# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets, QtCore, QtGui

class ListView(QtWidgets.QListView):
    def __init__(self, parent):
        super(ListView, self).__init__(parent)
        self.customContextMenuRequested.connect(self.context_menu)
        
    def context_menu(self, point):
        menu = QtWidgets.QMenu(self)
        menu.addAction('Delete', self.delete_selected_item)
        menu.exec( self.focusWidget().mapToGlobal(point) )
        
    def set_current_index(self, row):
        if self.model().rowCount() == 0:
            return
        index = self.model().createIndex( row, 0, self.model().root().child(row) )
        self.setCurrentIndex(index)

    def mouseReleaseEvent(self, event):
        QtWidgets.QListView.mouseReleaseEvent(self, event)

        mainwindow = self.mainwindow(self)
        if mainwindow is None:
            return
        
        tableview_selected_indexes = mainwindow.ui.tableView.selectedIndexes()
        if len(tableview_selected_indexes) == 0:
            return
        
        tableview_item = tableview_selected_indexes[0].internalPointer()
        tableview_item.data('rect_items_index', self.selectedIndexes()[0].row())
        mainwindow.graphics_view_update()

    def delete_selected_item(self):
        selected_indexes = self.ui.listView.selectedIndexes()

        if len(selected_indexes) == 0:
            return

        selected_row = selected_indexes[0].row()

        self.model().removeRow(selected_row)

        mainwindow = self.mainwindow(self)
        if mainwindow is None:
            return
        
        tableview_selected_indexes = mainwindow.ui.tableView.selectedIndexes()
        if len(tableview_selected_indexes) == 0:
            return
        tableview_item = tableview_selected_indexes[0].internalPointer()

        del tableview_item.data('rect_items')[selected_row]
        del tableview_item.data('rect_alpha_items')[selected_row]
        del tableview_item.data('rect_alpha_items_2')[selected_row]
        del tableview_item.data('rects')[selected_row]
        del tableview_item.data('crops')[selected_row]

        if selected_row - 1 < 0:
            row = 0
        else:
            row = selected_row - 1
        
        tableview_item.data('rect_items_index', row)

        mainwindow.graphics_view_update()

    def mainwindow(self, widget):
        if widget is None:
            return None
        if widget.inherits('QMainWindow'):
            return widget
        return self.mainwindow( widget.parent() )
