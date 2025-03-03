#!/usr/bin/python
# -*- coding: utf-8 -*-

from Autodesk.Revit import UI # pyright: ignore
from Autodesk.Revit import DB # pyright: ignore

def is_version_at_least(year_int = 2025):
    """Checks if the current Revit version is at least the specified year.
    Include the year if the version is exactly the year.
    
    Args:
        year_int (int): The year to compare against. Defaults to 2025. becasue this year has significant change in a lot of things
    """
    return int(get_app().VersionNumber) >= year_int


def get_app():
    """Returns the Revit Application instance.
    
    Returns:
        Application: The Revit Application object
    """
    app = __revit__ # pyright: ignore
    if hasattr(app, 'Application'):
        app = app.Application
    return app


def get_uiapp():
    """Returns the Revit UI Application instance.
    
    Returns:
        UIApplication: The Revit UI Application object
    """
    if isinstance(__revit__, UI.UIApplication): # pyright: ignore
        return __revit__  # pyright: ignore

    from Autodesk.Revit import ApplicationServices # pyright: ignore
    if isinstance(__revit__, ApplicationServices.Application): # pyright: ignore
        return UI.UIApplication(__revit__) # pyright: ignore
    return __revit__ # pyright: ignore


def get_uidoc():
    """Returns the active Revit UI Document.
    
    Returns:
        UIDocument: The active UI Document, or None if not available
    """
    return getattr(get_uiapp(), 'ActiveUIDocument', None)


def get_doc():
    """Returns the active Revit Document.
    
    Returns:
        Document: The active Document, or None if not available
    """
    return getattr(get_uidoc(), 'Document', None)



import os
import sys
root_folder = os.path.abspath((os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(root_folder)
import traceback
try:
    import FOLDER, SAMPLE_FILE, ERROR_HANDLE

except Exception as e:
    ERROR_HANDLE.print_note("REVIT_APPLICATION.py: Error importing Revit modules")
    ERROR_HANDLE.print_note(traceback.format_exc())







def get_active_view():
    """Returns the currently active view in Revit.
    
    Returns:
        View: The active view object, or None if not available
    """
    return getattr(get_uidoc(), 'ActiveView', None)




def open_safety_doc_family():
    filepath = SAMPLE_FILE.get_file("EnneadTab Safety Doc.rfa")
    safe_family = FOLDER.copy_file_to_local_dump_folder(filepath, ignore_warning=True)

    open_and_active_project(safe_family)


def open_and_active_project(filepath):
    """Opens and activates a Revit project or family file.
    
    Args:
        filepath (str): Full path to the Revit file to open
        
    Returns:
        UIDocument: The opened document's UI interface, or None if operation fails
    """
    try:
        return get_uiapp().OpenAndActivateDocument (filepath)
    except:
        pass
    try:
        app = __revit__ #pyright: ignore
        return UI.UIApplication(app).OpenAndActivateDocument (filepath)
    except:
        pass

    try:
        app = __revit__.ActiveUIDocument.Document  #pyright: ignore
        return UI.UIApplication(app).OpenAndActivateDocument (filepath)
    except:
        pass

    try:
        app = __revit__.ActiveUIDocument.Document  #pyright: ignore
        open_options = DB.OpenOptions()
        return UI.UIApplication(app).OpenAndActivateDocument (filepath, open_options, False)
    except:
        pass

    try:
        app = __revit__ #pyright: ignore
        open_options = DB.OpenOptions()
        return UI.UIApplication(app).OpenAndActivateDocument (filepath, open_options, False)
    except:
        pass

    ERROR_HANDLE.print_note ("Activate Failed")


def close_docs_by_name(names = [], close_all = False):
    """Closes specified Revit documents safely.
    
    Args:
        names (list): List of document names to close. Defaults to empty list
        close_all (bool): If True, closes all open documents regardless of names. Defaults to False
    """

    def safe_close(doc):
        name = doc.Title
        doc.Close(False)
        doc.Dispose()#########################
        print ("{} closed".format(name))

    docs = get_top_revit_docs()
    if close_all:
        map(safe_close, docs)
        return

    for doc in docs:
        if doc.Title in names:
            try:
                safe_close(doc)
            except Exception as e:
                print( e)
                print ("skip closing [{}]".format(doc.Title))


def get_top_revit_docs():
    """Retrieves all main Revit project documents.
    
    Returns:
        list: Collection of Document objects, excluding linked files and family documents
    """


    docs = get_app().Documents
    OUT = []
    for doc in docs:
        if doc.IsLinked:
            continue
        if doc.IsFamilyDocument:
            continue
        OUT.append(doc)
    return OUT


def get_all_family_docs(including_current_doc = False):
    """Retrieves all open family documents.
    
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
            # add attr check because if the context was zero-doc, there are no active UI doc.
            if hasattr(__revit__, "ActiveUIDocument") and doc.Title == __revit__.ActiveUIDocument.Document.Title: # pyright: ignore
                continue
        OUT.append(doc)
    return OUT


def select_family_docs(select_multiple = True, including_current_doc = False):
    """Displays UI for selecting open family documents.
    
    Args:
        select_multiple (bool): Allow multiple family selection. Defaults to True
        including_current_doc (bool): Include currently active family. Defaults to False
        
    Returns:
        list: Selected family Document objects, or single Document if select_multiple is False
    """
    from pyrevit import forms
    title = "Pick Families" if select_multiple else "Pick Family"
    return forms.SelectFromList.show(get_all_family_docs(including_current_doc = including_current_doc),
                                        name_attr = "Title",
                                        multiselect = select_multiple,
                                        title = title,
                                        button_name=title)


def select_top_level_docs(select_multiple = True):
    from pyrevit import forms
    docs = get_top_revit_docs()
    docs = forms.SelectFromList.show(docs,
                                    name_attr = "Title",
                                    multiselect = select_multiple,
                                    title = "Pick some open revit docs")
    return docs






def get_revit_link_docs(including_current_doc = False, link_only = False):
    """Retrieves Revit documents including or limited to linked files.
    
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
        
        if link_only:
            if not doc.IsLinked:
                continue

        OUT.append(doc)
    OUT.sort(key = lambda x: x.Title)
    return OUT

def select_revit_link_docs(select_multiple = True, including_current_doc = False, link_only = False):
    """Displays UI for selecting Revit link documents.
    
    Args:
        select_multiple (bool): Allow multiple document selection. Defaults to True
        including_current_doc (bool): Include active document. Defaults to False
        link_only (bool): Show only linked documents. Defaults to False
        
    Returns:
        list: Selected Document objects, or single Document if select_multiple is False
    """
    from pyrevit import forms
    docs = get_revit_link_docs(including_current_doc = including_current_doc, link_only = link_only )
    docs = forms.SelectFromList.show(docs,
                                    name_attr = "Title",
                                    multiselect = select_multiple,
                                    title = "Pick some revit links")
    return docs


def get_revit_link_types(doc):
    """Retrieves all RevitLinkType elements from specified document.
    
    Args:
        doc (Document): The Revit document to query
        
    Returns:
        list: Collection of RevitLinkType elements
    """
    return list(DB.FilteredElementCollector(doc).OfClass(DB.RevitLinkType).ToElements())

def close_revit_app():
    """Attempts to close the current Revit session using UI automation.
    """
    from Autodesk.Revit.UI import RevitCommandId,PostableCommand  #pyright: ignore

    uiapp = get_uiapp()


    CmndID = RevitCommandId.LookupPostableCommandId (PostableCommand .ExitRevit)
    CmId = CmndID.Id
    uiapp.PostCommand(CmndID)


