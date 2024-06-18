import sys
sys.path.append("..\lib")
import EnneadTab

@EnneadTab.ERROR_HANDLE.try_catch_error
def run_materialize():

    import subprocess
    path = r"L:\4b_Applied Computing\03_Rhino\13_External Generation\Materialize_Texture map creation\Materialize.exe - Run Me"
    path = r"L:\4b_Applied Computing\03_Rhino\13_External Generation\Materialize_Texture map creation\src"
    print(path)
    subprocess.Popen(r'explorer /select, {}'.format(path))

######################  main code below   #########
if __name__ == "__main__":
    run_materialize()
