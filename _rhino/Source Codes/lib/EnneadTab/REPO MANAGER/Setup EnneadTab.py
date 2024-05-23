import os
"""use this to make a standalone exe that can get user started without looking for toturials any where
clone repo, 
point pyrevit to this?
point rhino to this?

no outside dependency, no L drive denpendy.
"""


"""this is given up becasue cannot figure out the git-clone issue"""

# check this post about the CLI deployment
# https://discourse.pyrevitlabs.io/t/install-and-update-pyrevit-extension-from-a-private-repo/60/30

# how to get your token is here
# https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens

def create_bat_file():
    # Define the batch commands as a multi-line string
    batch_commands = """
pyrevit extend ui ENNEAD "https://github.com/Ennead-Architects-LLP/EnneadTab-for-Revit.git" --dest="{}" --token= "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"
pause""".format(r"C:\Users\szhang\AppData\Roaming\pyRevit\Extensions")
    batch_commands = """
pyrevit extend --debug EnneadTab-for-Revit "https://github.com/Ennead-Architects-LLP/EnneadTab-for-Revit.git" --token= "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"
"""
    batch_commands = """
pyrevit extend pyApex 
"""

    # create a bat file on the desktop
    file_path = os.path.join(os.path.expanduser("~"), "Desktop", "EnneadTab.bat")

    # Create the .bat file and write the batch commands to it
    with open(file_path, 'w') as file:
        file.write(batch_commands)

    print(f"Created {file_path}")

    os.startfile(file_path)



if __name__ == "__main__":
    create_bat_file()

    #os.system('cmd /c "pyrevit extensions update EnneadTab-for-Revit --token="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""')



"""2024-01-17 good discovery
prepare a .bat file that can change the 
C:\Users\szhang\AppData\Roaming\pyRevit-Master\extensions\extensions.json
by inserting new item

this git repo only has the final content, it is safe to be public and distribute because each script is made as a dll
the _script.py only function is to call dll


then user go to pyrevit extension setting to install this extension.



"""


"""
2024-01-18
change it to a exe single file standalone so it can handle all exception
use tkiner as well
    1. check if pyrevit json extension file exist
    2. append new entry to dict and save
    3. prompt user to install from pyrevit extension
"""