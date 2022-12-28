# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.10.8 (main, Nov  4 2022, 09:21:25) [GCC 12.2.0]
# Embedded file name: PyInstaller\loader\pyimod04_ctypes.py
# Compiled at: 2022-05-04 05:14:29
# Size of source mod 2**32: 3928 bytes
"""
Hooks to make ctypes.CDLL, .PyDLL, etc. look in sys._MEIPASS first.
"""
import sys

def install():
    """
    Install the hooks.

    This must be done from a function as opposed to at module-level, because when the module is imported/executed,
    the import machinery is not completely set up yet.
    """
    import os
    try:
        import ctypes
    except ImportError:
        return
    else:

        def _frozen_name(name):
            if name:
                if not os.path.isfile(name):
                    frozen_name = os.path.join(sys._MEIPASS, os.path.basename(name))
                    if os.path.isfile(frozen_name):
                        name = frozen_name
            return name

        class PyInstallerImportError(OSError):

            def __init__(self, name):
                self.msg = 'Failed to load dynlib/dll %r. Most likely this dynlib/dll was not found when the application was frozen.' % name
                self.args = (
                 self.msg,)

        class PyInstallerCDLL(ctypes.CDLL):

            def __init__(self, name, *args, **kwargs):
                name = _frozen_name(name)
                try:
                    (super().__init__)(name, *args, **kwargs)
                except Exception as base_error:
                    try:
                        raise PyInstallerImportError(name) from base_error
                    finally:
                        base_error = None
                        del base_error

        ctypes.CDLL = PyInstallerCDLL
        ctypes.cdll = ctypes.LibraryLoader(PyInstallerCDLL)

        class PyInstallerPyDLL(ctypes.PyDLL):

            def __init__(self, name, *args, **kwargs):
                name = _frozen_name(name)
                try:
                    (super().__init__)(name, *args, **kwargs)
                except Exception as base_error:
                    try:
                        raise PyInstallerImportError(name) from base_error
                    finally:
                        base_error = None
                        del base_error

        ctypes.PyDLL = PyInstallerPyDLL
        ctypes.pydll = ctypes.LibraryLoader(PyInstallerPyDLL)
        if sys.platform.startswith('win'):

            class PyInstallerWinDLL(ctypes.WinDLL):

                def __init__(self, name, *args, **kwargs):
                    name = _frozen_name(name)
                    try:
                        (super().__init__)(name, *args, **kwargs)
                    except Exception as base_error:
                        try:
                            raise PyInstallerImportError(name) from base_error
                        finally:
                            base_error = None
                            del base_error

            ctypes.WinDLL = PyInstallerWinDLL
            ctypes.windll = ctypes.LibraryLoader(PyInstallerWinDLL)

            class PyInstallerOleDLL(ctypes.OleDLL):

                def __init__(self, name, *args, **kwargs):
                    name = _frozen_name(name)
                    try:
                        (super().__init__)(name, *args, **kwargs)
                    except Exception as base_error:
                        try:
                            raise PyInstallerImportError(name) from base_error
                        finally:
                            base_error = None
                            del base_error

            ctypes.OleDLL = PyInstallerOleDLL
            ctypes.oledll = ctypes.LibraryLoader(PyInstallerOleDLL)


if sys.platform.startswith('darwin'):
    try:
        from ctypes.macholib import dyld
        dyld.DEFAULT_LIBRARY_FALLBACK.insert(0, sys._MEIPASS)
    except ImportError:
        pass