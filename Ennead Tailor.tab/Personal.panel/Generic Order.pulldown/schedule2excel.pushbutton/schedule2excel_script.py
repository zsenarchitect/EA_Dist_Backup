#! python3
import sys
sys.path.append(r"L:\4b_Applied Computing\03_Rhino\12_EnneadTab for Rhino\Dependency\PY3")
import pandas as pd



__doc__ = "Sen Zhang has not writed documentation for this tool, but he should!"
__title__ = "schedule2excel"

from pyrevit import forms #
from pyrevit import script #
from pyrevit import revit #
import os
import re

from Autodesk.Revit import DB 
# from Autodesk.Revit import UI
# uidoc = EnneadTab.REVIT.REVIT_APPLICATION.get_uidoc()
doc = revit.doc

def schedule2excel():

    schedules = forms.select_schedules()

    if not schedules: return

    basefolder = forms.pick_folder()
    export_option = DB.ViewScheduleExportOptions()
    
    export_option.ColumnHeaders = DB.ExportColumnHeaders.OneRow
    export_option.TextQualifier = DB.ExportTextQualifier.DoubleQuote

    # determine which separator to use
    csv_sp = ','
    

    export_option.FieldDelimiter = csv_sp
    export_option.Title = False
    export_option.HeadersFootersBlanks = False

    for schedule in schedules:
        file_name = re.sub(r'[\/:*?"<>|]', '', schedule.Name) + '.csv'
        
        schedule.Export(basefolder, file_name, export_option)
        exported_csv = os.path.join(basefolder, file_name)

        excel = convert_csv2excel(exported_csv)
        

        os.startfile(excel)

def convert_csv2excel(csv_file_path):
    # Load the CSV data into a DataFrame
    df = pd.read_csv(csv_file_path)

    excel_file_path = csv_file_path.replace(".csv", ".xls")

    # Export the DataFrame to an Excel file
    df.to_excel(excel_file_path, index=False)
    return excel_file_path

################## main code below #####################


if __name__ == "__main__":
    output = script.get_output()
    output.close_others()
    schedule2excel()
    ENNEAD_LOG.use_enneadtab(coin_change = 20, tool_used = __title__.replace("\n", " "), show_toast = True)







