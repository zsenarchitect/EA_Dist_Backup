
#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "DO NOT USE"
__title__ = "Publish &\nArchive(Classic)"
__context__ = "zero-doc"
# from pyrevit import forms #
from pyrevit import script #

from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
#doc = __revit__.ActiveUIDocument.Document # pyright: ignore
import distutils

import os
import shutil


def get_file_extension_from_path(file_path):
    return os.path.splitext(file_path)[1]


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

def is_file_exist_in_folder(check_file_name, folder):


    for file_name in os.listdir(folder):
        #ERROR_HANDLE.print_note(file_name)
        if check_file_name == file_name:
            return True
    return False


def copydir(source, dest, is_beta_tester = False):
    """Copy a directory structure overwriting existing files"""
    for root, dirs, files in os.walk(source):
        """
        print("\n#########")
        print(root)
        print(dirs)
        print(files)
        continue
        """
        if not is_beta_tester:
            if "EnneadTab_Beta" in root:
                continue


        if not os.path.isdir(root):
            os.makedirs(root)

        for file in files:
            rel_path = root.replace(source, '').lstrip(os.sep)
            dest_path = os.path.join(dest, rel_path)

            if not os.path.isdir(dest_path):
                os.makedirs(dest_path)

            try:
                file1 = os.path.join(root, file)
                file2 = os.path.join(dest_path, file)
                if is_file_exist_in_folder(file, dest_path):
                    if get_file_extension_from_path(file).lower() in [".txt", ".py", ".json", ".xaml"]:
                        if is_file_content_same(file1, file2):
                            #print "skip same content file: {}".format(file1)
                            #print "skip same content file"
                            continue

                shutil.copyfile(file1, file2)
                #print "{}  >>>  {}".format(file1, file2)
            except Exception as e:
                print("##")
                print(file,os.path.join(root, file),os.path.join(dest_path, file))
                print (e)
                print("\n\n")
################## main code below #####################
output = script.get_output()
output.close_others()
print("disabled!!!!")
script.exist()

"""
should ask if want to publish beta only or both beta+stable
"""
if 1 > 10:
    src = r"C:\Users\szhang\github\EnneadTab-for-Revit\ENNEAD.extension"
    #dst = r"L:\4b_Applied Computing\01_Revit\04_Tools\08_EA Extensions\Published\test folder_ennead_extension"
    dst = r"L:\4b_Applied Computing\01_Revit\04_Tools\08_EA Extensions\Published\ENNEAD.extension"
    beta_tester_dst = r"L:\4b_Applied Computing\01_Revit\04_Tools\08_EA Extensions\Published_Beta_Version\ENNEAD.extension"

    import datetime
    now = datetime.datetime.now()
    year, month, day = '{:02d}'.format(now.year), '{:02d}'.format(now.month), '{:02d}'.format(now.day)
    archive_dst = r"L:\4b_Applied Computing\01_Revit\04_Tools\08_EA Extensions\Published\_Archive\{}{}{}_ENNEAD.extension".format(year, month, day)
    SH_version_dst = r"L:\4b_Applied Computing\01_Revit\04_Tools\08_EA Extensions\Published_SH_VERSION\VERSION_{}_{}_{}\SH_ENNEAD.extension".format(year, month, day)
    #distutils.dir_util.copy_tree(src, dst, preserve_mode=1, preserve_times=1, preserve_symlinks=0, update=0, verbose=0, dry_run=0)


    #copytree(src, dst)
    copydir(src, dst)
    copydir(src, beta_tester_dst, is_beta_tester = True)
    copydir(src, archive_dst)

    if not os.path.exists(SH_version_dst):
        copydir(src, SH_version_dst)
        print("SH version created")

    print("\n\nTool finished")
    output.self_destruct(20)
