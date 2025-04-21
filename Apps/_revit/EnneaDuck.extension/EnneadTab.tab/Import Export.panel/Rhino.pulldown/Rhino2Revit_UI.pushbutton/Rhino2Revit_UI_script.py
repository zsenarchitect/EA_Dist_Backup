#!/usr/bin/python
# -*- coding: utf-8 -*-


__doc__ = """Convert .3dm and .dwg files into native Revit family elements.

Key Features:
- Assign subcategories per file
- Add new subcategories on the fly
- Use source filename as subcategory
- Support major curve conversion (except NURBS curves with control points on different CPlanes)

Best used with EnneadTab for Rhino's Rhino2Revit exporter window.

Format Support:
.3dm Files:
- Stable conversion to native Revit elements
- Individual control of Boolean, Subcategory, Visibility, Dimensions
- Requires clean source models

.dwg Files:
- More tolerant of model imperfections
- Handles lines, arcs, circles and planar NURBS curves
- Elements from same source file are grouped
- Creates Import subcategories (auto-cleaned)
"""

__title__ = "Rhino2Revit"
__tip__ = ["You can get curves from Rhino into Revit family - export as DWG in Rhino and import in Revit family.\nSee EnneadTab for Rhino LayerPackage for details",
           __doc__]
__is_popular__ = True
from pyrevit import forms
from pyrevit import script
from pyrevit.revit import ErrorSwallower

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
from EnneadTab.REVIT import REVIT_FORMS, REVIT_APPLICATION
from EnneadTab import DATA_FILE, NOTIFICATION, IMAGE, ERROR_HANDLE, FOLDER, TIME, LOG, UI, ENVIRONMENT

from Autodesk.Revit import DB # pyright: ignore  
import clr # pyright: ignore 
import os
import System # pyright: ignore 
import time
import traceback

# Import utility module for script
script_folder = os.path.dirname(__file__)
import sys
sys.path.append(script_folder)
import RHINO2REVIT_UTILITY

# Get current document
doc = REVIT_APPLICATION.get_doc()


def is_family_adaptive():
    """Check if the current family document supports adaptive components."""
    t = DB.Transaction(doc, "adaptive_test")
    t.Start()
    try:
        doc.FamilyCreate.NewReferencePoint(DB.XYZ(0, 0, 0))
        t.RollBack()
        return True
    except:
        t.RollBack()
        return False


def purge_geo_from_doc():
    """Delete all geometry elements of the same category as current family."""
    parent_category = doc.OwnerFamily.FamilyCategory

    all_categories = [x for x in parent_category.SubCategories]
    all_categories.append(parent_category)

    for category in all_categories:
        # Find all elements of the same category
        collector = DB.FilteredElementCollector(doc)
        category_filter = DB.ElementCategoryFilter(category.Id)
        elements_to_delete = collector.WherePasses(category_filter).ToElements()
        
        # Delete the elements
        if elements_to_delete:
            t = DB.Transaction(doc, "Delete elements of category: " + category.Name)
            t.Start()
            try:
                element_ids = [elem.Id for elem in elements_to_delete]
                deleted_count = len(element_ids)
                doc.Delete(System.Collections.Generic.List[DB.ElementId](element_ids))
                t.Commit()
                print ("Deleted " + str(deleted_count) + " elements of category: " + category.Name)
            except Exception as e:
                t.RollBack()
                print ("Error deleting elements of category: " + category.Name + " because " + str(e))
        else:
            print ("No elements found with category: " + category.Name)


class DataGridObj(object):
    """Data object for file information display in the UI grid."""
    def __init__(self, file_path, OST_list, selected_name=None):
        self.file_path = file_path
        self.display_name = FOLDER.get_file_name_from_path(file_path)
        self.display_name_naked = self.display_name.split(".")[0]
        self.extension = FOLDER.get_file_extension_from_path(
            file_path).lower()
        self.OST_list = OST_list
        if selected_name:
            self.selected_OST_name = selected_name
        else:
            self.selected_OST_name = OST_list[0]


class Rhino2Revit_UI(forms.WPFWindow):
    """Main UI window for Rhino2Revit conversion tool."""
    def __init__(self):
        xaml_file_name = 'Rhino2Revit_UI.xaml'
        forms.WPFWindow.__init__(self, xaml_file_name)

        logo_file = IMAGE.get_image_path_by_name("logo_vertical_light.png")
        self.set_image_source(self.logo_img, logo_file)
        self.button_convert.Visibility = System.Windows.Visibility.Collapsed
        self.Height = 800

        self.is_adaptive_family = is_family_adaptive()

    def is_pass_convert_precheck(self):
        """Verify all files have assigned object styles before conversion."""
        for item in self.data_grid.ItemsSource:
            if "Waiting" in item.selected_OST_name:
                self.button_convert.BorderBrush = System.Windows.Media.Brushes.Black
                self.button_convert.BorderThickness = System.Windows.Thickness(1)
                self.button_convert.Content = "ObjectStyle Test Not Passed"
                self.button_convert.IsEnabled = False
                return False

        self.button_convert.BorderBrush = System.Windows.Media.Brushes.GreenYellow
        self.button_convert.BorderThickness = System.Windows.Thickness(2)
        self.button_convert.Content = "Convert To Revit"
        self.button_convert.IsEnabled = True
        self.button_convert.Visibility = System.Windows.Visibility.Visible

        return True

    @ERROR_HANDLE.try_catch_error()
    def purge_geo_from_doc_clicked(self, sender, args):
        """Handler for purge button click."""
        purge_geo_from_doc()

    @ERROR_HANDLE.try_catch_error()
    def convert_clicked(self, sender, args):
        """Convert selected files to Revit geometry."""
        if not self.is_pass_convert_precheck():
            return

        t = DB.Transaction(doc, "Convert GEO to native Revit")
        t.Start()
        tool_start_time = time.time()
        self.detail_list = ""
     
        def _work(item):
            start_time = time.time()
            self.detail_list += "\t{}\n".format(item.display_name)

            if "Use Source File Name" in item.selected_OST_name:
                try:
                    parent_category = doc.OwnerFamily.FamilyCategory
                    new_subc = doc.Settings.Categories.NewSubcategory(
                        parent_category, item.display_name_naked)
                except Exception as e:
                    pass
                finally:
                    item.selected_OST_name = item.display_name_naked

            if item.extension == ".3dm":
                self.free_form_convert(item)
            if item.extension == '.dwg':
                self.DWG_convert(item)

            time_span = time.time() - start_time
            NOTIFICATION.messenger("{} import finished!!\nImport used {}".format(item.display_name, TIME.get_readable_time(time_span)))

        UI.progress_bar(self.data_grid.ItemsSource, _work, label_func=lambda x: "Working on [{}]".format(x.display_name))   
        
        t.Commit()
        tool_time_span = time.time() - tool_start_time
        REVIT_FORMS.notification(main_text="Rhino2Revit Finished.",
                                sub_text="Files processeds:\n{}\nTotal time:\n{}".format(self.detail_list, TIME.get_readable_time(tool_time_span)))
        self.Close()

    def free_form_convert(self, data_item):
        """Convert 3dm file to FreeForm elements."""
        bad_geo_found = False
        converted_els = []
        geos = DB.ShapeImporter().Convert(doc, data_item.file_path)
        
        for geo in geos:
            try:
                converted_els.append(DB.FreeFormElement.Create(doc, geo))
            except Exception as e:
                print("-----Cannot import this part of file, skipping: {}".format(geo))
                print(e)
                print("-----")
                bad_geo_found = True

        assign_subC(converted_els, subC=get_subC_by_name(
            data_item.selected_OST_name))

    def DWG_convert(self, data_item):
        """Convert DWG file to native Revit elements."""
        exisiting_cads = DB.FilteredElementCollector(
            doc).OfClass(DB.ImportInstance).ToElements()
        exisiting_import_OSTs = get_current_import_object_styles()

        options = DB.DWGImportOptions()
        cad_import_id = clr.StrongBox[DB.ElementId]()
        with ErrorSwallower() as swallower:
            doc.Import(data_item.file_path, options,
                       doc.ActiveView, cad_import_id)

        current_cad_imports = DB.FilteredElementCollector(
            doc).OfClass(DB.ImportInstance).ToElements()
        cad_import = None
        for cad_import in current_cad_imports:
            if cad_import not in exisiting_cads:
                break

        # Check if CAD import was successful
        if not cad_import:
            print("No CAD good import found in the family document.<{}>".format(data_item.display_name))
            return

        cad_trans = cad_import.GetTransform()
        cad_type = cad_import.Document.GetElement(cad_import.GetTypeId())

        family_cat = doc.OwnerFamily.FamilyCategory

        geo_elem = cad_import.get_Geometry(DB.Options())
        geo_elements = []
        for geo in geo_elem:
            if isinstance(geo, DB.GeometryInstance):
                geo_elements.extend([x for x in geo.GetSymbolGeometry()])

        solids = []
        model_lines = []
        for gel in geo_elements:
            if isinstance(gel, DB.Solid):
                solids.append(gel)
            elif isinstance(gel, DB.Mesh):
                print("found mesh, trying to convert: {}".format(gel))
                RHINO2REVIT_UTILITY.mesh_convert(
                    gel, cad_trans, family_cat, data_item.display_name_naked)
            elif isinstance(gel, DB.Line):
                model_lines.append(self.create_model_crv(gel))
            elif isinstance(gel, DB.Arc):
                if gel.IsBound:
                    model_lines.append(self.create_model_crv(
                        gel, additional_pt=gel.Evaluate(0.5, True)))
                else:
                    model_lines.append(self.create_model_circle(gel))
            elif isinstance(gel, DB.PolyLine):
                vertices = gel.GetCoordinates()
                for i in range(len(vertices)-1):
                    pt0 = vertices[i]
                    pt1 = vertices[i + 1]
                    try:
                        line = DB.Line.CreateBound(pt0, pt1)
                        model_lines.append(self.create_model_crv(line))
                    except Exception as e:
                        print("Cannot do it here becasue {}".format(e))
            elif isinstance(gel, DB.NurbSpline):
                model_lines.append(self.create_model_spline(gel))
            else:
                print("Other geo found: {}, will ignore...".format(gel))

        # Create freeform from solids
        converted_els = []
        for solid in solids:
            converted_els.append(DB.FreeFormElement.Create(doc, solid))

        cad_import.Pinned = False
        doc.Delete(cad_import.Id)

        assign_subC_to_crvs(model_lines, subC=get_graphic_style_by_name(
            data_item.selected_OST_name))
        assign_subC(converted_els, subC=get_subC_by_name(
            data_item.selected_OST_name))

        try:
            clean_import_object_style(existing_OSTs=exisiting_import_OSTs)
        except Exception as e:
            print("fail to clean up imported category SubC becasue " + str(e))

    @ERROR_HANDLE.try_catch_error()
    def add_OST_clicked(self, sender, args):
        """Add a new subcategory."""
        parent_category = doc.OwnerFamily.FamilyCategory
        new_subc_name = forms.ask_for_unique_string(reserved_values=get_all_subC_names(),
                                                    default="New SubC Name",
                                                    prompt="Name the new sub-c that will be used",
                                                    title="What is it called? Give it a unique SubC name.")

        t = DB.Transaction(doc, "Convert to User Created Sub-C")
        t.Start()
        try:
            new_subc = doc.Settings.Categories.NewSubcategory(
                parent_category, new_subc_name)
        except:
            pass
        t.Commit()

        if not self.data_grid.ItemsSource:
            return
        self.update_drop_down_selection_source()

        self.data_grid.ItemsSource = [DataGridObj(
            x.file_path, self.object_style_combos.ItemsSource, selected_name=x.selected_OST_name) for x in self.data_grid.ItemsSource]

    def update_drop_down_selection_source(self):
        """Update the dropdown selection options for object styles."""
        raw_subC_names = ["- Waiting Assignment -"] + \
            get_all_subC_names() + ["<Use Source File Name as SubC>"]
        self.object_style_combos.ItemsSource = raw_subC_names
     
    @ERROR_HANDLE.try_catch_error()
    def open_details_description(self, sender, args):
        """Display detailed information about file type options."""
        REVIT_FORMS.notification(main_text="<.3dm Files>\nPros:\n\tStable, feel more similar to native Revit elements.\n\tIndividual control on Boolean, Subc, Visibility, Dimension Control\nCons:\n\tRequire Higer Standard of Cleaness in model.\n\tCannot handle curves.\n\n<.DWG Files>\nPros:\n\tMore tolerance on imperfection in models\n\tCan deal with lines, arcs and circle. Can also deal with Nurbs if all control points on same CPlane.\nCons:\n\tNo individual control for multiple elements, each import from same source file is glued.\n\tIntroduce Import SubC (which can be fixed automatically)",
                                 sub_text="With the exception of curve elements, .3dm is always prefered format, if it fails to convert, try some fix source model as far as you can. You can see the help from the output window.\nUse .dwg as your last resort.",
                                 window_title="EnneadTab",
                                 button_name="Close",
                                 self_destruct=0,
                                 window_width=1200,
                                 window_height=800)
        import trouble_shooting
        trouble_shooting.show_instruction(output)

    @ERROR_HANDLE.try_catch_error()
    def open_youtube(self, sender, args):
        """Open YouTube tutorial."""
        script.open_url(r"https://youtu.be/gb2rG6ZteP8")

    @ERROR_HANDLE.try_catch_error()
    def pick_files(self, sender, args):
        """Allow user to select files for conversion."""
        recent_output_folder = ENVIRONMENT.ONE_DRIVE_DESKTOP_FOLDER
        recent_out_data = DATA_FILE.get_data("rhino2revit_out_paths")
        if recent_out_data:
            if recent_out_data["3dm_out_paths"]:
                recent_path = recent_out_data["3dm_out_paths"][-1]
                if os.path.exists(os.path.dirname(recent_path)):
                    recent_output_folder = os.path.dirname(recent_path)
            if recent_out_data["dwg_out_paths"]:
                recent_path = recent_out_data["dwg_out_paths"][-1]
                if os.path.exists(os.path.dirname(recent_path)):
                    recent_output_folder = os.path.dirname(recent_path)
                
        files = forms.pick_file(files_filter='Rhino and AutoCAD (*.3dm; *.dwg)|*.3dm; *.dwg|'
                                'Rhino (*.3dm)|*.3dm|'
                                'AutoCAD|*.dwg',
                                init_dir = recent_output_folder,
                                multi_file=True,
                                title="Pick your files, Rhino and/or CAD")
        if not files:
            NOTIFICATION.messenger("There are no files selected.")
            return
        self.post_file_load(files)

    def post_file_load(self, files):
        """Process files after they are loaded."""
        self.update_drop_down_selection_source()
        self.data_grid.ItemsSource = [DataGridObj(
            x, self.object_style_combos.ItemsSource) for x in files]
        self.data_grid.Visibility = System.Windows.Visibility.Visible

        self.Height = 800

        self.button_test_assignment.Visibility = System.Windows.Visibility.Visible
        self.button_force_filename_OST.Visibility = System.Windows.Visibility.Visible

    @ERROR_HANDLE.try_catch_error()
    def load_recent_output_clicked(self, sender, args):
        """Load recently used output files."""
        recent_out_data = DATA_FILE.get_data("rhino2revit_out_paths")
        files = []
        if recent_out_data:
            if recent_out_data["3dm_out_paths"]:
                for path in recent_out_data["3dm_out_paths"]:
                    if os.path.exists(path):
                        files.append(path)
            if recent_out_data["dwg_out_paths"]:
                for path in recent_out_data["dwg_out_paths"]:
                    if os.path.exists(path):
                        files.append(path)

        if not files:
            NOTIFICATION.messenger("No recent output found or files no longer exist.")
            return
        self.post_file_load(files)

        for item in self.data_grid.ItemsSource:
            item.selected_OST_name = item.OST_list[-1]

    def data_grid_value_changed(self, sender, args):
        """Handle changes in the data grid values."""
        self.is_pass_convert_precheck()

    @ERROR_HANDLE.try_catch_error()
    def test_assignment_clicked(self, sender, args):
        """Test if all items have been assigned object styles."""
        self.is_pass_convert_precheck()

    @ERROR_HANDLE.try_catch_error()
    def force_file_name_OST_clicked(self, sender, args):
        """Force using filename as object style."""
        for item in self.data_grid.ItemsSource:
            if item.selected_OST_name == self.object_style_combos.ItemsSource[0]:
                item.selected_OST_name = self.object_style_combos.ItemsSource[-1]
        self.data_grid.ItemsSource = [DataGridObj(
            x.file_path, self.object_style_combos.ItemsSource, selected_name=x.selected_OST_name) for x in self.data_grid.ItemsSource]

    def handle_click(self, sender, args):
        """Handle surface click event."""
        print("surface clicked")

    def close_click(self, sender, args):
        """Close the window."""
        self.Close()

    def mouse_down_main_panel(self, sender, args):
        """Allow dragging the window."""
        sender.DragMove()

    def create_model_crv(self, geo_crv, additional_pt=None):
        """Create a model curve from geometry curve."""
        try:
            pt0 = geo_crv.GetEndPoint(0)
            pt1 = geo_crv.GetEndPoint(1)
            if not additional_pt:
                pt2 = pt0 + DB.XYZ(0, 0, 1)
                pt2_alt = pt0 + DB.XYZ(1, 0, 0)
            else:
                pt2 = additional_pt

            parent_category = doc.OwnerFamily.FamilyCategory
            if parent_category.Name == "Mass" or self.is_adaptive_family:
                pt_arry = DB.ReferencePointArray()
                for pt in [pt0, pt1]:
                    pt_arry.Append(doc.FamilyCreate.NewReferencePoint(pt))

                model_crv = doc.FamilyCreate.NewCurveByPoints(pt_arry)
            else:
                try:
                    geo_plane = DB.Plane.CreateByThreePoints(pt0, pt1, pt2)
                except:
                    geo_plane = DB.Plane.CreateByThreePoints(pt0, pt1, pt2_alt)
                sketch_plane = DB.SketchPlane.Create(doc, geo_plane)
                model_crv = doc.FamilyCreate.NewModelCurve(
                    geo_crv, sketch_plane)
            return model_crv
        except Exception as e:
            print("\n\nCannot convert crv object {} becasue {}".format(
                geo_crv, traceback.format_exc()))

    def create_model_circle(self, geo_crv):
        """Create a model circle from geometry curve."""
        try:
            pt0 = geo_crv.Center
            normal = geo_crv.Normal

            geo_plane = DB.Plane.CreateByNormalAndOrigin(normal, pt0)
            sketch_plane = DB.SketchPlane.Create(doc, geo_plane)
            model_crv = doc.FamilyCreate.NewModelCurve(geo_crv, sketch_plane)
            return model_crv
        except Exception as e:
            print("Cannot convert crv object {} becasue {}".format(
                geo_crv, traceback.format_exc()))

    def create_model_spline(self, geo_crv):
        """Create a model spline from geometry curve."""
        try:
            control_pts = list(geo_crv.CtrlPoints)
            pt0 = control_pts[0]
            pt1 = control_pts[-1]
            pt2 = control_pts[1]

            geo_plane = DB.Plane.CreateByThreePoints(pt0, pt1, pt2)
            sketch_plane = DB.SketchPlane.Create(doc, geo_plane)
            model_crv = doc.FamilyCreate.NewModelCurve(geo_crv, sketch_plane)
            return model_crv
        except Exception as e:
            print("###############")
            print("Cannot convert spline object {} becasue {}".format(geo_crv, e))
            print("###############")
            REVIT_FORMS.notification(main_text="There are geometry that Revit didn't accept becasue {}".format(e),
                                     sub_text="Revit spline has to live in a plane. The plane can be angled, but a plane nonetheless.\n\nIf you need spatial free curve, consider make the curve a surface ribbon in Rhino and bring in here in Revit. You can then use the edge of this surface to do sweep and then keep the ribbon category hidden in template.", self_destruct=30)


def get_all_subC_names():
    """Get all subcategory names from current family category."""
    parent_category = doc.OwnerFamily.FamilyCategory
    
    subC_names = [
        x.Name for x in parent_category.SubCategories if "<" not in x.Name]
    subC_names.sort()
    return subC_names


def get_subC_by_name(name):
    """Get subcategory by name."""
    parent_category = doc.OwnerFamily.FamilyCategory
    subCs = parent_category.SubCategories
    for subC in subCs:
        if subC.Name == name:
            return subC


def get_graphic_style_by_name(name):
    """Get graphic style by name."""
    all_graphic_styles = DB.FilteredElementCollector(
        doc).OfClass(DB.GraphicsStyle).ToElements()
    for style in all_graphic_styles:
        if style.GraphicsStyleCategory.Name == name:
            return style


def assign_subC(converted_els, subC):
    """Assign subcategory to elements."""
    for element in converted_els:
        element.Subcategory = subC


def assign_subC_to_crvs(converted_els, subC):
    """Assign subcategory to curve elements."""
    if not subC:
        return
    for element in converted_els:
        if not element:
            continue
        try:
            element.Subcategory = subC
        except Exception as e:
            print("\ncannot assign SubC becasue {}".format(e))
            print(subC.Name)


def get_current_import_object_styles():
    """Get current import object styles from document."""
    categories = doc.Settings.Categories
    import_OSTs = filter(lambda x: "Imports in Families" in x.Name, categories)
    if len(import_OSTs) == 0:
        return
    import_OSTs = list(import_OSTs[0].SubCategories)
    return import_OSTs


def clean_import_object_style(existing_OSTs):
    """Remove imported object styles that weren't there before import."""
    import_OSTs = get_current_import_object_styles()

    for import_OST in import_OSTs:
        if import_OST not in existing_OSTs:
            doc.Delete(import_OST.Id)


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def main():
    """Main function to run the tool."""
    if not doc.IsFamilyDocument:
        NOTIFICATION.messenger("Must be in a family environment\nOtherwise cannot use effective subCategory")
        REVIT_FORMS.notification(main_text="Must be in a family environment for subCategory to be useful.",
                                 sub_text="DirectShape is never a good solution, so don't do it in project environment.",
                                 window_title="EnneadTab",
                                 button_name="Close",
                                 self_destruct=5,
                                 window_width=500,
                                 window_height=500)
        return
    Rhino2Revit_UI().show_dialog()


################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    main()
