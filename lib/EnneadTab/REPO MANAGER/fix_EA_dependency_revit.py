import os
import random
parent_folder = os.path.dirname(os.path.dirname(__file__))

import sys
sys.path.append(parent_folder)
import ENVIRONMENT





# import System
# System.Windows.Forms.Clipboard.SetText(TRY_CATCH_DECOR)

# set windows clipboard text

class PythonFile:
    def __init__(self, file_path):
        
        print (file_path)
        
        self.file_path = file_path
        try:
            with open(file_path, "r") as f:
                self.content = f.read()
        except:
            print ("!!There is nothing to read")
            self.content = None
            
        self.is_modified = False
            
    def replace_module_folder(self):
        OLD_MODULE_FOLDER = r"sys.path.append(r'L:\4b_Applied Computing\03_Rhino\12_EnneadTab for Rhino\Dependency Modules')"
        NEW_MODULE_FOLDER = """import EnneadTab
sys.path.append(EnneadTab.ENVIRONMENT.DEPENDENCY_FOLDER_LEGACY)"""
        if OLD_MODULE_FOLDER not in self.content:
            return
        
        content = self.content.replace(OLD_MODULE_FOLDER, NEW_MODULE_FOLDER)
        self.save_content(content)
        
        
        
    def insert_lib_path(self):

        if "import EnneadTab"  in self.content:
            return
            
        print ("--Adding new lib path")
        lib_path = """
import EnneadTab
"""
        # print (lib_path)
        content = lib_path + self.content
        self.save_content(content)



    def replace_old_EA(self):
        OLD_DEPEDENT_VALUE = "import EA_UTILITY"
        NEW_DEPEDENT_VALUE = "import EA_UTILITY\nimport EnneadTab"
        if OLD_DEPEDENT_VALUE in self.content and "import EnneadTab" not in self.content:
            print ("^^Replace old depdent value")
            content = self.content.replace(OLD_DEPEDENT_VALUE, NEW_DEPEDENT_VALUE)
                
            self.save_content(content)


    def add_deco(self):
        TRY_CATCH_DECOR = "@EnneadTab.ERROR_HANDLE.try_catch_error"
        if TRY_CATCH_DECOR  in self.content:
            return
        print ("**Adding try catch decor")
        
        self.open_file()

    
    def open_file(self):
        os.startfile(self.file_path)
        
    def save_content(self, content):
        self.is_modified = True
        
        print ("pretend to save content")
        return
        
        with open(self.file_path, "w") as f:
                f.write(content)
                



def fix_EA_dependency_in_file(file_path):
    
    python_file = PythonFile(file_path)

    
    if  python_file.content:
    
        # python_file.replace_old_EA()
        # python_file.insert_lib_path()
        
        python_file.add_deco()
        # python_file.replace_module_folder()
        
        if python_file.is_modified:
            python_file.open_file()
        
    

    return python_file.is_modified
   

            
def fix_EA_dependency():
    max_count = 1000
    count = 0
    to_do_list = []
    
    
    
    
    root_folder = ENVIRONMENT.WORKING_FOLDER_FOR_REVIT
    # get all the python file in the root directory of this repo, iterate thru each of them and find if there are "EA." in there.
    for root, dirs, files in os.walk(root_folder):
        if count >= max_count:
            break
        # print (files)
        
        if root.startswith(ENVIRONMENT.CORE_MODULE_FOLDER_FOR_REVIT):
            continue
        
        
        if "EnneadTab Developer" in root:
            continue
        
        if "Ennead.tab" not in root:
            continue
        
        if "archive"  in root:
            continue
        
        
        
        for file in files:
            if not file.endswith(".py"):
                continue
            if file == "EA_UTILITY.py":
                continue
            if file == "button.py":
                    continue
                
            if should_ignore(os.path.join(root, file)):
                continue
            
            
            
            count += 1
            to_do_list.append(os.path.join(root, file))
                    
    
    # print (to_do_list)    
    random.shuffle(to_do_list)
    print ("total bad files in to do list = {}".format(len(to_do_list)))
    # map(fix_EA_dependency_in_file, to_do_list)
    count = 0
    ceiling_limit = min(150, len(to_do_list))

    for i,path in enumerate(to_do_list):
        print ("\n\n{}/{}".format(i+1, len(to_do_list)))
        is_modifed = fix_EA_dependency_in_file(path)
        if is_modifed:
            count += 1
        
        
        if count >= ceiling_limit:
            break


    
def should_ignore(file_path):
    if "GH_python" in file_path:
        return True
    if "Fun" in file_path:
        return True
    
    
    return False

##############################
if __name__ == "__main__":
    fix_EA_dependency()