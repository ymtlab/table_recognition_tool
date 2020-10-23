# -*- coding: utf-8 -*-
from pathlib import Path
from PyQt5 import QtWidgets, QtCore, QtGui

from .mainwindow_ui import Ui_MainWindow
from model import Model
from item import Item
from delegate import Delegate
from column import Column
from poppler import Poppler
from image_process import ImageProcess
from tesseract import Tesseract
from .toolbar import ToolBar

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, app):
        super().__init__()

        self.copy_data = None
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.resize(800, 600)

        self.model = Model( self, Item(), Column(['File name', 'Resolution']) )
        #self.model = Model( self, Item(), Column(['File name', 'Resolution', 'Settings']) )
        
        self.ui.tableView.setModel(self.model)
        self.ui.tableView.setItemDelegate( Delegate() )
        self.ui.tableView.clicked.connect(self.tableview_clicked)
        self.ui.tableView.customContextMenuRequested.connect(self.context_menu_tableview)

        self.tool_bar = ToolBar(self.ui.toolBar)
        self.ui.toolBar.addWidget(self.tool_bar)

        self.tool_bar.ui.toolButton.clicked.connect(self.open_files)
        self.tool_bar.ui.toolButton_3.clicked.connect(self.recognize)
        self.tool_bar.ui.toolButton_4.clicked.connect(self.crop_by_rects)
        self.tool_bar.ui.toolButton_5.clicked.connect(self.graphics_view_update)
        self.tool_bar.ui.toolButton_6.clicked.connect(self.graphics_view_update)
        self.tool_bar.ui.toolButton_7.clicked.connect(self.graphics_view_update)
        self.tool_bar.ui.toolButton_8.clicked.connect(self.ocr)
        self.tool_bar.ui.toolButton_9.clicked.connect(self.crop_by_crops)

        self.ui.image_view.ui.graphicsView.mouse_left_released.connect(self.append_rect)
        self.tool_bar.slider_changed.connect(self.slider_changed_event)

    def slider_changed_event(self):
        self.recognize()
        
        tableview_items = self.tableview_selected_items()
        if tableview_items is None:
            return
        else:
            tableview_item = tableview_items[0]
        rects = tableview_item.data('rects')

        self.ui.image_view.update_rows(rects)
        self.graphics_view_update()

    def append_rect(self, coordinates):
        if not self.tool_bar.ui.toolButton_10.isChecked():
            return

        tableview_items = self.tableview_selected_items()
        if tableview_items is None:
            return
        else:
            tableview_item = tableview_items[0]

        if coordinates[0].x() < coordinates[1].x():
            x1, x2 = coordinates[0].x(), coordinates[1].x()
        else:
            x1, x2 = coordinates[1].x(), coordinates[0].x()

        if coordinates[0].y() < coordinates[1].y():
            y1, y2 = coordinates[0].y(), coordinates[1].y()
        else:
            y1, y2 = coordinates[1].y(), coordinates[0].x()
        
        rects = tableview_item.data('rects')
        rects.append([x1, y1, x2 - x1, y2 - y1])
        tableview_item.data('rects', rects)

        crops = tableview_item.data('crops')
        crops.append([x1, y1, x2 - x1, y2 - y1])
        tableview_item.data('crops', crops)

        self.tool_bar.ui.toolButton_10.setChecked(False)
        self.ui.image_view.update_rows(rects)
        self.graphics_view_update()

    def context_menu_tableview(self, point):
        menu = QtWidgets.QMenu(self)
        menu.addAction('Open files', self.open_files)
        menu.addAction('Remove all items', lambda : self.model.removeRows(0, self.model.rowCount()))
        menu.addAction('Copy setting', self.copy_setting)
        menu.addAction('Paste setting', self.paste_setting)
        menu.exec( self.focusWidget().mapToGlobal(point) )

    def copy_setting(self):
        items = self.tableview_selected_items()
        if items is None:
            return
        self.copy_data = {
            'Settings' : items[0].data('Settings'),
            'rects' : items[0].data('rects'),
            'crops' : items[0].data('crops')
        }

    def ocr(self):
        columns = list( range( self.model.columnCount() ) )[::-1]
        for item in self.model.root().children():
            for c in columns:
                column = self.model.headerData(c, QtCore.Qt.Horizontal)
                if column[:4] == 'rect' or column[:4] == 'crop':
                    try:
                        temp = int(column[4:])
                    except:
                        continue
                else:
                    continue

                column_text = column + '_text'
                if not self.model.headerData(c + 1, QtCore.Qt.Horizontal) == column_text:
                    self.model.insertColumn(c + 1)
                    self.model.setHeaderData(c + 1, QtCore.Qt.Horizontal, column_text)

                rect = item.data(column)
                if rect is None:
                    continue
                item.data( column_text, Tesseract().OCR(rect).strip() )

    def open_files(self):
        return_value = QtWidgets.QFileDialog.getOpenFileNames(self, 'Open files', '', 'Support Files (*.png *.pdf)')
        if len(return_value[0]) == 0:
            return
        
        column_count = self.model.columnCount()
        if column_count > 3:
            self.model.removeColumns(3, column_count-3)

        self.model.removeRows(0, self.model.rowCount())
        files = [ Path(f) for f in return_value[0] ]
        self.model.insertRows(0, len(files))

        for r, f in enumerate(files):
            item = self.model.root().child(r)
            item.data('File name', f.name)
            item.data('file_path', f)

            if f.suffix == '.pdf':
                output_path = Poppler().pdftocairo(f, Path('__temp__.png'), 300)
                item.data('qpixmap', QtGui.QPixmap(str(output_path)))
                output_path.unlink()
            else:
                item.data('qpixmap', QtGui.QPixmap( str(f) ) )
            h, w = item.data('qpixmap').rect().height(), item.data('qpixmap').rect().width()
            item.data('Resolution', str(h) + 'x' + str(w) )
        
        self.ui.image_view.update_rows(None)
        
        scene = self.ui.image_view.ui.graphicsView.scene()
        for item in scene.items():
            scene.removeItem(item)

    def paste_setting(self):
        if self.copy_data is None:
            return
        items = self.tableview_selected_items()
        if items is None:
            return
        for item in items:
            for key in self.copy_data:
                item.data(key, self.copy_data[key])

    def rect_to_rect_item(self, rect, color, pen_width):
        rect_item = QtWidgets.QGraphicsRectItem()
        rect_item.setRect( rect[0], rect[1], rect[2], rect[3] )
        pen = QtGui.QPen(color)
        pen.setWidth(pen_width)
        rect_item.setPen(pen)
        return rect_item

    def crop(self, column_key, item):

        rects = item.data(column_key)
        if rects is None or len(rects) == 0:
            return

        column_key = column_key[:-1]
        qpixmap = item.data('qpixmap')
        for i, c in enumerate(rects):
            cropped_qpixmap = qpixmap.copy( QtCore.QRect( c[0], c[1], c[2], c[3] ) )
            item.data(column_key + str(i), cropped_qpixmap)
        
        column_count = self.model.columnCount()
        columns = [ self.model.headerData(c, QtCore.Qt.Horizontal) for c in range(column_count) ]
        append_columns = [ column_key + str(i) for i in range(len(rects)) if not column_key + str(i) in columns ]

        self.model.insertColumns(column_count, len(append_columns))
        for c, column in enumerate(append_columns):
            self.model.setHeaderData(column_count + c, QtCore.Qt.Horizontal, column)

    def crop_by_crops(self):
        items = self.tableview_selected_items()
        if items is None:
            return
        self.crop('crops', items[0])

    def crop_by_rects(self):
        items = self.tableview_selected_items()
        if items is None:
            return
        self.crop('rects', items[0])

    def recognize(self):
        tableview_items = self.tableview_selected_items()
        if tableview_items is None:
            return
        else:
            tableview_item = tableview_items[0]
        
        area_range = ( self.tool_bar.ui.horizontalSlider.value(), self.tool_bar.ui.horizontalSlider_2.value() )
        dilate_size = ( self.tool_bar.ui.horizontalSlider_3.value(), self.tool_bar.ui.horizontalSlider_3.value() )
        image_process = ImageProcess( tableview_item.data('qpixmap') )
        edge, rects, crops = image_process.recognize_table(area_range, dilate_size)
        
        tableview_item.data('rects_index', 0)
        tableview_item.data('edge', edge)
        tableview_item.data('rects', rects)
        tableview_item.data('crops', crops)

        children = self.model.root().children()
        setting_names = [ c.data('Settings') for c in children if not c.data('Settings') is None ]
        setting_names = [ s for s in setting_names if not s in setting_names ]

        self.ui.image_view.update_rows(rects)
        self.graphics_view_update()

    def tableview_clicked(self, index):

        clicked_item = index.internalPointer()

        #if clicked_item.data('edge') is None:
        #    self.recognize()
        rects_index = clicked_item.data('rects_index')
        if rects_index is None:
            clicked_item.data('rects_index', 0)
            self.ui.image_view.set_current_index(0)
        else:
            self.ui.image_view.set_current_index(rects_index)
        
        self.ui.image_view.update_rows(clicked_item.data('rects'))
        self.graphics_view_update()
        self.ui.image_view.graphics_view_fit()

    def tableview_selected_items(self):
        selected_indexes = self.ui.tableView.selectedIndexes()
        if len(selected_indexes) == 0:
            return None
        items = []
        for index in selected_indexes:
            item = index.internalPointer()
            if not item in items:
                items.append(item)
        return items

    def graphics_view_update(self):
        tableview_items = self.tableview_selected_items()
        if tableview_items is None:
            return
        else:
            tableview_item = tableview_items[0]

        if self.tool_bar.ui.toolButton_5.isChecked():
            qpixmap = tableview_item.data('edge')
            if qpixmap is None:
                qpixmap = tableview_item.data('qpixmap')
        else:
            qpixmap = tableview_item.data('qpixmap')
        self.ui.image_view.draw_pixmap(qpixmap)

        rects = tableview_item.data('rects')
        crops = tableview_item.data('crops')

        if self.tool_bar.ui.toolButton_6.isChecked() and not rects is None:
            pen_width = self.tool_bar.ui.spinBox_2.value()
            for rect in rects:
                self.ui.image_view.draw_rect(rect, 0, 0, 255, 200, pen_width)

        if self.tool_bar.ui.toolButton_7.isChecked() and not crops is None:
            pen_width = self.tool_bar.ui.spinBox_3.value()
            for crop in crops:
                self.ui.image_view.draw_rect(crop, 0, 255, 0, 200, pen_width)

        if not rects is None and len(rects) > 0:
            indexes = tableview_item.data('rects_indexs')
            if indexes is None:
                return
            pen_width = self.tool_bar.ui.spinBox.value()
            for r in indexes:
                if r >= len(rects):
                    continue
                rect = rects[r]
                self.ui.image_view.draw_rect(rect, 255, 0, 0, 255, pen_width)
