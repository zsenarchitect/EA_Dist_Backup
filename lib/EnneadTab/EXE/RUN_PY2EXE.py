

# run this script in python 2.7 becasue it is running from the L drive dependecy folder

#also check the header for the ript to convert, does it say 2.7 or 3.x?

import subprocess
import sys


def start_UI():
    # run check to see what verion of python this machine has
    python_version = sys.version_info.major
    if python_version != 2:
        print("\033[91mThis script is for python 2.7 only\033[0m")
        return

    
    script = "L:\\4b_Applied Computing\\03_Rhino\\12_EnneadTab for Rhino\\Dependency Modules\\auto-py-to-exe-master\\run.py"
    subprocess.call(["python", script])


if __name__ == "__main__":
    start_UI()