#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Virtual achievement system that tracks your productivity and EnneadTab usage. This floating window displays your current MiniBank balance and leaderboard ranking, celebrating your contributions to the firm's digital ecosystem. Earn coins through regular tool usage, submitting bug reports, and helping colleagues. Perfect for encouraging healthy competition while building a culture of technology adoption."
__title__ = "MiniBank"
__context__ = "zero-doc"
__tip__ = True

from pyrevit.forms import WPFWindow
# from pyrevit import forms #
from pyrevit import script #


import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
from EnneadTab import ERROR_HANDLE, SOUND, NOTIFICATION, LOG, USER, ENVIRONMENT
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_FORMS
import traceback

uidoc = REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()
__persistentengine__ = True







# A simple WPF form used to call the ExternalEvent
class MiniBank(WPFWindow):
    """
    Simple modeless form sample
    """

    def pre_actions(self):


        return


    @ERROR_HANDLE.try_catch_error()
    def __init__(self):
        self.pre_actions()

        xaml_file_name = "MiniBank.xaml" ###>>>>>> if change from window to dockpane, the top level <Window></Window> need to change to <Page></Page>
        WPFWindow.__init__(self, xaml_file_name)

        self.title_text.Text = "EnneadTab MiniBank"

        self.sub_text.Text = "The moment of truth... Let's see your debts!"


        self.Title = "EnneadTab MiniBank UI"

        self.set_image_source(self.logo_img, "{}\icon_logo_dark_background.png".format(ENVIRONMENT.IMAGE_FOLDER))
        self.set_image_source(self.duck_img, "happy_duck.png")
        self.manual_click = 0


        self.Show()
        self.display_ranking()



    @ERROR_HANDLE.try_catch_error()
    def display_ranking(self):
        LEGACY_LOG.print_leader_board()
        
    @ERROR_HANDLE.try_catch_error()
    def bank_manager_Click(self, sender, e):
        if not USER.IS_DEVELOPER:
            REVIT_FORMS.notification(main_text = "This function is only available to Sen Zhang.")
            return

        LEGACY_LOG.manual_transaction()
    
    @ERROR_HANDLE.try_catch_error()
    def check_account_click(self, sender, e):

        LEGACY_LOG.print_history()
        
    @ERROR_HANDLE.try_catch_error()
    def manual_coin_Click(self, sender, e):
        self.manual_click += 1
        

        if self.manual_click % 10 == 0:
            NOTIFICATION.messenger(main_text = " +1UP\n经验+1")
            SOUND.play_sound("sound_effect_mario_1up.wav")
            return
        NOTIFICATION.messenger(main_text = " +$1\n金钱+1")
        SOUND.play_sound("sound_effect_mario_coin.wav")
    
    
    @ERROR_HANDLE.try_catch_error()
    def clear_data_click(self, sender, e):
        LEGACY_LOG.clear_user_data()
        NOTIFICATION.messenger(main_text = "Data has been cleared.")
    
    @ERROR_HANDLE.try_catch_error()
    def close_Click(self, sender, e):
        # This Raise() method launch a signal to Revit to tell him you want to do something in the API context
        self.Close()
        self.update_maunal_coin()

    def mouse_down_main_panel(self, sender, args):
        #print "mouse down"
        sender.DragMove()


    def update_maunal_coin(self):
        my_name = LEGACY_LOG.get_current_user_name()
        data = LEGACY_LOG.get_data_by_name(my_name)
        current_money = data["money"]
        change = self.manual_click

        data["money"] += int(change)
        LEGACY_LOG.set_data_by_name(my_name, data)



    

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def main():
    MiniBank()
################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    main()
