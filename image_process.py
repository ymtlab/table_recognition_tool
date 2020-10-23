# -*- coding: utf-8 -*-
import cv2
import numpy as np
from pathlib import Path, WindowsPath
from PyQt5 import QtGui

class ImageProcess(object):
    def __init__(self, data):
        self.data = self.load_data(data)
        
    def cv_to_pixmap(self, cv_image):
        shape_size = len(cv_image.shape)
        if shape_size == 2:
            rgb = cv2.cvtColor(cv_image, cv2.COLOR_GRAY2RGB)
        elif shape_size == 3:
            rgb = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
        height, width, bytesPerComponent = rgb.shape
        bytesPerLine = bytesPerComponent * width
        image = QtGui.QImage(rgb.data, width, height, bytesPerLine, QtGui.QImage.Format_RGB888)
        qpixmap = QtGui.QPixmap.fromImage(image)
        return qpixmap

    def edge_image(self, size):
        gray = cv2.cvtColor(self.data, cv2.COLOR_BGR2GRAY)
        edge = cv2.Canny(gray, 1, 100, apertureSize=3)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, size)
        dilate = cv2.dilate(edge, kernel)
        return dilate

    def edge_to_rects(self, edge, area_range):
        contours, hierarchy = cv2.findContours(edge, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        rects = []
        for contour, hierarchy in zip(contours, hierarchy[0]):

            if not area_range[0] < cv2.contourArea(contour) < area_range[1]:
                continue

            curve = cv2.approxPolyDP(contour, 0.01 * cv2.arcLength(contour, True), True)
            if len(curve) == 4:
                p1, p3 = curve[0][0], curve[2][0]
                x, y, w, h = p1[0], p1[1], p3[0] - p1[0], p3[1] - p1[1]
                rect =  [x, y, w, h]

                if False in [ False for r in rect if r < 1 ]:
                    continue
                
                if self.same_rect_is_in_rects(rect, rects, 10):
                    continue

                rects.append(rect)
        
        rects = sorted( rects, key=lambda x: (x[1], x[0]) )

        return rects

    def load_data(self, data):
        data_type = type(data)

        if data_type is str or data_type is WindowsPath:
            return cv2.imread( str(data) )

        if data_type is QtGui.QPixmap:
            return self.qimage_to_cv( data.toImage() )

    def qimage_to_cv(self, qimage):
        w, h, d = qimage.size().width(), qimage.size().height(), qimage.depth()
        bytes_ = qimage.bits().asstring(w * h * d // 8)
        arr = np.frombuffer(bytes_, dtype=np.uint8).reshape((h, w, d // 8))
        return arr

    def recognize_table(self, area_range=(10, 1000), dilate_size=(6, 6)):
        edge = self.edge_image(dilate_size)
        rects = self.edge_to_rects(edge, area_range)
        crops = self.rects_to_crops(rects)
        edge = self.cv_to_pixmap(edge)
        return edge, rects, crops

    def rects_to_crops(self, rects, margin=10):
        crops = []
        for rect in rects:
            x, y, w, h = rect[0], rect[1], rect[2], rect[3]
            cropped = self.data[ y : y + h, x : x + w ]

            gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
            threshold = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)[1]
            contours = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[0]

            rects_in_cropped = [ cv2.boundingRect(contour) for contour in contours[1:] ]

            if len(rects_in_cropped) == 0:
                continue

            x1 = min([ r[0] for r in rects_in_cropped ]) - margin
            y1 = min([ r[1] for r in rects_in_cropped ]) - margin
            x2 = max([ r[0] + r[2] for r in rects_in_cropped ]) + margin
            y2 = max([ r[1] + r[3] for r in rects_in_cropped ]) + margin

            if x1 < 0:
                x1 = 0
            if y1 < 0:
                y1 = 0
            if x2 > cropped.shape[1]:
                x2 = cropped.shape[1]
            if y2 > cropped.shape[0]:
                y2 = cropped.shape[0]

            crops.append([x + x1, y + y1, x2 - x1, y2 - y1])

        return crops

    def same_rect_is_in_rects(self, rect1, rects, tolerance=5):
        for rect2 in rects:
            frag = True
            for r1, r2 in zip(rect1, rect2):
                if not r2 - tolerance < r1 < r2 + tolerance:
                    frag = False
                    break
            if frag:
                return True
        return False
