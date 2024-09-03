#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "List selected detail items to a dump drafting view, or 3D family to a view you picked."
__title__ = "List\nFamilies"


import os
from pyrevit import script #



import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
from EnneadTab import NOTIFICATION
from EnneadTab.REVIT import REVIT_APPLICATION
from EnneadTab import ERROR_HANDLE, LOG
from EnneadTab.REVIT import REVIT_SELECTION, REVIT_VIEW, REVIT_FAMILY, REVIT_FORMS
from Autodesk.Revit import DB # pyright: ignore
# from rpw.db import family 
# from Autodesk.Revit import UI # pyright: ignore
UIDOC = REVIT_APPLICATION.get_uidoc()
DOC = REVIT_APPLICATION.get_doc()

DETAIL_ITEM_DUMP_VIEW = "EnneadTab_Detail Item Dump"
FAMILY_DUMP_VIEW = "EnneadTab_Family Dump"
FAMILY_DUMP_LEVEL = "EA_Family_List_Internal_Level"
INTERNAL_COMMENT = "EnneadTab List Family Dump"
FAMILY_DUMP_WALL_COMMENT = "EA_Family_List_Internal_Wall"
class Deployer:
    def __init__(self, view, families, tag_family):
        self.view = view
        self.families = families
        
        if tag_family:
            self.add_tag = True
            self.tag_symbol = DOC.GetElement(list(tag_family.GetFamilySymbolIds())[0])
            if not self.tag_symbol.IsActive:
                self.tag_symbol.Activate()
        else:
            self.add_tag = False

        self.pointer = DB.XYZ(0, 0, 0)

        self.purge_old_dump_family()

        for i, family in enumerate(families):
            NOTIFICATION.messenger("{}/{}: [{}]".format(i+1, len(families), family.Name))
            self.deploy_family(family)
            
    def purge_old_dump_family(self):
        all_instance = DB.FilteredElementCollector(DOC, self.view.Id).OfClass(DB.FamilyInstance).ToElements()
        for instance in all_instance:
            try:
                if instance.LookupParameter("Comments").AsString() == INTERNAL_COMMENT:
                    DOC.Delete(instance.Id)
            except:
                pass

        all_walls = DB.FilteredElementCollector(DOC, self.view.Id).OfClass(DB.Wall).ToElements()
        for wall in all_walls:
            try:
                if wall.LookupParameter("Comments").AsString().startswith( FAMILY_DUMP_WALL_COMMENT):
                    DOC.Delete(wall.Id)
            except:
                pass

        DOC.Regenerate()

    def step_right(self, x):
        self.pointer = self.pointer.Add(DB.XYZ(x, 0, 0))

    def step_down(self, y):
        self.pointer = self.pointer.Add(DB.XYZ(0, -y, 0))


    def reset_x(self):
        self.pointer = DB.XYZ(0, self.pointer.Y, 0)



    @ERROR_HANDLE.try_catch_error()
    def deploy_family(self, family):


        self.reset_x()
  
        max_h = -1
        min_gap = 5
        for type_id in family.GetFamilySymbolIds():
            family_type = DOC.GetElement(type_id)

            if not family_type.IsActive:
                family_type.Activate()

            if family.FamilyPlacementType == DB.FamilyPlacementType.ViewBased:
                instance = DOC.Create.NewFamilyInstance(self.pointer, family_type, self.view)
            elif family.FamilyPlacementType == DB.FamilyPlacementType.CurveBasedDetail:
                line = DB.Line.CreateBound(self.pointer, self.pointer + self.view.RightDirection  * 10)              
                instance = DOC.Create.NewFamilyInstance(line, family_type, self.view)
            elif family.FamilyPlacementType in [DB.FamilyPlacementType.OneLevelBased, DB.FamilyPlacementType.WorkPlaneBased]:
                level = self.view.GenLevel
                if not level:
                    dump_view = REVIT_VIEW.get_view_by_name(FAMILY_DUMP_VIEW)
                    if dump_view:
                        level = dump_view.GenLevel
                    else:
                        level = get_internal_dump_level()
                        
                project_pt = DB.XYZ(self.pointer.X,self.pointer.Y, 0)
                instance = DOC.Create.NewFamilyInstance(project_pt, family_type, level, DB.Structure.StructuralType.NonStructural)
            elif family.FamilyPlacementType == DB.FamilyPlacementType.OneLevelBasedHosted:
                level = self.view.GenLevel
                if not level:
                    dump_view = REVIT_VIEW.get_view_by_name(FAMILY_DUMP_VIEW)
                    if dump_view:
                        level = dump_view.GenLevel
                    else:
                        level = get_internal_dump_level()

                host_wall = get_internal_dump_wall(self.pointer, family.Name)
                secure_valid_wall_length(host_wall, self.pointer)
                wall_curve = host_wall.Location.Curve
                project_pt = wall_curve.Project(self.pointer).XYZPoint
                project_pt = DB.XYZ(project_pt.X, project_pt.Y, level.Elevation)
                ref_direction = DB.XYZ(0, 1, 0)
                instance = DOC.Create.NewFamilyInstance(project_pt, 
                                                        family_type, 
                                                        ref_direction, 
                                                        host_wall, 
                                                        DB.Structure.StructuralType.NonStructural)

                
                # immediately move the inserted element so it does not miss the host when the host is far away
                DB.ElementTransformUtils.MoveElement(DOC, instance.Id, DB.XYZ(0,0, level.Elevation))
            else:
                print ("[{}]:{} family_placement_type is [{}], need special handle, ask SZ for detail.".format(family.Name, 
                                                                                            family_type.LookupParameter("Type Name").AsString(), 
                                                                                            family.FamilyPlacementType))
                continue
            DOC.Regenerate()
            instance.LookupParameter("Comments").Set(INTERNAL_COMMENT)


        
            self.view.IsolateElementTemporary (instance.Id)
            # print ("[{}]:{}".format(family.Name, family_type.LookupParameter("Type Name").AsString()))
            if is_good_category(instance):
                UIDOC.ShowElements(instance)
            DOC.Regenerate()
            if self.view.ViewType != DB.ViewType.ThreeD:
                bbox = self.view.Outline
                if not bbox:
                    print ("no boundingbox for [{}]:{}".format(family.Name, family_type.LookupParameter("Type Name").AsString()))
                    self.view.DisableTemporaryViewMode (DB.TemporaryViewMode.TemporaryHideIsolate )
                    continue
                size_x = bbox.Max.U - bbox.Min.U
                size_y = bbox.Max.V - bbox.Min.V
                size_x, size_y = size_x * self.view.Scale, size_y * self.view.Scale
            else:
                bbox = instance.get_BoundingBox(self.view)
                if not bbox:
                    print ("no bbox for {}".format(instance))
                    self.view.DisableTemporaryViewMode (DB.TemporaryViewMode.TemporaryHideIsolate )
                    continue
                size_x = bbox.Max.X - bbox.Min.X
                size_y = bbox.Max.Y - bbox.Min.Y
                size_x, size_y = size_x * self.view.Scale, size_y * self.view.Scale
            max_h = max(max_h, size_y)
            self.view.DisableTemporaryViewMode (DB.TemporaryViewMode.TemporaryHideIsolate )



            
            DB.ElementTransformUtils.MoveElement(DOC, instance.Id, DB.XYZ(size_x/2, size_y/2, 0))




            if self.add_tag:
                tag = DB.IndependentTag.Create(DOC, 
                                                self.tag_symbol.Id, 
                                                self.view.Id, 
                                                DB.Reference(instance),
                                                True,
                                                DB.TagOrientation .Horizontal,
                                                self.pointer.Add(DB.XYZ(size_x/2, -min_gap * 0.2, 0)))

                DB.ElementTransformUtils.MoveElement(DOC, tag.Id, self.view.ViewDirection + DB.XYZ(size_x/2, 0, 0)) # this force tag to regenreate graphic
                

            self.step_right(size_x * 2)

        self.step_down(max(min_gap, max_h*2))


            
def is_good_category(instance):
    if isinstance(instance, DB.Panel):
        return False
    if isinstance(instance, DB.Mullion):
        return False
    return True
            


        
@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def list_family():
    opts = [
        ["List Detail Items", "They will showup in a drafting view"], 
        ["List 3D Family","Work In Progress feature: They will show up in a non-drafting view you picked. !!!<NOTE>!!!: 3D family will show in all project views."]
        ]
    sel = REVIT_FORMS.dialogue(main_text="Select what kind of family to list...", options=opts)
    if not sel:
        return
    if sel == opts[0][0]:
        list_detail_items()
    elif sel == opts[1][0]:
        list_3d_family()

def list_3d_family():
    families = REVIT_SELECTION.pick_family(multi_select=True, include_2D=False)
    if not families:
        return
    opts = [
        "Use 3D view", 
        "Use Plan view"
        ]
    sel = REVIT_FORMS.dialogue(main_text="Select what kind of view to show results...", options=opts)
    if not sel:
        return
    family_dump_view_localized = FAMILY_DUMP_VIEW
    if sel == opts[0]:
        family_dump_view_localized += "_3D"
    elif sel == opts[1]:
        family_dump_view_localized += "_Plan"
    view = REVIT_VIEW.get_view_by_name(family_dump_view_localized)
    
    if not view:
        t = DB.Transaction(DOC, "Make new view: " + family_dump_view_localized)
        t.Start()
        if sel == opts[0]:
            view = DB.View3D.CreateIsometric (DOC, REVIT_VIEW.get_default_view_type("3d").Id)
        else:
            new_level = get_internal_dump_level()
            view = DB.ViewPlan.Create(DOC, REVIT_VIEW.get_default_view_type("plan").Id, new_level.Id)
        view.Name = family_dump_view_localized
        view.Scale = 2
        t.Commit()

    UIDOC.ActiveView = view


        
    t = DB.Transaction(DOC, __title__)
    t.Start()

    change_view_group(view)
    
    family_name = "EA_Family_Tag"

    tag_family = REVIT_FAMILY.get_family_by_name(family_name,
                                                 load_path_if_not_exist=None)
    
    Deployer(view, families, tag_family)

    
    
    t.Commit()

    NOTIFICATION.messenger("Families listed at view: " + view.Name)

def list_detail_items():
    detail_families = REVIT_SELECTION.pick_detail_componenet(multi_select=True)


    if not detail_families:
        return


    view = REVIT_VIEW.get_view_by_name(DETAIL_ITEM_DUMP_VIEW)

    if not view:
        t = DB.Transaction(DOC, "Make new view: " + DETAIL_ITEM_DUMP_VIEW)
        t.Start()
        view = DB.ViewDrafting.Create(DOC, REVIT_VIEW.get_default_view_type("drafting").Id)
        view.Name = DETAIL_ITEM_DUMP_VIEW
        view.Scale = 2
        t.Commit()

    UIDOC.ActiveView = view
        
    t = DB.Transaction(DOC, __title__)
    t.Start()

    change_view_group(view)
    
    family_name = "EA_DetailItem_Tag"

    tag_family = REVIT_FAMILY.get_family_by_name(family_name,
                                                 load_path_if_not_exist="{}\\{}.rfa".format(os.path.dirname(__file__), family_name))
    
    Deployer(view, detail_families, tag_family)

    
    
    t.Commit()

    NOTIFICATION.messenger("Detail Items listed at view: " + view.Name)

def change_view_group(view):
    try:
        view.LookupParameter("Views_$Group").Set("Ennead")
        view.LookupParameter("Views_$Series").Set("List Item (´･ᆺ･`)")
    except:
        pass

def get_internal_dump_level():
    all_levels = DB.FilteredElementCollector(DOC).OfClass(DB.Level).ToElements()
    for level in all_levels:
        if level.Name == FAMILY_DUMP_LEVEL:
            return level

    new_level = DB.Level.Create(DOC, -999)
    new_level.Name = FAMILY_DUMP_LEVEL
    return new_level


def get_internal_dump_wall(family_ref_pt, family_name):
    all_walls = DB.FilteredElementCollector(DOC).OfClass(DB.Wall).ToElements()
    for wall in all_walls:
        if wall.LookupParameter("Comments").AsString() == FAMILY_DUMP_WALL_COMMENT + "_" + family_name:
            return wall
    level = get_internal_dump_level()

    wall = DB.Wall.Create(DOC, DB.Line.CreateBound(DB.XYZ(-10, family_ref_pt.Y, 0), DB.XYZ(10, family_ref_pt.Y, 0)), level.Id, False)
    wall.LookupParameter("Comments").Set(FAMILY_DUMP_WALL_COMMENT + "_" + family_name)
    wall.LookupParameter("Unconnected Height").Set(15) 
    DOC.Regenerate()
    return wall

def secure_valid_wall_length(wall, family_ref_pt):
    line = wall.Location.Curve
    end_pt = line.GetEndPoint(1)
    if end_pt.X + 10 < family_ref_pt.X:
        end_pt = family_ref_pt.X + DB.XYZ(10,0,0)
        line = DB.Line.CreateBound(wall.Location.Curve.GetEndPoint(0), end_pt)
        wall.Location.Curve = line



################## main code below #####################


if __name__ == "__main__":
    output = script.get_output()
    output.close_others()
    list_family()
    







