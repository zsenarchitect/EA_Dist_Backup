#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Add fire rating detail item family along walls that have 'Fire Rating' \
in the wall type.\n\n1 HR or 2HR graphic will be overlayed. Works on staright and \
arc walls."
__title__ = "Create/Update\nWall Fire Rating Graphic"
__youtube__ = "https://youtu.be/YHpJGcCpmUE"
from pyrevit import forms #
from pyrevit import script #
# from pyrevit import revit #
import EA_UTILITY
import EnneadTab
from Autodesk.Revit import DB 
# from Autodesk.Revit import UI
import traceback

doc = __revit__.ActiveUIDocument.Document

class FireRating:
    def __init__(self):
        self.rating_list = ["1 HR",
                            "2 HR",
                            "3 HR",
                            "4 HR"]

        self.rating_type_map = self.map_detail_family_type()
        self.log = ""


    def update_log(self, string):
        self.log += "\n" + string

    def print_log(self):
        print (self.log)

    def get_wall_rating(self, wall):
        return wall.WallType.LookupParameter("Fire Rating").AsString()


    def map_detail_family_type(self):
        OUT = dict()
        types = DB.FilteredElementCollector(doc).OfClass(DB.FamilySymbol ).ToElements()
        #print types
        types = filter(lambda x: "EA_Fire Rating" in x.FamilyName, types)
        #print types
        if not types:
            return OUT

        for type in types:
            type_name = type.LookupParameter("Type Name").AsString()
            if type_name in self.rating_list:
                OUT[type_name] = type

        return OUT

    def create_detail_instance(self, rating, curve, view):
        type = self.rating_type_map[rating]

        if not type.IsActive:
            #print family_type
            #t = DB.Transaction(doc, "Activate Symbol")
            #t.Start()
            type.Activate ()
            doc.Regenerate()
            #t.Commit()
        return doc.Create.NewFamilyInstance(curve, type, view)




    def create_update_wall_fire_rating(self):


        wall_types = DB.FilteredElementCollector(doc).OfClass(DB.WallType).WhereElementIsElementType().ToElements()
        #print wall_types
        #wall_types = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Walls).WhereElementIsElementType().ToElements()
        #print wall_types

        def a_good_fire_wall(type):
            #print type
            if not type.LookupParameter("Fire Rating"):
                return False

            if type.LookupParameter("Fire Rating").AsString() in self.rating_list:
                return True
            return False


        wall_types = filter(a_good_fire_wall, wall_types)
        #print wall_types[0]

        self.good_wall_type_ids = [x.Id for x in wall_types]

        views = forms.select_views()
        if not views:
            return

        views.sort(reverse = True)
        TG = DB.TransactionGroup(doc, "Create/Update fire rating graphic")
        TG.Start()
        map(self.process_view, views)
        #for view in views:
            #self.process_view(view)
        #T.Commit()
        TG.Assimilate ()
        self.update_log( "\n\n\nTool Finished.")

        self.print_log()


    def clear_all_EA_rating_graphic(self, view):

        instances = DB.FilteredElementCollector(doc, view.Id).OfClass(DB.FamilyInstance ).WhereElementIsNotElementType().ToElements()
        #print types
        instances = filter(lambda x: "EA_Fire Rating" in x.Symbol.FamilyName, instances)
        #print types
        if not instances:
            return


        t0 = DB.Transaction(doc, "purge old graphic")
        t0.Start()
        doc.Delete(EA_UTILITY.list_to_system_list([x.Id for x in instances]))
        t0.Commit()
        return

    def process_view(self, view):
        self.update_log( "\n\n## processing view: {}".format(output.linkify(view.Id, title = view.Name)))
        self.clear_all_EA_rating_graphic(view)
        walls = DB.FilteredElementCollector(doc, view.Id).OfClass(DB.Wall).WhereElementIsNotElementType().ToElements()
        #print walls[0].WallType
        #global self.good_wall_type_ids
        walls = filter(lambda x: x.WallType.Id in self.good_wall_type_ids, walls)


        healthy_walls = []
        for i, wall in enumerate(walls):
            # t = DB.Transaction(doc, "local")
            # t.Start()
            # [x.LookupParameter("Commxents").Set("000") for x in walls]
            # t.Commit()

            #try:


            #print "#####"
            curve =  wall.Location.Curve

            """ should check if curve is line or arc, only line can go on"""
            is_arc = hasattr(curve, "Radius")
            if is_arc:



                arc_radius = curve.Radius
                end0 = curve.GetEndPoint (0)
                end1 = curve.GetEndPoint (1)
                if curve.Normal.Z > 0:
                    end0, end1 = end1, end0
                curve = DB.Line.CreateBound(end0, end1)

                #print "Skipping creation/update: {}. This is a arc wall.".format(output.linkify(wall.Id, title = "This Wall"))
                #continue
            #print curve.GetEndPoint(0)
            #print curve.GetEndPoint(1)
            rating = self.get_wall_rating(wall)
            #print rating
            try:
                t = DB.Transaction(doc, "local")
                t.Start()
                new_element = self.create_detail_instance(rating, curve, view)
                if is_arc:
                    new_element.LookupParameter("is_arc").Set(1)
                    new_element.LookupParameter("R").Set(arc_radius)
                self.update_log( "# Creating {}/{} Fire Rating Graphic...".format(i + 1, len(walls)))
                healthy_walls.append(wall)

                t.Commit()


            except Exception as e:
                #print str(e)
                if "The line is not in the plane of view." not in str(e) :
                    #if EA_UTILITY.is_SZ():
                    self.update_log( traceback.format_exc())


                self.update_log("Skipping creation/update: {} has some problem...{}".format(output.linkify(wall.Id, title = "This Wall"), e)  )

                t.RollBack()
            finally:
                pass
                #t.Commit()
        self.update_log( "-------")

################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    func_class = FireRating()
    try:
        func_class.create_update_wall_fire_rating()
        import ENNEAD_LOG
        ENNEAD_LOG.use_enneadtab(coin_change = 60, tool_used = "Create/Update fire rating graphic.", show_toast = True)

    except:
        print (traceback.format_exc())
