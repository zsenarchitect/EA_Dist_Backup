#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Revit have this default behaviour to automatic apply property panel data when you change field. You can disable that feature so it only apply update after you clicked apply or move the mouse out of the property panel entirely. This is helpful for multiple data entrying."
__title__ = "Disable Auto Apply"
__context__ = 'zero-doc'
# from pyrevit import forms #
from pyrevit import script #

import ENNEAD_LOG
import EnneadTab
import os
import io
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
# doc = __revit__.ActiveUIDocument.Document # pyright: ignore

def OLD_disable_auto_apply():
    for version in [2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]:
        folder_path = "{}\Roaming\Autodesk\Revit\Autodesk Revit {}".format(EnneadTab.FOLDER.get_appdata_folder(), version)
        if not os.path.exists(folder_path):
            continue
        print("\n\n##################")
        print(folder_path)
        file = "{}\Revit.ini".format(folder_path)
        if not os.path.exists(file):
            continue
        with io.open(file, "r", encoding='UTF-16 LE') as f:
            lines = f.readlines()
            content = f.read()

        content = content.replace("DisableMppAutoApply=0", "DisableMppAutoApply=1")
        if "DisableMppAutoApply" not in content:
            print(123)
            content = content.replace("UserInterface]", "UserInterface]\nDisableMppAutoApply=1")
        #content = content.replace("DisplayRecentFilesPage=1", "DisplayRecentFilesPage=0")
        print(content)
        continue

        with io.open(file, "w", encoding='UTF-16 LE') as f:
            f.write(content)


        # print isinstance(lines, list)
        continue

















        out = ""
        for line in lines:
            #print line
            if "DisableMppAutoApply" in line:
                print(line)
                line = line.replace("DisableMppAutoApply=0", "DisableMppAutoApply=1")
                print(line)


            if "DisplayRecentFilesPage" in line:
                print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
                print(line)
                line = line.replace("DisplayRecentFilesPage=1", "DisplayRecentFilesPage=0")
                print("++++++++++++++++++++++++++++")
                print(line)

            out += line

        print("**************************")
        #print out



        """"""
        copy_file = "{}\Revit - Copy.ini".format(folder_path)
        if not os.path.exists(copy_file):
            continue
        with io.open(copy_file, "r", encoding='UTF-16 LE') as f:
            copy_lines = f.readlines()

        for copy_line in copy_lines:
            if not copy_line in lines:
                print(copy_line)
        """"""









        continue
        with io.open(file, "w", encoding='UTF-16 LE') as f:
            f.write(out)








    """
    t = DB.Transaction(doc, __title__)
    t.Start()
    $$$$$$$$$$$$$$$$$$$
    t.Commit()
    """
def OLD2_disable_auto_apply():
    for version in [2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]:
        folder_path = "{}\Roaming\Autodesk\Revit\Autodesk Revit {}".format(EnneadTab.FOLDER.get_appdata_folder(), version)
        if not os.path.exists(folder_path):
            continue
        print("\n\n##################")
        print(folder_path)
        file = "{}\Revit.ini".format(folder_path)
        if not os.path.exists(file):
            continue
        with io.open(file, "r", encoding='UTF-16 LE') as f:
            lines = f.readlines()


        OUT = []
        for line in lines:
            #print "----------{}".format(line)
            if "DisableMppAutoApply" in line:
                print("skipping")
                continue
            OUT.append(line)
            if "[UserInterface]" in line:
                OUT.append("DisableMppAutoApply=1\n")
                #OUT.append(line.replace("[UserInterface]", "DisableMppAutoApply=1").encode('utf-16 le'))


                #print "DisableMppAutoApply=1\n"
                #print "DisableMppAutoApply=1\n".encode('UTF-16 LE')
                #print "DisableMppAutoApply=1\n".decode('UTF-16 LE')
                #print "DisableMppAutoApply=1\n".decode("utf-8").encode("utf-16")
                print("adding")
        #content = content.replace("DisplayRecentFilesPage=1", "DisplayRecentFilesPage=0")
        #print OUT


        with io.open(file, "w", encoding='UTF-16 LE') as f:
            f.writelines(OUT)


def disable_auto_apply():
    EnneadTab.REVIT.REVIT_FORMS.notification(main_text = "To disable AutoApply, we need to mark 'DisableMppAutoApply=1' in the revit.ini file for each revit version. \nThe tool will do that for you, but the .ini file will be rejected and reset unless it is entered in a very specific unicode format.\n\nTo by pass that restriction, I will open each revit.ini file after the modification, all you need to do is ##SAVE and CLOSE## each .ini file and restart your revit.")
    version = 2019
    for _ in range(10):
        version += 1
        folder_path = "{}\Roaming\Autodesk\Revit\Autodesk Revit {}".format(EnneadTab.FOLDER.get_appdata_folder(), version)
        if not os.path.exists(folder_path):
            continue
        print("\n\n##################")
        print(folder_path)
        file = "{}\Revit.ini".format(folder_path)
        if not os.path.exists(file):
            continue
        with io.open(file, "r", encoding='UTF-16 LE') as f:
            lines = f.readlines()


        OUT = []
        for line in lines:
            #print "----------{}".format(line)
            if "DisableMppAutoApply" in line:
                print("skipping")
                continue
            OUT.append(line)
            if "[UserInterface]" in line:
                OUT.append("DisableMppAutoApply=1\n")

                print("adding")

        with io.open(file, mode="w", encoding="utf-16-le", newline="\n") as f:#newline="\r\n"
            #file.write('\xff\xfe')
            #file.write('\ufeff')  # Add the BOM
            f.writelines(OUT)

        print(file)
        EnneadTab.EXE.open_file_in_default_application(file)

        """
        Note that the newline parameter is set to "\r\n" to ensure that the line endings are correctly handled in Windows. The '\ufeff' character sequence writes the BOM to the beginning of the file.
        By adding the BOM to the beginning of the file, you can ensure that the text editor or viewer correctly interprets the UTF-16 LE encoding and displays the text without extra white space between letters.

        The extra white space between letters that you see in the added line could be caused by the way the text editor or viewer is interpreting the UTF-16 LE encoding.
        UTF-16 LE encoding uses two bytes to represent each character. However, some text editors or viewers may not recognize the byte order mark (BOM) at the beginning of the file that specifies the endianness of the encoding. As a result, the editor or viewer may incorrectly interpret the byte order and display extra white space between letters.
        To fix this issue, you can try adding the BOM to the beginning of the file manually by writing the byte sequence b'\xff\xfe' to the file before writing the lines.

        """











################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    disable_auto_apply()
    ENNEAD_LOG.use_enneadtab(coin_change = 20, tool_used = __title__.replace("\n", " "), show_toast = True)
