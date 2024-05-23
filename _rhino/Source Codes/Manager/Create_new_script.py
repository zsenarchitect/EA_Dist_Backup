import sys
sys.path.append("..\lib")
import EA_UTILITY as EA
import EnneadTab
import rhinoscriptsyntax as rs

"""
### TO-DO:
- Autofill initials into to-do list template throws error
  - # dev_initials = EnneadTab.USER.get_dev_value_from_username(username, "initials")
#### Assigned to: **CM**
"""

@EnneadTab.ERROR_HANDLE.try_catch_error
def create_new_button():
    # get new button name
    func_name = rs.StringBox(message = "Type in the name for new script", default_value = "New Button Name", title = "Create new tool")

    # pick folder location
    target_folder = rs.BrowseForFolder(folder = r"{}\Source Codes".format(EnneadTab.ENVIRONMENT.get_EnneadTab_For_Rhino_root()), message = "New script location of container pushbutton", title = "New script location of container pushbutton")

    #print folder
    new_location = "{}\{}.py".format(target_folder, func_name)
    #print new_location

    # copy from template to address
    # secure folder first
    #EnneadTab.FOLDER.secure_folder(target_folder)

    source_folder = r"{}\Source Codes\Template Scripts".format(EnneadTab.ENVIRONMENT.get_EnneadTab_For_Rhino_root())
    template_file = "start new script.py"
    search_file = template_file
    new_file_name =  func_name + ".py"
    EnneadTab.FOLDER.copy_file("{}\{}".format(source_folder, template_file), "{}\{}".format(target_folder, new_file_name))


    #EnneadTab.FOLDER.rename_file_in_folder(search_file, new_file_name, target_folder)


    # edit main func name
    with open(new_location) as f:
        lines = f.readlines()

    new_lines = []
    for line in lines:
        line = line.replace('run()', '{}()'.format(func_name))
        new_lines.append(line)

    with open(new_location, "w") as f:
        f.write("".join(new_lines))

    #open lib on the side

    EnneadTab.EXE.open_file_in_default_application(new_location)


    rhino_button_template = r"{}\Source Codes\Manager\button_content_template.txt".format(EnneadTab.ENVIRONMENT.get_EnneadTab_For_Rhino_root())
    with open(rhino_button_template) as f:
        lines = f.readlines()

    new_lines = []
    # username = EnneadTab.USER.get_user_name()
    # dev_initials = EnneadTab.USER.get_dev_value_from_username(username, "initials")
    for line in lines:
        # if "#### Assigned to: **{}**" in line:
        #     line = line.format(dev_initials)
        
        if "folder = " in line:
            # get the folder name from folder path
            folder = target_folder.split("\\")[-1]
            line = 'folder = "{}"\n'.format(folder)

        if "file_name = " in line:
            line = 'file_name = "{}"\n'.format(func_name)
        print(line)
        new_lines.append(line)

    with open(rhino_button_template, "w") as f:
        f.write("".join(new_lines))
    EnneadTab.EXE.open_file_in_default_application(rhino_button_template)


"""
! _-RunPythonScript (
import sys
sys.path.append("..\lib")
import EnneadTab

root = EnneadTab.ENVIRONMENT.get_EnneadTab_For_Rhino_root()
folder = "XXX"
file_name = "AAA"
path = "{}\Source Codes\{}\{}.py".format(root, folder, file_name)

import imp
ref_module = imp.load_source(file_name, path)
ref_module .BBB()
)
"""


################## main code below #####################


if __name__ == "__main__":
    #create_new_button()
    username = USER.get_user_name()
    print(EnneadTab.USER.get_dev_value_from_username(username, "initials"))
