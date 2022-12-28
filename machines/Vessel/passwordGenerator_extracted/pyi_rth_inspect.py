# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.10.8 (main, Nov  4 2022, 09:21:25) [GCC 12.2.0]
# Embedded file name: PyInstaller\hooks\rthooks\pyi_rth_inspect.py
import inspect, os, sys
_orig_inspect_getsourcefile = inspect.getsourcefile

def _pyi_getsourcefile(object):
    filename = inspect.getfile(object)
    if not os.path.isabs(filename):
        main_file = sys.modules['__main__'].__file__
        if filename == os.path.basename(main_file):
            return main_file
        if filename.endswith('.py'):
            filename = os.path.normpath(os.path.join(sys._MEIPASS, filename + 'c'))
            if filename.startswith(sys._MEIPASS):
                return filename
    elif filename.startswith(sys._MEIPASS):
        if filename.endswith('.pyc'):
            return filename
    return _orig_inspect_getsourcefile(object)


inspect.getsourcefile = _pyi_getsourcefile