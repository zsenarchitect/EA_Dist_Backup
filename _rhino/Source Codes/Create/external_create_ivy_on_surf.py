import sys
sys.path.append("..\lib")
import EnneadTab

@EnneadTab.ERROR_HANDLE.try_catch_error
def run_ivy_maker():

    import subprocess
    path = r"L:\4b_Applied Computing\03_Rhino\13_External Generation\ivy_generator\IvyGenerator.exe - Run Me"
    path = r"L:\4b_Applied Computing\03_Rhino\13_External Generation\ivy_generator\src"
    subprocess.Popen(r'explorer /select, {}'.format(path))

######################  main code below   #########
if __name__ == "__main__":
    run_ivy_maker()
