#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Randomly open 10 files that have no documentation"
__title__ = "Work On\nDocumentation"
__context__ = "zero-doc"
from pyrevit import forms #
from pyrevit import script #

import sys
sys.path.append(r"C:\Users\szhang\github\EnneadTab-for-Revit\ENNEAD.extension\lib")
import ENNEAD_LOG
import os
import random
import EnneadTab
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
uidoc = EnneadTab.REVIT.REVIT_APPLICATION.get_uidoc()
doc = EnneadTab.REVIT.REVIT_APPLICATION.get_doc()



def search_files(keyword, folder):
    matching_files = []
    for root, dirs, files in os.walk(folder):
        for file in files:
            if "template" in file:
                continue
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    contents = f.read()

                    # if "doc = EnneadTab.REVIT.REVIT_APPLICATION.get_doc()" in contents:
                    #     continue
                    
                    
                    if keyword in contents:
                        #print "Found keyword '%s' in file: %s" % (keyword, file_path)
                        matching_files.append(file_path)

    if len(matching_files) > 0:
        print ("Totally {} file with bad documentation".format(len(matching_files)))
        random_files = random.sample(matching_files, min(20, len(matching_files)))
        print ("Opening randomly selected files:")
        for file in random_files:
            print (file)
            os.startfile(file)
    else:
        print ("No files found containing keyword '%s'" % keyword)


def work_on_documentation():


    search_text = forms.ask_for_string(default = 'Sen Zhang has not writed documentation for this tool, but he should!', prompt = "What keyword to search?")
    if not search_text:
        return

    search_files(search_text, folder = "{}\ENNEAD.extension".format(EnneadTab.ENVIRONMENT.WORKING_FOLDER_FOR_REVIT))
    #search_files('#ideas', folder = "{}\ENNEAD.extension".format(EnneadTab.ENVIRONMENT.WORKING_FOLDER_FOR_REVIT))
    #search_files('get_detail_groups_by_name', folder = "{}\ENNEAD.extension".format(EnneadTab.ENVIRONMENT.WORKING_FOLDER_FOR_REVIT))

################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    work_on_documentation()
    ENNEAD_LOG.use_enneadtab(coin_change = 20, tool_used = __title__.replace("\n", " "), show_toast = True)
