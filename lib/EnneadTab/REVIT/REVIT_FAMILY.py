
try:
    from Autodesk.Revit import DB
    REF_CLASS = DB.IFamilyLoadOptions
    import clr
except:
    REF_CLASS = object # this is to trick that class can be used

    
import FOLDER 



class EnneadTabFamilyLoadingOption(REF_CLASS):
    def __init__(self, is_shared_using_family = True):
        self.is_shared_using_family = is_shared_using_family
        pass


    def OnFamilyFound(self, familyInUse, overwriteParameterValues):

        # true means use project value
        overwriteParameterValues = True

        return True

    def OnSharedFamilyFound(self, sharedFamily, familyInUse, source, overwriteParameterValues):
        overwriteParameterValues = True
        
        if self.is_shared_using_family:
            source = DB.FamilySource.Family
        else:
            source = DB.FamilySource.Project
        return True


def load_family(family_doc, project_doc):
    
    family_doc.LoadFamily(project_doc, EnneadTabFamilyLoadingOption())
    
    
def load_family_by_path(family_path, project_doc=None, ):
    project_doc = project_doc or __revit__.ActiveUIDocument.Document
    
    fam_ref = clr.StrongBox[DB.Family](None)
    family_path = FOLDER.copy_file_to_local_dump_folder(family_path, file_name=family_path.rsplit("\\", 1)[1].replace("_content",""))
    project_doc.LoadFamily(family_path, EnneadTabFamilyLoadingOption(), fam_ref)
    
    return fam_ref
    
  

def is_family_exist(family_name, doc=None):
    doc = doc or __revit__.ActiveUIDocument.Document
    all_families = DB.FilteredElementCollector(doc).OfClass(DB.Family).ToElements()
    for family in all_families:
        if family.Name == family_name:
            return True
    return False

def get_family_by_name(family_name, 
                       doc=None, 
                       load_path_if_not_exist=None):
    doc = doc or __revit__.ActiveUIDocument.Document
    all_families = DB.FilteredElementCollector(doc).OfClass(DB.Family).ToElements()
    families = filter(lambda x: x.Name == family_name, all_families)
    
    if len(families) == 0:
        print ("Cannot find this family")
        if load_path_if_not_exist:
            print ("Loading from [{}]".format(load_path_if_not_exist))
            return load_family_by_path(load_path_if_not_exist, project_doc=doc)
        else:
            return None
        
    return families[0]