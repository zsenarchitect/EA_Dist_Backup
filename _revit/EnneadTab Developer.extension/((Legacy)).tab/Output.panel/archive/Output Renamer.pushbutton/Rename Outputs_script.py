import os
import sys
import os.path as op

from pyrevit import UI
from pyrevit import forms


__title__ = 'Rename\nOutput Files'
__context__ = 'zero-doc'
__doc__ = 'This button renames all type of files exported from Revit and removes the Central ' \
          'model name from the names. The tool will ask for a folder ' \
          'containing the file.\n\n' \
          'Left-Click: \nRename DWG, PDF, JPG\n'\
          'Shift-Click:\nRename DWG only\n\n'\
          'IMPORTANT!: use auto-long name from the print/export setting.'\



# if user shift-clicks, rename dwg only
# otherwise ask for a folder containing the PDF files
extension_checker = [".DWG",".JPG",".PDF"]
if __shiftclick__:
	extension_checker.remove( ".PDF")
	extension_checker.remove( ".JPG")

title_line = 'Pick the folder that has all the auto-named the files. For CAD file remember to use auto-long name when exporting.'
with forms.WarningBar(title = title_line):

    basefolder = forms.pick_folder(title = title_line)



def renamefile(file):
    import re
    r = re.compile('(?<=Sheet - )(.+)')
    fname = r.findall(file)[0]
    r = re.compile('(.+)\s-\s(.+)')
    fnameList = r.findall(fname)
    return fnameList[0][0] + ' - ' + fnameList[0][1].upper()


def delete_pcp_file(basefolder):
    filenames = os.listdir(basefolder)
    PCP_file_found = False
    pcp_count = 0
    for current_file in filenames:
        ext = op.splitext(current_file)[1].upper()
        if ext == ".PCP":

            if PCP_file_found == False:#this is the first time find a pcp file
                res = forms.alert(msg = ".pcp file found in the folder.\nThis is usually the result of DWG export. They are safe to delete. \nDo you want to delete them?", options = ["Yes, Delete Them.", "No, Leave Them In My Folder."])
                if "Yes" in res:
                    PCP_file_found = True#set this to True and never ask again
                else:
                    break#break from for-loop
            else:#this is second time or more to find pcp, no need to ask questions.
                pass

            os.remove(op.join(basefolder, current_file))
            pcp_count+=1

    forms.alert("{} .pcp files removed.".format(pcp_count))

def delete_ps_file(basefolder):
    filenames = os.listdir(basefolder)
    ps_file_found = False
    ps_count = 0
    for current_file in filenames:
        ext = op.splitext(current_file)[1].upper()
        if ext == ".PS":

            if ps_file_found == False:#this is the first time find a ps file
                res = forms.alert(msg = ".ps file found in the folder.\nNot the photoshop PSD file!\nThis is usually the result of DWG export. They are safe to delete. \nDo you want to delete them?", options = ["Yes, Delete Them.", "No, Leave Them In My Folder."])
                if "Yes" in res:
                    ps_file_found = True#set this to True and never ask again
                else:
                    break#break from for-loop
            else:#this is second time or more to find ps, no need to ask questions.
                pass

            os.remove(op.join(basefolder, current_file))
            ps_count+=1

    forms.alert("{} .ps files removed.".format(ps_count))

if basefolder:
    sheetcount = 0

    # list files and find the files in the base folder with extension types in "extension_checker" list
    filenames = os.listdir(basefolder)
    fail_list = []
    for current_file in filenames:
        ext = op.splitext(current_file)[1].upper()
        if ext in extension_checker and ('Sheet' in current_file):
            # if extension in checklist make a new file name and rename the exisitng file
            newfilename = renamefile(current_file)
            try:
                os.rename(op.join(basefolder, current_file),
                          op.join(basefolder, newfilename))
                sheetcount += 1
            except Exception as e:
                print("Unexpected error:", sys.exc_info()[0], "-->", current_file)
                fail_list.append(current_file)

    if len(fail_list) > 0:
        fail_text = 'Those files are skipped, because a file with same destination name '\
                    'is in the same folder.\n'
        for item in fail_list:
            fail_text += "\n{}".format(item)
    else:
        fail_text = ""
    # let user know how many files have been renames
    forms.alert(msg = '{0} FILES RENAMED.'.format(sheetcount), sub_msg = fail_text)


    delete_pcp_file(basefolder)
    delete_ps_file(basefolder)
