
__title__ = "OpenSampleExcel"
__doc__ = "Open the sample excel with placeholder area size info."

import os
import rhinoscriptsyntax as rs
from EnneadTab import EXE
from EnneadTab import FOLDER
from EnneadTab import LOG
from EnneadTab import ERROR_HANDLE

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def visualize_excel():
    original = "{}\\Progam Spreadsheet.xlsx".format(os.path.dirname(__file__))
    copy = FOLDER.copy_file_to_local_dump_folder(original)
    EXE.try_open_app(copy)
    rs.TextOut("You can modify this excel to your like and saveas.\nFrom left to right, the fileds are: \nCategory, Area Name, Area Size, Color R, Color, G, Color B, Cateogry Area Sum")

if __name__ == "__main__":
    visualize_excel()