# -*- coding: utf-8 -*-

from EnneadTab import ERROR_HANDLE
import REVIT_APPLICATION

try:

    from Autodesk.Revit import DB # pyright: ignore
    from Autodesk.Revit import UI # pyright: ignore
    UIDOC = REVIT_APPLICATION.get_uidoc() 
    DOC = REVIT_APPLICATION.get_doc()
    
except:
    globals()["UIDOC"] = object()
    globals()["DOC"] = object()


def get_tagged_elements(tag, doc):
    """Get the elements that a tag is referencing. Always return a list even only one host.
    
    Args:
        tag: Revit tag element
        doc: Current Revit document
        
    Returns:
        List of elements, or None if no tagged elements found
    """
    try:
        # Check Host property first (for family instance tags)
        if hasattr(tag, "Host") and tag.Host:
            return tag.Host
            
        # Check different tag reference properties
        for property_name in ["TaggedLocalElementIds", "TaggedElementIds"]:
            if hasattr(tag, property_name):
                hosts = [doc.GetElement(id) for id in getattr(tag, property_name) if doc.GetElement(id)]
                if hosts:
                    return hosts if len(hosts) >= 1 else None
                    
        # Last resort - check tagged references
        if hasattr(tag, "GetTaggedReferences"):
            hosts = [doc.GetElement(ref.ElementId) for ref in tag.GetTaggedReferences() if doc.GetElement(ref.ElementId)]
            if hosts:
                return hosts if len(hosts) >= 1 else None
                
        return None
        
    except Exception:
        return None


def purge_tags(bad_host_family_names, tag_category, doc = DOC):
    """get all the tags from project, if its host's name is in the list, delete it.
    Note that: if tag is tagging multiple elements and anyone of them is in the list, the shared tag will be deleted.
    This should not be too much of a issue in most case it is used.
    
    Args:
        bad_host_family_names: list of family names that are not allowed to be tagged
        tag_category: the category of the tags to be deleted
        doc: the current document
    """
    from pyrevit import script
    output = script.get_output()
    all_tags = DB.FilteredElementCollector(doc).OfCategory(tag_category).WhereElementIsNotElementType().ToElements()
    for tag in all_tags:
        hosts = get_tagged_elements(tag, doc)
        if hosts is None:
            continue
        if len(hosts) > 1:
            is_shared = True
        else:
            is_shared = False

        for host in hosts:
            if host is None:
                continue
            try:
                if hasattr(host, "Symbol"):
                    if host.Symbol.FamilyName in bad_host_family_names:
                        doc.Delete(tag.Id)
                        if is_shared:
                            print ("Shared tag deleted for element: {}".format(output.linkify(host.Id)))
                else:
                    ERROR_HANDLE.print_note("Tag is not tagging a valid element: {}, {}".format(output.linkify(tag.Id), host))
            except Exception as e:
                ERROR_HANDLE.print_note(e)
                



def retag_by_family_type(tag_family_name, tag_type_name, host_family_name, host_type_name, doc = DOC):
    """retag all the tags with the given family and type name"""
    
    all_tags = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Tags).ToElements()
    
    # Get the tag type element id first
    tag_type = DB.FilteredElementCollector(doc)\
                .OfClass(DB.FamilySymbol)\
                .Where(lambda x: x.FamilyName == tag_family_name and x.Name == tag_type_name)\
                .FirstElement()
    
    if tag_type is None:
        print("Quack! Couldn't find that tag type. Did it fly south for the winter?")
        return
        
    for tag in all_tags:
        host = get_tagged_elements(tag, doc)
        if host and host.FamilyName == host_family_name and host.TypeName == host_type_name:
            try:
                # Here's the correct way to change the tag type
                tag.ChangeTypeId(tag_type.Id)
            except Exception as e:
                print("Oops! This tag is being rebellious: {}".format(e))
                # Maybe it's having an identity crisis?
                continue
