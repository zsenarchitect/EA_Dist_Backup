#!/usr/bin/python
# -*- coding: utf-8 -*-
import shutil
import os
import ERROR_HANDLE
import ENVIRONMENT
import USER

def is_file_content_same(file1, file2):
    try:
        with open(file1, 'r') as f1:
            content1 = f1.read()
        with open(file2, 'r') as f2:
            content2 = f2.read()

        if content1 == content2:
            return True
        else:
            return False
    except Exception as e:
        print (e)
        return False


def is_file_modification_date_same(file1, file2):
    ctime1 = os.path.getctime(file1)
    mtime1 = os.path.getmtime(file1)
    ctime2 = os.path.getctime(file2)
    mtime2 = os.path.getmtime(file2)

    if ctime1 == ctime2 and mtime1 == mtime2:
        return True
    else:
        return False

def should_override_file(file1, file2):
    #ctime1 = os.path.getctime(file1)
    mtime1 = os.path.getmtime(file1)
    #ctime2 = os.path.getctime(file2)
    mtime2 = os.path.getmtime(file2)

    if mtime1 < mtime2:# detination file is newer than the source or equal, do not override
        print ("!!!!!!!!!!!!!!!{}: skip files dest version newer than source version".format(file1))
        return False
    elif mtime1 == mtime2:
        print ("$$$$$${}: skip files dest version same as source version".format(file1))

        return False
    else:
        return True


def copy_dir(source, dest, show_progress = False, progress_bar_note = "", ignore_keywords = []):
    """Copy a directory structure overwriting existing files.
    ignore_keywords: list of keywords"""

    count = 0
    max = 0
    failed_files = dict()
    for root, dirs, files in os.walk(source):
        max += len(files)


    if ENVIRONMENT.is_Rhino_environment():
        import rhinoscriptsyntax as rs
        rs.StatusBarProgressMeterShow(label = "[{}] Total Files to Copy <{}>  ".format(progress_bar_note,  max), lower = 0, upper = max, embed_label = True, show_percent = True)

    #try to use progress bar
    for root, dirs, files in os.walk(source):

        # skip copy if find any keyword in the root path
        should_skip = False
        for keyword in ignore_keywords:
            if keyword in root:
                should_skip = True
                continue
        if should_skip:
            continue


        if not os.path.isdir(root):
            os.makedirs(root)




        for file in files:
            count += 1


            if ENVIRONMENT.is_Rhino_environment():
                rs.StatusBarProgressMeterUpdate(position = count, absolute = True)

            rel_path = root.replace(source, '').lstrip(os.sep)
            if ".git" in root or ".vs" in root or ".pyc" in file:
                ERROR_HANDLE.print_note( "####Skip .git and .vs folder and skip .pyc file: {}".format(count))
                continue


            dest_path = os.path.join(dest, rel_path)

            if not os.path.isdir(dest_path):
                os.makedirs(dest_path)

            try:
                if show_progress:
                    print ("{}/{}".format(count, max))

                file1 = os.path.join(root, file)
                file2 = os.path.join(dest_path, file)
                if is_file_exist_in_folder(file, dest_path):
                    if is_file_modification_date_same(file1, file2):
                        print ("{}: skip same date file".foramt(count))
                        continue
                    
                    # if not should_override_file(file1, file2):
                    #     continue

                    if get_file_extension_from_path(file).lower() in [".txt", ".py", ".json", ".xaml"]:
                        if is_file_content_same(file1, file2):
                            print ("{}: skip same content file".format(count))
                            continue
                shutil.copyfile(file1, file2)
                print ("{}: {}  >>>  {}".format(count,file1, file2))
            except Exception as e:
                if "Thumbs.db" in file:
                    pass
                else:
                    ERROR_HANDLE.print_note( "##Cannot Copy file in folder")
                    ERROR_HANDLE.print_note( "Filepath = {}".format(file))
                    ERROR_HANDLE.print_note( "Filepath old = {}".format(os.path.join(root, file)))
                    ERROR_HANDLE.print_note( "Filepath target = {}".format(os.path.join(dest_path, file)))
                    ERROR_HANDLE.print_note( str(e))
                    print ("\n\n")
                    failed_files[file] = "Filepath old = {}, Filepath target = {}. {}".format(os.path.join(root, file), os.path.join(dest_path, file), e)


    if ENVIRONMENT.is_Rhino_environment():
        rs.StatusBarProgressMeterHide()

    if len(failed_files.keys()) > 0:
        print ("\n\nFollowing file failed to copy.")
        for file, detail in failed_files.items():
            print ("\n###")
            print(file)
            print (detail)

def copy_file(original_path, new_path):
    shutil.copyfile(original_path, new_path)

def copy_file_to_folder(original_path, target_folder):
    new_path = original_path.replace(get_folder_path_from_path(original_path), target_folder)
    try:
        shutil.copyfile(original_path, new_path)
    except Exception as e:
        print (e)

    return new_path


def copy_file_to_local_dump_folder(original_path, file_name = None):
    #print original_path
    if file_name is None:
        file_name = original_path.rsplit("\\", 1)[1]
    local_folder = get_EA_setting_folder() + "\\" + "Local Copy Dump"
    local_folder = secure_folder(local_folder)
    local_path = "{}\{}".format(local_folder, file_name)
    shutil.copyfile(original_path, local_path)

    return local_path




def get_file_extension_from_path(file_path):
    return os.path.splitext(file_path)[1]

def get_file_name_from_path(file_path):

    head, tail = os.path.split(file_path)
    return tail


def get_filenames_in_folder(folder):
    return os.listdir(folder)


def is_file_exist_in_folder(check_file_name, folder):


    for file_name in os.listdir(folder):
        #ERROR_HANDLE.print_note(file_name)
        if check_file_name == file_name:
            return True
    return False


def is_file_with_keywords_exist_in_folder(keyword_list, folder, ignore_file_list = None):
    ERROR_HANDLE.print_note("search file with keyword in folder")

    for file_name in os.listdir(folder):
        if file_name in ignore_file_list:
            continue
        ERROR_HANDLE.print_note("-find file: " + file_name)
        for keyword in keyword_list:
            ERROR_HANDLE.print_note("--try keyword: " + keyword)
            if keyword not in file_name:
                ERROR_HANDLE.print_note("---keyword not in file_name, not my file, try next file. ")
                break

        else:
            ERROR_HANDLE.print_note("---search all keywords, keyword not in file_name, not my file, try next file. ")
            continue
        ERROR_HANDLE.print_note("---return True, find good file: " + file_name)
        return True
    ERROR_HANDLE.print_note("return False, not any file has all keywords together.")
    return False


def get_folder_path_from_path(file_path):

    head, tail = os.path.split(file_path)
    return head


def get_revit_user_folder():
    folder =  r"L:\4b_Applied Computing\01_Revit\04_Tools\08_EA Extensions\Project Settings\Users"
    try:
        import DATA_FILE
        res = DATA_FILE.save_dict_to_json(
            dict(), folder + "\\SH_tester_account.json")
        if not res:
            folder = get_EA_local_dump_folder()
    except:
        folder = get_EA_local_dump_folder()
    finally:
        return folder

def get_user_folder():
    return "{}\Documents".format(os.environ["USERPROFILE"])

def get_appdata_folder():
    return "{}\AppData".format(os.environ["USERPROFILE"])


def get_EA_setting_folder():
    folder = get_user_folder() + "\EnneadTab Settings"
    return secure_folder(folder)

def get_EA_local_dump_folder():
    return get_special_folder_in_EA_setting("Local Copy Dump")

def get_EA_dump_folder_file(file_name):
    """include extension"""
    return "{}\{}".format(get_EA_local_dump_folder(), file_name)

def is_file_exist_in_dump_folder(file_name):
    return is_file_exist_in_folder(file_name, get_EA_local_dump_folder())

def remove_file_from_dump_folder(file_name):
    if is_file_exist_in_dump_folder(file_name):
        os.remove(os.path.join(get_EA_local_dump_folder(), file_name))

def get_special_folder_in_EA_setting(folder_name):
    folder = get_EA_setting_folder() + "\{}".format(folder_name)
    return secure_folder(folder)



def get_filepath_in_special_folder_in_EA_setting(folder_name, file_name):
    return get_special_folder_in_EA_setting(folder_name) + "\{}".format(file_name)

def is_path_exist(path):
    return os.path.exists(path)

def secure_folder(path):

    try:
        if os.path.exists(path):
            return path
        os.makedirs(path)

    except Exception as e:

        ERROR_HANDLE.print_note( "folder cannot be secured")
        ERROR_HANDLE.print_note(e)
        pass
    return path



def cleanup_folder(folder = "folder path",
                    extension = "extension"):

    filenames = os.listdir(folder)

    count = 0
    for current_file in filenames:
        ext = os.path.splitext(current_file)[1]
        if ext.upper() == extension.upper():
            try:
                os.remove(os.path.join(folder, current_file))
                count += 1
            except Exception as e:
                ERROR_HANDLE.print_note("Cannot delete file [{}] becasue error: {}".format(current_file, e))
    return count


def cleanup_name_in_folder(output_folder, desired_name, extension):
    """make sure the desired name of file is formated as such in the output folder.
    This is usually a requirement after export revit jpg becasue revit will auto append other name in the jpg export.

    Args:
        output_folder (str): folder to search
        desired_name (str): desired final name, also the name to search for among existing files in output folder. THIS NAME DOES NOT CONTAIN EXTENSION.
        extension (str): extension to lock search. THIS CONTAINS DOT, such as ".xxx"
    """
    
    
    remove_exisitng_file_in_folder(output_folder, desired_name + extension)

    #print keyword
    keyword = " - Sheet - "
    file_names = get_filenames_in_folder(output_folder)

    for file_name in file_names:
        if desired_name in file_name and extension in file_name.lower():
            #new_name = file_name.split(keyword)[0]
            new_name = desired_name
            #new_name = file_name.split(keyword)[0]

            try:
                os.rename(os.path.join(output_folder, file_name),os.path.join(output_folder, new_name + extension))

            except Exception as e:
                ERROR_HANDLE.print_note( "B:skip {} becasue: {}".format(file_name, e))


def rename_file_in_folder(search_file, new_file_name, folder):


    try:
        os.rename(os.path.join(folder, search_file),os.path.join(folder, new_file_name))
        return True
    except Exception as e:
        ERROR_HANDLE.print_note(e)
        return False


def remove_file_by_keyword_in_folder(folder, keyword, ignore_file_list = None):


    for file_name in os.listdir(folder):
        ERROR_HANDLE.print_note(file_name)
        if file_name in ignore_file_list:
            continue
        if string_contain_keywords(file_name, [keyword]):
            remove_exisitng_file_in_folder(folder, file_name)


def remove_exisitng_file_in_folder(folder, file_name):
    """remove a file from folder

    Args:
        folder (str): folder to search
        file_name (_type_): file name to search, CONTAINING DOT, such as "abcd.xxx".
    """

    if file_name not in os.listdir(folder):
        return
    try:
        os.remove(os.path.join(folder, file_name))
    except Exception as e:
        ERROR_HANDLE.print_note( "Cannot remove <{}> becasue of error: {}".format(file_name, e))





def get_script_file_folder():
    """get the parrent folder of script

    Returns:
        str: parent folder path
    """
    return os.path.dirname(__file__)



def compile_files(directory):
    import py_compile
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                py_compile.compile(filepath)


def remap_filepath_to_folder(full_file_path):
    """  
    
    remap  sccript path that point to Sen document---->to L drive
    

    Args:
        full_file_path (_type_): _description_

    Returns:
        _type_: _description_
    """
    if USER.is_revit_beta_tester():
        address = r"L:\\4b_Applied Computing\\01_Revit\\04_Tools\\08_EA Extensions\Published_Beta_Version\ENNEAD.extension"
    else:
        address = r"L:\\4b_Applied Computing\\01_Revit\\04_Tools\\08_EA Extensions\Published\ENNEAD.extension"

        
    return full_file_path.replace(r"C:\Users\szhang\github\EnneadTab-for-Revit\ENNEAD.extension", address)




#############
if __name__ == "__main__":
    print(__file__ + "   -----OK!")