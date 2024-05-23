import Rhino # pyright: ignore
import rhinoscriptsyntax as rs
import scriptcontext as sc

import sys
sys.path.append("..\lib")
import EnneadTab


sys.path.append(EnneadTab.ENVIRONMENT_CONSTANTS.DEPENDENCY_FOLDER_LEGACY)


@EnneadTab.ERROR_HANDLE.try_catch_error
def send_duck():
    EnneadTab.FUN.EnneaDuck.quack()
    


######################  main code below   #########
if __name__ == "__main__":

    send_duck()




