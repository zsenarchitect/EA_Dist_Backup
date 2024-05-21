#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Fire ChatGPT Revit UI."
__title__ = "Fire Chat GPT"

from pyrevit import script
from pyrevit import forms

import time


from Autodesk.Revit.UI import IExternalEventHandler, ExternalEvent
from Autodesk.Revit.Exceptions import InvalidOperationException
from pyrevit.forms import WPFWindow
# from pyrevit import forms #
from pyrevit import script #
# from pyrevit import revit #
import EA_UTILITY

from EnneadTab import SOUNDS, FOLDER, ERROR_HANDLE
import traceback

from Autodesk.Revit import DB 
import random
# from Autodesk.Revit import UI
uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document
__persistentengine__ = True


#@ERROR_HANDLE.try_catch_error
def clock_work(window):
    current_text = window.debug_textbox.Text
    max_wait = 20
    wait = 0
    while True:
        if wait > max_wait:
            break
        wait += 1
        deco = "." * (wait % 5)
        #print deco
        if not window.simple_event_handler.OUT:
            window.debug_textbox.Text = current_text + "\n\nThinking{}".format(deco)

        else:
            window.debug_textbox.Text = window.simple_event_handler.OUT
            break
        time.sleep(1)

    window.simple_event_handler.OUT = None

def get_api_key():

    file_path = r"L:\4b_Applied Computing\01_Revit\04_Tools\08_EA Extensions\Project Settings\Misc\EA_API_KEY.json"



    data = EA_UTILITY.read_json_as_dict(file_path)
    return data["chatgpt_api_key"]


def get_conversation(input):
    #print "aaaaaaaaa"
    new_prompt = input
    #print new_prompt

    session_token = get_api_key()
    #print session_token


    human_name = "You: "
    #print human_name

    file_name = "EA_COPILOT.json"
    #print file_name

    dump_folder = EA_UTILITY.get_EA_local_dump_folder()

    #print dump_folder
    file_path = "{}\{}".format(dump_folder, file_name)
    #print file_path
    if EA_UTILITY.is_file_exist_in_folder(file_name, dump_folder):
        old_record = EA_UTILITY.read_json_as_dict(file_path)
        old_record["conversation_history"] += "\n{}{}".format(human_name, new_prompt)
        old_record["direction"] = "input"

        EA_UTILITY.save_dict_to_json(old_record, file_path)
        #print "CCCCCCCC"

    else:
        data = dict()
        data["ai_name"] = "EnneadTab Copilot: "
        data["human_name"] = human_name
        data["session_token"] = session_token
        data["key_prompt"] = "The following is a conversation with an AI assistant called '{}' for answering problems in Rhino and Revit. The assistant is helpful, creative, clever, friendly and very funny. Also the reponse line should be immediately below the user question without gap line\n\n".format(data["ai_name"].replace(":", ""))
        data["conversation_history"] = "{}{}{}".format(data["key_prompt"], data["human_name"], new_prompt)
        data["direction"] = "input"
        EA_UTILITY.save_dict_to_json(data, file_path)
        #print "DDDDDDDDD"
        #"The following is a conversation with an AI assistant for problems in Rhino and Revit. The assistant is helpful, creative, clever, friendly and very funny.\n\nYou: How do I create a sheet in Revit\nEnneadTab Copilot:"

    max_attempt = 20
    run_exe()
    attempt = 0
    while True:
        #print "Thinking..."

        if attempt > max_attempt:
            print("cannot get response")
            break
        attempt += 1
        time.sleep(1)
        record = EA_UTILITY.read_json_as_dict(file_path)

        if record["direction"] == "output":
            #print record["conversation_history"].split(record["key_prompt"])[-1]
            #print "Figured out!!!!!!!!!!!!!!"
            SOUNDS.play_sound("sound effect_popup msg3.wav")
            return record["conversation_history"].split(record["key_prompt"])[-1]


# Create a subclass of IExternalEventHandler
class conversation_SimpleEventHandler(IExternalEventHandler):
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
                self.OUT = self.do_this(self.kwargs)
            except:
                self.OUT =  traceback.format_exc()
                print ("failed")
        except InvalidOperationException:
            # If you don't catch this exeption Revit may crash.
            print ("InvalidOperationException catched")

    def GetName(self):
        return "simple function executed by an IExternalEventHandler in a Form"





# A simple WPF form used to call the ExternalEvent
class chatGPT_modelessForm(WPFWindow):
    """
    Simple modeless form sample
    """
    def initiate_form(self):
        sample = ["How do I add a new level in Revit?",
                    "Why Rhino viewport flicker when I zoom in and out?",
                    "How to create curtain panel family in revit?",
                    "Write me a peom for Revit in 14th century Sonnets",
                    "Is NYC bigger than D.C.?",
                    "What is the shortcut to unlock all in Rhino?",
                    "What is the difference between curtain wall and window wall?",
                    "Give me 10 ideas for architect office happy hour",
                    "what is the meaning of life as architects?",
                    "How do you make ginger bread in Frank Gahry style?",
                    "How to create furnichure schedule in Revit?",
                    "Give me 10 ideas to prepare New Year Dinner for a lot of architects?",
                    "Write me an email to complain about the client without sounding angery, the problem is that the client is not paying us."]
        self.user_input_textbox_1.Text = random.choice(sample)



    def pre_actions(self):


        #print "doing preaction"
        # Now we need to make an instance of this handler. Moreover, it shows that the same class could be used to for
        # different functions using different handler class instances
        self.simple_event_handler = conversation_SimpleEventHandler(get_conversation)
        self.clock_event_handler = conversation_SimpleEventHandler(clock_work)

        # We now need to create the ExternalEvent
        self.ext_event = ExternalEvent.Create(self.simple_event_handler)
        self.ext_event_clock = ExternalEvent.Create(self.clock_event_handler)
        #print "preaction done"
        #print self.simple_event_handler
        #print self.simple_event_handler.kwargs
        #print self.ext_event
        #print "-------"
        return

    def __init__(self):
        self.pre_actions()
        self.script_location = FOLDER.get_folder_path_from_path(__file__)
        xaml_file_name = "{}\EA_Copilot_ModelessForm.xaml".format(self.script_location) ###>>>>>> if change from window to dockpane, the top level <Window></Window> need to change to <Page></Page>
        WPFWindow.__init__(self, xaml_file_name)

        self.title_text.Text = "EnneadTab Copilot (ft. openAI)"

        self.sub_text.Text = "Use openai's ChatGPT to answer all kinds of questions you might have in Revit and Rhino, or anything else in life.  Note: Result not garanteed to be correct for Architect softwares becasue the database is so little compared to others field, but still interesting in many ways.\n\nIf there is a error on getting AI to work, try 'Clear Conversation' and ask again."


        self.Title = "EnneadTab Copilot"
        #self.Width = 800
        self.Height = 1000
        self.set_image_source(self.logo_img, "{}\logo_V_light.png".format(self.script_location))
        self.initiate_form()
        self.get_previous_conversation()
        self.Show()


    def get_previous_conversation(self):
        file_name = "EA_COPILOT.json"
        #print file_name

        dump_folder = EA_UTILITY.get_EA_local_dump_folder()

        #print dump_folder
        file_path = "{}\{}".format(dump_folder, file_name)
        #print file_path
        if EA_UTILITY.is_file_exist_in_folder(file_name, dump_folder):
            record = EA_UTILITY.read_json_as_dict(file_path)
            self.debug_textbox.Text = record["conversation_history"].split(record["key_prompt"])[-1]


    def ask_Click(self, sender, e):
        # This Raise() method launch a signal to Revit to tell him you want to do something in the API context

        self.generic_click(self.user_input_textbox_1.Text)
        #self.get_conversation(self, self.user_input_textbox_1.Text)
        pass

    def clear_history_Click(self, sender, e):
        file_name = "EA_COPILOT.json"
        dump_folder = EA_UTILITY.get_EA_local_dump_folder()
        file_path = "{}\{}".format(dump_folder, file_name)
        EA_UTILITY.remove_exisitng_file_in_folder(dump_folder, file_name)
        self.debug_textbox.Text = ''
        self.simple_event_handler.OUT = None
        pass

    def mouse_move_event(self, sender, args):
        #print "mouse down"
        #self.debug_textbox.Text = self.simple_event_handler.OUT
        pass

    def mouse_down_main_panel(self, sender, args):
        #print "mouse down"
        sender.DragMove()


    def close_Click(self, sender, args):
        #print "mouse down"
        self.Close()
        #self.debug_textbox.Text = self.simple_event_handler.OUT
        pass


    @ERROR_HANDLE.try_catch_error
    def clock_work(self):
        current_text = self.debug_textbox.Text
        max_wait = 200
        wait = 0
        while True:
            if wait > max_wait:
                break
            wait += 1
            deco = "." * (wait % 5)
            print(deco)
            if not self.simple_event_handler.OUT:
                self.debug_textbox.Text = current_text + "\n\nThinking{}".format(deco)

            else:
                self.debug_textbox.Text = self.simple_event_handler.OUT
                break
            #time.sleep(1)

        self.simple_event_handler.OUT = None


    def generic_click(self, keyword):
        #print "Clicking " + keyword
        self.simple_event_handler.kwargs = keyword
        self.ext_event.Raise()
        self.clock_event_handler.kwargs = self
        self.ext_event_clock.Raise()
        #print "bbbbbbbb"
        res = self.simple_event_handler.OUT

        if res:
            #print res
            self.debug_textbox.Text = res
        else:
            self.debug_textbox.Text = "Thinking..."








def main_manual():
    sample = ["How do I add a new level in Revit?",
                "Why Rhino viewport flicker when I zoom in and out?",
                "How to create curtain panel family in revit?"]

    helper_text = "Ask anything for Revit and Rhino. The openAI will try its best to answer."
    new_prompt = forms.ask_for_string(default = random.choice(sample), prompt = helper_text, title = "EnneadTab Copilot")
    if not new_prompt:
        return



    session_token = "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"


    human_name = "You:"

    file_name = "EA_COPILOT.json"
    dump_folder = EA_UTILITY.get_EA_local_dump_folder()
    file_path = "{}\{}".format(dump_folder, file_name)
    if EA_UTILITY.is_file_exist_in_folder(file_name, dump_folder):
        old_record = EA_UTILITY.read_json_as_dict(file_path)
        old_record["conversation_history"] += "\n{}{}".format(human_name, new_prompt)
        old_record["direction"] = "input"

        EA_UTILITY.save_dict_to_json(old_record, file_path)

    else:
        data = dict()
        data["ai_name"] = "EnneadTab Copilot:"
        data["human_name"] = human_name
        data["session_token"] = session_token
        data["key_prompt"] = "The following is a conversation with an AI assistant called '{}' for answering problems in Rhino and Revit. The assistant is helpful, creative, clever, friendly and very funny. Also the reponse line should be immediately below the user question without gap line\n\n".format(data["ai_name"].replace(":", ""))
        data["conversation_history"] = "{}{}{}".format(data["key_prompt"], data["human_name"], new_prompt)
        data["direction"] = "input"
        EA_UTILITY.save_dict_to_json(data, file_path)
        #"The following is a conversation with an AI assistant for problems in Rhino and Revit. The assistant is helpful, creative, clever, friendly and very funny.\n\nYou: How do I create a sheet in Revit\nEnneadTab Copilot:"

    max_attempt = 20
    run_exe()
    attempt = 0
    while True:
        print("Thinking...")

        if attempt > max_attempt:
            print("cannot get response")
            break
        attempt += 1
        time.sleep(1)
        record = EA_UTILITY.read_json_as_dict(file_path)

        if record["direction"] == "output":
            print(record["conversation_history"].split(record["key_prompt"])[-1])
            break



def run_exe():
    #exe_location = "L:\\4b_Applied Computing\\03_Rhino\\12_EnneadTab for Rhino\Source Codes\lib\EA_TEXT2SPEECH\EA_TEXT2SPEECH.exe"
    exe_location = r"L:\\4b_Applied Computing\\01_Revit\\04_Tools\\08_EA Extensions\Project Settings\Exe\EA_CHATGPT\EA_CHATGPT.exe - Shortcut"


    try:
        EA_UTILITY.open_file_in_default_application(exe_location)
        return
    except Exception as e:
        pass

    try:
        EA_UTILITY.open_file_in_default_application(exe_location.replace(" - Shortcut", ""))
        return
    except Exception as e:
        pass


def main():
    output = script.get_output()
    output.close_others()
    try:
        modeless_form = chatGPT_modelessForm()
    except:
        print (traceback.format_exc())

if __name__ == "__main__":
    main()
