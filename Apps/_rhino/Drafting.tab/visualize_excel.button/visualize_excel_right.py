__title__ = "OpenSampleExcel"
__doc__ = """Access sample Excel template for area visualization.

Key Features:
- Pre-formatted Excel template
- Example data structure
- Color coding guidelines
- Area calculation formulas
- Category organization samples"""

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