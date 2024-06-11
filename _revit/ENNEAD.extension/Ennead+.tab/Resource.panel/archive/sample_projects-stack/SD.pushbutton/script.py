__tooltip__ = "See other SD project documentations."
__context__ = 'zero-doc'
__title__ = "SD Projects Reference"

import os
path = r"file:\\L:\4b_Applied Computing\01_Revit\04_Tools\08_EA Extensions\Library Docs\SD Documentation Samples\#PDF in this directory are reference only"


import subprocess
subprocess.Popen(r'explorer /select, {}'.format(path))
