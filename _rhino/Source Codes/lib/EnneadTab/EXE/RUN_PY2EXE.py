
# work for both 2.7 and 3.X
# run this script in python 2.7 becasue it is running from the L drive dependecy folder



import subprocess
import sys


def start_UI():
    # run check to see what verion of python this machine has
    python_version = sys.version_info.major
    if python_version == 2:
        print("\033[91mUsing version python 2.7\033[0m")

    
        script = "L:\\4b_Applied Computing\\03_Rhino\\12_EnneadTab for Rhino\\Dependency Modules\\auto-py-to-exe-master\\run.py"
        subprocess.call(["python", script])
        return
    else:
        print("\033[91mUsing version python 3.X\033[0m")
        from auto_py_to_exe import __main__ as apte
        apte.__name__ = '__main__'
        apte.run()

if __name__ == "__main__":
    start_UI()