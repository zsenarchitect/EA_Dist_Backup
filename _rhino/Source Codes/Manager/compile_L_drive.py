import Rhino # pyright: ignore
import rhinoscriptsyntax as rs
import scriptcontext as sc

import sys
sys.path.append("..\lib")

import EnneadTab

sys.path.append(EnneadTab.ENVIRONMENT.DEPENDENCY_FOLDER_LEGACY)



def OLD_compile_L_drive():

    #EnneadTab.FOLDER.compile_files(EnneadTab.ENVIRONMENT.PUBLISH_FOLDER_FOR_RHINO)
    directory = r"L:\4b_Applied Computing\03_Rhino\12_EnneadTab for Rhino\Source Codes\Fun"
    # directory = "C:\Users\szhang\Desktop"

    import py_compile
    import os
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                print(filepath)
                py_compile.compile(filepath)

    print("Finished !!!!!!!!!!")

@EnneadTab.ERROR_HANDLE.try_catch_error
def compile_L_drive():

    directory = r"L:\4b_Applied Computing\03_Rhino\12_EnneadTab for Rhino\Source Codes\Fun"
    directory = r"C:\Users\szhang\Desktop\test_moudle"
    directory = r"L:\4b_Applied Computing\03_Rhino\12_EnneadTab for Rhino\Source Codes\lib\EnneadTab"
    import clr # pyright: ignore


    import os
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                print(filepath)
                clr.CompileModules(filepath.replace(".py", ".dll"), filepath)


    print("Finished !!!!!!!!!!")

######################  main code below   #########
if __name__ == "__main__":
    rs.EnableRedraw(False)
    compile_L_drive()


