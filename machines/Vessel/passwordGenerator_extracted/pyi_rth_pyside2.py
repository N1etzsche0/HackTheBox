# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.10.8 (main, Nov  4 2022, 09:21:25) [GCC 12.2.0]
# Embedded file name: PyInstaller\hooks\rthooks\pyi_rth_pyside2.py
import os, sys
if sys.platform.startswith('win'):
    pyqt_path = os.path.join(sys._MEIPASS, 'PySide2')
else:
    pyqt_path = os.path.join(sys._MEIPASS, 'Qt', 'PySide2')
os.environ['QT_PLUGIN_PATH'] = os.path.join(pyqt_path, 'plugins')
os.environ['QML2_IMPORT_PATH'] = os.path.join(pyqt_path, 'qml')
if sys.platform.startswith('win'):
    if 'PATH' in os.environ:
        os.environ['PATH'] = sys._MEIPASS + os.pathsep + os.environ['PATH']