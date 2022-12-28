# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.10.8 (main, Nov  4 2022, 09:21:25) [GCC 12.2.0]
# Embedded file name: PyInstaller\hooks\rthooks\pyi_rth_pkgutil.py
import os, pkgutil, sys
from pyimod03_importers import FrozenImporter
_orig_pkgutil_iter_modules = pkgutil.iter_modules

def _pyi_pkgutil_iter_modules(path=None, prefix=''):
    yield from _orig_pkgutil_iter_modules(path, prefix)
    for importer in pkgutil.iter_importers():
        if isinstance(importer, FrozenImporter):
            break
    else:
        return

    if path is None:
        for entry in importer.toc:
            if entry.count('.') != 0:
                continue
            is_pkg = importer.is_package(entry)
            yield pkgutil.ModuleInfo(importer, prefix + entry, is_pkg)

    else:
        SYS_PREFIX = os.path.realpath(sys._MEIPASS) + os.path.sep
        SYS_PREFIXLEN = len(SYS_PREFIX)
        for pkg_path in path:
            pkg_path = os.path.realpath(pkg_path)
            if not pkg_path.startswith(SYS_PREFIX):
                continue
            pkg_prefix = pkg_path[SYS_PREFIXLEN:]
            pkg_prefix = pkg_prefix.replace(os.path.sep, '.')
            if not pkg_prefix.endswith('.'):
                pkg_prefix += '.'
            pkg_prefix_len = len(pkg_prefix)
            for entry in importer.toc:
                if not entry.startswith(pkg_prefix):
                    continue
                name = entry[pkg_prefix_len:]
                if name.count('.') != 0:
                    continue
                is_pkg = importer.is_package(entry)
                yield pkgutil.ModuleInfo(importer, prefix + name, is_pkg)


pkgutil.iter_modules = _pyi_pkgutil_iter_modules