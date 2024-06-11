__doc__ = "Sen Zhang has not writed documentation for this tool, but he should!"
__title__ = "GUI\ntemplate_other method"
# dependencies
import clr
clr.AddReference('System.Windows.Forms')
clr.AddReference('IronPython.Wpf')

# find the path of ui.xaml
from pyrevit import UI, DB
from pyrevit import script, revit, forms, HOST_APP
from pyrevit.forms import WPFWindow
import EVENT
xamlfile = script.get_bundle_file('GUI template_UI.xaml')
uidoc = revit.uidoc
import Autodesk.Revit.UI.Selection as ARUS

customizable_event = EVENT.CustomizableEvent()

class data_grid_obj(object):
    def __init__(self, eid, checked, comment,window):
        self.element_id = eid
        self.checked = checked
        self.comment = comment
        self.mark = "{}_{}".format("opt A" if window.optA else "optB", comment)


class UI_Window(WPFWindow):
    def __init__(self):
        WPFWindow.__init__(self, xamlfile)

        self.set_image_source(self.logo_img, "{}\logo_vertical_light.png".format(EnneadTab.ENVIRONMENT_CONSTANTS.CORE_IMAGES_FOLDER_FOR_PUBLISHED_REVIT))

        self.dropdown_list.ItemsSource =  ["item" + str(x + 1) for x in range(10)]
        self.display1.Content = ""
        self.optA = self.radiobutton_1.IsChecked
        self.optB = self.radiobutton_2.IsChecked
        self.optC = self.checkbox_1.IsChecked
        self.display3.Content = ""
        self.progress_bar.Value = 0
        self.progress_bar_display.Text = ""
        #self.progress_bar.Visibility  = False
        #self.print_opt_status()

        sample_elements = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_Walls).WhereElementIsNotElementType().ToElements()
        self.data_grid.ItemsSource = []
        for x, element in enumerate(sample_elements):
            if x > 150:
                break
            self.data_grid.ItemsSource.append(data_grid_obj(element.Id, False if x%3 ==0 else True, "odd number" if x%2 == 1 else "", self) )

        output= script.get_output()
        output.close_others()

    @property
    def shared_varabile(self):
        return self.textbox1.Text

    def dropdown_list_value_changed(self, sender, e):#e as in "event"
        print("dropdown menu selection changed")
        self.display3.Content = "preview {}".format(self.dropdown_list.SelectedItem)



    def function_in_script(self, sender, args):###sender and args must be here even when not used to pass data between GUI and python
        variable = self.shared_varabile
        #variable = self.textbox1.Text   use this line if dont want to use @property in the class

        self.display1.Content = "Text Captured!"
        self.set_image_source(self.status_icon, "ok_icon.png")

        self.display2.Content = "Select {}".format(self.dropdown_list.SelectedItem)

        print("Function run ok after clicking button\n\tget: {}".format(variable))
        UI.TaskDialog.Show(
            "title here from script",
            "sample text in function with: {}".format(variable)
            )

        with revit.Transaction("temp"):
            #print self.data_grid.ItemsSource
            for obj in self.data_grid.ItemsSource:
                #print revit.doc.GetElement(obj.element_id).LookupParameter("Mark")
                temp = obj.mark + "$" + self.display2.Content
                print(revit.doc.GetElement(obj.element_id).LookupParameter("Mark").Set(temp))
                #revit.doc.GetElement(obj.element_id).Parameter("Mark").Set(obj.mark)

        sample_elements = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_Walls).WhereElementIsNotElementType().ToElements()
        #doors = DB.FilteredElementCollector(revit.doc).WhereElementIsNotElementType().ToElements()
        self.progress_bar.Value = 0
        self.progress_bar.Maximum = len(sample_elements)
        #self.progress_bar.Visible  = True

        for i, sample_element in enumerate(sample_elements):
            print(sample_element.Id)
            self.progress_bar.Value = i + 1
            self.progress_bar_display.Text = "{}/{}\nId = {}\n{}".format(int(self.progress_bar.Value),\
                                                                int(self.progress_bar.Maximum), \
                                                                sample_element.Id,\
                                                                "checked optA" if self.optA else "checked optB")

        forms.alert("progress bar finished")



    def pick_element_click(self, sender, args):
        print("click on GUI pick element button")
        element = revit.pick_element("pick fllor")
        print(element.UniqueId)
        sheet = forms.select_sheets()
        #return customizable_event.raise_event(pick_element())

    def options_changed(self, sender, args):
        print("options_changed")
        self.optA = self.radiobutton_1.IsChecked
        self.optB = self.radiobutton_2.IsChecked
        self.optC = self.checkbox_1.IsChecked
        self.print_opt_status()

    def print_opt_status(self):
        print("optA = {}\noptB = {}\noptC = {}".format(self.optA,self.optB,self.optC))


    def update_progress_bar(self):
        self.progress_bar.Value += 1
#################################################################################
def pick_element():
    print("start to run pick element function")
    print(uidoc)
    print(uidoc.Selection)
    print(ARUS.ObjectType.Element)
    #element = uidoc.Selection.PickObject(UI.Selection.ObjectType.Element, AxisISelectionFilter(), "Select an curve based element")
    with DB.Transaction( revit.doc,"temp"):
        element = ARUS.Selection.PickObject(uidoc.Selection, ARUS.ObjectType.Element,  "Select an element")
    print(element)
    uidoc.Selection.SetElementIds(element.ElementId)
    return element

class AxisISelectionFilter(UI.Selection.ISelectionFilter):
    """ISelectionFilter that allow only which have an axis (Line)"""

    # noinspection PyMethodMayBeStatic, PyPep8Naming
    def AllowElement(self, element):
        if isinstance(element.Location.Curve, Line):
            return True
        else:
            return False

"""
def axis_selection():
    #Ask user to select an element, return the axis of the element
    try:
        reference = uidoc.Selection.PickObject(UI.Selection.ObjectType.Element, AxisISelectionFilter(), "Select an axis")
    except OperationCanceledException:
        pass
    else:
        axis = doc.GetElement(reference).Location.Curve
        return axis
"""
##################################################



UI_Window().ShowDialog()
