import sys
sys.path.append("..\lib")
import EnneadTab
import os
import re

META_FILE_FOLDER = r"L:\\4b_Applied Computing\\03_Rhino\\12_EnneadTab for Rhino\Demo Files\\test folder for meta file"

class  MetaData:
    def __init__(self):
        self.used_id = [0,1,2,3,5]
        self.used_id = []
        self.meta_file_folder = META_FILE_FOLDER
        for file in os.listdir(self.meta_file_folder):
            #print file
            #print get_file_name(file)
            self.used_id.append(get_file_name(file))
        
        #print "meta_list = "
        #print self.used_id
        #self.used_id = [int(x) for x in self.used_id]


    def get_new_index(self):
        new_index = 0
        while True:
            formated_index = str(new_index).zfill(5)
            if formated_index not in self.used_id:
                self.used_id.append(formated_index)
                # self.create_meta_file(formated_index)
                #print "current used id list = {}".format(self.used_id)

                return formated_index
            new_index += 1 


class FileData:
    def __init__(self, formated_index, full_path):
        self.index = formated_index
        self.full_path = full_path
        self.meta_file_folder = META_FILE_FOLDER

    def create_meta_file(self):
        with open("{}\\{}.meta".format(self.meta_file_folder, self.index), "w") as f:
            f.write(self.full_path)

def get_file_name(file):
    return os.path.splitext(file)[0]


@EnneadTab.ERROR_HANDLE.try_catch_error
def index_all_file():
    folder = r"L:\\4b_Applied Computing\\03_Rhino\\02_Block Library"
    folder = r"L:\\4b_Applied Computing\\03_Rhino\\12_EnneadTab for Rhino\Demo Files\\test folder for indexing"

    #print folder
    #print 123

    data_base = MetaData()
    unique_extension = set()
    for (root, dirs, files) in os.walk(folder):
        print("#####root = {}, dirs = {}, files = {}".format(root, dirs, files))
        for file in files:

            file_name, extension = os.path.splitext(file)

            # extension ignore list
            if extension.lower() in [".dll", ".gha", ".ghuser", ".db", ".lnk"]:
                continue

            unique_extension.add(extension)
            print(file_name)
            # need to use regex to check format is same as _[]
            pattern = re.compile(r"(.+)_\[([0-9]+?)\]")
            #there was a stupid mistake to check only 1-9, but actually should check 0-9. This is fixed now.
            x = pattern.search(file_name)
            
            # print x
            # print x.group(2)
            if x is not None:#match exist, so this have been indexed in the past, 
                #but later still need to check if meta info valid.
                formated_index = (x.group(2))
                if validate_index(formated_index, file):
                    continue
                    

            
            
            new_index = data_base.get_new_index()
            new_name = "{}_[{}]".format(file_name, new_index)
            print("***{0}{2}-->{1}{2}".format(file_name, new_name, extension) )
            old_path = "{}\{}".format(root, file)
            new_path = "{}\{}{}".format(root, new_name, extension)
            try:
                os.rename(old_path, new_path)
            except Exception as e:
                print("Cannot rename file for {}, error = {}".format(old_path, e))
            this_file_data = FileData(new_index, new_path)
            this_file_data.create_meta_file()
    
    print("\n\n***********************\n\n")
    print("unique extension found = ")
    print(sorted(list(unique_extension)))

def validate_index(formated_index, source_path):
    print("&& validating index meta file")
    print(formated_index)
    print(source_path)
    print(META_FILE_FOLDER)
    check_address = os.path.join(META_FILE_FOLDER ,"{}.meta".format(formated_index))
    print(check_address)
    if not os.path.exists(check_address):
        return False
    with open(check_address, "r") as f:
        lines = f.readlines()
        print(lines)
        print("&& validating end")

        #lines = lines.split("\n")
        if lines[0] == source_path:
            return True

    """
    replace_text = source_path
    for temp in lines[1:]:
        replace_text += "\n{}".format(temp)
    """
    replace_text = [source_path].extend(lines[1:])
    with open(check_address, "w") as f:
        f.writelines(replace_text)

    return True

if __name__ == "__main__":
    index_all_file()