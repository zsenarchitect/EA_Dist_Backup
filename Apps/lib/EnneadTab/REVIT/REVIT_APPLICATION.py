#!/usr/bin/python
# -*- coding: utf-8 -*-

from Autodesk.Revit import UI # pyright: ignore
from Autodesk.Revit import DB # pyright: ignore
import os
import sys
import traceback

# Setup imports
root_folder = os.path.abspath((os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(root_folder)

try:
    import FOLDER, SAMPLE_FILE, ERROR_HANDLE
except Exception as e:
    ERROR_HANDLE.print_note("REVIT_APPLICATION.py: Error importing Revit modules")
    ERROR_HANDLE.print_note(traceback.format_exc())


def get_revit_version():
    """Get the current Revit version.
    
    Returns:
        int: The current Revit version
    """
    return int(get_app().VersionNumber)

def is_version_at_least(year_int=2025):
    """Check if current Revit version meets or exceeds specified year.
    
    Args:
        year_int (int): Year to compare against. Defaults to 2025.
        
    Returns:
        bool: True if version meets or exceeds specified year
    """
    return get_revit_version() >= year_int

def get_app():
    """Get the Revit Application instance.
    
    Returns:
        Application: The Revit Application object
    """
    app = __revit__ # pyright: ignore
    if hasattr(app, 'Application'):
        app = app.Application
    return app

def get_uiapp():
    """Get the Revit UI Application instance.
    
    Returns:
        UIApplication: The Revit UI Application object
    """
    if isinstance(__revit__, UI.UIApplication): # pyright: ignore
        return __revit__ # pyright: ignore

    from Autodesk.Revit import ApplicationServices # pyright: ignore
    if isinstance(__revit__, ApplicationServices.Application): # pyright: ignore
        return UI.UIApplication(__revit__) # pyright: ignore
    return __revit__ # pyright: ignore

def get_uidoc():
    """Get the active Revit UI Document.
    
    Returns:
        UIDocument: The active UI Document, or None if not available
    """
    return getattr(get_uiapp(), 'ActiveUIDocument', None)

def get_doc():
    """Get the active Revit Document.
    
    Returns:
        Document: The active Document, or None if not available
    """
    return getattr(get_uidoc(), 'Document', None)

def get_active_view():
    """Get the currently active view in Revit.
    
    Returns:
        View: The active view object, or None if not available
    """
    return getattr(get_uidoc(), 'ActiveView', None)

def switch_away_from_family(family_name_to_avoid):
    """Switch away from current family document to another open family.
    
    Args:
        family_name_to_avoid (str): Name of family to avoid switching to
    """
    all_family_docs = get_all_family_docs()
    if len(all_family_docs) <= 1:
        return None
        
    for family_doc in all_family_docs:
        if family_doc.Title == family_name_to_avoid:
            continue
        return get_uiapp().OpenAndActivateDocument(family_doc.PathName)
    return None

def open_safety_doc_family():
    """Open a safety family document for closing operations."""
    filepath = SAMPLE_FILE.get_file("Closing Safety Doc.rfa")
    safe_family = FOLDER.copy_file_to_local_dump_folder(filepath, ignore_warning=True)
    open_and_active_project(safe_family)

def open_and_active_project(filepath):
    """Open and activate a Revit project or family file.
    
    Args:
        filepath (str): Full path to the Revit file to open
        
    Returns:
        UIDocument: The opened document's UI interface, or None if operation fails
    """
    try:
        return get_uiapp().OpenAndActivateDocument(filepath)
    except Exception as e:
        ERROR_HANDLE.print_note(traceback.format_exc())
        
    try:
        app = __revit__ # pyright: ignore
        return UI.UIApplication(app).OpenAndActivateDocument(filepath)
    except Exception as e:
        ERROR_HANDLE.print_note(traceback.format_exc())
        
    try:
        app = __revit__.ActiveUIDocument.Document # pyright: ignore
        return UI.UIApplication(app).OpenAndActivateDocument(filepath)
    except Exception as e:
        ERROR_HANDLE.print_note(traceback.format_exc())
        
    try:
        app = __revit__.ActiveUIDocument.Document # pyright: ignore
        open_options = DB.OpenOptions()
        return UI.UIApplication(app).OpenAndActivateDocument(filepath, open_options, False)
    except Exception as e:
        ERROR_HANDLE.print_note(traceback.format_exc())
        
    try:
        app = __revit__ # pyright: ignore
        open_options = DB.OpenOptions()
        return UI.UIApplication(app).OpenAndActivateDocument(filepath, open_options, False)
    except Exception as e:
        ERROR_HANDLE.print_note(traceback.format_exc())
        
    ERROR_HANDLE.print_note("Activate Failed")
    return None

def close_docs_by_name(names=None, close_all=False):
    """Close specified Revit documents safely.
    
    Args:
        names (list): List of document names to close. Defaults to empty list
        close_all (bool): If True, closes all open documents. Defaults to False
    """
    if names is None:
        names = []
        
    def safe_close(doc):
        name = doc.Title
        doc.Close(False)
        doc.Dispose()
        print("{} closed".format(name))

    docs = get_top_revit_docs()
    if close_all:
        map(safe_close, docs)
        return

    for doc in docs:
        if doc.Title in names:
            try:
                safe_close(doc)
            except Exception as e:
                print(traceback.format_exc())
                print("skip closing [{}]".format(doc.Title))

def get_top_revit_docs():
    """Get all main Revit project documents.
    
    Returns:
        list: Collection of Document objects, excluding linked files and family documents
    """
    docs = get_app().Documents
    return [doc for doc in docs if not doc.IsLinked and not doc.IsFamilyDocument]

def get_document_by_name(doc_name):
    """Get a document by its name.
    
    Args:
        doc_name (str): Name of document to find
        
    Returns:
        Document: The matching document, or None if not found
    """
    docs = get_app().Documents
    for doc in docs:
        if doc.Title == doc_name:
            return doc
    return None

def get_all_family_docs(including_current_doc=False):
    """Get all open family documents.
    
    Args:
        including_current_doc (bool): Include currently active family document. Defaults to False
        
    Returns:
        list: Collection of family Document objects
    """
    docs = get_app().Documents
    OUT = []
    for doc in docs:
        if not doc.IsFamilyDocument:
            continue
        if not including_current_doc:
            if hasattr(__revit__, "ActiveUIDocument") and doc.Title == __revit__.ActiveUIDocument.Document.Title: # pyright: ignore
                continue
        OUT.append(doc)
    return OUT

def select_family_docs(select_multiple=True, including_current_doc=False):
    """Display UI for selecting open family documents.
    
    Args:
        select_multiple (bool): Allow multiple family selection. Defaults to True
        including_current_doc (bool): Include currently active family. Defaults to False
        
    Returns:
        list: Selected family Document objects, or single Document if select_multiple is False
    """
    from pyrevit import forms
    title = "Pick Families" if select_multiple else "Pick Family"
    return forms.SelectFromList.show(
        get_all_family_docs(including_current_doc=including_current_doc),
        name_attr="Title",
        multiselect=select_multiple,
        title=title,
        button_name=title
    )

def select_top_level_docs(select_multiple=True):
    """Display UI for selecting top-level documents.
    
    Args:
        select_multiple (bool): Allow multiple document selection. Defaults to True
        
    Returns:
        list: Selected Document objects, or single Document if select_multiple is False
    """
    from pyrevit import forms
    docs = get_top_revit_docs()
    return forms.SelectFromList.show(
        docs,
        name_attr="Title",
        multiselect=select_multiple,
        title="Pick some open revit docs"
    )

def get_revit_link_docs(including_current_doc=False, link_only=False):
    """Get Revit documents including or limited to linked files.
    
    Args:
        including_current_doc (bool): Include active document. Defaults to False
        link_only (bool): Return only linked documents. Defaults to False
        
    Returns:
        list: Collection of Document objects matching specified criteria
    """
    docs = get_app().Documents
    OUT = []
    for doc in docs:
        if doc.IsFamilyDocument:
            continue
        if not including_current_doc:
            try:
                if doc.Title == get_doc().Title: # pyright: ignore
                    continue
            except:
                pass
        if link_only and not doc.IsLinked:
            continue
        OUT.append(doc)
    OUT.sort(key=lambda x: x.Title)
    return OUT

def select_revit_link_docs(select_multiple=True, including_current_doc=False, link_only=False):
    """Display UI for selecting Revit link documents.
    
    Args:
        select_multiple (bool): Allow multiple document selection. Defaults to True
        including_current_doc (bool): Include active document. Defaults to False
        link_only (bool): Show only linked documents. Defaults to False
        
    Returns:
        list: Selected Document objects, or single Document if select_multiple is False
    """
    from pyrevit import forms
    docs = get_revit_link_docs(including_current_doc=including_current_doc, link_only=link_only)
    return forms.SelectFromList.show(
        docs,
        name_attr="Title",
        multiselect=select_multiple,
        title="Pick some revit links"
    )

def get_revit_link_types(doc):
    """Get all RevitLinkType elements from specified document.
    
    Args:
        doc (Document): The Revit document to query
        
    Returns:
        list: Collection of RevitLinkType elements
    """
    return list(DB.FilteredElementCollector(doc).OfClass(DB.RevitLinkType).ToElements())

def close_revit_app():
    """Close the current Revit session using UI automation."""
    from Autodesk.Revit.UI import RevitCommandId, PostableCommand # pyright: ignore
    uiapp = get_uiapp()
    cmd_id = RevitCommandId.LookupPostableCommandId(PostableCommand.ExitRevit)
    uiapp.PostCommand(cmd_id)


def run_picked_command():
    from pyrevit import forms
    from Autodesk.Revit.UI import RevitCommandId, PostableCommand # pyright: ignore
    all_commands = [str(cmd) for cmd in dir(PostableCommand)]
    command_name = forms.SelectFromList.show(all_commands, 
                                     name_attr="Title", 
                                     multiselect=False, 
                                     title="Pick a command")
    cmd_id = RevitCommandId.LookupPostableCommandId(getattr(PostableCommand, command_name))
    uiapp = get_uiapp()
    uiapp.PostCommand(cmd_id)

# ------------------------------------------------------------------------------
# Cloud region helpers
# ------------------------------------------------------------------------------


def _collect_available_cloud_regions():
    """Return a list of all CloudRegion* static strings supported by this Revit.

    It inspects ModelPathUtils for region constants so the list automatically
    follows Autodesk additions (e.g. CloudRegionAPAC was introduced in 2023)."""
    names = [a for a in dir(DB.ModelPathUtils) if a.startswith("CloudRegion")]
    regions = []
    for attr in names:
        try:
            regions.append(getattr(DB.ModelPathUtils, attr))
        except Exception:
            continue
    # Ensure deterministic order (US first, then the rest alphabetically)
    regions.sort()
    if DB.ModelPathUtils.CloudRegionUS in regions:
        regions.remove(DB.ModelPathUtils.CloudRegionUS)
        regions.insert(0, DB.ModelPathUtils.CloudRegionUS)
    return regions


_REGION_LITERALS = {
    "US": DB.ModelPathUtils.CloudRegionUS,
    "EMEA": DB.ModelPathUtils.CloudRegionEMEA
}

# Dynamically add APAC if available
if hasattr(DB.ModelPathUtils, "CloudRegionAPAC"):
    _REGION_LITERALS["APAC"] = getattr(DB.ModelPathUtils, "CloudRegionAPAC")


def convert_region(region_text):
    """Convert human-readable region identifiers ("US", "EMEA", etc.) to the
    exact literals required by ConvertCloudGUIDsToCloudPath(). If the text is
    already a valid literal, it's passed through unchanged.

    Args:
        region_text (str): User or config supplied region string.

    Returns:
        str: Region literal accepted by Autodesk API.
    """
    if not region_text:
        # Default to US
        return DB.ModelPathUtils.CloudRegionUS

    upper = str(region_text).strip().upper()
    return _REGION_LITERALS.get(upper, region_text)


def get_known_regions():
    """Return a deterministic list of all known region literals."""
    # Combine literal mapping and any extras discovered dynamically
    regions = list(set(_collect_available_cloud_regions()) | set(_REGION_LITERALS.values()))
    # Keep ordering stable – US first, then alpha
    regions.sort()
    if DB.ModelPathUtils.CloudRegionUS in regions:
        regions.remove(DB.ModelPathUtils.CloudRegionUS)
        regions.insert(0, DB.ModelPathUtils.CloudRegionUS)
    return regions


if __name__ == "__main__":
    print(get_known_regions())