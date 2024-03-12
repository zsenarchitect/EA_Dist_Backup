#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Sen Zhang has not writed documentation for this tool, but he should!"
__title__ = "List\nDetail Items"

# from pyrevit import forms #
from pyrevit import script #

import ENNEAD_LOG
import EnneadTab
from EnneadTab.REVIT import REVIT_SELECTION, REVIT_VIEW
from Autodesk.Revit import DB 
# from Autodesk.Revit import UI
uidoc = EnneadTab.REVIT.REVIT_APPLICATION.get_uidoc()
doc = EnneadTab.REVIT.REVIT_APPLICATION.get_doc()

LIST_VIEW = "EA_DETAIL_DUMP"


class Deployer:
    def __init__(self, view, families, textnote_type):
        self.view = view
        self.families = families
        self.textnote_type = textnote_type

        self.pointer = DB.XYZ(0, 0, 0)


        map(self.deploy_family, families)
            


    def step_right(self, x):
        self.pointer = self.pointer.Add(DB.XYZ(x, 0, 0))

    def step_down(self, y):
        self.pointer = self.pointer.Add(DB.XYZ(0, -y, 0))


    def reset_x(self):
        self.pointer = DB.XYZ(0, self.pointer.Y, 0)




    def deploy_family(self, family):

        self.reset_x()
  
        max_h = -1
        min_gap = 3
        for type_id in family.GetFamilySymbolIds():
            print (self.pointer)
            family_type = doc.GetElement(type_id)

            if not family_type.IsActive:
                
                family_type.Activate()

            instance = doc.Create.NewFamilyInstance(self.pointer, family_type, self.view)
            doc.Regenerate()


            # get rough 2D boundingbox
            self.view.IsolateElementTemporary (instance.Id)
            uidoc.ShowElements(instance)
            bbox = self.view.Outline
            if not bbox:
                print ("no bbox for {}".format(instance))
                continue
            size_x = bbox.Max.U - bbox.Min.U
            size_y = bbox.Max.V - bbox.Min.V
            size_x, size_y = size_x * self.view.Scale, size_y * self.view.Scale
            max_h = max(max_h, size_y)
            self.view.DisableTemporaryViewMode (DB.TemporaryViewMode.TemporaryHideIsolate )



            
            DB.ElementTransformUtils.MoveElement(doc, instance.Id, DB.XYZ(size_x/2, size_y/2, 0))

            note = "[{}]\n{}".format(family.Name, family_type.LookupParameter("Type Name").AsString())
            print (note)


            textnote_option = DB.TextNoteOptions()
            textnote_option.HorizontalAlignment = DB.HorizontalTextAlignment.Center
            textnote_option.TypeId = self.textnote_type.Id
            DB.TextNote.Create(doc, self.view.Id, self.pointer.Add(DB.XYZ(size_x/2, -min_gap * 0.5, 0)), note, textnote_option)

            self.step_right(size_x * 1.2)

        self.step_down(max(min_gap, max_h*2))


            

            


        
        

    
@EnneadTab.ERROR_HANDLE.try_catch_error
def list_detail_items():
    detail_families = REVIT_SELECTION.pick_detail_componenet(multi_select=True)


    if not detail_families:
        return

    textnote_type = REVIT_SELECTION.pick_textnote_type()
    if not textnote_type:
        return

    view = REVIT_VIEW.get_view_by_name(LIST_VIEW)

    if not view:
        t = DB.Transaction(doc, "Make new view: " + LIST_VIEW)
        t.Start()
        view = DB.ViewDrafting.Create(doc, REVIT_VIEW.get_default_view_type("drafting").Id)
        view.Name = LIST_VIEW
        t.Commit()

    uidoc.ActiveView = view
        
    t = DB.Transaction(doc, __title__)
    t.Start()
    Deployer(view, detail_families, textnote_type)

    
    
    t.Commit()
    


    # doc.ActiveView = view





################## main code below #####################


if __name__ == "__main__":
    output = script.get_output()
    output.close_others()
    list_detail_items()
    ENNEAD_LOG.use_enneadtab(coin_change = 20, tool_used = __title__.replace("\n", " "), show_toast = True)







