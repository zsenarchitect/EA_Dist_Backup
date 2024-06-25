

import System # pyright: ignore
import Rhino # pyright: ignore
import Rhino # pyright: ignore.UI
import rhinoscriptsyntax as rs

import Eto # pyright: ignore
import Eto # pyright: ignore.Drawing as drawing
import Eto # pyright: ignore.Forms as forms

import scriptcontext as sc
import sys
sys.path.append("..\\..\\lib")

import EnneadTab
import os
import fnmatch

import itertools
flatten = itertools.chain.from_iterable
graft = itertools.combinations

print("tell_a_joke_with_form.py is loaded")

# make modal dialog
class DadJokeDialog(Eto.Forms.Dialog[bool]):
    # Initializer
    def __init__(self, title, main_text,  sub_text,  self_destruct, button_name , width, height):
        # Eto initials
        self.Title = title
        self.Resizable = True
        self.Padding = Eto.Drawing.Padding(5)
        self.Spacing = Eto.Drawing.Size(5, 5)
        self.Icon = Eto.Drawing.Icon(r"L:\4b_Applied Computing\03_Rhino\12_EnneadTab for Rhino\Source Codes\lib\ennead-e-logo.png")
        #self.Bounds = Eto.Drawing.Rectangle()
        self.height = height
        self.width = width
        self.self_destruct = self_destruct
        self.main_text = main_text
        self.sub_text = sub_text
        self.Button_Name = button_name




        # initialize layout
        layout = Eto.Forms.DynamicLayout()
        layout.Padding = Eto.Drawing.Padding(5)
        layout.Spacing = Eto.Drawing.Size(5, 5)

        layout.AddSeparateRow(None, self.CreateLogoImage())

        # add message
        layout.BeginVertical()
        layout.AddRow(self.CreateMainTextBar())
        layout.EndVertical()

        layout.BeginVertical()
        layout.AddRow(self.CreateMessageBar())
        layout.EndVertical()


        layout.AddSpace()
        layout.AddSeparateRow(self.Create_setting_label())
        layout.AddSeparateRow(*self.create_setting_buttons())

        # add buttons
        layout.BeginVertical()
        layout.AddSpace()
        layout.AddRow(*self.CreateButtons())
        layout.EndVertical()

        layout.Width = self.width
        layout.Height = self.height

        # set content
        self.Content = layout
        
        EnneadTab.RHINO.RHINO_UI.apply_dark_style(self)

        return
        if self.self_destruct:
            self.count_down(self.self_destruct)


    def count_down(self, life_span):
        import time
        for i in range(int(life_span)):
            time.sleep(i )
            print (int(life_span) - i)



    def CreateLogoImage(self):
        self.logo = Eto.Forms.ImageView()

        self.FOLDER_PRIMARY = r"L:\4b_Applied Computing\00_Asset Library"
        self.FOLDER_APP_IMAGES = r"{}\Database\app images".format(self.FOLDER_PRIMARY)
        self.LOGO_IMAGE = r"{}\Ennead_Architects_Logo.png".format(self.FOLDER_APP_IMAGES)
        temp_bitmap = Eto.Drawing.Bitmap(self.LOGO_IMAGE)
        self.logo.Image = temp_bitmap.WithSize(200,30)
        return self.logo

    def CreateMainTextBar(self):
        self.main_msg = Eto.Forms.Label()
        self.main_msg.Text = self.main_text
        self.main_msg.Font = Eto.Drawing.Font("Arial", 20)
        return self.main_msg

    # create message bar function
    def CreateMessageBar(self):
        self.msg = Eto.Forms.Label()
        self.msg.Text = self.sub_text
        self.msg.Font = Eto.Drawing.Font("Arial", 12)
        return self.msg
        #self.msg.HorizontalAlignment = Eto.Forms.HorizontalAlignment.Left

    def Create_setting_label(self):
        self.setting_label = Eto.Forms.Label()
        self.setting_label.Text = "The initiation for EnneadTab Talkie takes a few seconds. So it is better to leave it running in the background. Do not quickly flip on and off for the swicth.\nWhen the button is green light, it will try to read out.\nWhen it is grey, it is will not read."
        self.setting_label.Font = Eto.Drawing.Font("Arial", 8)
        return self.setting_label
        #self.msg.HorizontalAlignment = Eto.Forms.HorizontalAlignment.Left


    def CreateButtons(self):
        """
        Creates buttons for either print the selection result
        or exiting the dialog
        """
        user_buttons = []

        self.btn_Run = Eto.Forms.Button()
        self.btn_Run.Text = self.Button_Name
        self.btn_Run.Click += self.btn_Run_Clicked
        user_buttons.append(self.btn_Run)

        self.btn_Cancel = Eto.Forms.Button()
        self.btn_Cancel.Text = "Cancel"
        self.btn_Cancel.Click += self.btn_Cancel_Clicked
        return user_buttons


        user_buttons.extend([ None, self.btn_Cancel])
        return user_buttons


    def create_setting_buttons(self):
        """
        Creates buttons for either print the selection result
        or exiting the dialog
        """
        user_buttons = []

        self.btn_audio_setting = Eto.Forms.Button()
        self.btn_audio_setting.Text = "Click to initate EnneadTab Talkie."
        self.btn_audio_setting.Click += self.btn_audio_Clicked
        self.btn_audio_setting.Image = Eto.Drawing.Bitmap(r"{}\checked_toggle_off.png".format(__file__.split(r"\tell_a_joke")[0]))
        self.is_reading = False
        self.btn_audio_setting.ImagePosition = Eto.Forms.ButtonImagePosition.Left#behind text
        user_buttons.append(self.btn_audio_setting)

        user_buttons.append(None)
        self.btn_Run = Eto.Forms.Button()
        self.btn_Run.Text = "Give me another one.."
        self.btn_Run.Click += self.btn_refresh_Clicked
        user_buttons.append(self.btn_Run)
        return user_buttons




    # function to run when call at button click
    def RunScript(self):
        # return selected items
        print ("Something important")




    # event handler handling clicking on the 'run' button
    def btn_Run_Clicked(self, sender, e):
        # close window after double click action. Otherwise, run with error
        self.Close(True)
        self.RunScript()

    def btn_audio_Clicked(self, sender, e):
        # close window after double click action. Otherwise, run with error
        self.is_reading = not self.is_reading


        if self.is_reading:
            self.btn_audio_setting.Text = "Status: Reading it on EnneadTab Talkie."
            EnneadTab.SPEAK.speak(self.msg.Text)
            self.btn_audio_setting.Image = Eto.Drawing.Bitmap(r"{}\checked_toggle_on.png".format(__file__.split(r"\tell_a_joke")[0]))
        else:
            self.btn_audio_setting.Text = "Status: Will not read."
            self.btn_audio_setting.Image = Eto.Drawing.Bitmap(r"{}\checked_toggle_off.png".format(__file__.split(r"\tell_a_joke")[0]))

    def btn_refresh_Clicked(self, sender, e):
        # close window after double click action. Otherwise, run with error

        self.msg.Text = EnneadTab.FUN.JOKES.give_me_a_joke(talk = False)
        if self.is_reading:
            EnneadTab.SPEAK.speak(self.msg.Text, force_talk = True)


    # event handler handling clicking on the 'cancel' button
    def btn_Cancel_Clicked(self, sender, e):
        self.Close(False)



def show_DadJokeDialog(title = "EnneadTab",
                            main_text = "",
                            sub_text = "",
                            self_destruct = None,
                            button_name = "Ok..enough...",
                            width = 500,
                            height = 200):



    dlg = DadJokeDialog(title, main_text, sub_text, self_destruct, button_name, width, height)
    rc = Rhino.UI.EtoExtensions.ShowSemiModal(dlg, Rhino.RhinoDoc.ActiveDoc, Rhino.UI.RhinoEtoApp.MainWindow)

    if (rc):



        print("User clicked primary button")
        return True

    else:
        print("Dialog did not run")
        return None


def tell_a_joke():


    main_text = "Dad Joke of the day..."
    show_DadJokeDialog(main_text = main_text, sub_text = EnneadTab.FUN.JOKES.give_me_a_joke(talk = False), height = 300)


@EnneadTab.ERROR_HANDLE.try_catch_error
def tell_a_joke_with_form():
    import traceback
    try:
        tell_a_joke()


    except Exception as e:

        error =  traceback.format_exc()
        print(error)

######################  main code below   #########
if __name__ == "__main__":
    tell_a_joke_with_form()
