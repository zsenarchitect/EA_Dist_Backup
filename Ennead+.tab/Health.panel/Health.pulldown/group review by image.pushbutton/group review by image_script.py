__doc__ = "Export detail groups as Jpgs so you can review usage.\nThe file name\
 will be GroupName_(x) counts in projects."
__title__ = "Review Group\nAs Image"

from pyrevit import forms, DB, revit, script, UI



def get_dump_view():
    prefered_drafting_view_name = "$$EnneadTab Little Helper"
    views = DB.FilteredElementCollector(revit.doc).OfClass(DB.View).WhereElementIsNotElementType().ToElements()
    try:
        dump_view = filter(lambda x: x.Name == prefered_drafting_view_name, views)[0]
    except:
        view_family_types = DB.FilteredElementCollector(revit.doc).OfClass(DB.ViewFamilyType).WhereElementIsElementType().ToElements()
        for view_family_type in view_family_types:
            if view_family_type.ViewFamily == DB.ViewFamily.Drafting:
                break
        with revit.Transaction("local set dump view"):
            dump_view = DB.ViewDrafting.Create(revit.doc, view_family_type.Id)
            dump_view.Name = prefered_drafting_view_name
            dump_view.Scale = 1

    revit.uidoc.ActiveView = dump_view
    return dump_view

################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
        
    original_view = revit.uidoc.ActiveView
    #print original_view.Name
    #pick a drafting view, create one if no empty drafting view availible
    dump_view = get_dump_view()


    #pick a folder, make sure it si empty
    dump_folder =  forms.pick_folder(title = "empty folder used to store exported images")
    if dump_folder == None:
        script.exit()


    #get all detail groups
    detail_group_types = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_IOSDetailGroups).WhereElementIsElementType().ToElements()
    #print detail_group_types


    """
    class MyOption(forms.TemplateListItem):
        @property
        def name(self):
            return list(self.item.Groups)[0].Name
            

    detail_group_types = [MyOption(item) for item in detail_group_types]

    detail_group_types = forms.SelectFromList(detail_group_types, title = "pick a detail group type")
    """
    #place one instance on the drafting views, isolate, zoom extend, export image to folder with group name, delete instance
    with revit.TransactionGroup("review group by images"):
        bad_group = []
        total_count = len(detail_group_types)
        print "total {} detail group types found...".format(total_count)

        for i, detail_group_type in enumerate(detail_group_types):


            location = DB.XYZ(0,0,0)
            with revit.Transaction("local create"):
                temp_group = revit.doc.Create.PlaceGroup(location, detail_group_type)
                UI.UIDocument(revit.doc).ShowElements(temp_group)
                revit.doc.Regenerate()
                UI.UIDocument(revit.doc).RefreshActiveView()

            opts = DB.ImageExportOptions()
            #opts.FilePath = r'C:\image.gif'
            name = list(detail_group_type.Groups)[0].Name
            count = len(list(detail_group_type.Groups)) - 1  # minus one becasue we just created one in the dump view
            try:
                opts.FilePath = dump_folder + r'\{}_({} in proj).jpg'.format(name, count)
            except Exception as e:
                print "Skip [{}] becasue".format(name)
                continue
            print "\t\t{}/{}: exporting <{}>, {} found in the project".format(i+1, total_count, name, count)
            opts.ImageResolution = DB.ImageResolution.DPI_300
            opts.ExportRange = DB.ExportRange.VisibleRegionOfCurrentView
            opts.ZoomType = DB.ZoomFitType.FitToPage
            opts.PixelSize = 3000
            try:
                revit.doc.ExportImage(opts)
            except:
                print "!Detail group <{}> fail to export image. See solution at the end".format(name)
                bad_group.append(name)

            with revit.Transaction("local delete"):
                try:
                    revit.doc.Delete(temp_group.Id)
                except Exception as e:
                    print e
                    bad_group.append(name)
        """
        revit.uidoc.ActiveView = original_view
        with revit.Transaction("delete draft view"):
            revit.doc.Delete(dump_view.Id)
        """
        if len(bad_group) > 0:

            print "\n\n Group name contatining any of the following character cannot be saved on window folder, please consider replace special character with underscore '_':"
            print r'/\?*<>":'

            print "\n\nshort list groups that give errors during export"
            for item in bad_group:
                print item


