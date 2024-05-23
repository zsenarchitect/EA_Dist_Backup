import time

import rhinoscriptsyntax as rs
import Rhino # pyright: ignore
try:
    import Grasshopper
except:
    pass
import scriptcontext as sc

import os
import sys
parent_folder = os.path.dirname(os.path.dirname(__file__))
parent_folder = os.path.dirname(os.path.dirname(parent_folder))
parent_folder = os.path.dirname(os.path.dirname(parent_folder))
sys.path.append("{}\\lib".format(parent_folder))
import EnneadTab

sys.path.append(os.path.dirname(__file__))
import divider_solution
reload(divider_solution)
import block_solution
reload(block_solution)

import helper
reload(helper)

import traceback
import logging

# logging.c(r"C:\Users\szhang\github\EnneadTab-for-Rhino\Source Codes\Grasshopper\GH_python\Lenox\Map Facade\error.txt")
logging.basicConfig(level=logging.INFO,  # Set the desired logging level
                    format='%(asctime)s - %(levelname)s - %(message)s',  # Define log message format
                    filename=r"C:\Users\szhang\github\EnneadTab-for-Rhino\Source Codes\Grasshopper\GH_python\Lenox\Map Facade\error.log",  # Specify the log file name (optional)
                    filemode='w')  # Choose the file mode (w for write, a for append)
logger = logging.getLogger(__name__)

from divider_solution import DividerSolution
from block_solution import BlockSolution
from design_definition import Mode


if "design_option" not in globals():
    design_option = rs.DocumentName().split(".3dm")[0]
    
def main():
    sc.doc = Rhino.RhinoDoc.ActiveDoc
    
    rs.EnableRedraw(False)

    
    print (time.time())
    start = time.time()

    rs.CurrentLayer("Massing")

    for mode in [Mode.Tower]:#, Mode.Podium]:
        divider_solution = DividerSolution(mode)
        divider_solution.process_srfs()

        panels= divider_solution.good_panels_default + divider_solution.good_panels_flipped
        edges = divider_solution.misc_panels

        # logger.info(panels)
        # logger.info ("\n\n")
        # logger.info (edges)
        
        
        helper.bake_brep(panels, "Massing::temp")
        rs.LayerVisible("Massing::temp", False)

        
        bake_solution = BlockSolution(panels, edges, design_option, mode)
        bake_solution.pre_action()
        bake_solution.process_srfs()
        bake_solution.post_action()

    print ("done!")
    print (time.time())
    time_delta = EnneadTab.TIME.get_readable_time (time.time() - start)
    EnneadTab.NOTIFICATION.messenger("Script rerun after {}".format(time_delta))

    
    rs.CurrentView("Perspective")
    rs.EnableRedraw(True)
    if "Grasshopper" in globals():
        sc.doc = Grasshopper.Instances.ActiveCanvas.Document
    
try:
    main()
except:
    print (traceback.format_exc())
    EnneadTab.NOTIFICATION.messenger("Something is not right")
