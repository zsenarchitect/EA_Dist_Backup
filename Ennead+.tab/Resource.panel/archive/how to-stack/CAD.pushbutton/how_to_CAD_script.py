__doc__ = "Handy CAD command bundle to prepare CAD before get into Revit."
__title__ = "How to Install EnneadTab for CAD"
__context__ = 'zero-doc'
__youtube__ = "https://youtu.be/KOidXxsioCg"
import os
path = r"file:\\L:\4b_Applied Computing\01_Revit\04_Tools\08_EA Extensions\Library Docs\CAD LISP\CAD Command list.txt"


import subprocess
subprocess.Popen(r'explorer /select, {}'.format(path))
