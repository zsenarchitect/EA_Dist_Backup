__title__ = "Mark/Clear\nTitle Corner"
__doc__ = "Mark or clear multiple viewports view title corner.\n\nNote: Since revit 2022, the new API allows for seeting position of the view title, and Ideate update their view align tool to allow title alignment, this tool is no longer needed. It is only kept for working with old revit project."


from math import pi
from pyrevit import DB, script, revit, forms


def clear_title_corner(linestyle_name):
    lines = DB.FilteredElementCollector(revit.doc).OfClass(DB.CurveElement).WhereElementIsNotElementType().ToElements()
    for line in lines:
        #print line.LineStyle.Name
        if line.LineStyle.Name == linestyle_name:
            DB.Document.Delete(revit.doc, line.Id)


def get_linestyle(linestyle_name):
    line_category = revit.doc.Settings.Categories.get_Item(DB.BuiltInCategory.OST_Lines)
    line_subcs = line_category.SubCategories
    for line_style in line_subcs:
        if line_style.Name == linestyle_name:
            #print "~~~~~"
            #print line_style, line_style.Name
            #print line_style.GetType()
            #print line_style.GetGraphicsStyle(DB.GraphicsStyleType.Projection)#line_style.GraphicsStyleCategory

            return line_style.GetGraphicsStyle(DB.GraphicsStyleType.Projection)



def create_linestyle(linestyle_name):
    line_category = revit.doc.Settings.Categories.get_Item(DB.BuiltInCategory.OST_Lines)
    with revit.Transaction("Make new LineStyle"):
        new_linestyle_category = revit.doc.Settings.Categories.NewSubcategory(line_category, linestyle_name)
        new_linestyle_category.SetLineWeight( 5, DB.GraphicsStyleType.Projection )
        new_linestyle_category.LineColor = DB.Color(0xFF, 0x00, 0x00 )

        """
        line_patterns = DB.FilteredElementCollector( revit.doc ).OfClass( DB.LinePatternElement ).ToElements()
        for line_pattern in line_patterns:
            print(line_pattern.GetLinePattern().Name)
            if line_pattern.GetLinePattern().Name == "Solid":
                print("find solid")
                break
        new_linestyle_category.SetLinePatternId(line_pattern.Id,DB.GraphicsStyleType.Projection )
        """
        solid_pattern_id = DB.LinePatternElement.GetSolidPatternId()
        new_linestyle_category.SetLinePatternId(solid_pattern_id,DB.GraphicsStyleType.Projection )






def special_linestyle_existing(linestyle_name):
    line_category = revit.doc.Settings.Categories.get_Item(DB.BuiltInCategory.OST_Lines)
    line_subcs = line_category.SubCategories
    for line_style in line_subcs:
        if line_style.Name == linestyle_name:
            return True
    return False
    #return true or f

    pass

def get_all_sheet_labels(sheet):
    labels = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_ViewportLabel).ToElements()
    print("print labels")
    print(len(labels))
    for label in labels:

        print(label.Family.Name)
    """
    this will actually get the annotation symbole family for the viewport label.
    """



def mark_title_corner(ref_pt, desired_linestyle_name):
    sel_sheets = forms.select_sheets(title='Select Sheets That contain views that you want to mark title corner.')


    #all_viewports = DB.FilteredElementCollector(revit.doc).OfClass(DB.Viewport).WhereElementIsNotElementType().ToElements()


    for sheet in sel_sheets:
        #get_all_sheet_labels(sheet)
        all_viewport_ids = []
        all_viewport_ids.extend(sheet.GetAllViewports())


        sheet_annos = []
        for viewport_id in all_viewport_ids:
            #print "~~~~~~~~new viewport"
            view_id = revit.doc.GetElement(viewport_id).ViewId
            #print "view name below:"
            #print revit.doc.GetElement(view_id).Name#view name


            try:
                outline = revit.doc.GetElement(viewport_id).GetLabelOutline()
                #print "print max point and min pt below"
                #print outline.MaximumPoint, outline.MinimumPoint

            except Exception as e:
                print("skipped '{}' becasue: {}\n".format(revit.doc.GetElement(view_id).Name,e))
                continue

            #print "print ref_pt below"
            #print ref_pt
            vector = ref_pt - outline.MinimumPoint
            #print "print vector below"
            #print vector
            sheet_id = revit.doc.GetElement(viewport_id).SheetId
            """
            new ideas!!!!
            messure vector between the minimupoint and a desired DB.XYZ point, then move the outline label in the negative direction.
            """

            """
            print(outline.Id)
            print(vector)
            DB.ElementTransformUtilis.MoveElement(revit.doc, outline.Id, vector)
            """



            """
            OST_ViewportLabel
            try collect all viewpot label from cuurent sheetview and them try to move by vector


            failed
            """


            """
            sheet_id = revit.doc.GetElement(viewport_id).SheetId
            origin = revit.doc.GetElement(sheet_id).Origin
            basis_x = revit.doc.GetElement(sheet_id).UpDirection
            basis_y = revit.doc.GetElement(sheet_id).RightDirection
            #print "print origion below"
            #print origin
            #print "print basic X below"
            #print basis_x
            #print "print basic Y below"
            #print basis_y
            """


            """
            line = DB.Line.CreateBound(outline.MaximumPoint, outline.MinimumPoint)
            current_line = revit.doc.Create.NewDetailCurve(revit.doc.GetElement(sheet_id), line)
            """
            mod_ref_pt = DB.XYZ(ref_pt.X,ref_pt.Y,outline.MinimumPoint.Z)
            try:
                line = DB.Line.CreateBound(mod_ref_pt, outline.MinimumPoint)
            except:
                print("skip view '{}' becasue the title is already too close. For precise snapping please move it away randomly so it is above tolerence.".format(revit.doc.GetElement(view_id).Name))
                continue
            current_line = revit.doc.Create.NewDetailCurve(revit.doc.GetElement(sheet_id), line)
            #center_mark = DB.Arc.Create(mod_ref_pt,200,0,2*pi-0.1,DB.XYZ.BasisX,DB.XYZ.BasisY)
            #circle_mark_crv = revit.doc.Create.NewDetailCurve(revit.doc.GetElement(sheet_id), center_mark)
            #print current_line.LineStyle.Name
            """

            should put all the line into container, so per sheet, only create lines on paper for the shortest dist.
            Make this an option if people want to.

            """

            """
            #revit.doc.GetElement(view_id).ViewDirection
            sheet_plane = DB.Plane.CreateByOriginAndBasis(origin, basis_x, basis_y)
            pt_on_sheet = sheet_plane.Project(ref_pt)
            print(list(pt_on_sheet))

            #outline.MinimumPoint = DB.XYZ(list(pt_on_sheet)[0],list(pt_on_sheet)[1],list(pt_on_sheet)[2])


            line = DB.Line.CreateBound(project_pt, outline.MinimumPoint)
            #line = DB.Line.CreateBound(ref_pt, outline.MinimumPoint)
            current_line = revit.doc.Create.NewDetailCurve(revit.doc.GetElement(sheet_id), line)
            print(current_line.LineStyle.Name)
            """

            if not special_linestyle_existing(desired_linestyle_name):
                #create line style called "desired_linestyle_name"
                create_linestyle(desired_linestyle_name)
                pass

            current_line.LineStyle = get_linestyle(desired_linestyle_name)
            sheet_annos.append(current_line)
            #make that line as the special line style


        sheet_annos.sort(key = lambda x: x.GeometryCurve.Length, reverse = False)
        override_setting = DB.OverrideGraphicSettings().SetProjectionLineWeight(10)
        #sheet = revit.doc.GetElement(sheet_annos[0].OwerViewId)
        if len(sheet_annos) > 0:
            sheet.SetElementOverrides(sheet_annos[0].Id, override_setting)






################ main code below #############

"""

try to test pick the label, or even anything in general....this is not working..

from pyrevit import UI
uidoc = UI.UIApplication.ActiveUIDocument
print(uidoc)
#selection = uidoc.Selection.GetElementIds()
#print selection
#selection = uidoc.Selection.PickObject()
selection = uidoc.Selection.PickObject(UI.ObjectType.Element, "pick something")

print(selection)
selection = revit.get_selection()
print(selection[0])
print(selection[0].Category.Name)
"""

desired_linestyle_name = "$$EnneadTab Label Line"

res = forms.alert(options = ["mark title corners at sheets", "remove existing marks from sheets."], msg = "I want to [.....]")

if "remove" in res:
    option = False
elif "mark" in res:
    option = True
else:
    script.exit()


if option:
    with revit.Transaction("Mark View Title Corner"):

        with forms.WarningBar(title='Pick title corner point on sheet. I recommand you embed some detail line in the title block with Visibility control so you can come back to this locations later.'):
            ref_pt = revit.pick_point()

        mark_title_corner(ref_pt,desired_linestyle_name)
else:
    with revit.Transaction("Clear View Title Corner"):
        clear_title_corner(desired_linestyle_name)
