# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.10.8 (main, Nov  4 2022, 09:21:25) [GCC 12.2.0]
# Embedded file name: PyInstaller\hooks\rthooks\pyi_rth_subprocess.py
import subprocess, sys, io

class Popen(subprocess.Popen):
    if sys.platform == 'win32':
        if not isinstance(sys.stdout, io.IOBase):

            def _get_handles(self, stdin, stdout, stderr):
                stdin, stdout, stderr = ((subprocess.DEVNULL if pipe is None else pipe) for pipe in (stdin, stdout, stderr))
                return super()._get_handles(stdin, stdout, stderr)


subprocess.Popen = Popen