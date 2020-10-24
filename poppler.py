# -*- coding: utf-8 -*-
import subprocess
from pathlib import Path
import chardet

class Poppler():
    def __init__(self):
        pdftocairo = list(Path('poppler/').glob('**/pdftocairo.exe'))
        if len(pdftocairo) > 0:
            self.pdftocairo_path = pdftocairo[0]
        else:
            self.pdftocairo_path = None
        
    def pdftocairo(self, input_path, output_path, resolution):
        suffix = '-'+str(output_path.suffix).replace('.', '')
        cmd = [str(self.pdftocairo_path), suffix, '-r', str(resolution), str(input_path), str(output_path.stem)]
        return_value = self.subprocess_run(cmd)
        if Path(output_path.stem + '.png').exists():
            Path(output_path.stem + '.png').unlink()
        Path(output_path.stem + '-1.png').rename(output_path.stem + '.png')
        return Path(output_path.stem + '.png')

    def subprocess_run(self, cmd):
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
        
        returncode = subprocess.Popen(cmd, startupinfo=startupinfo)
        returncode.wait()
        
        return returncode
