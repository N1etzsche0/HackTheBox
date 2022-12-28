# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.10.8 (main, Nov  4 2022, 09:21:25) [GCC 12.2.0]
# Embedded file name: PyInstaller\loader\pyiboot01_bootstrap.py
import sys, pyimod03_importers
pyimod03_importers.install()
import os
if not hasattr(sys, 'frozen'):
    sys.frozen = True
sys.prefix = sys._MEIPASS
sys.exec_prefix = sys.prefix
sys.base_prefix = sys.prefix
sys.base_exec_prefix = sys.exec_prefix
VIRTENV = 'VIRTUAL_ENV'
if VIRTENV in os.environ:
    os.environ[VIRTENV] = ''
    del os.environ[VIRTENV]
python_path = []
for pth in sys.path:
    python_path.append(os.path.abspath(pth))
    sys.path = python_path

class NullWriter:
    softspace = 0
    encoding = 'UTF-8'

    def write(*args):
        pass

    def flush(*args):
        pass

    def isatty(self):
        return False


if sys.stdout is None:
    sys.stdout = NullWriter()
if sys.stderr is None:
    sys.stderr = NullWriter()
try:
    import encodings
except ImportError:
    pass

if sys.warnoptions:
    import warnings
import pyimod04_ctypes
pyimod04_ctypes.install()
d = 'eggs'
d = os.path.join(sys._MEIPASS, d)
if os.path.isdir(d):
    for fn in os.listdir(d):
        sys.path.append(os.path.join(d, fn))