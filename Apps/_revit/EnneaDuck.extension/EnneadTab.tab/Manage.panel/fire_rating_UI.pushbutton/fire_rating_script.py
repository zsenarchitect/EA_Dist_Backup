#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = """Fire Rating Graphic Manager

A comprehensive fire rating management system that streamlines code compliance documentation.
This powerful utility helps you:
- Assign and track fire ratings across wall types
- Generate intelligent graphics that update automatically across multiple views
- Maintain consistent fire separation documentation
- Ensure building code requirements are clearly communicated

Key Features:
- Intuitive UI for managing wall type fire ratings
- Batch updates across selected views
- Support for linked models
- Smart graphic family (EA_Fire Rating) with customizable appearance
- Real-time wall instance counting and preview

Perfect for maintaining consistent fire separation documentation and ensuring 
building code requirements are clearly communicated in your drawings."""

__title__ = "Fire Rating\nGraphic"
__tip__ = True
__is_popular__ = True
import traceback
import os
import System # pyright: ignore 

from Autodesk.Revit.UI import IExternalEventHandler, ExternalEvent # pyright: ignore 


from Autodesk.Revit.Exceptions import InvalidOperationException # pyright: ignore 
from pyrevit.forms import WPFWindow
from pyrevit.forms import select_views as PYFORM_SELECT_VIEWS
from pyrevit import script 

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
from EnneadTab.REVIT import REVIT_FORMS, REVIT_APPLICATION, REVIT_GEOMETRY, REVIT_FAMILY
from EnneadTab import NOTIFICATION, DATA_CONVERSION, ENVIRONMENT, ERROR_HANDLE, FOLDER, IMAGE, LOG, SAMPLE_FILE
from Autodesk.Revit import DB # pyright: ignore 

uidoc = REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()
__persistentengine__ = True

FAMILY_NAME = "EA_Fire Rating"


class FireRatingGraphicMaker:
    """Handles creation and update of fire rating graphics in views.
    
    Args:
        views: List of views to process
        rating_list: List of valid fire ratings
        allow_link: Whether to process walls in linked models
    """
    def __init__(self, views, rating_list, allow_link):
        self.rating_list = rating_list
        self.rating_type_map = self.map_detail_family_type()
        self.log = ""
        self.views = views
        self.allow_link = allow_link

    def update_log(self, string):
        """Append message to log with newline."""
        self.log += "\n" + string

    def print_log(self):
        print (self.log)

    def get_wall_rating(self, wall):
        """Get fire rating parameter value from wall type."""
        return wall.WallType.LookupParameter("Fire Rating").AsString()

    def map_detail_family_type(self):
        """Map fire rating values to family symbol types.
        
        Returns:
            Dict mapping rating strings to family symbol types
        """
        OUT = dict()
        types = DB.FilteredElementCollector(doc).OfClass(DB.FamilySymbol).ToElements()
        types = filter(lambda x: "EA_Fire Rating" in x.FamilyName, types)
        
        if not types:
            return OUT

        for type in types:
            type_name = type.LookupParameter("Type Name").AsString()
            if type_name == self.rating_list[0]:
                continue

            if type_name in self.rating_list:
                OUT[type_name] = type

        return OUT

    def create_detail_instance(self, rating, curve, view):
        type = self.rating_type_map.get(rating, None)
        if not type:
            print("type not found: {}".format(rating))
            return 

        if not type.IsActive:
 
            type.Activate ()
            doc.Regenerate()

        # introduce a temp detailcurve element to avoid the curve not in view plane issue
        temp_detail_line = doc.Create.NewDetailCurve(view, curve)
        base_line = temp_detail_line.GeometryCurve
        instance = doc.Create.NewFamilyInstance(base_line, type, view)
        doc.Delete(temp_detail_line.Id)

        return instance




    def create_update_wall_fire_rating(self):


        wall_types = DB.FilteredElementCollector(doc).OfClass(DB.WallType).WhereElementIsElementType().ToElements()

        def a_good_fire_wall(type):
            #print type
            if not type.LookupParameter("Fire Rating"):
                return False

            if type.LookupParameter("Fire Rating").AsString() in self.rating_list:
                return True
            return False

        wall_types = filter(a_good_fire_wall, wall_types)

        self.good_wall_type_ids = [x.Id for x in wall_types]


        TG = DB.TransactionGroup(doc, "Create/Update Fire Rating Graphic")
        TG.Start()
        map(self.process_view, self.views)

        TG.Assimilate ()
        self.update_log( "\n\n\nTool Finished.")

        self.print_log()


    def clear_all_EA_rating_graphic(self, view):
        try:
            uidoc.ActiveView = view
        except:
            pass
        uidoc.RefreshActiveView ()

        instances = DB.FilteredElementCollector(doc, view.Id).OfClass(DB.FamilyInstance ).WhereElementIsNotElementType().ToElements()
        #print types
        instances = filter(lambda x: "EA_Fire Rating" in x.Symbol.FamilyName, instances)

        clean_list = []
        for instance in instances:
            para = instance.LookupParameter("is_override")
            if not para or para.AsInteger() == 0:
                clean_list.append(instance)
            
        #print types
        if not clean_list:
            return


        t0 = DB.Transaction(doc, "purge old graphic")
        t0.Start()
        doc.Delete(DATA_CONVERSION.list_to_system_list([x.Id for x in clean_list]))
        #doc.Regenerate()
        t0.Commit()
        
        return

    def process_view(self, view):
        self.update_log( "\n\n## processing view: {}".format(output.linkify(view.Id, title = view.Name)))
        NOTIFICATION.messenger(main_text = "Processing view: {}".format(view.Name))
        self.clear_all_EA_rating_graphic(view)
        
        walls = DB.FilteredElementCollector(doc, view.Id).OfClass(DB.Wall).WhereElementIsNotElementType().ToElements()


        if self.allow_link:
            walls = list(walls)
            link_docs = REVIT_APPLICATION.get_revit_link_docs()

            for link_doc in link_docs:
                additional_walls = DB.FilteredElementCollector(link_doc).OfClass(DB.Wall).WhereElementIsNotElementType().ToElements()
                walls.extend(additional_walls)
                
        walls = filter(lambda x: x.WallType.Id in self.good_wall_type_ids, walls)


        healthy_walls = []
        for i, wall in enumerate(walls):

            curve =  wall.Location.Curve
            # print (curve.GetEndPoint (0), curve.GetEndPoint (1))
            # curve = REVIT_GEOMETRY.project_crv_in_view(curve, view)
            # print (curve.GetEndPoint (0), curve.GetEndPoint (1))
            # print (view.Origin)


            is_arc = hasattr(curve, "Radius")
            if is_arc:

                arc_radius = curve.Radius
                end0 = curve.GetEndPoint (0)
                end1 = curve.GetEndPoint (1)
                if curve.Normal.Z > 0:
                    end0, end1 = end1, end0
                curve = DB.Line.CreateBound(end0, end1)


            rating = self.get_wall_rating(wall)

            try:
                t = DB.Transaction(doc, "local")
                t.Start()
                new_element = self.create_detail_instance(rating, curve, view)
                if not new_element:
                    t.RollBack()
                    continue
                
                if is_arc:
                    new_element.LookupParameter("is_arc").Set(1)
                    new_element.LookupParameter("R").Set(arc_radius)
                self.update_log( "# Creating {}/{} Fire Rating Graphic...".format(i + 1, len(walls)))
                healthy_walls.append(wall)

                t.Commit()


            except Exception as e:
                print (e)
                if "The line is not in the plane of view."  in str(e) :
       
                    self.update_log("Skipping creation/update: {} has some problem...The line is not in the plane of view, or it is outside the view crop.".format(output.linkify(wall.Id, title = "This Wall"))  )
                else:

                    self.update_log("Skipping creation/update: {} has some problem...{}".format(output.linkify(wall.Id, title = "This Wall"), e)  )

                t.RollBack()

               
        self.update_log( "-------")

@ERROR_HANDLE.try_catch_error()
def update_fire_rating_graphic( views, rating_list, allow_link):

    # t = DB.Transaction(doc, "Update fire rating graphic.")
    # t.Start()
    FireRatingGraphicMaker(views, rating_list, allow_link).create_update_wall_fire_rating()
    # t.Commit()


@ERROR_HANDLE.try_catch_error()
def update_wall_data(data_grid_source):

    t = DB.Transaction(doc, "Update wall rating data.")
    t.Start()
    for obj in data_grid_source:
        if obj.selected_rating != "Unrated":
            obj.wall_type.LookupParameter("Fire Rating").Set(obj.selected_rating)
    t.Commit()




@ERROR_HANDLE.try_catch_error()
def load_EA_family(title):
    """Load the EA Fire Rating family into current document.
    
    Args:
        title: Title string for transaction name
        
    Returns:
        str: Success/failure message
    """

    lib_family_path = SAMPLE_FILE.get_file(FAMILY_NAME + ".rfa")
    fam_ref = REVIT_FAMILY.load_family_by_path(lib_family_path, doc)
    return "Successfully loaded EA Fire Rating family"



# Create a subclass of IExternalEventHandler
class fire_rating_SimpleEventHandler(IExternalEventHandler):
    """
    Simple IExternalEventHandler sample
    """

    # __init__ is used to make function from outside of the class to be executed by the handler. \
    # Instructions could be simply written under Execute method only
    def __init__(self, do_this):
        self.do_this = do_this
        self.kwargs = None
        self.OUT = None


    # Execute method run in Revit API environment.
    def Execute(self,  uiapp):
        try:
            try:
                #print "try to do event handler func"
                self.OUT = self.do_this(*self.kwargs)
            except:
                print ("failed")
                print (traceback.format_exc())
        except InvalidOperationException:
            # If you don't catch this exeption Revit may crash.
            print ("InvalidOperationException catched")

    def GetName(self):
        return "simple function executed by an IExternalEventHandler in a Form"

class data_grid_obj:
    def __init__(self, wall_type, rating_list):
        self.wall_type = wall_type
        self.format_name = wall_type.LookupParameter("Type Name").AsString()

        # do some checking to using other index
        rating = wall_type.LookupParameter("Fire Rating").AsString()
        for rating_opt in rating_list:
            if rating == rating_opt:
                self.selected_rating = rating
                break
        else:
            self.selected_rating = rating_list[0]




# A simple WPF form used to call the ExternalEvent
class fire_rating_ModelessForm(WPFWindow):
    """
    Simple modeless form sample
    """

    def pre_actions(self):

        self.update_graphic_event_handler = fire_rating_SimpleEventHandler(update_fire_rating_graphic)
        self.ext_event_update_graphic = ExternalEvent.Create(self.update_graphic_event_handler)


        self.update_wall_data_event_handler = fire_rating_SimpleEventHandler(update_wall_data)
        self.ext_event_update_wall_data = ExternalEvent.Create(self.update_wall_data_event_handler)


        self.load_family_event_handler = fire_rating_SimpleEventHandler(load_EA_family)
        self.ext_event_load_family = ExternalEvent.Create(self.load_family_event_handler)
        return


    @ERROR_HANDLE.try_catch_error()
    def __init__(self):
        self.pre_actions()

        xaml_file_name = "fire_rating_UI.xaml" ###>>>>>> if change from window to dockpane, the top level <Window></Window> need to change to <Page></Page>
        WPFWindow.__init__(self, xaml_file_name)

        self.title_text.Text = "EnneadTab Fire Rating Manager"

        self.sub_text.Text = "Manage your wall type fire rating info and control the rating graphic across multiple views. It will also auto-load EA_rating family if it is not presented in the document. You have the option to further customize the EA_rating family once loaded."


        self.Title = self.title_text.Text

        logo_file = IMAGE.get_image_path_by_name("logo_vertical_light.png")
        self.set_image_source(self.logo_img, logo_file)


        self.selected_views = None


        self.init_data_grid()

        self.Show()

    @ERROR_HANDLE.try_catch_error()
    def init_data_grid(self):


        rating_list = ["Unrated",
                        "1 HR",
                        "2 HR",
                        "3 HR"]
        rating_family = REVIT_FAMILY.get_family_by_name(FAMILY_NAME, doc)
        if rating_family:
            rating_list = ["Unrated"] +REVIT_FAMILY.get_all_types_by_family_name(FAMILY_NAME, return_name = True)
            
        self.rating_list = rating_list
        
        self.rating_combos.ItemsSource = self.rating_list


        all_wall_types = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Walls).WhereElementIsElementType().ToElements()
        all_wall_types = sorted(list(all_wall_types), key=lambda x: x.LookupParameter("Type Name").AsString())
      
        self.main_data_grid.ItemsSource = [data_grid_obj(wall_type, self.rating_list) for wall_type in all_wall_types]


        

    @ERROR_HANDLE.try_catch_error()
    def preview_selection_changed(self, sender, args):
        obj = self.main_data_grid.SelectedItem
        if not obj:
            self.textblock_wall_detail.Text = ""
            return


        if not self.checkbox_auto_update.IsChecked:
            return



        active_view_filtered_collector = DB.FilteredElementCollector(doc, doc.ActiveView.Id)

        project_filtered_collector = DB.FilteredElementCollector(doc)

        # type_filter = DB.ElementFilter (doc, obj.wall_type.Id)


        # active_view_walls = list(active_view_filtered_collector.OfClass(DB.Wall).WherePasses (type_filter).ToElements())
        # project_walls = list(project_filtered_collector.OfClass(DB.Wall).WherePasses (type_filter).ToElements())
 
        active_view_walls = list(active_view_filtered_collector.OfClass(DB.Wall).WhereElementIsNotElementType().ToElements())
        project_walls = list(project_filtered_collector.OfClass(DB.Wall).WhereElementIsNotElementType().ToElements())

        active_view_walls = filter(lambda x: x.WallType.Id == obj.wall_type.Id, active_view_walls)
        project_walls = filter(lambda x: x.WallType.Id == obj.wall_type.Id, project_walls)

        self.textblock_wall_detail.Text = "Current Document Only:\nActive view [{}] wall count: {}\nProject wall count: {}".format(doc.ActiveView.Name, 
                                                                                                        len(active_view_walls), 
                                                                                                        len(project_walls))


    @ERROR_HANDLE.try_catch_error()
    def UI_setting_changed(self, sender, args):
        if self.checkbox_auto_update.IsChecked:
            self.textblock_wall_detail.Visibility = System.Windows.Visibility.Visible
        else:
            self.textblock_wall_detail.Visibility = System.Windows.Visibility.Collapsed

    @ERROR_HANDLE.try_catch_error()
    def update_graphic_click(self, sender, args):

        # push update for current wall data first
        self.update_wall_data_event_handler.kwargs = self.main_data_grid.ItemsSource,
        self.ext_event_update_wall_data.Raise()


        if not self.is_EA_family_loaded():
            res = REVIT_FORMS.dialogue(main_text = "There is no EA fire rating graphic family loaded.",
                                                       sub_text = "Do you want to load it now?",
                                                       options = ["Yes", "No"])
            if res == "No" or res is None:
                return

            self.load_family_event_handler.kwargs = __title__,
            self.ext_event_load_family.Raise()



        
        if not self.selected_views:
            res = REVIT_FORMS.dialogue(main_text = "No view selected",
                                                       sub_text = "Do you want to apply active view instead?",
                                                       options = ["Yes", "No"])
            if res == "No" or res is None:
                return
            views_to_apply = [doc.ActiveView]
        else:
            views_to_apply = self.selected_views

        self.update_graphic_event_handler.kwargs =  views_to_apply, self.rating_list, self.checkbox_allow_link.IsChecked
        self.ext_event_update_graphic.Raise()
        res = self.update_graphic_event_handler.OUT
        if res:
            self.debug_textbox.Text = res
        else:
            self.debug_textbox.Text = "Debug Output:"

    @ERROR_HANDLE.try_catch_error()
    def force_reload_family_click(self, sender, args):
        self.load_family_event_handler.kwargs = __title__,
        self.ext_event_load_family.Raise()
        res = self.load_family_event_handler.OUT
        if res:
            self.debug_textbox.Text = res
        else:
            self.debug_textbox.Text = "Debug Output:"

            
    @ERROR_HANDLE.try_catch_error()
    def update_wall_type_data_click(self, sender, args):

        self.update_wall_data_event_handler.kwargs = self.main_data_grid.ItemsSource,
        self.ext_event_update_wall_data.Raise()
        res = self.update_wall_data_event_handler.OUT
        if res:
            self.debug_textbox.Text = res
        else:
            self.debug_textbox.Text = "Debug Output:"
  

    @ERROR_HANDLE.try_catch_error()
    def pick_view_click(self, sender, args):
        self.selected_views = PYFORM_SELECT_VIEWS(filterfunc = lambda x: x.ViewType == DB.ViewType.FloorPlan or  x.ViewType == DB.ViewType.AreaPlan)
        if not self.selected_views:
            self.textblock_view_list.Text = "No view selected"
            return


        if len(self.selected_views) > 3:
            display_list =  self.selected_views[:3] + ["... and {} more".format(len(self.selected_views) - 3)]
        else:
            display_list = self.selected_views
        self.textblock_view_list.Text = "\n".join([x.Name if isinstance(x, DB.View) else x for x in display_list ])



    def is_EA_family_loaded(self):
        for family in DB.FilteredElementCollector(doc).OfClass(DB.Family).ToElements():
            if "EA_Fire Rating" in family.Name:
                return True
        return False


    @ERROR_HANDLE.try_catch_error()
    def close_Click(self, sender, e):
        # This Raise() method launch a signal to Revit to tell him you want to do something in the API context
        self.Close()
    

    def mouse_down_main_panel(self, sender, args):
        #print "mouse down"
        sender.DragMove()



@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def main():
    fire_rating_ModelessForm()
    

################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    main()
