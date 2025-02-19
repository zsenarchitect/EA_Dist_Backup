#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "This will be the foundation for all future health care tools"
__title__ = "HealthCare\nHelper"
__tip__ = True

# from pyrevit import forms #
from pyrevit import script #
from pyrevit import forms #

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_PROJ_DATA
from EnneadTab import USER, ERROR_HANDLE, LOG
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
UIDOC = REVIT_APPLICATION.get_uidoc()
DOC = REVIT_APPLICATION.get_doc()
            
import dgsf_chart
import color_pallete
import design_guideline
import healthcare_project_setup
@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def generic_healthcare_tool(doc, show_log):

    options = {
        "0. How to HealthCare Project in Ennead(NYU as an example)(WIP)": design_guideline.show_design_outline,
        "1. Initialize Healthcare Project": healthcare_project_setup.setup_healthcare_project,
        "2. Edit Project Data Setup": REVIT_PROJ_DATA.edit_project_data_file,
        "3. Open Project Data Setup": REVIT_PROJ_DATA.open_project_data_file,
        "4. Detail DGSF Chart Update": dgsf_chart.dgsf_chart_update,
        "5. Update Color Pallete From Excel": color_pallete.update_color_pallete,
    }

    select_option = forms.SelectFromList.show(sorted(options.keys()), multiselect=False, title="How can I help you today?", button_name="Help Me!")
    if select_option is None:
        return

    func = options[select_option]
    func(doc)
    

################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    generic_healthcare_tool(DOC, show_log=True)
    


