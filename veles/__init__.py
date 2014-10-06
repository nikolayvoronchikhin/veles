# -*- coding: utf-8 -*-
'''
Created on May 21, 2013

Copyright (c) 2013 Samsung Electronics Co., Ltd.
'''


from email.utils import parsedate_tz, mktime_tz
from sys import version_info, modules
from types import ModuleType
from warnings import warn

from veles.logger import Logger
from veles.units import Unit, IUnit
from veles.workflow import Workflow
from veles.opencl_units import OpenCLUnit, OpenCLWorkflow


__project__ = "Veles Machine Learning Platform"
__version__ = "0.4.3"
__license__ = "Samsung Proprietary License"
__copyright__ = "© 2013 Samsung Electronics Co., Ltd."
__authors__ = ["Gennady Kuznetsov", "Vadim Markovtsev", "Alexey Kazantsev",
               "Lyubov Podoynitsina", "Denis Seresov", "Dmitry Senin",
               "Alexey Golovizin", "Egor Bulychev", "Ernesto Sanches"]

try:
    __git__ = "$Commit$"
    __date__ = mktime_tz(parsedate_tz("$Date$"))
except Exception as ex:
    warn("Cannot expand variables generated by Git, setting them to None")
    __git__ = None
    __date__ = None

if version_info.major == 3 and version_info.minor == 4 and \
   version_info.micro < 1:
    warn("Python 3.4.0 has a bug which is critical to Veles OpenCL subsystem ("
         "see issue #21435). It is recommended to upgrade to 3.4.1.")


def __html__():
    import os
    from veles.portable import show_file

    root = os.path.dirname(__file__)
    page = os.path.join(root, "../docs/build/html/veles.html")
    if not os.path.exists(page):
        from runpy import run_path
        print("Building the documentation...")
        run_path(os.path.join(root, "../docs/generate_docs.py"))
    if os.path.exists(page):
        show_file(page)


class VelesModule(ModuleType):
    """Redefined module class with added properties which are lazily evaluated.
    """
    def __init__(self, *args, **kwargs):
        super(VelesModule, self).__init__(__name__, *args, **kwargs)
        self.__dict__.update(modules[__name__].__dict__)
        self.__units_cache__ = None

    @property
    def __units__(self):
        """
        Returns the array with all Unit classes found in the package file tree.
        """
        if self.__units_cache__ is not None:
            return self.__units_cache__

        import os
        import sys

        # Temporarily disable standard output since some modules produce spam
        # during import
        stdout = sys.stdout
        with open(os.devnull, 'w') as null:
            sys.stdout = null
        for root, _, files in os.walk(os.path.dirname(__file__)):
            if root.find('tests') >= 0:
                continue
            for file in files:
                modname, ext = os.path.splitext(file)
                if ext == '.py':
                    try:
                        sys.path.insert(0, root)
                        __import__(modname)
                        del sys.path[0]
                    except:
                        pass
        sys.stdout = stdout
        from veles.units import UnitRegistry
        self.__units_cache__ = UnitRegistry.units
        return self.__units_cache__


if not isinstance(modules[__name__], VelesModule):
    modules[__name__] = VelesModule()

if __name__ == "__main__":
    __html__()
