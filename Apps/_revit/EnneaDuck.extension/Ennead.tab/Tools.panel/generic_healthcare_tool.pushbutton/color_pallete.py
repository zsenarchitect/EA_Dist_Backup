from EnneadTab import NOTIFICATION
from EnneadTab.REVIT import REVIT_COLOR_SCHEME, REVIT_FORMS
from pyrevit import forms

def update_color_pallete(doc):


    NOTIFICATION.messenger(main_text="Select the excel file that contains the color pallete")
    excel_path = forms.pick_excel_file(title="Select the excel file")
    if not excel_path:
        NOTIFICATION.messenger(main_text="No excel file selected")
        return



    department_color_scheme_name = REVIT_COLOR_SCHEME.pick_color_scheme(doc, title="Select the department color scheme", button_name="Select department color scheme")
    if not department_color_scheme_name:
        NOTIFICATION.messenger(main_text="No department color scheme selected")
        return
    program_color_scheme_name = REVIT_COLOR_SCHEME.pick_color_scheme(doc, title="Select the program color scheme", button_name="Select program color scheme")     
    if not program_color_scheme_name:
        NOTIFICATION.messenger(main_text="No program color scheme selected")
        return

    naming_map = {"department_color_map":department_color_scheme_name,
                  "program_color_map":program_color_scheme_name}

    options = ["Remove Bad Color", "Keep Bad Color"]
    select_option = REVIT_FORMS.dialogue(options = options, main_text="Do you want to remove the bad color?")
    if select_option == options[0]:
        is_remove_bad = True
    else:
        is_remove_bad = False
    

    REVIT_COLOR_SCHEME.load_color_template(doc, naming_map, excel_path, is_remove_bad)
