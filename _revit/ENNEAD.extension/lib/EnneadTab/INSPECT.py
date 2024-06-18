import sys

class MyFinder:
    def find_spec(self, fullname, path, target=None):
        print("Looking for:", fullname, " at ", path)

        # Return None to fall back to the next finder in the list
        return None

# Adding the custom finder to the start of the meta path
# sys.meta_path.insert(0, MyFinder())

# Trying to import a module
# import math


"""note to self
this is to check if the module is loaded with specific version.

sometimes same module name are are hard to tell, such as which folder is current enneadtab loading from, L or local""" 