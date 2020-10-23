# -*- coding: utf-8 -*-
import subprocess
from pathlib import Path, WindowsPath
from PyQt5 import QtGui

class Tesseract():
    def __init__(self):
        self.tesseract = 'Tesseract-OCR/tesseract.exe'

    def command(self, filename, output_file):
        return [self.tesseract, str(filename), output_file.stem]

    def OCR(self, data):
        if type(data) is str or type(data) is WindowsPath:
            return self.OCR_file(data)
        if type(data) is QtGui.QPixmap:
            imagefile = Path('__temp__.png')
            data.save(str(imagefile))
            output = self.OCR_file(imagefile)
            imagefile.unlink()
            return output

    def OCR_file(self, filename):
        output_file = Path('__temp__.txt')
        cmd = [self.tesseract, str(filename), output_file.stem]

        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
        
        returncode = subprocess.Popen(cmd, startupinfo=startupinfo)
        returncode.wait()
        
        try:
            with open(output_file, 'r', encoding='utf-8') as file:
                output = file.readline()
            output_file.unlink()
            return output
        except:
            return ''
