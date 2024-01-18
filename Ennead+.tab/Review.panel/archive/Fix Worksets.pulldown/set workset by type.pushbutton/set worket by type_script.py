


__title__ = "Set Workset\nBy Type"
# dependencies
import clr
clr.AddReference('System.Windows.Forms')
clr.AddReference('IronPython.Wpf')

# find the path of ui.xaml
from pyrevit import UI, DB
from pyrevit import script, revit, forms
from pyrevit.forms import WPFWindow
import System.Collections.Generic.List
import WORKSET as WS
import EA_UTILITY
import EnneadTab
xamlfile = script.get_bundle_file('fix workset_UI.xaml')


class data_grid_obj(object):
    def __init__(self, type_name, default_workset,is_to_A = False, is_to_B = False):
        self.type_name = type_name
        #self.target_workset =  System.Collections.Generic.List[str](["a","b","c"]) #item 0 as "Keep as it..."
        self.final_workset = default_workset
        self.is_to_A = is_to_A
        self.is_to_B = is_to_B
        #self.workset_dropdown_list.ItemsSource =  ["item" + str(x + 1) for x in range(10)]

class UI_Window(WPFWindow):
    def __init__(self):
        WPFWindow.__init__(self, xamlfile)
        self.set_image_source(self.logo_img, "{}\logo_vertical_light.png".format(EnneadTab.ENVIRONMENT_CONSTANTS.CORE_IMAGES_FOLDER_FOR_PUBLISHED_REVIT))
        self.process_wall = self.radioBT1.IsChecked
        self.process_floor = self.radioBT2.IsChecked
        self.progress_bar.Value = 0
        self.progress_bar_display.Text = ""
        self.note.Text = "Notes:\nChange the target workset from dropdown menu."
        user_worksets = WS.get_all_userworkset_name()
        user_worksets.insert(0,"...keep current...")
        self.target_A_list.ItemsSource = user_worksets
        self.target_B_list.ItemsSource = user_worksets
        self.main_button.Content = "Test Assignment"
        self.target_combo.ItemsSource = ["a","b","c"]
        output= script.get_output()
        output.close_others()
        self.initiate_data_grid()

    def get_current_category(self):
        if self.process_wall:
            return DB.BuiltInCategory.OST_Walls
        if self.process_floor:
            return DB.BuiltInCategory.OST_Floors

    def initiate_data_grid(self):
        EA_UTILITY.print_note( "-----------initiat grid")
        self.data_grid.ItemsSource = []
        category = self.get_current_category()

        types = DB.FilteredElementCollector(revit.doc).OfCategory(category).WhereElementIsElementType().ToElements()
        types = list(types)
        print_type_name(types)

        types.sort(key = lambda x: x.LookupParameter("Type Name").AsString(), reverse = False)
        if len(types) == 0:
            return

        print_type_name(types)

        for type in types:
            self.data_grid.ItemsSource.append(data_grid_obj(type.LookupParameter("Type Name").AsString(), "waiting for assignment"))


    def update_data_grid_final_display(self):
        #print "======updating datagrid display"
        def get_selected_workset_name(list = "A"):
            if list == "A":
                return self.target_A_list.ItemsSource[self.target_A_list.SelectedIndex]
            else:
                return self.target_B_list.ItemsSource[self.target_B_list.SelectedIndex]

        temp = []
        for data in self.data_grid.ItemsSource:
            EA_UTILITY.print_note(  "==")
            EA_UTILITY.print_note(  data.type_name)
            EA_UTILITY.print_note(  data.is_to_A)
            EA_UTILITY.print_note(  data.is_to_B)
            if data.is_to_A:
                data.final_workset = get_selected_workset_name("A")
                #data.update_final("will use A")
            if data.is_to_B:
                data.final_workset = get_selected_workset_name("B")
            EA_UTILITY.print_note(  data.final_workset)
            temp.append(data)
            #temp.append(data_grid_obj(data.type_name,data.final_workset,data.is_to_A, data.is_to_B))
            #self.data_grid.ItemsSource[i] = data
        self.data_grid.ItemsSource = temp

    def process_types(self, sender, args):###sender and args must be here even when not used to pass data between GUI and python
        EA_UTILITY.print_note(  self.main_button.Content)
        if self.main_button.Content == "Test Assignment":
            EA_UTILITY.print_note(  "will update final workset display")
            self.update_data_grid_final_display()
            self.main_button.Content = "Process Workset"
            return

        self.progress_bar.Value = 0
        self.progress_bar.Maximum = len(self.data_grid.ItemsSource)
        #self.progress_bar.Visible  = True

        with revit.Transaction("Fix workset by type"):
            for i, data in enumerate(self.data_grid.ItemsSource):
                try:
                    self.process_data(data)
                except Exception as e:
                    print "Failed to set workset for: {}".format(data.type_name)
                    EA_UTILITY.print_traceback()
                self.progress_bar.Value = i + 1
                self.progress_bar_display.Text = "{}/{}\nChange {}".format(int(self.progress_bar.Value),\
                                                                    int(self.progress_bar.Maximum), \
                                                                    data.type_name)

        self.initiate_data_grid()
        self.main_button.Content = "Test Assignment"

    def dropdown_list_value_changed(self, sender, args):
        EA_UTILITY.print_note(  "dropdown value changed, need to update final workset text")
        try:
            self.update_data_grid_final_display()
        except:
            self.initiate_data_grid()

    def cate_options_changed(self, sender, args):
        EA_UTILITY.print_note(  "options_changed")
        self.process_wall = self.radioBT1.IsChecked
        self.process_floor = self.radioBT2.IsChecked
        self.initiate_data_grid()
        #self.print_opt_status()

    def process_data(self, data):
        #get the workset from final workset name
        workset = WS.get_workset_by_name(data.final_workset)
        if workset == None:
            return
        EA_UTILITY.print_note( workset)

        #get all element of this type name
        category = self.get_current_category()
        elements_raw = DB.FilteredElementCollector(revit.doc).OfCategory(category).WhereElementIsNotElementType().ToElements()

        type_name = data.type_name
        def is_my_type(el):

            if hasattr(el, "WallType"):
                type = el.WallType
            if hasattr(el, "FloorType"):
                type = el.FloorType
            if "type" not in locals():
                #print "!!!!! no type set"
                return False

            if type.LookupParameter("Type Name").AsString() == type_name:
                return True
            else:
                return False

        elements = filter(is_my_type, elements_raw)
        EA_UTILITY.print_note(  elements)

        #for loop WS.push each element to workset
        for element in elements:
            WS.set_element_workset(element, workset)

def print_type_name(types):
    return
    EA_UTILITY.print_note( "*"*20)
    for type in types:
        #print type
        #print type.FamilyName
        #print type.Kind
        EA_UTILITY.print_note( type.LookupParameter("Type Name").AsString())

@EnneadTab.ERROR_HANDLE.try_catch_error
def main():
    UI_Window().ShowDialog()
##################################################
try:
    pass
    #EA_UTILITY.show_toast(title = "Saving Local File before workset changes...")
    #revit.doc.Save()

    #EA_UTILITY.show_toast(title = "Local File Saved.")
except:
    print "save failed"
    pass
## save revit
main()
