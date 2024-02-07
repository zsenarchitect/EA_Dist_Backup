__doc__ = "Load families from revit link. Work for primary load condition.\nWhich means first time bring in.\n\nThere are several senario where it is helpful, for example:\n\t-You want to get the object style from another file to your current document, and you only want to bring in subcategories binded to a family\n\t-You want to get contents from a container file without opening the container file."
__title__ = "Load Families\nFrom Link"

"""

new idea, just give ability to open faimily from link and make active document. A selection list need to be created to user to pick which family to open

"""



from pyrevit import forms, script
from Autodesk.Revit import DB 
# from Autodesk.Revit import UI
doc = __revit__.ActiveUIDocument.Document
import EA_UTILITY
import EnneadTab
import ENNEAD_LOG






class FamilyOption(DB.IFamilyLoadOptions):
    def OnFamilyFound(self, familyInUse, overwriteParameterValues):
        update_log( "#Normal Family Load option")
        update_log( "is family in use?: {}".format(familyInUse))
        overwriteParameterValues = True# true means use project value
        update_log( "is overwriteParameterValues?: {}".format(overwriteParameterValues))
        update_log( "should load")
        return True

    def OnSharedFamilyFound(self, sharedFamily, familyInUse, source, overwriteParameterValues):
        update_log( "#Shared Family Load option")
        update_log( "is family in use?: {}".format(familyInUse))
        overwriteParameterValues = True
        update_log( "is overwriteParameterValues?: {}".format(overwriteParameterValues))

        global LOADING_SOURCE
        source = LOADING_SOURCE
        #source = DB.FamilySource.Family
        update_log( "is shared component using family or project definition?: {}".format(str(source)))
        update_log( "should load")
        return True


def update_log(string):
    global LOG
    LOG.append(string)

def load_family_to_link(doc, family):
    family_doc = doc.EditFamily(family)


    update_log("\n\nLoading [{}]".format(family_doc.Title))
    try:
        family_doc.LoadFamily(doc, FamilyOption())
        update_log("Family load succesfully to {}.".format(doc.Title))
    except Exception as e:
        update_log("Family [{}] fail to load to {}.\n Error = {}".format(family_doc.Title, doc.Title, e))

    family_doc.Close(False)

def load_families():
    link_doc = EA_UTILITY.select_revit_link_docs(select_multiple = False)
    if link_doc is None:
        EA_UTILITY.dialogue(main_text = "Link is not loadded or not found. This action will cancel.")
        return


    link_families = list(DB.FilteredElementCollector(link_doc).OfClass(DB.Family).ToElements())

    #link_families = filter(lambda x:x.FamilyCategory.Name in ["Detail Items", "Generic Annotations"], link_families)

    link_families.sort(key = lambda x: x.Name)


    link_families = forms.SelectFromList.show(link_families,
                                            name_attr = "Name",
                                            multiselect = True,
                                            title = "pick families from the link model that you want to load",
                                            button_name='try to find same name family in current file')
    if link_families is None:##### cannot find a family matching name
        return

    options = [["Project Version",""], ["Family Doc Version","(Recommanded)"]]
    res = EA_UTILITY.dialogue(main_text = "When shared componnet disovered, which version to use?", sub_text = "Shared component is not always loaded.", options = options)
    global LOADING_SOURCE
    if res == options[0][0]:
        LOADING_SOURCE = DB.FamilySource.Project
    else:
        LOADING_SOURCE = DB.FamilySource.Family

    global LOG
    LOG = []


    #t = DB.Transaction(doc, "load family from link")
    #t.Start()
    map(lambda x: load_family_to_link(doc, x), link_families)
    #t.Commit()


    for line in LOG:
        print line

    EA_UTILITY.tool_has_ended()

################## main code below #####################
output = script.get_output()
output.close_others(all_open_outputs = True)



if __name__ == "__main__":
    load_families()
    ENNEAD_LOG.use_enneadtab(coin_change = 20, tool_used = __title__.replace("\n", " "), show_toast = True)




#select waht propoerty to copy over
#want to preserve keynote value
