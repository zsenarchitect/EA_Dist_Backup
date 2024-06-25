import os 
import imp

parent_folder = os.path.dirname(os.path.realpath(__file__))

def is_good(x):
    if x.startswith("_"):
        return False
    if not  x.endswith(".py"):
        return False
    if "NOT_IN_USE" in x:
        return False
    return True
    

Scripts = filter(is_good, os.listdir(parent_folder))


script_paths = [os.path.join(parent_folder, x) for x in Scripts]
print(script_paths)

def get_help_doc(script_path):
    file_module_name = os.path.basename(script_path).split(".py")[0]
    try:
        module = imp.load_source(file_module_name, script_path)
        return module.__doc__
    except:
        return "There are some warnings need to be fixed first."


HelpDocs = [get_help_doc(x) for x in script_paths]