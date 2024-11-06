#! python3

__doc__ = "Sen Zhang has not writed documentation for this tool, but he should!"
__title__ = "Test Cpython"

import os
import sys

# Define the relative path to the "lib" directory (2 levels up, then into "lib")
relative_lib_path = os.path.join('..', '..', 'lib')

# Convert the relative path to an absolute path
current_dir = os.path.dirname(os.path.abspath(__file__))
lib_dir = os.path.abspath(os.path.join(current_dir, relative_lib_path))

# Add the "lib" directory to sys.path
if lib_dir not in sys.path:
    sys.path.append(lib_dir)

print(sys.path)

# Import Revit API inside a try-catch to handle potential memory issues
try:
    from Autodesk.Revit import DB
except Exception as e:
    print("Error importing Revit API: {}".format(e))
    
# Import custom module with error handling
try:
    import proDUCKtion
    proDUCKtion.validify()
except Exception as e:
    print("Error in proDUCKtion module: {}".format(e))



from pyrevit import script


print ("\n\n\n\nOKOKOK!")
def test_cpython():
    pass

if __name__ == "__main__":
    test_cpython()







