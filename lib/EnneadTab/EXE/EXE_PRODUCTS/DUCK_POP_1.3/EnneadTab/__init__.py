#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
NOTE: __all__ affects the from <module> import * behavior only. Members that are not mentioned in __all__ are still accessible from outside the module and can be imported with from <module> import <member>.


__all__ = ["DATA_FILE",
            "EMAIL",
            "ERROR_HANDLE",
            "VERSION_CONTROL"]
"""

"""
import VERSION_CONTROL
import IMAGES
import EMAIL
"""
#print ("Primary EnneadTab Module")


import os
for module in os.listdir(os.path.dirname(__file__)):
    #print (module)
    if module == '__init__.py':
        continue
    if module in ["RHINO", "REVIT", "EXE", "FUN"]:
        __import__(module, locals(), globals())
        continue
    if module[-3:] != '.py':
        continue
    try:
        __import__(module[:-3], locals(), globals())
    except Exception as e:
        print (e)
        print ("Cannot import {}".format(module))
del module# delete this varible becaue it is refering to last item on the for loop



