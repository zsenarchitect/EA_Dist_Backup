import os
import sys

def quack ():
    root_folder = os.path.abspath(os.path.dirname((os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
    sys.path.append(root_folder)
    #print (root_folder)
    import EXE

    exe = r"L:\4b_Applied Computing\01_Revit\04_Tools\08_EA Extensions\Project Settings\Exe\desktop_pet_V2.2\desktop_pet_V2.2.exe - Shortcut"
    exe = r"L:\4b_Applied Computing\01_Revit\04_Tools\08_EA Extensions\Project Settings\Exe\EnneaDuck_1.0\desktop_pet_V2.2.exe - Shortcut"
    EXE.open_file_in_default_application(exe)

"""
Use duck right click display that host all recent popup toast as long term such as incorrect area boundary, thank you for using.
It is a duck log.


Use it for alarming queue turn


In last sync monitor exe gui. allow to record setting on if it should announce popup or speak.
"""
