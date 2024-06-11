#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Schedule the total replacement."
__title__ = "Schedule\nPublish"


from Autodesk.Revit.UI import IExternalEventHandler, ExternalEvent
from System import EventHandler, Uri


from Autodesk.Revit.Exceptions import InvalidOperationException
from pyrevit.forms import WPFWindow
from pyrevit import forms #
from pyrevit import script #
# from pyrevit import _HostApplication


import sys
sys.path.append(r"C:\Users\szhang\github\EnneadTab-for-Revit\ENNEAD.extension\lib")
import EnneadTab
import traceback
from Autodesk.Revit import DB # pyright: ignore 
import random
import datetime
import time
import calendar
from Autodesk.Revit import UI # pyright: ignore
uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document # pyright: ignore
__persistentengine__ = True

import ENNEAD_LOG

import shutil






# A simple WPF form used to call the ExternalEvent
class schedule_publish_ModelessForm(WPFWindow):
    """
    Simple modeless form sample
    """

    def pre_actions(self):



        return


    @EnneadTab.ERROR_HANDLE.try_catch_error
    def __init__(self):
        self.pre_actions()

        xaml_file_name = "schedule_publish_ModelessForm.xaml" ###>>>>>> if change from window to dockpane, the top level <Window></Window> need to change to <Page></Page>
        WPFWindow.__init__(self, xaml_file_name)

        self.title_text.Text = "EnneadTab Schedule Publisher"

        self.sub_text.Text = "This publisher will REMOVE beta extension and then copy BETA extension. This is to ensure that the format is current."


        self.Title = "EnneadTab schedule publish UI"

        self.set_image_source(self.logo_img, "{}\logo_vertical_light.png".format(EnneadTab.ENVIRONMENT_CONSTANTS.CORE_IMAGES_FOLDER_FOR_PUBLISHED_REVIT))
        self.final_time = None


        self.Show()

    @EnneadTab.ERROR_HANDLE.try_catch_error
    def pick_date_click(self, sender, e):
        self.on_stop_watch = False
        time = forms.ask_for_date(prompt = "Will use 01:00 am of that date.", title="Enter date to publish:")
        self.final_time = time + datetime.timedelta(hours = 1)
        #datetime.datetime(2019, 5, 17, 0, 0)(arg):
        self.display_time.Text = "{} - {}".format(self.final_time, calendar.day_name[self.final_time.weekday()])


        time_diff = self.final_time - datetime.datetime.now()
        if time_diff.total_seconds()  > 0:
            self.bt_confirm.IsEnabled = True
        else:
            self.display_time.Text = "Pulish time is backward."
        pass


    @EnneadTab.ERROR_HANDLE.try_catch_error
    def confirm_schedule_Click(self, sender, e):
        if not hasattr(self, "final_time"):
            return

        if not self.final_time:
            return
        # This Raise() method launch a signal to Revit to tell him you want to do something in the API context
        #print "confirm schedule"
        self.on_stop_watch = True
        safety = 0
        while self.on_stop_watch:
            time.sleep(1)
            time_diff = self.final_time - datetime.datetime.now()

            self.debug_textbox.Text = "Time till publish: {}".format(time_diff)

            print(safety)
            output.set_width(300)
            output.set_height(300)
            safety += 1
            if safety > 10000000 or time_diff.total_seconds()  < 0:
                self.on_stop_watch = False
                



        self.publish()



    @EnneadTab.ERROR_HANDLE.try_catch_error
    def close_Click(self, sender, e):
        # This Raise() method launch a signal to Revit to tell him you want to do something in the API context
        self.on_stop_watch = False
        self.Close()


    def mouse_down_main_panel(self, sender, args):
        #print "mouse down"
        sender.DragMove()


    def publish(self):
        print("pretend copying")

        current_beta_folder = r"L:\4b_Applied Computing\01_Revit\04_Tools\08_EA Extensions\Published_Beta_Version\ENNEAD.extension"

        #current_beta_folder = r"L:\4b_Applied Computing\01_Revit\04_Tools\08_EA Extensions\Published_Beta_Version\test bad folder"

        shutil.rmtree(current_beta_folder)
        time.sleep(10)

        EnneadTab.VERSION_CONTROL._publish_Revit_source_code(publish_stable_version = False, publish_beta_version = True)

        EnneadTab.SOUNDS.play_sound("sound effect_mario stage clear.wav")

        self.debug_textbox.Text = "publish done...."






################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    # Let's launch our beautiful and useful form !
    try:
        modeless_form = schedule_publish_ModelessForm()
        ENNEAD_LOG.use_enneadtab(coin_change = 20, tool_used = __title__.replace("\n", " "), show_toast = True)
    except:
        print (traceback.format_exc())
