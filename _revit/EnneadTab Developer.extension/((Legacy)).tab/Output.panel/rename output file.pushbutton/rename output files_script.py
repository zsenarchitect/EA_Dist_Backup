__doc__ = 'This button renames all type of files exported from Revit and removes the Central ' \
          'model name from the names. The tool will ask for a folder ' \
          'containing the file.\n\n' \
          'IMPORTANT!: use auto-long name from the print/export setting.'\


__title__ = "Rename\nOutput Files"
# dependencies
import clr
clr.AddReference('System.Windows.Forms')
clr.AddReference('IronPython.Wpf')

# find the path of ui.xaml
from pyrevit import UI, DB
from pyrevit import script, revit, forms
from pyrevit.forms import WPFWindow
import os
import sys
import os.path as op
import re

xamlfile = script.get_bundle_file('rename output_UI.xaml')
"""to do:  add checkbox to extension checker"""

extension_checker = [".DWG",".JPG",".PDF"]

def remove_exisitng(folder, file, old_file):
    if file not in os.listdir(folder) or old_file not in os.listdir(folder):
        return
    os.remove(op.join(folder, file))

def delete_extra_file(basefolder, key_ext):
    filenames = os.listdir(basefolder)
    PCP_file_found = False
    count = 0
    for current_file in filenames:
        ext = op.splitext(current_file)[1].upper()
        if ext == key_ext:
            os.remove(op.join(basefolder, current_file))
            count+=1
    return count

def using_view_export(file_name):
    check_list = ["Drafting View" , "Floor Plan" , "Elevation" , "Section" , "3D View" , "Reflected Ceiling Plan" , "Detail View" , "Rendering" , "Area Plan", "Structural Plan"]
    for checker in check_list:
        if checker in file_name:
            return " - "
    return None

def rename_non_dwg_file(file):
    if file == "":#for empty grid initiation
        return file

    r = re.compile('(?<=Sheet - )(.+)')
    fname = r.findall(file)[0]
    r = re.compile('(.+)\s-\s(.+)')
    fnameList = r.findall(fname)
    return fnameList[0][0] + ' - ' + fnameList[0][1].upper()


def rename_dwg_file(file):
    if file == "":#for empty grid initiation
        return file

    split_keyword = using_view_export(file)
    if split_keyword == None:
        print("shouldnt be here, ask Sen Zhang for debug")
        print(file)

    #print file.split(split_keyword, 1)[1]
    #print "****"
    return file.split(split_keyword, 1)[1]

class data_grid_obj(object):
    def __init__(self, file_name):
        self.old_name = file_name
        if "- Sheet - " in file_name:##pdf, jpg, png exported from sheet set
            self.new_name = rename_non_dwg_file(file_name)
        elif "-Sheet - " in file_name:##dwg exported from sheet set
            self.new_name = rename_non_dwg_file(file_name)
        else:## dwg export from dwg set
            self.new_name = rename_dwg_file(file_name)



class UI_Window(WPFWindow):
    def __init__(self):
        WPFWindow.__init__(self, xamlfile)
        self.set_image_source(self.logo_img, "{}\logo_vertical_light.png".format(EnneadTab.ENVIRONMENT_CONSTANTS.CORE_IMAGES_FOLDER_FOR_PUBLISHED_REVIT))
        self.folder_status_display.Content = ""
        self.clearPCP = self.checkbox_1.IsChecked
        self.clearPS = self.checkbox_2.IsChecked
        self.override_existing = self.checkbox_3.IsChecked
        self.progress_bar.Value = 0
        self.progress_bar_display.Text = ""
        self.note.Text = "Notes:\nPcp and Ps file are from general export.The deletion of those files does not affect file function."
        self.button_rename.Content = "pick folder first"


        output= script.get_output()
        output.close_others()
        self.initiate_empty_data_grid()

    def initiate_empty_data_grid(self):
        self.data_grid.ItemsSource = []
        for x in range(10):
            self.data_grid.ItemsSource.append(data_grid_obj(""))


    def pick_folder(self, sender, args):
        title_line = 'Pick the folder that has all the auto-named the files. For CAD file remember to use auto-long name when exporting.'
        with forms.WarningBar(title = title_line):
            folder = None
            while folder == None:
                folder = forms.pick_folder(title = title_line)
        self.folder_status_display.Content = "Folder Picked!"
        self.set_image_source(self.status_icon, "ok_icon.png")
        self.textbox_folder.Text = folder
        self.button_rename.IsEnabled = True
        self.button_rename.Content = "Rename Files"
        #self.button_rename.Foreground = "#FF464646"
        self.initiate_data_grid(folder)

    def initiate_data_grid(self, folder):
        #print revit.doc.Title
        self.data_grid.ItemsSource = []
        filenames = os.listdir(folder)
        for current_file in filenames:

            ext = op.splitext(current_file)[1].upper()
            if ext in extension_checker and revit.doc.Title in current_file:
                try:
                    data = data_grid_obj(current_file)
                    self.data_grid.ItemsSource.append(data )
                except:
                    print("skip {}".format(current_file))

        #print self.data_grid.ItemsSource

        self.data_grid_title.Text = "{} DWG, PDF, JPG and/or PNG found.\nIf not displaying full content, click the excel header to expand the whole display grid.".format(len(self.data_grid.ItemsSource))
        if len(self.data_grid.ItemsSource) == 0:
            self.initiate_empty_data_grid()
            self.button_rename.IsEnabled = False
            self.button_rename.Content = "Pick next folder"


    def rename_file(self, sender, args):###sender and args must be here even when not used to pass data between GUI and python
        folder = self.textbox_folder.Text
        if folder == None or "Path..." in folder:
            forms.alert("no folder picked")

        self.progress_bar.Value = 0
        self.progress_bar.Maximum = len(self.data_grid.ItemsSource)
        #self.progress_bar.Visible  = True

        sheetcount = 0
        fail_list = []
        for i, data in enumerate(self.data_grid.ItemsSource):
            if self.override_existing:
                remove_exisitng(folder, data.new_name, data.old_name)
            try:
                os.rename(op.join(folder, data.old_name),
                          op.join(folder, data.new_name))
                sheetcount += 1
            except Exception as e:
                print("Unexpected error:", sys.exc_info()[0], "-->", data.old_name, e)
                fail_list.append(data.old_name)
            self.progress_bar.Value = i + 1
            self.progress_bar_display.Text = "{}/{}\nRename {}".format(int(self.progress_bar.Value),\
                                                                int(self.progress_bar.Maximum), \
                                                                data.old_name)


        if len(fail_list) > 0:
            fail_text = 'Those files are skipped, because a file with same destination name '\
                        'is in the same folder, or the conntection to network drive is unstable.\n'
            for item in fail_list:
                fail_text += "\n{}".format(item)
        else:
            fail_text = ""


        pcp_count = delete_extra_file(folder,".PCP") if self.clearPCP else 0
        ps_count = delete_extra_file(folder,".PS") if self.clearPS else 0

        main_msg = '{0} FILES RENAMED.'.format(sheetcount)
        if pcp_count > 0 and self.clearPCP:
            main_msg += "\n{0} Pcp removed.".format(pcp_count)
        if ps_count > 0 and self.clearPS:
            main_msg += "\n{0} Ps removed.".format(ps_count)
        forms.alert(msg = main_msg, sub_msg = fail_text)

        self.initiate_data_grid(folder)



    def options_changed(self, sender, args):
        #print "options_changed"
        self.clearPCP = self.checkbox_1.IsChecked
        self.clearPS = self.checkbox_2.IsChecked
        self.override_existing = self.checkbox_3.IsChecked
        #self.print_opt_status()

    def print_opt_status(self):
        print("clearPCP = {}\nclearPS = {}".format(self.clearPCP,self.clearPS))



##################################################



UI_Window().ShowDialog()
