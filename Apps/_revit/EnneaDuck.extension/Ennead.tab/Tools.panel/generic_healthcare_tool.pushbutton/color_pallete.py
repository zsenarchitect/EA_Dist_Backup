
from EnneadTab.REVIT import REVIT_COLOR_SCHEME

def update_color_pallete(doc):
    print ("update_color_pallete")

    print ("excel path has been defined")

    print ("area scheme for GFA and DGSF has been defined")

    print ("color sceme name has been defined")

    REVIT_COLOR_SCHEME.load_color_template(doc, naming_map, excel_path, is_remove_bad)
