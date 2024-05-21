import os
import random
parent_folder = os.path.dirname(os.path.dirname(__file__))

import sys
sys.path.append(parent_folder)
import ENVIRONMENT
import ENVIRONMENT_CONSTANTS

import re



# import System # pyright: ignore
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
            
    def replace_LDrive_folder(self):
        if "b_Applied Computing" not in self.content:
            return

        
        pattern = 'r\"L:\\4b_Applied Computing\\01_Revit\\04_Tools\\08_EA Extensions\\([^\"]*)\"'
        def replacement(match):
            
            print ("\n\n")
            original = match.match(1)  # Capture the whole match
            print (original)
            dynamic_part = match.group(1)  # Capture the dynamic part

            new_path_start = '"{}\\'
            new_path_end = '".format(ENVIRONMENT.PUBLISH_FOLDER_FOR_REVIT)'
            new_syntax = new_path_start + dynamic_part + new_path_end

            # new_syntax = '"{}\\{}".format(ENVIRONMENT.PUBLISH_FOLDER_FOR_REVIT, "{}")'.format(dynamic_part)
            print (new_syntax)
            return new_syntax

        # Replace using the replacement function
        updated_content = re.sub(pattern, replacement, self.content)

        

      
        
        content = self.content
        self.save_content(content)
        


    
    def open_file(self):
        os.startfile(self.file_path)
        
    def save_content(self, content):
        self.is_modified = True
        
        print ("pretend to save content")
        return
        
        with open(self.file_path, "w") as f:
                f.write(content)
                



def fix_Ldrive_dependency_in_file(file_path):
    
    python_file = PythonFile(file_path)

    
    if  python_file.content:
    
        
        python_file.replace_LDrive_folder()
        
        if python_file.is_modified:
            python_file.open_file()
        
    

    return python_file.is_modified
   

            
def fix_Ldrive_dependency():
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
    # map(fix_Ldrive_dependency_in_file, to_do_list)
    count = 0
    ceiling_limit = min(3, len(to_do_list))

    for i,path in enumerate(to_do_list):
        print ("\n\n{}/{}".format(i+1, len(to_do_list)))
        is_modifed = fix_Ldrive_dependency_in_file(path)
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
    fix_Ldrive_dependency()