#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "Registration tool for automatic Area comment updates from Excel data. Monitors area elements for changes and syncs with external data."
__title__ = "(Un)Register Area Comment Updater"

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

from EnneadTab import ERROR_HANDLE, LOG, DATA_FILE, GUID
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_UPDATER
from Autodesk.Revit import DB # pyright: ignore 

UIDOC = REVIT_APPLICATION.get_uidoc()
DOC = REVIT_APPLICATION.get_doc()

# Reference to external script that handles area processing
import os
import sys

# Path to the target script
script_dir = os.path.dirname(os.path.dirname(__file__))
target_dir = os.path.join(script_dir, "transfer_in_excel_target.pushbutton")

# Add directory to path
if not target_dir in sys.path:
    sys.path.append(target_dir)



class AreaCommentsUpdaterFromExcel(REVIT_UPDATER.EnneadTabUpdater):
    @ERROR_HANDLE.try_catch_error()
    def Initialize(self):
        from transfer_in_excel_target_script import process_area, get_program_target_dict
        self.process_area = process_area
        self.program_target_dict = get_program_target_dict()
        self.app_name = "area_comment_updater"

    @ERROR_HANDLE.try_catch_error()
    def Execute(self, data):
        """this is where the actual code will happen"""
        doc = data.GetDocument()
        modded_ids = data.GetModifiedElementIds()


        for id in modded_ids:
            area = doc.GetElement(id)
            self.process_area(area, self.program_target_dict)



@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def register_area_comment_updater(doc):
   
    # Get the current document and application
    app = REVIT_APPLICATION.get_app()

    # Create an instance of the updater
    updater = AreaCommentsUpdaterFromExcel()
    updater.Initialize()

    # Create a unique Guid for the updater
    guid = GUID.get_guid("area_comment_updater")

    # Create an UpdaterId using the AddInId of the current application and the unique Guid
    updater_id = DB.UpdaterId(app.ActiveAddInId, guid)

    # Set the identifier in the updater instance
    updater.updater_id = updater_id


    sample_area = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Areas).FirstElement()
    para = sample_area.LookupParameter("Area_$Department_Program Type")

    # Register the updater with a trigger for area elements
    if not DB.UpdaterRegistry.IsUpdaterRegistered(updater_id, doc):
        DB.UpdaterRegistry.RegisterUpdater(updater, doc)
        
        # Create a filter for area elements
        area_filter = DB.ElementCategoryFilter(DB.BuiltInCategory.OST_Areas)
        
        # Assign the trigger to the updater for element updates
        DB.UpdaterRegistry.AddTrigger(updater_id, area_filter, DB.Element.GetChangeTypeParameter (para))
        
        print('Success', 'Updater has been registered and trigger has been set!')
        print('Notice', 'IF YOU MAKE CHANGES TO EXCEL FILE PLEASE RE-REGISTER updater')
    else:
        print('Notice', 'Updater is already registered. Now unregistering...Revit will stop auto updating comments')
        DB.UpdaterRegistry.UnregisterUpdater(updater_id, doc)
        DB.UpdaterRegistry.RemoveDocumentTriggers(updater_id, doc)


################## main code below #####################
if __name__ == "__main__":
    register_area_comment_updater(DOC)







