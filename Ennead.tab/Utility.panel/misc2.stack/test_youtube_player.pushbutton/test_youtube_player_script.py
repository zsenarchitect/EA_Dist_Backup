#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "NOT IN USE, test web WPF"
__title__ = "Test Youtube Player"


from Autodesk.Revit import UI
from Autodesk.Revit import DB # fastest DB
from Autodesk.Revit.UI import IExternalEventHandler, ExternalEvent
from Autodesk.Revit.Exceptions import InvalidOperationException



from pyrevit.revit import ErrorSwallower
from pyrevit import script, forms


import EnneadTab
import ENNEAD_LOG
import clr
import System
import time
import traceback
import random

uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document
__persistentengine__ = True



def get_all_instance_of_type(type):

    type_filter = DB.FamilyInstanceFilter (doc, type.Id)
    instances = list(DB.FilteredElementCollector(doc).OfClass(DB.FamilyInstance).WherePasses (type_filter).ToElements())

    return instances


@EnneadTab.ERROR_HANDLE.try_catch_error
def apply_radius_action(window):
    t = DB.Transaction(doc, __title__)
    t.Start()
    solution = Solution(window.bad_type, window.para_textbox.Text)

    # get all instacen of bad family, first check can we get a matching type name, record all instacne data
    bad_instances = get_all_instance_of_type(solution.bad_type)

    if len(bad_instances) == 0:
        note = "Cannot get anything from {}".format(solution.bad_type.LookupParameter("Type Name").AsString())
        EnneadTab.REVIT.REVIT_FORMS.notification(main_text = note,
                                                sub_text = "There might be no instance of bad type in the file, you should try purging.",
                                                window_title = "EnneadTab",
                                                button_name = "Close",
                                                self_destruct = 15,
                                                window_width = 1200)

        return

    output.print_md( "--Applying Panel Radius By Host Wall **[{}]:{}** ----Found {} Items".format(solution.bad_type.Family.Name,
                                            solution.bad_type.LookupParameter("Type Name").AsString(),
                                            len(bad_instances)))
    #print all_instances
    map(solution.fix_panel, bad_instances)
    #envvars.get_pyrevit_env_var("IS_SYNC_QUEUE_DISABLED")
    #envvars.set_pyrevit_env_var("EA_INSTANCE_DATA_TRANSFER", DATA)








    EnneadTab.NOTIFICATION.toast(sub_text = "",
                                main_text = "Radius Applied Finished!")


    t.Commit()
    window.update_drop_down_selection_source()
    text_out = "Radius Applied:\n[{}]: {} --> {} fixed.".format(solution.bad_type.Family.Name,
                                                            solution.bad_type.LookupParameter("Type Name").AsString(),
                                                            solution.fix_count)
    window.debug_textbox.Text = text_out
    window.debug_textbox.FontSize = 12

class Solution:
    def __init__(self, bad_type, para_name):
        self.bad_type = bad_type
        self.para_name = para_name


        self.error_panel_found = False
        self.fix_count = 0


    def fix_panel(self, panel):
        if not panel.LookupParameter(self.para_name):
            return

        desires_r = self.find_panel_host_wall_radius(panel)
        if panel.LookupParameter(self.para_name).AsDouble() != desires_r:
            panel.LookupParameter(self.para_name).Set(desires_r)
            self.fix_count += 1

    def find_panel_host_wall_radius(self, panel):

        radius = panel.Host.get_Parameter(DB.BuiltInParameter.CURVE_ELEM_ARC_RADIUS).AsDouble()
        if radius == 0.0:
            print "Panel {} should be in curved wall.{}".format(panel.Id, output.linkify(panel.Id,title = "Click to zoom to panel"))

            self.error_panel_found = True

        return radius


# Create a subclass of IExternalEventHandler
class SimpleEventHandler(IExternalEventHandler):
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

class DropDownItem():
    def __init__(self, item):
        if isinstance(item, str):
            self.item = item
            self.display_text = item
            return

        self.item = item
        self.display_text = item.LookupParameter("Type Name").AsString()


# A simple WPF form used to call the ExternalEvent
class test_youtube_UI(forms.WPFWindow):
    """
    Simple modeless form sample
    """

    def pre_actions(self):


        #print "doing preaction"
        # Now we need to make an instance of this handler. Moreover, it shows that the same class could be used to for
        # different functions using different handler class instances
        self.apply_radius_action_event_handler = SimpleEventHandler(apply_radius_action)
        #self.clock_event_handler = SimpleEventHandler(clock_work)
        # We now need to create the ExternalEvent
        self.ext_event = ExternalEvent.Create(self.apply_radius_action_event_handler)
        #self.ext_event_clock = ExternalEvent.Create(self.clock_event_handler)
        #print "preaction done"
        #print self.apply_radius_action_event_handler
        #print self.apply_radius_action_event_handler.kwargs
        #print self.ext_event
        #print "-------"
        return


    def __init__(self):

        self.pre_actions()
        xaml_file_name = 'test_youtube_UI.xaml'
        forms.WPFWindow.__init__(self, xaml_file_name)

        self.set_image_source(self.logo_img, "{}\logo_vertical_light.png".format(EnneadTab.ENVIRONMENT_CONSTANTS.CORE_IMAGES_FOLDER_FOR_PUBLISHED_REVIT))
        self.Height = 800
        self.family_bad = None

        txt_link = "https://www.youtube.com/watch?v=Pe_-870butM&list=PLz3VQzyVrU1haAuLItzhxEXajzyIv95pR&index=29"
        #print txt_link

        """
        html = "<html><head>"
        html += "<meta content='IE=Edge' http-equiv='X-UA-Compatible'/>"
        html += "<iframe id='video' src= 'https://www.youtube.com/embed/{0}' width='600' height='300' frameborder='0' allowfullscreen></iframe>"
        html += "</body></html>"

        import urllib
        print html
        print "###########"
        html = html.format(txt_link.split('=')[1])
        print html
        html = urllib.quote_plus(html)
        print html
        #from requests.compat import urljoin
        """
        """
        from requests.compat import urlparse
        url1 = 'https://docs.python.org/2/py-modindex.html#cap-f'

        self.web.Source =  urlparse(url1)
        """
        # import sys
        # sys.path.append(r"C:\Python27\Lib\site-packages")
        """
        from requests import urlopen
        html = urlopen(txt_link).read().decode('utf-8')
        self.web.Source = html
        """
        import clr

        # Add a reference to the WPF assemblies
        clr.AddReference("PresentationFramework")
        clr.AddReference("PresentationCore")
        clr.AddReference("System.Xaml")
        clr.AddReference("WindowsBase")


        self.Show()


        import urlparse
        #import clr
        from System import Uri
        # Parse the URL string into a ParseResult object
        url_string = "https://www.youtube.com/watch?v=Pe_-870butM&list=PLz3VQzyVrU1haAuLItzhxEXajzyIv95pR&index=29"
        # url_object = urlparse.urlparse(url_string)
        #
        # # Convert the ParseResult object to a string URL using urlunparse()
        # url_string = urlparse.urlunparse(url_object)

        # Create a Uri object from the string URL
        uri = Uri(url_string)
        print uri
        #self.web.Navigate("https://www.youtube.com/watch?v=Pe_-870butM&list=PLz3VQzyVrU1haAuLItzhxEXajzyIv95pR&index=29")

        self.web.Source = uri










    def close_click(self, sender, args):
        self.Close()





@EnneadTab.ERROR_HANDLE.try_catch_error
def main():

    modeless_form = test_youtube_UI()


################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    main()
    ENNEAD_LOG.use_enneadtab(coin_change = 20, tool_used = __title__.replace("\n", " "), show_toast = True)
