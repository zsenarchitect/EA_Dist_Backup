
__title__ = "SelectSimilarBlocks"
__doc__ = "Select blocks of similar definitions from the selected blocks"
import rhinoscriptsyntax as rs

from EnneadTab import NOTIFICATION, LOG, ERROR_HANDLE

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def similar_blocks():


    orginal_blocks = rs.GetObjects("Select block instances to isolate", filter = 4096, preselect = True)
    if not orginal_blocks:
        NOTIFICATION.messenger("No block instances selected.")
        return
    rs.EnableRedraw(False)
    block_names = [rs.BlockInstanceName(x) for x in orginal_blocks]
    block_names = list(set(block_names))

    block_collection = []
    for block_name in block_names:
        block_collection.extend(rs.BlockInstances(block_name))

    rs.UnselectAllObjects()
    rs.SelectObjects( block_collection)


if __name__ == "__main__":
    similar_blocks()