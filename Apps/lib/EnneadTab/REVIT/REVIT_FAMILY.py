
try:
    from Autodesk.Revit import DB # pyright: ignore
    import clr # pyright: ignore
    import REVIT_APPLICATION
except:
    pass
try:
    REF_CLASS = DB.IFamilyLoadOptions
except:
    REF_CLASS = object # this is to trick that class can be used during INIT process
try:    
    DOC = REVIT_APPLICATION.get_doc()
except:
    DOC = object
    
import os
from EnneadTab import ERROR_HANDLE
import NOTIFICATION
import FOLDER 
import REVIT_SELECTION



class EnneadTabFamilyLoadingOption(REF_CLASS):
    def __init__(self, is_shared_using_family = True):
        self.is_shared_using_family = is_shared_using_family
        pass


    def OnFamilyFound(self, familyInUse, overwriteParameterValues):

        # true means use family value
        overwriteParameterValues = True

        return True

    def OnSharedFamilyFound(self, sharedFamily, familyInUse, source, overwriteParameterValues):
        overwriteParameterValues = True
        
        if self.is_shared_using_family:
            source = DB.FamilySource.Family
        else:
            source = DB.FamilySource.Project
        return True



class DryLoadFamilyOption(REF_CLASS):
    """this option will always return False becasue it is only to check the difference but not really load family"""
    def __init__(self):
        # assuming it is same at beging and check to see if it is changed during load, which mean a found is triggered
        self.is_version_different = False
        
    def OnFamilyFound(self, familyInUse, overwriteParameterValues):
        self.is_version_different = True
        return False

    def OnSharedFamilyFound(self, sharedFamily, familyInUse, source, overwriteParameterValues):
        self.is_version_different = True
        return False


def is_family_version_different(family_doc, project_doc, load_if_not_exist=False):
    """_summary_

    Args:
        family_doc (DB.Document): _description_
        project_doc (DB.Document): _description_

    return : True: family exist, but version different
            False: family exsit, and version is same
            None: family not exist in project.
    """
    if not is_family_exist(family_doc.Title, project_doc):
        # NOTIFICATION.messenger("[{}] does not exist in [{}]".format(family_doc.Title, project_doc.Title))
        if load_if_not_exist:
            load_family(family_doc, project_doc)
        return None
    dry_opt = DryLoadFamilyOption()

    # to-do: this dry load will always trigger family-load hook to fail, even though that is intentional. 
    # need to find a better way to stop hook display/trigger
    load_family(family_doc,project_doc,loading_opt=dry_opt) 

    
    if dry_opt.is_version_different:
        NOTIFICATION.messenger("family [{}] is different version".format(family_doc.Title)) 
    return dry_opt.is_version_different  

def load_family(family_doc, project_doc, loading_opt = EnneadTabFamilyLoadingOption()):
    """safely load a family to a project.

    Args:
        family_doc (DB.Document): _description_
        project_doc (DB.Document): _description_
        loading_opt (DB.IFamilyLoadOptions, optional): What behaviour to use during loading conflict. Defaults to EnneadTabFamilyLoadingOption(), which prefer family value for normal parameter and shared family.
    """
    try:
        family_doc.LoadFamily.Overloads[DB.Document, DB.IFamilyLoadOptions](project_doc, loading_opt)
    except Exception as e:
        ERROR_HANDLE.print_note ("Failed to load family [{}], level 1, becasue {}".format(family_doc.Title, e))
        try:
            family_doc.LoadFamily(project_doc, loading_opt)

        except Exception as e:
            ERROR_HANDLE.print_note ("Failed to load family [{}], level 2, becasue {}".format(family_doc.Title, e))
            try:
                save_option = DB.SaveAsOptions()
                save_option.OverwriteExistingFile = True
                temp_path = FOLDER.get_EA_dump_folder_file( family_doc.Title + ".rfa")
                family_doc.SaveAs(temp_path, save_option)
                family_ref = clr.StrongBox[DB.Family](None)
                success, family_ref = project_doc.LoadFamily.Overloads[str, DB.IFamilyLoadOptions](temp_path, loading_opt, family_ref)
                os.remove(temp_path)
            except Exception as e:
                NOTIFICATION.messenger("Cannot load family [{}]".format(family_doc.Title))
                ERROR_HANDLE.print_note ("Failed to load family [{}], level 3, becasue {}".format(family_doc.Title, e))
    
def load_family_by_path(family_path, project_doc=None, loading_opt = EnneadTabFamilyLoadingOption()):
    project_doc = project_doc or DOC
    
    fam_ref = clr.StrongBox[DB.Family](None)
    family_path = FOLDER.copy_file_to_local_dump_folder(family_path, file_name=family_path.rsplit("\\", 1)[1].replace("_content",""))

    res = project_doc.LoadFamily(family_path, loading_opt, fam_ref)
    if not res:
        print ("failed to load family [{}], trying to load by open and close".format(family_path))
        family_doc = REVIT_APPLICATION.get_app().OpenDocumentFile(family_path)
        load_family(family_doc, project_doc, loading_opt)
        family_doc.Close(False)

    return fam_ref
    
  

def is_family_exist(family_name, doc=None):
    doc = doc or DOC
    all_families = DB.FilteredElementCollector(doc).OfClass(DB.Family).ToElements()
    for family in all_families:
        if family.Name == family_name:
            return True
    return False

def get_family_by_name(family_name, 
                       doc=None, 
                       load_path_if_not_exist=None):
    doc = doc or DOC
    all_families = DB.FilteredElementCollector(doc).OfClass(DB.Family).ToElements()
    families = filter(lambda x: x.Name == family_name, all_families)
    
    if len(families) == 0:
        if load_path_if_not_exist:
            print ("Loading from [{}]".format(load_path_if_not_exist))
            return load_family_by_path(load_path_if_not_exist, project_doc=doc)
        else:
            NOTIFICATION.messenger("Cannot find family [{}]".format(family_name))
            return None
        
    return families[0]


def is_family_used(family_name, doc=None):
    doc = doc or DOC
    family = get_family_by_name(family_name, doc=doc)
    if family is None:
        return False
    is_used = False
    for x in family.GetFamilySymbolIds():
        if doc.GetElement(x).IsActive:
            is_used = True
            break
    return is_used

def get_all_types_by_family_name(family_name, doc=None, return_name = False):
    doc = doc or DOC
    family = get_family_by_name(family_name, doc=doc)
    if family is None:
        return None
    if return_name:
        return [doc.GetElement(x).LookupParameter("Type Name").AsString() for x in family.GetFamilySymbolIds()]
    else:
        return [doc.GetElement(x) for x in family.GetFamilySymbolIds()]

def get_family_type_by_name(family_name, type_name, doc=None, create_if_not_exist=False):
    doc = doc or DOC
    family = get_family_by_name(family_name, doc=doc)
    if family is None:
        return None
    types = [doc.GetElement(x) for x in family.GetFamilySymbolIds()]

    if not types:
        NOTIFICATION.messenger("Cannot find any type in [{}]".format(family_name))
        return None
    
    for type in types:
        if type.LookupParameter("Type Name").AsString() == type_name:
            return type
    else:
        if create_if_not_exist:
            return type.Duplicate(type_name)
        else:
            return None

def get_family_instances_by_family_name_and_type_name(family_name, type_name, doc=None, editable_only = False):
    doc = doc or DOC
    family_type = get_family_type_by_name(family_name, type_name, doc=doc)
    if not family_type:
        NOTIFICATION.messenger("Cannot find any type")
        return

    res = [el for el in DB.FilteredElementCollector(doc).OfClass(DB.FamilyInstance).WhereElementIsNotElementType().ToElements() if el.Symbol.Id == family_type.Id]

    if res and editable_only:
        res = REVIT_SELECTION.filter_elements_changable(res)

    return res


def update_family_type(doc, family_name, type_name, update_para_dict, show_log=True):
    family_type = get_family_type_by_name(family_name, type_name, doc=doc, create_if_not_exist=False)
    if not family_type:
        if show_log:
            print ("Cannot find family type [{}]-[{}]".format(family_name,type_name))
        return
    if not REVIT_SELECTION.is_changable(family_type):
        if show_log:
            print ("Cannot update family type [{}]-[{}] becasue it is not editable or not activated at the moment.".format(family_name,type_name))
        return
    
    
    for para_name, value in update_para_dict.items():
        para = family_type.LookupParameter(para_name)
        if isinstance(value, bool):
            value = 1 if value else 0
        if para:
            para.Set(value)
        else:
            if show_log:
                print ("Cannot find parameter [{}] in [{}]".format(para_name, family_name))

def update_family_type_by_dict(doc, family_data, show_log=True):
    for family_name, type_data in family_data.items():
        for type_name, para_dict in type_data.items():
            update_family_type(doc, family_name, type_name, para_dict, show_log=show_log)
        
class RevitInstance:
    def __init__(self, element):
        self.element = element
        
    @property
    def paras(self):
        return list(self.element.Parameters)
        

    def get_para(self, name):
        para =  self.element.LookupParameter(name)
        if not para:
            return None
        if para.StorageType == DB.StorageType.String:
            return para.AsString()
        elif para.StorageType == DB.StorageType.Integer:
            return para.AsInteger()
        elif para.StorageType == DB.StorageType.Double:
            return para.AsDouble()
        elif para.StorageType == DB.StorageType.ElementId:
            return para.AsElementId()


    def set_para(self, name, value):
        para =  self.element.LookupParameter(name)
        if not para:
            return None
        para.Set(value)



class RevitType(RevitInstance):

    @property
    def type_name(self):
        return self.element.LookupParameter("Type Name").AsString()

    @property
    def family_name(self):
        # handle textnote type seperately becasue it does not category
        if isinstance(self.element, DB.TextNoteType):
            return "TextNote"
            
        # handle loadble family
        if hasattr(self.element, "FamilyName"):
            return self.element.FamilyName

        # handle system family
        elif hasattr(self.element,"Category"):
            return self.element.Category.Name
        else:
            return "Unknown family name"

        
    @property
    def pretty_name(self):
        return "[{}]: {}".format(self.family_name, self.type_name)

    # def __getattr__(self, name):
    #     try:
    #         # First, try to get the attribute from the class itself
    #         return self.__getattribute__(name)
    #     except AttributeError:
    #         # If it's not found, return the attribute from self.element
    #         return getattr(self.element, name)