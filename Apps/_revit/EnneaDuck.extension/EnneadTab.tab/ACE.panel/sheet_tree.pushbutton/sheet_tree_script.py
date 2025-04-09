#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "Generate sheet and view relationship data for visualization. Data is saved to DUMP folder for later use with visualization tools."
__title__ = "View Reference\nTree"

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

from EnneadTab import ERROR_HANDLE, LOG, DATA_FILE, NOTIFICATION, EXE, UI
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_VIEW, REVIT_SHEET
from Autodesk.Revit import DB # pyright: ignore 


UIDOC = REVIT_APPLICATION.get_uidoc()
DOC = REVIT_APPLICATION.get_doc()


    
def get_view_references(view):
    """Get all views referenced by the given view through callouts, sections, elevation markers.
    
    Args:
        view: The source view to check for references
        
    Returns:
        list: List of dictionaries containing referenced view information:
            - id: Integer ID of referenced view
            - name: Name of referenced view
            - type: View type (e.g., FloorPlan, Section, Elevation)
            - ref_type: Reference type (Callout, Section, or Elevation)
    """
    references = []
    try:
        # print("\nProcessing references for view: {}".format(view.Name))

        # Get all view references in one collector call
        everything = DB.FilteredElementCollector(DOC, view.Id).ToElements()
        for item in everything:
            if item.Category is None or item.Category.Name != "Views":
                continue
                
            source_view = REVIT_VIEW.get_view_by_name(item.Name)
            if source_view:
                if source_view.ViewType == DB.ViewType.Schedule:
                    continue
                # print("  Find view marker <{}>, type: {}".format(source_view.Name, source_view.ViewType))
                source_view_sheet = REVIT_SHEET.get_sheet_by_view(source_view)
                if not source_view_sheet:
                    # if the view pointing to is not on sheet then i don't want to count as valid connection
                    continue
                references.append({
                    'name': source_view.Name,
                    # 'type': str(source_view.ViewType),
                    # "sheet": source_view_sheet.SheetNumber
                })


    except Exception as e:
        print("Error in get_view_references for view {}: {}".format(view.Name, str(e)))
        
    # print("# Found {} total references.".format(len(references)))
    return references

def get_sheet_data():
    data = {}
   
    all_views = REVIT_VIEW.ViewFilter().filter_archi_views().filter_sheeted_views().filter_non_viewsheet_views().to_views()


    # def inner_func(view):
    #     sheet = REVIT_SHEET.get_sheet_by_view(view)
                
    #     data[view.Name] = {
    #         'type': str(view.ViewType),
    #         'sheet': sheet.SheetNumber if sheet else None,
    #         'references': get_view_references(view)
    #     }

    # def label_func(view):
    #     return "Processing view: {}".format(view.Name)

    # UI.progress_bar(all_views, inner_func, label_func=label_func)



    for i, view in enumerate(all_views):
        print ("{}/{}: {}".format(i+1, len(all_views), view.Name))
        # Get the sheet number if view is placed on a sheet
        sheet = REVIT_SHEET.get_sheet_by_view(view)
        if sheet:
            sheet_number = sheet.SheetNumber
            detail_number = REVIT_VIEW.get_detail_number(view)
        else:
            sheet_number = None
            detail_number = None
                
        data[view.Name] = {
            'type': str(view.ViewType),
            'sheet': sheet_number,
            'detail': detail_number,
            'references': get_view_references(view)
        }

    return data
        
        

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def sheet_tree(doc):
    """Generate sheet and view relationship data and save to file.
    
    Args:
        doc: The Revit document to process
    """
    NOTIFICATION.messenger("Generating sheet tree data...Please hold tight!")
    data = get_sheet_data()
    DATA_FILE.set_data(data, "sheet_tree_data")
    # DATA_FILE.pretty_print_dict(data)
    NOTIFICATION.messenger("Sheet tree data generated successfully!")
    EXE.try_open_app("VizSheetTree")

################## main code below #####################
if __name__ == "__main__":
    sheet_tree(DOC)







