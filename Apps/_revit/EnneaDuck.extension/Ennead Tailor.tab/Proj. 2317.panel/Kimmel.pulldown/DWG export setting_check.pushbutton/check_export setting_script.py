__doc__ = """check NYU CAD export layer mapping rule"""
__title__ = "Check DWG Export Layer Mapping"
__tip__ = True
from pyrevit import forms, script
from Autodesk.Revit import DB # pyright: ignore

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
from EnneadTab.REVIT import REVIT_FORMS, REVIT_APPLICATION
from EnneadTab import NOTIFICATION, ERROR_HANDLE, LOG

uidoc = REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()

class DWGLayerTablePrinter:
    """A fancy table printer that makes Excel jealous """
    
    def __init__(self, doc):
        self.doc = doc
        self.output = script.get_output()
        

        
    def get_layer_data(self, setting):
        """Extracts layer info faster than a duck can swim"""
        export_options = setting.GetDWGExportOptions()
        layer_table = export_options.GetExportLayerTable()
        
        table_data = []
        for layer_key in layer_table.GetKeys():
            layer_info = layer_table.GetExportLayerInfo (layer_key)
            layer_modifiers = layer_info.GetLayerModifiers()
            modifier_note = ""
            for modifier in layer_modifiers:
                modifier_note += str(modifier.ModifierType) + " "
            cut_modifiers = layer_info.GetCutLayerModifiers ()
            cut_modifier_note = ""
            for cut_modifier in cut_modifiers:
                cut_modifier_note += str(cut_modifier.ModifierType) + " "
            row = [
                layer_key.CategoryName,
                layer_key.SubCategoryName,
                layer_info.LayerName,
                layer_info.ColorNumber,
                layer_info.CutLayerName,
                layer_info.CutColorNumber,
                modifier_note,
                cut_modifier_note
            ]
            table_data.append(row)
            

        table_data.sort(key=lambda x: (x[0] or "", x[1] or ""))
        return table_data
    
    def print_setting(self, setting):
        """Prints a setting faster than you can say 'quack'"""
        self.output.print_md("## Export Setting: {}".format(setting.Name))

        table_data = self.get_layer_data(setting)
        self.output.print_table(table_data=table_data, 
                                columns=["Category", "Subcategory", "Project Layer Name", "ProjectColor Number", "Cut Layer Name", "Cut Color Number", "Modifier Note", "Cut Modifier Note"],
                                formats=['', '', '', '', '', '', '', ''])

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def main():
    doc = REVIT_APPLICATION.get_doc()
    
    # Get all DWG export settings (like finding ducks in a pond)
    settings = DB.FilteredElementCollector(doc)\
                .OfClass(DB.ExportDWGSettings)\
                .WhereElementIsNotElementType()\
                .ToElements()
    
    # Let user pick their favorite duck... I mean, setting
    selected_setting = forms.SelectFromList.show(settings,
                                               name_attr="Name",
                                               multiselect=False,
                                               button_name='Show Layer Table',
                                               title="Select DWG Export Setting")
    
    if not selected_setting:
        NOTIFICATION.messenger(main_text="No setting selected! The ducks are disappointed ")
        return
        
    # Time to make that table look gorgeous!
    printer = DWGLayerTablePrinter(doc)
    printer.print_setting(selected_setting)

if __name__ == "__main__":
    output = script.get_output()
    output.close_others()
    main()




