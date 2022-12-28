# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.10.8 (main, Nov  4 2022, 09:21:25) [GCC 12.2.0]
# Embedded file name: PyInstaller\loader\pyimod01_os_path.py
# Compiled at: 2022-05-04 05:14:29
# Size of source mod 2**32: 3042 bytes
"""
Set up 'os' and 'os.path' module replacement functions for use during import bootstrap.
"""
import sys
_builtin_names = sys.builtin_module_names
_mindirlen = 0
if 'posix' in _builtin_names:
    from posix import environ as os_environ
    from posix import listdir as os_listdir
    os_sep = '/'
    _mindirlen = 1
else:
    if 'nt' in _builtin_names:
        from nt import environ as os_environ
        from nt import listdir as os_listdir
        os_sep = '\\'
        _mindirlen = 3
    else:
        raise ImportError('No OS-specific module found!')

def os_path_join(a, b, sep=os_sep):
    if a == '':
        return b
    lastchar = a[-1:]
    if lastchar == '/' or lastchar == sep:
        return a + b
    return a + sep + b


def os_path_dirname(a, sep=os_sep, mindirlen=_mindirlen):
    for i in range(len(a) - 1, -1, -1):
        c = a[i]
        if not c == '/':
            if c == sep:
                if i < mindirlen:
                    return a[:i + 1]
            return a[:i]

    return ''


if sys.platform.startswith('win'):

    def os_path_basename(pth):
        if pth[1:2] == ':':
            p = pth[2:]
        else:
            p = pth
        i = len(p)
        while i and p[(i - 1)] not in '/\\':
            i = i - 1

        return p[i:]


else:

    def os_path_basename(pth):
        i = pth.rfind('/') + 1
        return pth[i:]


if 'PYTHONCASEOK' not in os_environ:

    def caseOk(filename):
        files = os_listdir(os_path_dirname(filename))
        return os_path_basename(filename) in files


else:

    def caseOk(filename):
        return True