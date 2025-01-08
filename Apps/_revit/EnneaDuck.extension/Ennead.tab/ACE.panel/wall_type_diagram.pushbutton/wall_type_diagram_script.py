#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "Sen Zhang has not writed documentation for this tool, but he should!"
__title__ = "Wall Type\nDiagram"

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
import traceback
from pyrevit import forms
from EnneadTab import DATA_CONVERSION, ERROR_HANDLE, LOG
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_SELECTION, REVIT_VIEW, REVIT_FILTER
from Autodesk.Revit import DB # pyright: ignore 
import random

UIDOC = REVIT_APPLICATION.get_uidoc()
DOC = REVIT_APPLICATION.get_doc()


FILTER_NAME_PREFIX = "EnneadTab_WallType"

class WallTypeDiagram:
    def __init__(self, doc):
        self.doc = doc
        self.uidoc = REVIT_APPLICATION.get_uidoc()
        self.FILTER_NAME_PREFIX = "EnneadTab_WallType"
        self.walltypes_selected = None
        self.color_dict = {}

    def create_diagram(self):
        self.walltypes_selected = REVIT_SELECTION.pick_system_types(self.doc, "wall")
        if not self.walltypes_selected:
            return

        with DB.Transaction(self.doc, __title__) as t:
            t.Start()
            try:
                legend_view = REVIT_VIEW.get_view_by_name("Wall Type Diagrams")
                if not legend_view:
                    legend_view = REVIT_VIEW.create_legend_view(self.doc, "Wall Type Diagrams", scale=100)
                self._add_wall_type_box_and_text(legend_view)
                self._create_or_update_view_filters()
                
                template_view = forms.select_viewtemplates("Select a view to apply the wall type diagram to", multiple=False)
                if template_view:
                    self._add_filters_to_diagram_template(template_view)
                t.Commit()
            except:
                t.RollBack()
                print(traceback.format_exc())

    def _add_wall_type_box_and_text(self, legend_view):
        # all_elements = DB.FilteredElementCollector(self.doc, legend_view.Id).ToElementIds()
        # for element_id in all_elements:
        #     try:
        #         self.doc.Delete(element_id)
        #     except:
        #         pass
        
        cursor_x, cursor_y = 0, 0
        edge = 3
        
        self.walltypes_selected.sort(key=lambda x: x.LookupParameter("Keynote").AsString(), reverse=True)
        
        for walltype in self.walltypes_selected:
            wall_type_name = walltype.LookupParameter("Type Name").AsString()
            region_type_name = "EnneadTab_WallType_{}".format(wall_type_name)
            
            # Create filled region
            filled_region_type = REVIT_SELECTION.get_filledregion_type(
                self.doc, 
                region_type_name, 
                color_if_not_exist=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            )
            
            # Create geometry
            points = [
                DB.XYZ(cursor_x, cursor_y, 0),
                DB.XYZ(cursor_x + edge, cursor_y, 0),
                DB.XYZ(cursor_x + edge, cursor_y + edge, 0),
                DB.XYZ(cursor_x, cursor_y + edge, 0)
            ]
            
            curveloop = DB.CurveLoop()
            for i in range(4):
                curveloop.Append(DB.Line.CreateBound(points[i], points[(i+1)%4]))
            
            curveloop = DATA_CONVERSION.list_to_system_list([curveloop], type="CurveLoop")
            DB.FilledRegion.Create(self.doc, filled_region_type.Id, legend_view.Id, curveloop)
            
            self.color_dict[wall_type_name] = filled_region_type.ForegroundPatternColor

            # Create text note
            key_note = walltype.LookupParameter("Keynote").AsString()
            text_note_type_id = self.doc.GetDefaultElementTypeId(DB.ElementTypeGroup.TextNoteType)
            DB.TextNote.Create(
                self.doc,
                legend_view.Id,
                DB.XYZ(cursor_x + edge*1.2, cursor_y + edge*1.2, 0),
                key_note,
                text_note_type_id
            )
            cursor_y += edge*1.2

    def _create_or_update_view_filters(self):
        categories = [
            DB.BuiltInCategory.OST_Walls,
            DB.BuiltInCategory.OST_GenericModel
            ]

        for walltype in self.walltypes_selected:
            filter_name = "{}_{}".format(self.FILTER_NAME_PREFIX, walltype.LookupParameter("Type Name").AsString())
            filter = REVIT_FILTER.get_view_filter_by_name(self.doc, filter_name)
            if not filter:
                filter = REVIT_FILTER.create_view_filter(self.doc, filter_name, categories)

            filter_rules = []
            keynote_param_id = DB.ElementId(DB.BuiltInParameter.KEYNOTE_PARAM)
            filter_rules.append(
                    DB.ParameterFilterRuleFactory.CreateEqualsRule(
                    keynote_param_id, 
                    walltype.LookupParameter("Keynote").AsString()
                )
            )

            
            elem_filter = DB.LogicalAndFilter(
                [DB.ElementParameterFilter(rule) for rule in filter_rules]
            )
            filter.SetElementFilter(elem_filter)

    def _add_filters_to_diagram_template(self, template_view):
        for walltype in self.walltypes_selected:
            wall_type_name = walltype.LookupParameter("Type Name").AsString()
            filter_name = "{}_{}".format(self.FILTER_NAME_PREFIX, wall_type_name)
            filter = REVIT_FILTER.get_view_filter_by_name(self.doc, filter_name)
            try:
                template_view.AddFilter(filter.Id)
            except:
                pass
            override_settings = DB.OverrideGraphicSettings()
            override_settings.SetSurfaceForegroundPatternColor (self.color_dict[wall_type_name])  
            override_settings.SetSurfaceForegroundPatternId  (REVIT_SELECTION.get_solid_fill_pattern_id())
            template_view.SetFilterOverrides(filter.Id, override_settings)

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def main():
    diagram = WallTypeDiagram(DOC)
    diagram.create_diagram()

if __name__ == "__main__":
    main()







