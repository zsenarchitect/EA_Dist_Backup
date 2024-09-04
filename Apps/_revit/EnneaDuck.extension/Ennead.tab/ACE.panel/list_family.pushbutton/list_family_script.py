#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "List selected detail items to a dump drafting view, or 3D family to a 3D view or floor plan view. Note that 3D family will show in all view, so this tool will first create a internal level far from main set and host most items there."
__title__ = "List\nFamilies"


import os
from pyrevit import script #



import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
from EnneadTab import DATA_CONVERSION, NOTIFICATION
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
FAMILY_DUMP_CEILING_COMMENT = "EA_Family_List_Internal_Ceiling"



class Deployer:
    def __init__(self, view, families, tag_family):
        self.view = view
        self.families = families
        
        if tag_family:
            self.add_tag = True
            self.tag_symbol = DOC.GetElement(list(tag_family.GetFamilySymbolIds())[0])
            if not self.tag_symbol.IsActive:
                t = DB.Transaction(DOC, "activate tag family")
                t.Start()
                self.tag_symbol.Activate()
                t.Commit()
        else:
            self.add_tag = False

        self.pointer = DB.XYZ(0, 0, 0)

        self.purge_old_dump_family()

        for i, family in enumerate(families):
            NOTIFICATION.messenger("{}/{}: [{}]".format(i+1, len(families), family.Name))
            self.deploy_family(family)

        t = DB.Transaction(DOC, "Disable Temporary View Mode")
        t.Start()
        self.view.DisableTemporaryViewMode (DB.TemporaryViewMode.TemporaryHideIsolate )
        t.Commit()


            
    def purge_old_dump_family(self):
        t = DB.Transaction(DOC, "purge old family")
        t.Start()
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
        t.Commit()

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
        is_need_host_wall = False
        for type_id in family.GetFamilySymbolIds():
            family_type = DOC.GetElement(type_id)
            if not family_type.IsActive:
                t = DB.Transaction(DOC, "Activate Symbol")
                t.Start()
                family_type.Activate()
                t.Commit()
                
            if family.FamilyPlacementType == DB.FamilyPlacementType.ViewBased:
                t = DB.Transaction(DOC, "Create Instance")
                t.Start()
                instance = DOC.Create.NewFamilyInstance(self.pointer, family_type, self.view)
                t.Commit()
            elif family.FamilyPlacementType == DB.FamilyPlacementType.CurveBasedDetail:
                t = DB.Transaction(DOC, "Create Instance")
                t.Start()
                line = DB.Line.CreateBound(self.pointer, self.pointer + self.view.RightDirection  * 10)              
                instance = DOC.Create.NewFamilyInstance(line, family_type, self.view)
                t.Commit()
            elif family.FamilyPlacementType in [DB.FamilyPlacementType.OneLevelBased, DB.FamilyPlacementType.WorkPlaneBased]:
                level = self.view.GenLevel
                if not level:
                    dump_view = REVIT_VIEW.get_view_by_name(FAMILY_DUMP_VIEW)
                    if dump_view:
                        level = dump_view.GenLevel
                    else:
                        level = get_internal_dump_level()
                        
                project_pt = DB.XYZ(self.pointer.X,self.pointer.Y, 0)
                t = DB.Transaction(DOC, "Create Instance")
                t.Start()
                instance = DOC.Create.NewFamilyInstance(project_pt, family_type, level, DB.Structure.StructuralType.NonStructural)
                t.Commit()
            elif family.FamilyPlacementType == DB.FamilyPlacementType.OneLevelBasedHosted:
                level = self.view.GenLevel
                if not level:
                    dump_view = REVIT_VIEW.get_view_by_name(FAMILY_DUMP_VIEW)
                    if dump_view:
                        level = dump_view.GenLevel
                    else:
                        level = get_internal_dump_level()

                # need to figure out host type is wall or ceiling
                host_type = get_family_host_type(family)

                if host_type == "Ceiling":
                    host_ceiling = get_internal_dump_ceiling(self.pointer, family.Name)
                    t = DB.Transaction(DOC, "Hide host to get better family sizing")
                    t.Start()
                    self.view.HideElementTemporary (host_ceiling.Id)
                    t.Commit()
                  
                    project_pt = DB.XYZ(self.pointer.X,self.pointer.Y, level.Elevation)

                    t = DB.Transaction(DOC, "Create Instance")
                    t.Start()
                    instance = DOC.Create.NewFamilyInstance(project_pt, 
                                                            family_type, 
                                                            host_ceiling, 
                                                            DB.Structure.StructuralType.NonStructural)

                    
                    # immediately move the inserted element so it does not miss the host when the host is far away
                    ceiling_offset = host_ceiling.LookupParameter("Height Offset From Level").AsDouble()
                    DB.ElementTransformUtils.MoveElement(DOC, instance.Id, DB.XYZ(0,0, level.Elevation + ceiling_offset))
                    t.Commit()
                elif host_type == "Wall":
                    is_need_host_wall = True
                    host_wall = get_internal_dump_wall(self.pointer, family.Name)
                    t = DB.Transaction(DOC, "Hide host to get better family sizing")
                    t.Start()
                    self.view.HideElementTemporary (host_wall.Id)
                    t.Commit()
                    
                    secure_valid_wall_length(host_wall, self.pointer)
                    wall_curve = host_wall.Location.Curve
                    project_pt = wall_curve.Project(self.pointer).XYZPoint
                    project_pt = DB.XYZ(project_pt.X, project_pt.Y, level.Elevation)
                    ref_direction = DB.XYZ(0, 1, 0)
                    t = DB.Transaction(DOC, "Create Instance")
                    t.Start()
                    instance = DOC.Create.NewFamilyInstance(project_pt, 
                                                            family_type, 
                                                            ref_direction, 
                                                            host_wall, 
                                                            DB.Structure.StructuralType.NonStructural)

                    
                    # immediately move the inserted element so it does not miss the host when the host is far away
                    DB.ElementTransformUtils.MoveElement(DOC, instance.Id, DB.XYZ(0,0, level.Elevation))
                    t.Commit()
                else:
                    print ("[{}]:{} host type is [{}], need special handle, ask SZ for detail.".format(family.Name, 
                                                                                            family_type.LookupParameter("Type Name").AsString(), 
                                                                                            host_type))
                    continue
            else:
                print ("[{}]:{} family_placement_type is [{}], need special handle, ask SZ for detail.".format(family.Name, 
                                                                                            family_type.LookupParameter("Type Name").AsString(), 
                                                                                            family.FamilyPlacementType))
                continue

            if not instance.IsValidObject:
                continue
            t = DB.Transaction(DOC, "Update Comments")
            t.Start()
            instance.LookupParameter("Comments").Set(INTERNAL_COMMENT)
            t.Commit()


            t = DB.Transaction(DOC, "Isolate Element To Zoom and get size")
            t.Start()
            self.view.IsolateElementTemporary (instance.Id)
            # print ("[{}]:{}".format(family.Name, family_type.LookupParameter("Type Name").AsString()))
            if is_good_category(instance):
                UIDOC.ShowElements(instance)
            DOC.Regenerate()
            if self.view.ViewType != DB.ViewType.ThreeD:
                bbox = self.view.Outline
                if not bbox:
                    print ("no boundingbox for [{}]:{}, not placing this instance".format(family.Name, family_type.LookupParameter("Type Name").AsString()))
                    self.view.DisableTemporaryViewMode (DB.TemporaryViewMode.TemporaryHideIsolate )
                    t.RollBack()
                    continue
                size_x = bbox.Max.U - bbox.Min.U
                size_y = bbox.Max.V - bbox.Min.V
                size_x, size_y = size_x * self.view.Scale, size_y * self.view.Scale
            else:
                bbox = instance.get_BoundingBox(self.view)
                if not bbox:
                    print ("no bbox for {}, not placing this instance".format(instance))
                    self.view.DisableTemporaryViewMode (DB.TemporaryViewMode.TemporaryHideIsolate )
                    t.RollBack()
                    continue
                size_x = bbox.Max.X - bbox.Min.X
                size_y = bbox.Max.Y - bbox.Min.Y
                size_x, size_y = size_x * self.view.Scale, size_y * self.view.Scale
            max_h = max(max_h, size_y)
            self.view.DisableTemporaryViewMode (DB.TemporaryViewMode.TemporaryHideIsolate )
            t.RollBack()



            t = DB.Transaction(DOC, "Create Instance")
            t.Start()
            DB.ElementTransformUtils.MoveElement(DOC, instance.Id, DB.XYZ(size_x/2, size_y/2, 0))
            t.Commit()




            if self.add_tag:
                t = DB.Transaction(DOC, "Create Tag")
                t.Start()
                tag = DB.IndependentTag.Create(DOC, 
                                                self.tag_symbol.Id, 
                                                self.view.Id, 
                                                DB.Reference(instance),
                                                True,
                                                DB.TagOrientation .Horizontal,
                                                self.pointer.Add(DB.XYZ(size_x/2, -min_gap * 0.2, 0)))

                DB.ElementTransformUtils.MoveElement(DOC, tag.Id, self.view.ViewDirection + DB.XYZ(size_x/2, 0, 0)) # this force tag to regenreate graphic
                t.Commit()
                

            self.step_right(size_x * 2)


            #  this is for prettification, so the end of wall looks more balanced.
            if is_need_host_wall:
                secure_valid_wall_length(host_wall, self.pointer)

        self.step_down(max(min_gap, max_h*2))


            
def is_good_category(instance):
    if isinstance(instance, DB.Panel):
        return False
    if isinstance(instance, DB.Mullion):
        return False
    return True
            
def get_family_host_type(family):
    return family.Parameter[DB.BuiltInParameter.FAMILY_HOSTING_BEHAVIOR].AsValueString()

  

        
@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def list_family():
    opts = [
        ["List Detail Items", "They will showup in a drafting view"], 
        ["List 3D Family","They will show up in a non-drafting view.\n<NOTE>: 3D family will show in all project views."]
        ]
    sel = REVIT_FORMS.dialogue(main_text="Select what kind of family to list...", options=opts)
    if not sel:
        return
    tg = DB.TransactionGroup(DOC, __title__)
    tg.Start()
    if sel == opts[0][0]:
        list_detail_items()
    elif sel == opts[1][0]:
        list_3d_family()
    tg.Commit()

    NOTIFICATION.messenger("all families listed.")

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


        


    change_view_group(view)
    
    family_name = "EA_Family_Tag"

    tag_family = REVIT_FAMILY.get_family_by_name(family_name,
                                                 load_path_if_not_exist=None)
    
    Deployer(view, families, tag_family)

    
    


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
        


    change_view_group(view)
    
    family_name = "EA_DetailItem_Tag"

    tag_family = REVIT_FAMILY.get_family_by_name(family_name,
                                                 load_path_if_not_exist="{}\\{}.rfa".format(os.path.dirname(__file__), family_name))
    
    Deployer(view, detail_families, tag_family)

    


    NOTIFICATION.messenger("Detail Items listed at view: " + view.Name)

def change_view_group(view):
    t = DB.Transaction(DOC, "Change View Group")
    t.Start()
    try:
        view.LookupParameter("Views_$Group").Set("Ennead")
        view.LookupParameter("Views_$Series").Set("List Item (´･ᆺ･`)")
        t.Commit()
    except:
        t.RollBack()

def get_internal_dump_level():
    all_levels = DB.FilteredElementCollector(DOC).OfClass(DB.Level).ToElements()
    for level in all_levels:
        if level.Name == FAMILY_DUMP_LEVEL:
            return level
    t = DB.Transaction(DOC, "Create Internal Level")
    t.Start()
    new_level = DB.Level.Create(DOC, -999)
    new_level.Name = FAMILY_DUMP_LEVEL
    t.Commit()
    return new_level


def get_internal_dump_wall(family_ref_pt, family_name):
    all_walls = DB.FilteredElementCollector(DOC).OfClass(DB.Wall).ToElements()
    for wall in all_walls:
        if wall.LookupParameter("Comments").AsString() == FAMILY_DUMP_WALL_COMMENT + "_" + family_name:
            return wall
    level = get_internal_dump_level()
    t = DB.Transaction(DOC, "Create Internal Wall")
    t.Start()
    wall = DB.Wall.Create(DOC, DB.Line.CreateBound(DB.XYZ(-5, family_ref_pt.Y, 0), DB.XYZ(20, family_ref_pt.Y, 0)), level.Id, False)
    wall.LookupParameter("Comments").Set(FAMILY_DUMP_WALL_COMMENT + "_" + family_name)
    wall.LookupParameter("Unconnected Height").Set(10) 
    t.Commit()
    return wall


def get_internal_dump_ceiling(family_ref_pt, family_name):
    all_ceilings = DB.FilteredElementCollector(DOC).OfClass(DB.Ceiling).ToElements()
    for ceiling in all_ceilings:
        if ceiling.LookupParameter("Comments").AsString() == FAMILY_DUMP_CEILING_COMMENT + "_" + family_name:
            return ceiling
    level = get_internal_dump_level()
    t = DB.Transaction(DOC, "Create Internal ceiling")
    t.Start()
    ceiling_type_id = DB.FilteredElementCollector(DOC).OfClass(DB.CeilingType).FirstElementId()
    #  make a rect curve loop for the ceiling
    short_side = 2
    long_side = 6

    crv_pts = [
        DB.XYZ(family_ref_pt.X-short_side, family_ref_pt.Y-short_side, 0),
        DB.XYZ(family_ref_pt.X+long_side, family_ref_pt.Y-short_side, 0), 
        DB.XYZ(family_ref_pt.X+long_side, family_ref_pt.Y+short_side, 0), 
        DB.XYZ(family_ref_pt.X-short_side, family_ref_pt.Y+short_side, 0)
        ]
    crvs = [DB.Line.CreateBound(crv_pts[i], crv_pts[i+1]) for i in range(len(crv_pts)-1)] + [DB.Line.CreateBound(crv_pts[-1], crv_pts[0])]
    crv_loop = DB.CurveLoop.Create(DATA_CONVERSION.list_to_system_list(crvs, type = DATA_CONVERSION.DataType.Curve, use_IList=False))
    
    # use a collection even though there is only one loop, note that the crv_loop is made into a list as well here.
    crv_loop_collection = DATA_CONVERSION.list_to_system_list([crv_loop], type = DATA_CONVERSION.DataType.CurveLoop, use_IList=False)
    
    ceiling = DB.Ceiling.Create(DOC, crv_loop_collection, ceiling_type_id, level.Id)
    ceiling.LookupParameter("Comments").Set(FAMILY_DUMP_CEILING_COMMENT + "_" + family_name)
    ceiling.LookupParameter("Height Offset From Level").Set(10)
    
    t.Commit()
    return ceiling


def secure_valid_wall_length(wall, family_ref_pt):
    line = wall.Location.Curve
    end_pt = line.GetEndPoint(1)
    if end_pt.X + 5 < family_ref_pt.X:
        end_pt = DB.XYZ(end_pt.X + 15,end_pt.Y,end_pt.Z)
        line = DB.Line.CreateBound(wall.Location.Curve.GetEndPoint(0), end_pt)
        t = DB.Transaction(DOC, "Modify wall curve")
        t.Start()
        wall.Location.Curve = line
        t.Commit()



################## main code below #####################


if __name__ == "__main__":
    output = script.get_output()
    output.close_others()
    list_family()
    







