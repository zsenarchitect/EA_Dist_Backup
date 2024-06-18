""" requested by Sakakibara, Lucia for 2338. This is a rushed emergecy help, not using best practice....BUT!
this have many potentials, should rework and make to actual button"""

import Rhino # pyright: ignore
import rhinoscriptsyntax as rs
import scriptcontext as sc
import os
import sys
sys.path.append("..\lib")
import EnneadTab

sys.path.append(EnneadTab.ENVIRONMENT.DEPENDENCY_FOLDER_LEGACY)


MAIN_FOLDER = "J:\\2338\\0_CAD\\2023-12-01 Gonda Building CAD from BWBR\\GO CAD All Levels"

def get_all_dwgs():
    raw_list = [x for x in os.listdir(MAIN_FOLDER) if x.endswith(".dwg")]
    return sorted(raw_list, key=lambda x: x[-6] == "a")

    
@EnneadTab.ERROR_HANDLE.try_catch_error
def batch_print_dwg():
    # rs.EnableRedraw(False)


    map(process_dwg, get_all_dwgs()[::-1])
    rs.EnableRedraw(True)
    
def process_dwg(dwg_file):
    print (dwg_file)
    rs.EnableRedraw(False)
    dwg_file_path = os.path.join(MAIN_FOLDER, dwg_file)

    # template = r"C:\Users\szhang\AppData\Roaming\McNeel\Rhinoceros\7.0\Localization\en-US\Template Files\Large Objects - Inches.3dm"
    # rs.Command("!_-New \"{}\" -Enter".format(template))

    
    rs.DeleteObjects(rs.AllObjects())
    EnneadTab.RHINO.RHINO_CLEANUP.purge_block()
    EnneadTab.RHINO.RHINO_CLEANUP.purge_layer()
    units = "Inches"
    rs.Command("_-import \"{}\" _ModelUnits={} -enter -enter".format(dwg_file_path, units))

    EnneadTab.NOTIFICATION.toast(main_text = "Come Back, come back!", sub_text = "Import Finish!")
    imported_objs = rs.LastCreatedObjects()
    # rs.SelectObjects(imported_objs)
    # # rs.ZoomSelected()
    rs.UnselectAllObjects()

    #blacken all layer color to BW
    for layer in rs.LayerNames():
        rs.LayerColor(layer, (0, 0, 0))
 
    # trigger text object to regenerate. The default stage after import is not readable.
    rs.MoveObjects(imported_objs, (0,0,10))

    rs.Redraw()

    # rs.SelectObjects(imported_objs)
    output_folder = "{}\\pdfs3".format(MAIN_FOLDER)
    EnneadTab.FOLDER.secure_folder(output_folder)
    filepath = "{}\{}.pdf".format(output_folder,
                                  dwg_file.replace(".dwg", ""))
    # rs.Command("!_-Export \"{}\" -Enter -Enter".format(filepath))
    #rs.Command("!_-Export \"{}\" _Pause -SaveSmall = -Yes -Enter -Enter".format(filepath))

    """bluebeam driver is weak....consider using microsoft fax pdf!!! should add to seting for future use"""
    rs.Command("!_-Print Setup View Scale  768 -Enter Destination PageSize 431.8 279.4 OutputColor BlackWhite  -Enter -Enter Go \"{}\" -Enter -Enter".format(filepath))

    """the viewcapture to file is also a good solution when printer fails."""
    # rs.Command("!_-ViewCaptureToFile  Unit inches Width 34 Height 22 \"{}\" -Enter".format(filepath.replace(".pdf", ".png")))

    # this is to move objs under the paper. For raster related output this could be a good solution before the discovery of definition.Clear()
    rs.MoveObjects(imported_objs, (0,0,-100))

    rs.DeleteObjects(rs.AllObjects())
    rs.AddLayer("EA")
    rs.CurrentLayer("EA")

    
    sc.doc.InstanceDefinitions.Clear()
    # for block in rs.BlockNames():
    #     try:
    #         rs.DeleteBlock(block)
    #     except:
    #         pass

    
    for layer in rs.LayerNames():
        if layer == "EA":
            continue
        
        try:
            rs.PurgeLayer(layer)
        except:
            pass
    for layer in rs.LayerNames():
        if layer == "EA":
            continue
        try:
            rs.PurgeLayer(layer)
        except:
            pass
    EnneadTab.NOTIFICATION.messenger(main_text = "[{}] exported!".format(dwg_file))
    

######################  main code below   #########
if __name__ == "__main__":

    batch_print_dwg()




