import Rhino # pyright: ignore
import rhinoscriptsyntax as rs
import scriptcontext as sc

import sys


sys.path.append("..\lib")
import EnneadTab


sys.path.append(EnneadTab.ENVIRONMENT.DEPENDENCY_FOLDER_LEGACY)




@EnneadTab.ERROR_HANDLE.try_catch_error
def excel2shape():
    print (999)



######################  main code below   #########
if __name__ == "__main__":
    excel2shape()


