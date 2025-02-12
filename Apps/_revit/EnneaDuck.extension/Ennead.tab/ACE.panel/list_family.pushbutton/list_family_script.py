#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = """List selected detail items to a dump drafting view, or 3D family to a 3D view or floor plan view. 
Note that 3D family will show in all view, so this tool will first create a internal level far from main set and host most items there."""
__title__ = "List\nFamilies"
__tip__ = True


import os
from pyrevit import script
from pyrevit.revit import ErrorSwallower
import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
from EnneadTab import DATA_CONVERSION, NOTIFICATION, UI, SOUND
from EnneadTab.REVIT import REVIT_APPLICATION
from EnneadTab import ERROR_HANDLE, LOG
from EnneadTab.REVIT import REVIT_SELECTION, REVIT_VIEW, REVIT_FAMILY, REVIT_FORMS
from Autodesk.Revit import DB # pyright: ignore
# from rpw.db import family 
# from Autodesk.Revit import UI # pyright: ignore

# View and level naming constants
DETAIL_ITEM_DUMP_VIEW = "EnneadTab_Detail Item Dump"
FAMILY_DUMP_VIEW = "EnneadTab_Family Dump"
FAMILY_DUMP_LEVEL = "EA_Family_List_Internal_Level"
INTERNAL_COMMENT = "EnneadTab List Family Dump"
FAMILY_DUMP_WALL_COMMENT = "EA_Family_List_Internal_Wall"
FAMILY_DUMP_CEILING_COMMENT = "EA_Family_List_Internal_Ceiling"


class Deployer:
    """Handles deployment of families into views with optional tagging"""
    def __init__(self, view, families, tag_family=None):

        tag_family = None# Force turn to None during debugging
        self.doc = REVIT_APPLICATION.get_doc()
        self.uidoc = REVIT_APPLICATION.get_uidoc()
        self.view = view
        self.families = families
        if self.doc.ActiveView.Id != self.view.Id:
            self.uidoc.ActiveView = view
        
        # Update DOC references to self.doc
        if tag_family is not None:
            self.add_tag = True
            print ("tag_family: {}".format(tag_family))
            self.tag_symbol = self.doc.GetElement(list(tag_family.GetFamilySymbolIds())[0])
            if not self.tag_symbol.IsActive:
                t = DB.Transaction(self.doc, "activate tag family")
                t.Start()
                self.tag_symbol.Activate()
                t.Commit()
        else:
            self.add_tag = False

        # Initialize placement pointer and process families
        level = self.get_internal_dump_level()
        self.pointer = DB.XYZ(0, 0, level.Elevation)
        self.purge_old_dump_family()
        with ErrorSwallower() as swallower:
            UI.progress_bar(families,self.deploy_family,label_func=lambda x: "Deploying Family [{}]".format(x.Name), title="Deploying Families")


        # Cleanup view modes
        t = DB.Transaction(self.doc, "Disable Temporary View Mode")
        t.Start()
        self.view.DisableTemporaryViewMode(DB.TemporaryViewMode.TemporaryHideIsolate)
        t.Commit()
        
    def _get_model_text_elements(self):
        """Gets or creates model text elements needed for labeling
        
        Returns:
            tuple: (sample_model_text, label_text_type) or (None, None) if failed
        """
        # Get sample model text
        sample_model_text = DB.FilteredElementCollector(self.doc).OfClass(DB.ModelText).FirstElement()
        if not sample_model_text:
            print ("No sample model text found, you need to have at least 1 model text in the document otherwise you will see no labeling. Please please please.")
            return None, None

        # Get or create label text type
        all_text_types = DB.FilteredElementCollector(self.doc).OfClass(DB.ModelTextType).ToElements()
        label_text_type = None
        
        # Look for existing "Label" text type
        for text_type in all_text_types:
            if text_type.LookupParameter("Type Name").AsString() == "Label":
                label_text_type = text_type
                break
                
        # Create new label text type if not found
        if not label_text_type:
            t = DB.Transaction(self.doc, "Create Label Text Type")
            t.Start()
            label_text_type = sample_model_text.ModelTextType.Duplicate("Label")
            t.Commit()
            
        # Set label text type properties   
        t = DB.Transaction(self.doc, "Set Label Text Type Properties")
        t.Start()
        label_text_type.LookupParameter("Text Font").Set("Impact")
        label_text_type.LookupParameter("Text Size").Set(1)
        t.Commit()
        
        return sample_model_text, label_text_type

    def add_label_text(self, family):
        sample_model_text, label_text_type = self._get_model_text_elements()
        if not sample_model_text or not label_text_type:
            return
            
        t = DB.Transaction(self.doc, "Add Label Text")
        t.Start()
        new_text_model = DB.ElementTransformUtils.CopyElement(self.doc, 
                                                              sample_model_text.Id, 
                                                              self.pointer - sample_model_text.Location.Point)
        new_text_model = self.doc.GetElement(new_text_model[0])
  
        new_text_model.Depth = 0.01
        new_text_model.ModelTextType = label_text_type
        new_text_model.HorizontalAlignment = DB.HorizontalAlign.Right
        if family.FamilyCategory:
            family_cate_name = family.FamilyCategory.Name
        else:
            family_cate_name = "Unknown Category"
        new_text_model.Text = "[{}] {}".format(family_cate_name, family.Name)
        new_text_model.LookupParameter("Comments").Set(INTERNAL_COMMENT)
        size_x, size_y = self._calculate_instance_size(new_text_model)
        DB.ElementTransformUtils.MoveElement(self.doc, 
                                            new_text_model.Id, 
                                            self.pointer - new_text_model.Location.Point + DB.XYZ(-5,-size_y/2,0)) # adding Y as 2 to make it visually along to pointer Y axis


        self.max_label_width = max(self.max_label_width, size_x)
        t.Commit()
    
    def purge_old_dump_family(self):
        """Purges all elements with specific comments from the view"""
        elements_to_purge = [
            (DB.BuiltInCategory.OST_ModelText, INTERNAL_COMMENT, "equals"),
            (DB.BuiltInCategory.OST_GenericModel, INTERNAL_COMMENT, "equals"),
            (DB.BuiltInCategory.OST_Walls, FAMILY_DUMP_WALL_COMMENT, "startswith"),
            (DB.BuiltInCategory.OST_Ceilings, FAMILY_DUMP_CEILING_COMMENT, "startswith"),
            (DB.BuiltInCategory.OST_CurtainWallPanels, INTERNAL_COMMENT, "equals"),
            (DB.BuiltInCategory.OST_DetailComponents, INTERNAL_COMMENT, "equals"),
            (DB.FamilyInstance, INTERNAL_COMMENT, "equals")
        ]
        
        t = DB.Transaction(self.doc, "purge old family")
        t.Start()
        
        for category_or_class, comment_value, comparison_type in elements_to_purge:
            self._delete_elements_by_comment(category_or_class, comment_value, comparison_type)
            
        self.doc.Regenerate()
        t.Commit()
        
    def _delete_elements_by_comment(self, category_or_class, comment_value, comparison_type):
        """Helper method to delete elements based on their comment parameter
        
        Args:
            category: Revit DB BuiltInCategory to filter
            comment_value: String to match in Comments parameter
            comparison_type: String indicating comparison method ('equals' or 'startswith')
        """
        if "OST" in str(category_or_class):
            elements = DB.FilteredElementCollector(self.doc, self.view.Id)\
                        .OfCategory(category_or_class)\
                        .WhereElementIsNotElementType()\
                        .ToElements()
        else:
            elements = DB.FilteredElementCollector(self.doc, self.view.Id)\
                        .OfClass(category_or_class)\
                        .WhereElementIsNotElementType()\
                        .ToElements()

        # print ("purging {} elements of category {}".format(len(elements), category_or_class))
        for element in elements:
            try:
                comment = element.LookupParameter("Comments").AsString()
                should_delete = False
                
                if comparison_type == "equals":
                    should_delete = (comment == comment_value)
                elif comparison_type == "startswith":
                    should_delete = comment.startswith(comment_value)
                    
                if should_delete:
                    self.doc.Delete(element.Id)
            except:
                continue

    def step_right(self, x):
        self.row_width += x
        self.pointer = self.pointer.Add(DB.XYZ(x, 0, 0))

    def step_down(self, y):
        self.pointer = self.pointer.Add(DB.XYZ(0, -y, 0))

    def reset_x_to_header(self):
        self.max_row_width = max(self.max_row_width, self.row_width)
        self.row_width = 0
        self.pointer = DB.XYZ(self.header_x, self.pointer.Y, self.pointer.Z)

    def confirm_new_layout_header(self, family):
        """if we are getting a new category, we need to reset the x position and add a new header"""
        if not hasattr(self, "header_x"):
            self.header_x = 0
            self.current_category_header = family.FamilyCategory.Name
            self.max_label_width = -1
            self.row_width = 0
            self.max_row_width = -1

        if family.FamilyCategory.Name != self.current_category_header:
            self.header_x += self.max_label_width + 30 + self.max_row_width # ideally it should be using current label max widht with previous row max width, but , well, i am not care enough to improve that yet. Just using mahic 10 and hope for the best
            self.pointer = DB.XYZ(self.header_x, 0, self.pointer.Z)
            self.current_category_header = family.FamilyCategory.Name

        return True

    
    def deploy_family(self, family):
        self.confirm_new_layout_header(family)
   
        self.reset_x_to_header()
        self.add_label_text(family)
  
        max_h = -1
        min_gap = 5
        is_need_host_wall = False
        
        for type_id in family.GetFamilySymbolIds():
            family_type = self.doc.GetElement(type_id)
            self._activate_family_type(family_type)
            
            instance = self._create_family_instance(family, family_type)
            if not instance or not instance.IsValidObject:
                continue
                
            self._set_instance_comments(instance)
            
            size_x, size_y, should_continue = self._get_instance_size(instance)
            if should_continue:
                continue
                
            max_h = max(max_h, size_y)
            
            self._position_instance(instance, size_x, size_y)
            
            if self.add_tag:
                self._add_tag_to_instance(instance, size_x, min_gap)
                
            self.step_right(size_x * 2)

            if is_need_host_wall:
                wall = self.get_internal_dump_wall( family.Name)
                self.secure_valid_wall_length( wall)

        self.step_down(max(min_gap, max_h*2))

    def _activate_family_type(self, family_type):
        if not family_type.IsActive:
            t = DB.Transaction(self.doc, "Activate Symbol")
            t.Start()
            family_type.Activate()
            t.Commit()

    def _create_family_instance(self, family, family_type):
        """Creates a family instance based on placement type"""
        if family.FamilyPlacementType == DB.FamilyPlacementType.ViewBased:
            return self._create_view_based_instance(family_type)
        elif family.FamilyPlacementType == DB.FamilyPlacementType.CurveBasedDetail:
            return self._create_curve_based_instance(family_type)
        elif family.FamilyPlacementType in [DB.FamilyPlacementType.OneLevelBased, 
                                          DB.FamilyPlacementType.WorkPlaneBased,
                                          DB.FamilyPlacementType.TwoLevelsBased]:  # Added TwoLevelsBased
            return self._create_level_based_instance(family_type)
        elif family.FamilyPlacementType == DB.FamilyPlacementType.OneLevelBasedHosted:
            return self._create_hosted_instance(family, family_type)
        else:
            print("[{}]:{} family_placement_type is [{}], need special handle, ask SZ for detail.".format(
                family.Name,
                family_type.LookupParameter("Type Name").AsString(),
                family.FamilyPlacementType))
            return None

    def _set_instance_comments(self, instance):
        if not instance.LookupParameter("Comments"):
            return
        t = DB.Transaction(self.doc, "Update Comments")
        t.Start()
        instance.LookupParameter("Comments").Set(INTERNAL_COMMENT)
        t.Commit()

    def _get_instance_size(self, instance):
        t = DB.Transaction(self.doc, "Isolate Element To Zoom and get size")
        t.Start()
        self.view.IsolateElementTemporary(instance.Id)
        if self.is_good_category(instance):
            self.uidoc.ShowElements(instance)
        self.doc.Regenerate()
        
        size_x, size_y = self._calculate_instance_size(instance)
        
        self.view.DisableTemporaryViewMode(DB.TemporaryViewMode.TemporaryHideIsolate)
        t.RollBack()
        
        return size_x, size_y, False

    def _position_instance(self, instance, size_x, size_y):
        t = DB.Transaction(self.doc, "Position Instance")
        t.Start()
        DB.ElementTransformUtils.MoveElement(self.doc, instance.Id, DB.XYZ(size_x/2, size_y/2, 0))
        t.Commit()

    def _add_tag_to_instance(self, instance, size_x, min_gap):
        t = DB.Transaction(self.doc, "Create Tag")
        t.Start()
        tag = DB.IndependentTag.Create(self.doc, 
                                    self.tag_symbol.Id, 
                                    self.view.Id, 
                                    DB.Reference(instance),
                                    True,
                                    DB.TagOrientation.Horizontal,
                                    self.pointer.Add(DB.XYZ(size_x/2, -min_gap * 0.2, 0)))

        DB.ElementTransformUtils.MoveElement(self.doc, tag.Id, self.view.ViewDirection + DB.XYZ(size_x/2, 0, 0))
        t.Commit()

    def _create_view_based_instance(self, family_type):
        """Creates a view-based family instance"""
        t = DB.Transaction(self.doc, "Create View Based Instance")
        t.Start()
        try:
            instance = self.doc.Create.NewFamilyInstance(self.pointer, 
                                                    family_type, 
                                                    self.view)
        except Exception as e:
            print("Failed to create view based instance: {}".format(str(e)))
            t.RollBack()
            return None
        t.Commit()
        return instance

    def _create_curve_based_instance(self, family_type):
        """Creates a curve-based detail family instance"""
        t = DB.Transaction(self.doc, "Create Curve Based Instance")
        t.Start()
        line = DB.Line.CreateBound(self.pointer, 
                                  self.pointer.Add(DB.XYZ(1, 0, 0)))
        instance = self.doc.Create.NewFamilyInstance(line,
                                                   family_type,
                                                   self.view)
        t.Commit()
        return instance

    def _create_level_based_instance(self, family_type):
        """Creates a level-based family instance"""
        level = self.get_internal_dump_level()
        t = DB.Transaction(self.doc, "Create Level Based Instance")
        t.Start()
        instance = self.doc.Create.NewFamilyInstance(self.pointer,
                                                   family_type,
                                                   level,
                                                   DB.Structure.StructuralType.NonStructural)
        try:
            instance.LookupParameter("Elevation from Host").Set(0)
        except:
            pass
        t.Commit()
        return instance

    def _create_hosted_instance(self, family, family_type):
        """Creates a hosted family instance with appropriate host"""
        host_type = self.get_family_host_type(family)
        
        if "Wall" in host_type:
            host = self._get_or_create_host_wall(family)
        elif "Ceiling" in host_type:
            host = self._get_or_create_host_ceiling(family)
        elif "Roof" in host_type:  # Added Roof support
            host = self._get_or_create_host_roof(family)
        else:
            print("Host type [{}] not supported yet, ask SZ for detail.".format(host_type))
            return None
            
        if not host:
            return None
            
        t = DB.Transaction(self.doc, "Create Hosted Instance")
        t.Start()
        try:
            instance = self.doc.Create.NewFamilyInstance(self.pointer,
                                                       family_type,
                                                       host,
                                                       DB.Structure.StructuralType.NonStructural)
        except Exception as e:
            print("Failed to create hosted instance: {}".format(str(e)))
            t.RollBack()
            return None
        t.Commit()
        return instance

    def _get_or_create_host_wall(self, family):
        """Gets existing or creates new host wall"""
        walls = DB.FilteredElementCollector(self.doc)\
                 .OfCategory(DB.BuiltInCategory.OST_Walls)\
                 .WhereElementIsNotElementType()\
                 .ToElements()
                 
        wall_comment = "{}_{}".format(FAMILY_DUMP_WALL_COMMENT, family.Name)
        
        for wall in walls:
            if wall.LookupParameter("Comments").AsString() == wall_comment:
                return wall
                
        t = DB.Transaction(self.doc, "Create Host Wall")
        t.Start()
        line = DB.Line.CreateBound(self.pointer.Add(DB.XYZ(-5, 0, 0)),
                                  self.pointer.Add(DB.XYZ(20, 0, 0)))
        wall = DB.Wall.Create(self.doc,
                            line,
                            self.get_internal_dump_level().Id,
                            False)
        wall.LookupParameter("Comments").Set(wall_comment)
        wall.LookupParameter("Unconnected Height").Set(10)
        t.Commit()
        return wall

    def _get_or_create_host_ceiling(self, family):
        """Gets existing or creates new host ceiling"""
        ceilings = DB.FilteredElementCollector(self.doc)\
                    .OfCategory(DB.BuiltInCategory.OST_Ceilings)\
                    .WhereElementIsNotElementType()\
                    .ToElements()
                    
        ceiling_comment = "{}_{}".format(FAMILY_DUMP_CEILING_COMMENT, family.Name)
        
        for ceiling in ceilings:
            if ceiling.LookupParameter("Comments").AsString() == ceiling_comment:
                return ceiling
                
        t = DB.Transaction(self.doc, "Create Host Ceiling")
        t.Start()
        
        ceiling_type_id = DB.FilteredElementCollector(self.doc)\
                           .OfCategory(DB.BuiltInCategory.OST_Ceilings)\
                           .WhereElementIsElementType()\
                           .FirstElementId()
                           
        # Create rectangle points for ceiling boundary
        short_side = 2
        long_side = 6
        points = [
            self.pointer.Add(DB.XYZ(-short_side, -short_side, 0)),
            self.pointer.Add(DB.XYZ(long_side, -short_side, 0)),
            self.pointer.Add(DB.XYZ(long_side, short_side, 0)),
            self.pointer.Add(DB.XYZ(-short_side, short_side, 0))
        ]
        
        # Create lines and curve loop
        curves = []
        for i in range(len(points)):
            next_i = (i + 1) % len(points)
            line = DB.Line.CreateBound(points[i], points[next_i])
            curves.append(line)
            
        # Convert curves to CurveLoop using DATA_CONVERSION
        curve_loop = DB.CurveLoop.Create(DATA_CONVERSION.list_to_system_list(curves, 
                                                                           type=DATA_CONVERSION.DataType.Curve, 
                                                                           use_IList=False))
        
        # Create curve loops collection
        curve_loops = DATA_CONVERSION.list_to_system_list([curve_loop], 
                                                        type=DATA_CONVERSION.DataType.CurveLoop, 
                                                        use_IList=False)
        
        ceiling = DB.Ceiling.Create(self.doc,
                                  curve_loops,
                                  ceiling_type_id,
                                  self.get_internal_dump_level().Id)
                                  
        ceiling.LookupParameter("Comments").Set(ceiling_comment)
        ceiling.LookupParameter("Height Offset From Level").Set(10)
        t.Commit()
        return ceiling

    def _get_or_create_host_roof(self, family):
        """Gets or creates a roof for hosting family instances
        
        Args:
            family: Family requiring roof host
            
        Returns:
            DB.RoofBase: The host roof
        """
        roofs = DB.FilteredElementCollector(self.doc)\
                 .OfCategory(DB.BuiltInCategory.OST_Roofs)\
                 .WhereElementIsNotElementType()\
                 .ToElements()
                 
        roof_comment = "{}_{}".format("EA_Family_List_Internal_Roof", family.Name)
        
        for roof in roofs:
            if roof.LookupParameter("Comments").AsString() == roof_comment:
                return roof
                
        t = DB.Transaction(self.doc, "Create Host Roof")
        t.Start()
        
        # Get default roof type
        roof_type_id = DB.FilteredElementCollector(self.doc)\
                        .OfCategory(DB.BuiltInCategory.OST_Roofs)\
                        .WhereElementIsElementType()\
                        .FirstElementId()
        
        # Create roof footprint
        level = self.get_internal_dump_level()
        short_side = 2
        long_side = 6
        points = [
            self.pointer.Add(DB.XYZ(-short_side, -short_side, 10)),
            self.pointer.Add(DB.XYZ(long_side, -short_side, 10)),
            self.pointer.Add(DB.XYZ(long_side, short_side, 10)),
            self.pointer.Add(DB.XYZ(-short_side, short_side, 10))
        ]
        
        curves = []
        for i in range(len(points)):
            next_i = (i + 1) % len(points)
            line = DB.Line.CreateBound(points[i], points[next_i])
            curves.append(line)
            
        curve_array = DB.CurveArray()
        for curve in curves:
            curve_array.Append(curve)
            
        roof = self.doc.Create.NewFootPrintRoof(curve_array, 
                                              level, 
                                              roof_type_id, 
                                              DATA_CONVERSION.list_to_system_list([level.Id]))
                                              
        roof.LookupParameter("Comments").Set(roof_comment)
        t.Commit()
        return roof

    def _calculate_instance_size(self, instance):
        """Calculates the size of a family instance by its bounding box
        
        Args:
            instance: The family instance to measure
            
        Returns:
            tuple: (width, height) of the instance
        """
        try:
            bbox = instance.get_BoundingBox(self.view)
            if not bbox:
                return 1, 1
                
            min_pt = bbox.Min
            max_pt = bbox.Max
            
            # Get size in each direction
            size_x = abs(max_pt.X - min_pt.X)
            size_y = abs(max_pt.Y - min_pt.Y)
            
            # Ensure minimum size
            min_size = 1
            size_x = max(size_x, min_size)
            size_y = max(size_y, min_size)
            
            return size_x, size_y
            
        except Exception as e:
            print("Failed to calculate instance size: {}".format(str(e)))
            return 1, 1  # Return default size on error

    @staticmethod
    def is_good_category(instance):
        """Checks if the instance category should be included in deployment
        
        Args:
            instance: Revit family instance to check
            
        Returns:
            bool: True if category should be included, False otherwise
        """
        if isinstance(instance, DB.Panel):
            return False
        if isinstance(instance, DB.Mullion):
            return False
        return True
                
    @staticmethod
    def get_family_host_type(family):
        """Gets the hosting behavior type of a family
        
        Args:
            family: Revit family to check
            
        Returns:
            str: Host type as string (e.g. 'Wall Based', 'Ceiling Based')
        """
        return family.Parameter[DB.BuiltInParameter.FAMILY_HOSTING_BEHAVIOR].AsValueString()

    def get_internal_dump_level(self):
        """Gets or creates an internal level for family dumping
        
        Returns:
            DB.Level: The internal dump level
        """
        all_levels = DB.FilteredElementCollector(self.doc).OfClass(DB.Level).ToElements()
        for level in all_levels:
            if level.Name == FAMILY_DUMP_LEVEL:
                return level
                
        t = DB.Transaction(self.doc, "Create Internal Level")
        t.Start()
        new_level = DB.Level.Create(self.doc, 0)
        new_level.Name = FAMILY_DUMP_LEVEL
        t.Commit()
        return new_level

    def get_internal_dump_wall(self, family_name):
        """Gets or creates a wall for hosting family instances
        
        Args:
            family_ref_pt: Reference point for wall placement
            family_name: Name of family for wall comment
            
        Returns:
            DB.Wall: The host wall
        """
        all_walls = DB.FilteredElementCollector(self.doc).OfClass(DB.Wall).ToElements()
        for wall in all_walls:
            if wall.LookupParameter("Comments").AsString() == FAMILY_DUMP_WALL_COMMENT + "_" + family_name:
                return wall
                
        level = self.get_internal_dump_level()
        t = DB.Transaction(self.doc, "Create Internal Wall")
        t.Start()
        wall = DB.Wall.Create(self.doc, 
                             DB.Line.CreateBound(DB.XYZ(self.pointer.X-3, self.pointer.Y, self.pointer.Z), 
                                               DB.XYZ(self.pointer.X+20, self.pointer.Y, self.pointer.Z)), 
                             level.Id, 
                             False)
        wall.LookupParameter("Comments").Set(FAMILY_DUMP_WALL_COMMENT + "_" + family_name)
        wall.LookupParameter("Unconnected Height").Set(10) 
        t.Commit()
        return wall

    def get_internal_dump_ceiling(self, family_name):
        """Gets or creates a ceiling for hosting family instances
        
        Args:
            family_ref_pt: Reference point for ceiling placement
            family_name: Name of family for ceiling comment
            
        Returns:
            DB.Ceiling: The host ceiling
        """
        all_ceilings = DB.FilteredElementCollector(self.doc).OfClass(DB.Ceiling).ToElements()
        for ceiling in all_ceilings:
            if ceiling.LookupParameter("Comments").AsString() == FAMILY_DUMP_CEILING_COMMENT + "_" + family_name:
                return ceiling
                
        level = self.get_internal_dump_level()
        t = DB.Transaction(self.doc, "Create Internal ceiling")
        t.Start()
        ceiling_type_id = DB.FilteredElementCollector(self.doc).OfClass(DB.CeilingType).FirstElementId()
        
        short_side = 2
        long_side = 6

        crv_pts = [
            DB.XYZ(self.pointer.X-short_side, self.pointer.Y-short_side, self.pointer.Z),
            DB.XYZ(self.pointer.X+long_side, self.pointer.Y-short_side, self.pointer.Z), 
            DB.XYZ(self.pointer.X+long_side, self.pointer.Y+short_side, self.pointer.Z), 
            DB.XYZ(self.pointer.X-short_side, self.pointer.Y+short_side, self.pointer.Z)
        ]
        
        crvs = [DB.Line.CreateBound(crv_pts[i], crv_pts[i+1]) for i in range(len(crv_pts)-1)]
        crvs.append(DB.Line.CreateBound(crv_pts[-1], crv_pts[0]))
        
        crv_loop = DB.CurveLoop.Create(DATA_CONVERSION.list_to_system_list(crvs, 
                                                                          type=DATA_CONVERSION.DataType.Curve, 
                                                                          use_IList=False))
        
        crv_loop_collection = DATA_CONVERSION.list_to_system_list([crv_loop], 
                                                                type=DATA_CONVERSION.DataType.CurveLoop, 
                                                                use_IList=False)
        
        ceiling = DB.Ceiling.Create(self.doc, crv_loop_collection, ceiling_type_id, level.Id)
        ceiling.LookupParameter("Comments").Set(FAMILY_DUMP_CEILING_COMMENT + "_" + family_name)
        ceiling.LookupParameter("Height Offset From Level").Set(10)
        
        t.Commit()
        return ceiling

    def secure_valid_wall_length(self, wall):
        """Extends wall length if needed to accommodate family placement
        
        Args:
            pointer: Current placement point (DB.XYZ)
            wall: Wall to modify
        """
        line = wall.Location.Curve
        end_pt = line.GetEndPoint(1)
        if end_pt.X + 5 < self.pointer.X:
            end_pt = DB.XYZ(end_pt.X + 15, end_pt.Y, end_pt.Z)
            line = DB.Line.CreateBound(wall.Location.Curve.GetEndPoint(0), end_pt)
            t = DB.Transaction(self.doc, "Modify wall curve")
            t.Start()
            wall.Location.Curve = line
            t.Commit()

  

        
@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def list_family():
    """Main entry point for the script"""
    opts = [
        ["List Detail Items", "They will showup in a drafting view"], 
        ["List 3D Family", "They will show up in a non-drafting view.\nNOTE: 3D family will show in all project views"]
    ]
    sel = REVIT_FORMS.dialogue(main_text="Select what kind of family to list...", options=opts)
    if not sel:
        return
        
    tg = DB.TransactionGroup(REVIT_APPLICATION.get_doc(), __title__)
    tg.Start()
   
    if sel == opts[0][0]:
        lister = List2DFamily()
    else:
        lister = List3DFamily()
        
    lister.run()
    tg.Commit()
    
    NOTIFICATION.messenger("All families listed.")
    SOUND.play_sound()


class ListFamily:
    """Base class for handling family listing operations"""
    def __init__(self):
        self.doc = REVIT_APPLICATION.get_doc()
        self.uidoc = REVIT_APPLICATION.get_uidoc()
        
    def run(self):
        """Main execution method"""
        families = self._get_families()
        if not families:
            return
            
        view = self.get_or_create_view()
        if not view:
            return
            
        self.uidoc.ActiveView = view
        self._change_view_group(view)
        
        tag_family = self.get_tag_family()
        Deployer(view, families, tag_family)
        
        NOTIFICATION.messenger("Families listed at view: {}".format(view.Name))

    def _change_view_group(self, view):
        """Changes view group settings
        
        Args:
            view: View to modify
        """
        t = DB.Transaction(self.doc, "Change View Group")
        t.Start()
        try:
            view.LookupParameter("Views_$Group").Set("Ennead")
            view.LookupParameter("Views_$Series").Set("List Item (´･ᆺ･`)")
            t.Commit()
        except:
            t.RollBack()
        
    def _get_families(self):
        """Abstract method to get families"""
        raise NotImplementedError
        
    def get_or_create_view(self):
        """Abstract method to get or create view"""
        raise NotImplementedError
        
    def get_tag_family(self):
        """Abstract method to get tag family"""
        raise NotImplementedError


class List2DFamily(ListFamily):
    """Handles listing of 2D detail items"""
    def _get_families(self):
        """Gets detail component families"""
        return REVIT_SELECTION.pick_detail_componenet(self.doc,multi_select=True)
        
    def get_or_create_view(self):
        """Gets or creates drafting view"""
        view = REVIT_VIEW.get_view_by_name(DETAIL_ITEM_DUMP_VIEW)
        if not view:
            t = DB.Transaction(self.doc, "Make new view: " + DETAIL_ITEM_DUMP_VIEW)
            t.Start()
            view = DB.ViewDrafting.Create(self.doc, REVIT_VIEW.get_default_view_type("drafting").Id)
            view.Name = DETAIL_ITEM_DUMP_VIEW
            view.Scale = 2
            t.Commit()
        return view
        
    def get_tag_family(self):
        """Gets detail item tag family"""
        family_name = "EA_DetailItem_Tag"
        tag_family_path = "{}\\{}.rfa".format(os.path.dirname(__file__), family_name)
        tag_family = REVIT_FAMILY.get_family_by_name(family_name, load_path_if_not_exist=tag_family_path)
        if not tag_family:
            NOTIFICATION.messenger("Warning: Tag family '{}' not found and could not be loaded. Proceeding without tags.".format(family_name))
        return None  # to be fixed later


class List3DFamily(ListFamily):
    """Handles listing of 3D families"""
    def _get_families(self):
        """Gets 3D families"""
        return REVIT_SELECTION.pick_family(multi_select=True, include_2D=False, exclude_categories=["Curtain Panels", "Curtain Wall Mullions"])

        
    def get_or_create_view(self):
        """Gets or creates appropriate view based on user selection"""
        view_type = self._get_view_type_from_user()
        if not view_type:
            return None
            
        view_name = self._get_view_name(view_type)
        view = REVIT_VIEW.get_view_by_name(view_name)
        
        if not view:
            view = self._create_new_view(view_type, view_name)
        
        return view
        
    def get_tag_family(self):
        """Gets 3D family tag family"""
        family_name = "EA_Family_Tag"
        return REVIT_FAMILY.get_family_by_name(family_name, load_path_if_not_exist=None)
        
    def _get_view_type_from_user(self):
        """Gets view type preference from user"""
        opts = ["Use 3D view", "Use Plan view"]
        return REVIT_FORMS.dialogue(main_text="Select what kind of view to show results...", options=opts)
        
    def _get_view_name(self, view_type):
        """Gets appropriate view name based on type"""
        if view_type == "Use 3D view":
            return "{}_3D".format(FAMILY_DUMP_VIEW)
        return "{}_Plan".format(FAMILY_DUMP_VIEW)
        
    def _create_new_view(self, view_type, view_name):
        """Creates new view based on type"""
        t = DB.Transaction(self.doc, "Make new view: {}".format(view_name))
        t.Start()
        
        if view_type == "Use 3D view":
            view = DB.View3D.CreateIsometric(self.doc, REVIT_VIEW.get_default_view_type("3d").Id)
        else:
            new_level = Deployer.get_internal_dump_level()
            view = DB.ViewPlan.Create(self.doc, REVIT_VIEW.get_default_view_type("plan").Id, new_level.Id)
        
        view.Name = view_name
        view.Scale = 2
        t.Commit()
        
        return view


################## main code below #####################

if __name__ == "__main__":
    output = script.get_output()
    output.close_others()
    list_family()
    







