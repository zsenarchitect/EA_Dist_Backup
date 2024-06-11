#!/usr/bin/python
# -*- coding: utf-8 -*-
from pyrevit import script
output = script.get_output()
output.close_others()
__doc__ = "Sen Zhang has not writed documentation for this tool, but he should!"
__title__ = "Publish\nEnneadTab Module"
__context__ = "zero-doc"

GITHUB_FOLDER = r"C:\Users\szhang\github"
WORKING_FOLDER_FOR_REVIT = r"{}\EnneadTab-for-Revit".format(GITHUB_FOLDER)

import sys
sys.path.append(r"{}\ENNEAD.extension\lib".format(WORKING_FOLDER_FOR_REVIT))
print(r"{}\ENNEAD.extension\lib".format(WORKING_FOLDER_FOR_REVIT))
print(r"C:\Users\szhang\github\EnneadTab-for-Revit\ENNEAD.extension\lib")

import EnneadTab
print("module of EnneadTab = {}".format(dir(EnneadTab)))
print("__path__ of EnneadTab = {}".format(EnneadTab.__path__))
print("__file__ of EnneadTab = {}".format(EnneadTab.__file__))

@EnneadTab.ERROR_HANDLE.try_catch_error_silently
def test():
    print("\n\n\ntest")
    print(apple)


# test()
EnneadTab.VERSION_CONTROL.publish_ENNEAD_module()
