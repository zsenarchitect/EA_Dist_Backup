import rhinoscriptsyntax as rs
import scriptcontext as sc
import sys
sys.path.append("..\lib")
import EnneadTab




def replace_block(block, new_block_name):

    rs.Command("")









@EnneadTab.ERROR_HANDLE.try_catch_error
def remove_block_textdot():




    original_blocks = rs.GetObjects("Select block instances remove textdot", filter = 4096, preselect = True)
    selected_block_names = list(set([rs.BlockInstanceName(x) for x in original_blocks]))
    rs.EnableRedraw(False)

    map(remove_textdot, selected_block_names)
    map(lambda x: replace_block(x, "block 1"))

def remove_textdot(block_name):
    objs = rs.BlockObjects(block_name)
    block_definition = sc.doc.InstanceDefinitions.Find(block_name)
    objs = block_definition.GetObjects()

    for obj in objs:


        if rs.ObjectType(obj) == int(8192):
            print("delete dot")
            rs.DeleteObject(obj)
            print("done")



if __name__ == "__main__":
    remove_block_textdot()
