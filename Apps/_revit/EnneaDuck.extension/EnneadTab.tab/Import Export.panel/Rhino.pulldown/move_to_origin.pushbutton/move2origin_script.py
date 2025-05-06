__doc__ = """Move family instances to the internal origin while maintaining current orientation.

Three operation modes are available:
1: Family is placed in 3D view with incorrect location - Select it and move it.
2: Family is placed somewhere in 3D view but location unknown - Select from listbox and move it.
3: Family is newly loaded but not yet placed - Select from list and place at origin.

Note: Some element types have location constraints and may not be movable to absolute origin.
Report any issues to the EnneadTab team.
"""
__title__ = "Move2Origin"
__tip__ = True
__is_popular__ = True
from pyrevit import forms
from pyrevit import script


import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
from EnneadTab.REVIT import REVIT_UNIT, REVIT_APPLICATION, REVIT_FORMS
from EnneadTab import ERROR_HANDLE, LOG
from EnneadTab import NOTIFICATION 
from Autodesk.Revit import DB # pyright: ignore
uidoc = REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()


class Solution:


    def pick_instances(self):
        families = DB.FilteredElementCollector(doc)\
            .OfClass(DB.Family)\
            .WhereElementIsNotElementType()\
            .ToElements()
        families = sorted(families, key=lambda x: x.Name.lower())
        family = forms.SelectFromList.show(
            families,
            multiselect=False,
            name_attr='Name',
            title="Pick family",
            button_name='Select Family')
        if not family:
            NOTIFICATION.messenger("No family selected, operation cancelled.")
            return

        types = [doc.GetElement(x) for x in family.GetFamilySymbolIds()]
        types = sorted(
            types, 
            key=lambda x: x.LookupParameter("Type Name").AsString())

        class MyOption(forms.TemplateListItem):
            @property
            def name(self):
                return "[{}]: {}".format(
                    self.FamilyName, 
                    self.LookupParameter("Type Name").AsString())

        types = [MyOption(x) for x in types]
        family_type = forms.SelectFromList.show(
            types,
            multiselect=False,
            title="Pick family type",
            button_name='Select Type')
        if not family_type:
            NOTIFICATION.messenger("No family type selected, operation cancelled.")
            return


        if not family_type.IsActive:
            t = DB.Transaction(doc, "Activate Symbol")
            t.Start()
            family_type.Activate ()
            doc.Regenerate()
            t.Commit()

        self.symbol = family_type
        family_instances = DB.FilteredElementCollector(doc).OfClass(DB.FamilyInstance).WhereElementIsNotElementType().ToElements()
        def check_type(instance):
            try:
                if instance.Symbol.Id == family_type.Id:
                    return True
                return False
            except Exception as e:
                return False

        instances = filter(check_type, family_instances)
        return instances

    def place_new_instance(self):


        levels = DB.FilteredElementCollector(doc)\
            .OfClass(DB.Level)\
            .WhereElementIsNotElementType()\
            .ToElements()
        levels = sorted(levels, key=lambda x: x.Elevation)

        class MyOption(forms.TemplateListItem):
            @property
            def name(self):
                return "{}: {}ft = {}mm".format(
                    self.Name,
                    self.Elevation,
                    REVIT_UNIT.internal_to_mm(self.Elevation))

        levels = [MyOption(x) for x in levels]
        level = forms.SelectFromList.show(
            levels,
            multiselect=False,
            width=1000,
            title="Pick hosting level(this has no effect on actual location, but "
                  "probably make sense to pick a level closer to your intent.)",
            button_name='Select Level that is closest to absolute zero.')
        if not level:
            NOTIFICATION.messenger("No level selected, operation cancelled.")
            return


        t = DB.Transaction(doc, "Create new instance")
        t.Start()


        if not self.symbol.IsActive:
            self.symbol.Activate()
        if doc.IsFamilyDocument:
            doc_create = doc.FamilyCreate
        else:
            doc_create = doc.Create
        try:
            instance = doc_create.NewFamilyInstance(
                DB.XYZ(0,0,0),
                self.symbol,
                level,
                DB.Structure.StructuralType.NonStructural)
        except Exception as e:
            t.RollBack()
            REVIT_FORMS.dialogue(
                main_text=str(e), 
                sub_text="Notify Sen Zhang for this issue...")
            return

        if level.Elevation != 0:
            offset = level.Elevation
            for para_name in ["Elevation from Level", "Offset from Host"]:
                para = instance.LookupParameter(para_name)
                if para:
                    para.Set(-offset)
                    break


        t.Commit()
        return instance

    @ERROR_HANDLE.try_catch_error()
    def move_to_origin(self):
        selection = [doc.GetElement(x) for x in uidoc.Selection.GetElementIds()]
        if len(selection) < 1:
            selection = self.pick_instances()

        if not selection or len(selection) < 1:
            selection = [self.place_new_instance()]

        t = DB.Transaction(doc, "Move2Origin")
        t.Start()
        for element in selection:
            if not element:
                continue
            if element.Pinned == True:
                res1 = REVIT_FORMS.dialogue(
                    main_text="It is currently pinned.",
                    title="wait...",
                    options=["Unpin this element and move it.", "Leave it as it is."])
                if res1 == "Unpin this element and move it.":
                    element.Pinned = False
                else:
                    continue
            try:
                moving_vec = DB.XYZ.Negate(element.Location.Point)
                element.Location.Move(moving_vec)
            except Exception as e:
                # First try the direct assignment approach
                try:
                    element.Location = DB.XYZ(0,0,0)
                except Exception as direct_e:
                    # If direct assignment fails, try alternative methods
                    ERROR_HANDLE.print_note("Cannot move element directly: {}".format(str(e)))
                    try:
                        # Try alternative methods to move the element
                        if hasattr(element, "Location") and element.Location:
                            if hasattr(element.Location, "Move"):
                                # Use the Move method if available
                                element.Location.Move(DB.XYZ(-element.Location.Point.X, 
                                                           -element.Location.Point.Y, 
                                                           -element.Location.Point.Z))
                            else:
                                # Use ElementTransformUtils as a fallback
                                DB.ElementTransformUtils.MoveElement(
                                    doc, 
                                    element.Id, 
                                    DB.XYZ(0, 0, 0) - (element.Location.Point if hasattr(element.Location, "Point") else DB.XYZ(0, 0, 0))
                                )
                    except Exception as inner_e:
                        ERROR_HANDLE.print_note("Failed to move element to origin: {}".format(str(inner_e)))
                        NOTIFICATION.messenger("Could not move this element to origin. It may require special handling.")

            res = REVIT_FORMS.dialogue(
                main_text="It has moved to the origin point.\nNow I want to ...",
                title="good news!",
                options=["Pin this element.", "Don't Pin this element."])
            if res == "Pin this element.":
                element.Pinned = True

        t.Commit()


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def main():
    if doc.IsFamilyDocument:
        NOTIFICATION.messenger("this function is meant to use in project environment not in family environment")
        return
    
    Solution().move_to_origin()

output = script.get_output()
output.close_others()

if __name__ == "__main__":
    main()
   
