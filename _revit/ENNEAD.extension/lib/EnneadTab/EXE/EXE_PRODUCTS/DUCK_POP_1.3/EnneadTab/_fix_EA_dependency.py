import os

OLD_VALUE = "import EA_UTILITY as EA"
NEW_VALUE = "import EA_UTILITY as EA\nimport EnneadTab"

def fix_EA_dependency_in_file(file_path):
    print (file_path)
    # os.startfile(file_path)
    # return
    with open(file_path, "r") as f:
        content = f.read()
        
    content = content.replace(OLD_VALUE, NEW_VALUE)
        
    with open(file_path, "w") as f:
        f.write(content)
        
    #os.startfile(file_path)
            

def fix_EA_dependency():
    max_count = 100
    count = 0
    to_do_list = []
    
    
    
    
    root_folder = r"C:\Users\szhang\github\EnneadTab-for-Rhino"
    # get all the python file in the root directory of this repo, iterate thru each of them and find if there are "EA." in there.
    for root, dirs, files in os.walk(root_folder):
        if count >= max_count:
            break
        # print (files)
        for file in files:
            if not file.endswith(".py"):
                continue
            with open(os.path.join(root, file), "r") as f:
                content = f.read()
                if OLD_VALUE in content and "import EnneadTab" not in content:

                    count += 1
                    to_do_list.append(os.path.join(root, file))
                    
    print (to_do_list)    
    map(fix_EA_dependency_in_file, to_do_list)


    
    

##############################
if __name__ == "__main__":
    fix_EA_dependency()