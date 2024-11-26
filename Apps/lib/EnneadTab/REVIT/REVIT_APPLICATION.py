#!/usr/bin/python
# -*- coding: utf-8 -*-

from Autodesk.Revit import UI # pyright: ignore
from Autodesk.Revit import DB # pyright: ignore

def get_app():
    app = __revit__ # pyright: ignore
    if hasattr(app, 'Application'):
        app = app.Application
    return app


def get_uiapp():
    """Return UIApplication provided to the running command."""
    if isinstance(__revit__, UI.UIApplication): # pyright: ignore
        return __revit__  # pyright: ignore

    from Autodesk.Revit import ApplicationServices # pyright: ignore
    if isinstance(__revit__, ApplicationServices.Application): # pyright: ignore
        return UI.UIApplication(__revit__) # pyright: ignore
    return __revit__ # pyright: ignore


def get_uidoc():
    """Return active UIDocument."""
    return getattr(get_uiapp(), 'ActiveUIDocument', None)


def get_doc():
    """Return active Document."""
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
    """Return view that is active (UIDocument.ActiveView)."""
    return getattr(get_uidoc(), 'ActiveView', None)




def open_safety_doc_family():
    filepath = SAMPLE_FILE.get_file("EnneadTab Safety Doc.rfa")
    safe_family = FOLDER.copy_file_to_local_dump_folder(filepath, ignore_warning=True)

    open_and_active_project(safe_family)


def open_and_active_project(filepath):
    """return a ui document"""
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
    """close opened docs by providing the name of the docs to close

    Args:
        names (list, optional): list of docs to close. Defaults to [].
        close_all (bool, optional): if true, close every open docs, you do not need to provide the name list. Defaults to False.
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
    """get main docs that is NOT link doc or family doc

    Returns:
        list of docs: all docs that is not link or family doc
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
    """get all the opened family docs

    Args:
        including_current_doc (bool, optional): if true, current family doc is included as well. Defaults to False.

    Returns:
        list of family docs: _description_
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
    """pick opended family docs.

    Args:
        select_multiple (bool, optional): _description_. Defaults to True.
        including_current_doc (bool, optional): _description_. Defaults to False.

    Returns:
        list of family docs: _description_
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
    from pyrevit import forms
    docs = get_revit_link_docs(including_current_doc = including_current_doc, link_only = link_only )
    docs = forms.SelectFromList.show(docs,
                                    name_attr = "Title",
                                    multiselect = select_multiple,
                                    title = "Pick some revit links")
    return docs


def get_revit_link_types(doc):
    return list(DB.FilteredElementCollector(doc).OfClass(DB.RevitLinkType).ToElements())

def close_revit_app():
    """try its best to close the revit session.
    """
    from Autodesk.Revit.UI import RevitCommandId,PostableCommand  #pyright: ignore

    uiapp = get_uiapp()


    CmndID = RevitCommandId.LookupPostableCommandId (PostableCommand .ExitRevit)
    CmId = CmndID.Id
    uiapp.PostCommand(CmndID)


