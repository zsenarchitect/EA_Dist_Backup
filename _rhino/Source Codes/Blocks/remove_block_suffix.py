import rhinoscriptsyntax as rs
from scriptcontext import doc
import Rhino # pyright: ignore
import sys
sys.path.append("..\lib")
import EnneadTab


def Rename(keyword, replacement_text, blockName):
#    blockName = rs.GetString("block to rename")
    if keyword not in blockName:
        return
    instanceDefinition = doc.InstanceDefinitions.Find(blockName, True)
    if not instanceDefinition:
        print("{0} block does not exist".format(blockName))
        return





    newName =  blockName.replace(keyword, replacement_text)
    while True:

        try:
            instanceDefinition = doc.InstanceDefinitions.Find(newName, True)
            break
        except:
            newName += "_"



    data = "{}  -->  {}".format(blockName, newName)
    rs.RenameBlock(blockName, newName)
    return data

    
    
@EnneadTab.ERROR_HANDLE.try_catch_error    
def remove_block_suffix():
    
    log = []

   
    keyword = rs.StringBox(message = "type in keyword to search in name", default_value = "keyword text to remove from blocks names", title = "rename block names")
    if not keyword:
        return
    replacement_text = rs.StringBox(message = "type in text, you can type '#empty'(yes hashtag, no quote) as a way to remove previous keyword.", default_value = "replacement text to replace previous keyword", title = "rename block names")
    if not replacement_text:
        return
    if replacement_text == "#empty":
        replacement_text = ""


    block_names = rs.BlockNames()

    for name in block_names:
        # print name
        data = Rename(keyword, replacement_text, name)
        if data:
            log.append(data)


    print(log)
    if len(log) > 0:

        log = "\n".join(log)
        rs.TextOut(message = log, title = "here are the changed block names")
    else:
        Rhino.UI.Dialogs.ShowMessage("No block changed", title = "it is good!")



#############################################
if __name__ == "__main__":
    remove_block_suffix()
