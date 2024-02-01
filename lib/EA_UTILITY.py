#!/usr/bin/python
# -*- coding: utf-8 -*-


try:
    import inspect
    import traceback
 
    def get_caller_file_path():
        stack = inspect.stack()
        
        caller_frame = stack[1]
        # frame,filename,line_number,function_name,lines,index = inspect.stack()[1]
        caller_file_path = caller_frame[1]  # The filename is the second element in the tuple
        OUT = ""
        for x in inspect.stack():
            OUT += "{}\n".format(x)
        return OUT

    
    
    # import EnneadTab
    # EnneadTab.EMAIL.email(sender_email=None,
    #                     receiver_email_list=["szhang@ennead.com"],
    #                     subject="EnneadTab Auto Email: EA_UTILITY Detected",
    #                     body="EA_UTILITY is called from {}".format(get_caller_file_path()),
    #                     body_folder_link_list=None,
    #                     body_image_link_list=None,
    #                     attachment_list=None,
    #                     schedule_time=None)
except Exception as e:
    from os import environ
    if environ["USERPROFILE"] == r"C:\Users\szhang":
        print ("EA_UTITLITY detected")
        print( traceback.format_exc())
finally:
    pass
    # print ("EA_UTILITY loaded, this should not happen!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")



try:
    from Autodesk.Revit import DB
except:
    print "Cannot import DB module"

"""
misc
"""
""""""
def random_speak(lines, chance = 1.0):
    import random
    if random.random() <= chance:
        random.shuffle(lines)
        speak(lines[0])

""""""
def warn_revit_session_too_long(non_interuptive = True):
    import ENNEAD_LOG
    from pyrevit.coreutils import envvars
    try:

        if time_has_passed_too_long(envvars.get_pyrevit_env_var("APP_UPTIME"), tolerence = 60 * 60 * 24):
            #EA_UTILITY.dialogue(main_text = "This Revit session has been running for more than 24Hours.\n\nPlease consider restarting Revit to release memory and improve performance.")
            ENNEAD_LOG.session_too_long()
            if non_interuptive:
                show_toast(message = "That is just bad..", title = "Your Revit seesion has been running for more than 24Hours.")
            else:
                modeless_form_no_func(main_text = "This Revit session has been running for more than 24Hours.\nPaying $300 EA Coins.", sub_text = "Please consider restarting Revit to release memory and improve performance.", window_width = 500, window_height = 300, self_destruct = 60)
    except Exception as e:
        print_note("cannot warn too long session")
        print_traceback()
        pass

""""""
def try_catch_error(func):
    import traceback
    def wrapper(*args, **kwargs):

        print_note ("Wrapper func for EA Log -- Begin:")
        try:
            # print "main in wrapper"
            out = func(*args, **kwargs)
            print_note ( "Wrapper func for EA Log -- Finish:")
            return out
        except Exception as e:
            print_note ( str(e))
            print_note (  "Wrapper func for EA Log -- Error: " + str(e)  )
            error = traceback.format_exc()
            error_file = "{}\error_log.txt".format(get_user_folder())
            with open(error_file, "w") as f:
                f.write(error)
            open_file_in_default_application(error_file)
    return wrapper


def tool_has_ended():
    play_sound()
    return

    import webbrowser
    webbrowser.open("https://www.youtube.com/watch?v=jfKfPfyJRdk")

def zombie_function():
    print "B"


def is_owned(element):
    def get_good_name(element):
        if isinstance(element, DB.View):
            return element.Name
        if hasattr(element, "Name"):
            return element.Name

        return None


    from pyrevit import revit
    eh = revit.query.get_history(element)
    #print eh.owner
    if len(eh.owner) == 0:
        return False
    elif eh.owner == revit.doc.Application.Username:
        return False
    else:
        if get_good_name(element) is not None:
            print "{}, {} Owned by {}".format(element.Id, get_good_name(element), eh.owner)
        else:
            print "{} Owned by {}".format(element.Id, eh.owner)
        return True

def get_element_full_info(element, output = None):
    """
    [category, level , type name, workset] if it can
    """
    doc = element.Document
    category = element.Category.Name
    try:
        level = doc.GetElement(element.LevelId).Name
    except:
        if element.ViewSpecific:
            view = doc.GetElement(element.OwnerViewId )
            if output:
                level = "{}".format(output.linkify(view.Id, title = view.Name))
            else:
                level =  view.Name
        else:
            level = ""

    try:
        family_name = element.FamilyName
    except:
        family_name = ""
    try:
        type_name = element.LoopupParameter("Type Name").AsString()
    except:
        try:
            type_name = element.Name
        except:
            type_name = ""
    info = "[{},{},{},{}]".format(category, level, family_name, type_name)
    return info


""""""
def pick_shared_para_definition(doc):
    from pyrevit import forms
    class MyOption(forms.TemplateListItem):
        @property
        def name(self):
            return "{} : {} ({})".format(self.item[0], \
                                        self.item[1].Name, \
                                        self.item[1].ParameterType)


    shared_para_file = doc.Application.OpenSharedParameterFile()
    options = []
    for definition_group in shared_para_file.Groups:
        #print "*"*10
        #print definition_group.Name
        for definition in definition_group.Definitions:

            options.append(MyOption((definition_group.Name, definition)))


    options.sort(key = lambda x:x.name)
    sel = forms.SelectFromList.show(options,
                                    multiselect = False,
                                    title = "Pick shared parameter.",
                                    button_name= "Let's go!"
                                    )
    if not sel:
        return None
    return sel[1]


""""""
def get_formatted_current_time(show_user_name = True,
                                show_year = True,
                                show_month = True,
                                show_day = True,
                                show_hour = True,
                                show_minute = True,
                                show_secound = True,
                                show_weekday = True,
                                use_unix_time = False):
    import time
    if show_user_name:
        user_name = get_application().Username + "_"
    else:
        user_name = ""
    localtime = time.asctime( time.localtime(time.time()) ).replace(":","-")

    localtime = time.localtime()
    result = time.strftime("%I:%M:%S %p", localtime).replace(":","-")
    if use_unix_time:
        result += "_{}".format(time.time())
    return "{}{}".format(user_name, result)

    pass



""""""
def time_has_passed_too_long(unix_time, tolerence = 60 * 30):
    "tolerence in seconds, default 60s x 30 = 30mins"
    import time
    current_time = time.time()
    try:
        if float(current_time) - float(unix_time) > tolerence:
            return True
        return False
    except Exception as e:
        print "Failed becasue: {}".format(e) 

def mark_time():
    import time
    from pyrevit.coreutils import envvars
    envvars.set_pyrevit_env_var("MARKED_TIME", time.time())

def time_since_last_marked_time():
    marked_time = envvars.get_pyrevit_env_var("MARKED_TIME"),
    return time.time() - marked_time

def string_contain_keywords(string, keyword_list, ignore_case = True):
    for keyword in keyword_list:
        if ignore_case:
            keyword = keyword.lower()
            string = string.lower()

        if keyword in string:
            return True
    return False




def almost(a,b):
    if abs(a - b) < 0.000001:
        return True
    return False

""""""
def dim_text(added_text):
    app = get_application()
    doc = __revit__.ActiveUIDocument.Document
    uidoc = __revit__.ActiveUIDocument
    selection_ids = uidoc.Selection.GetElementIds ()
    selection = [doc.GetElement(x) for x in selection_ids]

    t = DB.Transaction(doc, "Dim segement with [{}]".format(added_text))
    t.Start()
    for dim in selection:
        #print dim.NumberOfSegments
        if dim.NumberOfSegments == 0:
            value = int(dim.ValueString)
            dim.Below = added_text
            continue

        for dim_seg in dim.Segments:
            value = int(dim_seg.ValueString)
            dim_seg.Below = added_text

    t.Commit()


""""""
def get_solid_fill_pattern_id(doc):
    fill_patterns = DB.FilteredElementCollector(doc).OfClass(DB.FillPatternElement).WhereElementIsNotElementType().ToElements()
    for fill_pattern in fill_patterns:
        if fill_pattern.GetFillPattern().IsSolidFill:
            return fill_pattern.Id
    return None

""""""
def random_loading_message():
    import random
    with open('{}\FUN\LOADING_SCREEN_MESSAGE.txt'.format(get_folder_path_from_path(__file__)), "r") as f:
        lines = f.readlines()
    random.shuffle(lines)
    return lines[0].replace("\n", "")

""""""
def pick_emoji_text():
    import io
    with io.open('{}\FUN\EMOJI_TEXT.txt'.format(get_folder_path_from_path(__file__)), "r", encoding = "utf8") as f:
        lines = f.readlines()
    lines = [x.replace("\n", "") for x  in lines if x != "\n"]
    from pyrevit import forms
    sel = forms.SelectFromList.show(lines, select_multiple = False, title = "Go wild")
    if not sel:
        return

    forms.ask_for_string(default = sel,
                        prompt = 'Copy below text to anywhere, maybe SheetName or Schedule',
                        title = 'pick_emoji_text')


""""""
def play_sound(file = "sound effect_mario message.wav"):
    folder = 'L:\\4b_Applied Computing\\03_Rhino\\12_EnneadTab for Rhino\Source Codes\Fun\sound effects'


    try:
        path = folder + "\\" + file

        from System.Media import SoundPlayer
        sp = SoundPlayer()
        sp.SoundLocation = path
        sp.Play()
    except:
        print_note("Cannot play Sound")
    """
    import sys
    sys.path.append(r'L:\4b_Applied Computing\03_Rhino\12_EnneadTab for Rhino\Source Codes\lib')
    import EA_SOUND
    EA_SOUND.play_sound(file)
    """

def text_to_speech_generate(title, mytext, is_testing = False, use_Chinese = False):
    """ failed"""
    return

    try:
        import sys
        sys.path.append(r'L:\4b_Applied Computing\03_Rhino\12_EnneadTab for Rhino\Source Codes\lib')
        sys.path.append(r'L:\4b_Applied Computing\03_Rhino\12_EnneadTab for Rhino\Dependency Modules')
        import EA_TEXT2SPEECH
        import urllib3
        import six
        """
        title = "12"
        mytext = 'Today, Revit has finished syncing document Bilibili HQ_N3. What do you want to do next?'
        """
        EA_TEXT2SPEECH.text_to_speech_generate(title, mytext, is_testing = False, use_Chinese = False)
    except:
        print_note("Cannot play text to speech")

def text_to_speech_play(title):
    """failed"""
    return

    try:
        import sys
        sys.path.append(r'L:\4b_Applied Computing\03_Rhino\12_EnneadTab for Rhino\Source Codes\lib')
        sys.path.append(r'L:\4b_Applied Computing\03_Rhino\12_EnneadTab for Rhino\Dependency Modules')
        import EA_TEXT2SPEECH
        import urllib3
        import six
        """
        title = "12"
        """
        EA_TEXT2SPEECH.text_to_speech_play(title)
    except:
        print_note("Cannot play text to speech")

""""""
def speak(text, language = 'en', accent = 'com'):
    """
    #language = 'zh-CN'
    #language = 'zh-TW'
    #language = 'en'

    #accent = 'co.uk'
    #accent = 'co.in'
    #accent = 'com'
    """
    return # disable this old func, no attempt to fix
    if is_file_exist_in_folder("EA_TALKIE_KILL.kill", get_EA_local_dump_folder()):
        return


    if text:
        data = dict()
        data["text"] = text
        data["language"] = language
        data["accent"] = accent
        file_name = "EA_Text2Speech.json"
        dump_folder = get_EA_local_dump_folder()
        file_path = "{}\{}".format(dump_folder, file_name)
        save_dict_to_json(data, file_path)

    import imp
    full_file_path = r'C:\Users\szhang\github\EnneadTab-for-Revit\ENNEAD.extension\Ennead.tab\Utility.panel\exe_1.stack\text2speech.pushbutton\TTS_script.py'
    if not is_SZ():
        full_file_path = remap_filepath_to_folder(full_file_path)
    ref_module = imp.load_source("TTS_script", full_file_path)

    ref_module.run_exe()

    """
    exe_location = "L:\\4b_Applied Computing\\03_Rhino\\12_EnneadTab for Rhino\Source Codes\lib\EA_TEXT2SPEECH\EA_TEXT2SPEECH.exe"

    try:
        open_file_in_default_application(exe_location)
    except Exception as e:
        print exe_location
        print str(e)
    """

""""""
def show_loading_screen(display_text, time = 2):
    text_source_file = "EA_LOADING_SCREEN_TEXT.json"
    file = "{}\{}".format(get_EA_local_dump_folder(), text_source_file)
    data = dict()
    data["text"] = display_text
    data["time"] = time# in seconds
    save_dict_to_json(data, file)
    loading_screen_exe = r"L:\4b_Applied Computing\03_Rhino\12_EnneadTab for Rhino\Source Codes\lib\EA_LOADING_SCREEN_EXE\make_loading_bar\make_loading_bar.exe"
    open_file_in_default_application(loading_screen_exe)

""""""
def merge_pdfs(combined_pdf_file_path, list_of_filepaths, reorder = False):
    if not list_of_filepaths or len(list_of_filepaths) == 0:
        return

    import sys
    sys.path.append(r'L:\4b_Applied Computing\03_Rhino\12_EnneadTab for Rhino\Dependency Modules')
    from PyPDF2 import PdfFileMerger




    merger = PdfFileMerger()

    if reorder:
        list_of_filepaths.sort()

    for filepath in list_of_filepaths:
        #print filepath
        merger.append(filepath)

    merger.write(combined_pdf_file_path)
    merger.close()


"""
UI interaction and output
"""

""""""
def print_note(string):
    from pyrevit import script
    show_note = False#false will not print any note
    show_note = True#true for debug mode
    show_note = is_SZ()
    if show_note:
        try:
            string = str(string)
            script.get_output().print_md( "***[DEBUG NOTE]***:{}".format(string))
        except Exception as e:
            pass
            # print "***[DEBUG NOTE]***:{}".format(string)
            # print "--Cannot use markdown becasue: {}".format(e)

""""""
def dialogue( title = "EnneadTab",
            main_text = "main_text",
            sub_text = None,
            options = None,
            footer_link = "http://www.ennead.com",
            footer_text = "EnneadTab",
            use_progress_bar = False,
            expended_content = None,
            extra_check_box_text = None,
            verification_check_box_text = None,
            icon = "shield"):

    """
    extra check box appear before commands options
    verification_check_box_text appear after commands options
    is activaed, the result of dialogue will return a tuple of two values.

    options = [["opt 1","description long long long long"], ["opt 2"]]   if options is a string, then used as main text, but if it is a list of two strings, the second string will be used as description. In either case, the command link will return main text


    TaskDialogIconNone,	No icon.
    TaskDialogIconShield,	Shield icon.
    TaskDialogIconInformation,	Information icon.
    TaskDialogIconError,	Error icon.
    TaskDialogIconWarning, Warning icon
    """
    def result_append_checkbox_result(res):
        try:
            extra_checkbox_status = main_dialog.WasExtraCheckBoxChecked ()
            return res, extra_checkbox_status #extra_checkbox_status:{}".format(extra_checkbox_status)
        except:
            pass
        try:
            verification_checkbox_status = main_dialog.WasVerificationChecked  ()

            return res , verification_checkbox_status #"#verification_checkbox_status:{}".format(verification_checkbox_status)
        except:
            pass
        return res


    """
    if not is_SZ():
        return
    """
    from Autodesk.Revit import UI
    main_dialog = UI.TaskDialog(title)
    main_dialog.MainInstruction = main_text
    main_dialog.MainContent = sub_text
    main_dialog.TitleAutoPrefix = False
    if footer_link is not None:
        #https://www.ennead.com/
        #http://usa.autodesk.com/adsk/servlet/index?siteID=123112&id=2484975
        main_dialog.FooterText = "<a href=\"{} \">".format(footer_link) + "{}</a>".format(footer_text)
    else:
        main_dialog.FooterText = footer_text

    if extra_check_box_text is not None:
        main_dialog.ExtraCheckBoxText  = extra_check_box_text
    else:
        if verification_check_box_text is not None:
            main_dialog.VerificationText   = verification_check_box_text
    main_dialog.ExpandedContent  = expended_content

    from pyrevit.coreutils import get_enum_values
    if options:
        clinks = get_enum_values(UI.TaskDialogCommandLinkId)
        max_clinks = len(clinks)
        for idx, cmd in enumerate(options):
            if idx < max_clinks:
                if isinstance(cmd, list):
                    main_dialog.AddCommandLink(clinks[idx], cmd[0], cmd[1])
                else:
                    main_dialog.AddCommandLink(clinks[idx], cmd)

    if icon == "shield":
        main_dialog.MainIcon = UI.TaskDialogIcon.TaskDialogIconShield
    elif icon == "warning":
        main_dialog.MainIcon = UI.TaskDialogIcon.TaskDialogIconWarning
    elif icon == "error":
        main_dialog.MainIcon = UI.TaskDialogIcon.TaskDialogIconError
    elif icon == "info":
        main_dialog.MainIcon = UI.TaskDialogIcon.TaskDialogIconInformation
    res = main_dialog.Show()


    if res == UI.TaskDialogResult.Close:
        res = "Close"
    if res == UI.TaskDialogResult.Cancel:
        res = "Cancel"


    if 'CommandLink' in str(res):
        tdresults = sorted([x for x in get_enum_values(UI.TaskDialogResult) if 'CommandLink' in str(x)])
        residx = tdresults.index(res)
        if isinstance(options[residx], list):
            res = options[residx][0]
        else:
            res = options[residx]


    return result_append_checkbox_result(res)

def dialogue_modeless( title = "EnneadTab",
                    main_text = "main_text",
                    sub_text = None):
    pass

def modeless_form(function = None,
                main_text = "template title",
                sub_text = "",
                window_title = "EnneadTab",
                button_name = "Run",
                self_destruct = 0):
    import MODELESS_FORM
    xmal_template = "Template_ModelessForm.xaml"
    xmal_template = remap_filepath_between_folder(xmal_template, new_folder_after_dot_extension = "lib")
    res = MODELESS_FORM.ModelessForm(xmal_template,
                                    main_text,
                                    sub_text,
                                    button_name,
                                    window_title,
                                    self_destruct,
                                    function)


""""""
def modeless_form_no_func(main_text = "template title",
                        sub_text = "",
                        window_title = "EnneadTab",
                        button_name = "Close",
                        self_destruct = 0,
                        window_width = 500,
                        window_height = 500):
    import MODELESS_FORM_NO_FUNC
    xmal_template = "Template_ModelessForm_NO_FUNC.xaml"
    xmal_template = remap_filepath_between_folder(xmal_template, new_folder_after_dot_extension = "lib")
    MODELESS_FORM_NO_FUNC.ModelessForm(xmal_template,
                                        main_text,
                                        sub_text,
                                        button_name,
                                        window_title,
                                        self_destruct,
                                        window_width,
                                        window_height)
""""""
def remap_filepath_to_folder(full_file_path):
    """
    remap  sccript path that point to Sen document---->to L drive
    """
    return full_file_path.replace(r"C:\Users\szhang\github\EnneadTab-for-Revit\ENNEAD.extension", r"L:\\4b_Applied Computing\\01_Revit\\04_Tools\\08_EA Extensions\Published\ENNEAD.extension")

def remap_filepath_between_folder(file_name, new_folder_after_dot_extension):
    from pyrevit import script
    bundle_path = script.get_bundle_file(file_name)
    #print bundle_path
    current_folder = bundle_path.split(".extension\\")[1].split(file_name)[0]
    bundle_path = bundle_path.replace(current_folder, new_folder_after_dot_extension + r"\\")
    #print bundle_path
    return bundle_path

""""""
def is_hate_toast():
    # need beeter way to looup setting
    dump_folder = get_EA_local_dump_folder()
    file_name = "EA_TOASTER_KILL.kill"
    filepath = "{}\{}".format(dump_folder, file_name)
    return is_file_exist_in_folder(file_name, dump_folder)

""""""
def show_toast(message = "",
                title = "Some title text",
                app_name = "EnneadTab Monitor",
                button_name = "click me",
                action_dict = {},
                image = None):

    """
    image if want to use cutomised image, use full path directly.
    """

    """
    click="https://eirannejad.github.io/pyRevit/",
    ...              actions={
    ...                  "Open Google":"https://google.com",
    ...                  "Open Toast64":"https://github.com/go-toast/toast"
    ...                  })
    """

    # action_dict = {}
    # action_dict["A"] = 10
    # action_dict["B"] = 20
    if is_hate_toast():
        return

    if image is None:
        # print_note("user did not assign an icon")
        from pyrevit import script
        filepath = script.get_bundle_file("ennead-e-logo.jpg")
        image = filepath.split(".extension")[0] + ".extension\lib\ennead-e-logo.png"
    else:
        backup_image = image[:]
        # print_note("input image path for icon = {}".format(image))
        from pyrevit import script
        try:

            main_folder = script.get_bundle_file("ennead-e-logo.jpg")
            #print image.split(".extension")
            if len(image.split(".extension")) > 1:
                # image_input = "C:\Users\szhang\github\EnneadTab 2.0\ENNEAD.extension\Ennead.tab\Tailor Shop.panel\misc1.stack\Proj 2135.pulldown\icon.png"
                # image_path = "C:\Users\szhang\github\EnneadTab 2.0\ENNEAD.extension\lib\surprised_face.png"
                image = main_folder.split(".extension")[0] + ".extension" + image.split(".extension")[1]
        except Exception as e:
            print "Toast Error: " + str(e)
            image = backup_image
            #print image
        # print_note("processed image path for icon = {}".format(image))


    from pyrevit import forms
    res = forms.toast(message, title = title, appid = app_name, icon = image, click = button_name, actions = action_dict)
    return res


def show_dockpanel():
    pass


def autosave_output(output = "output_window",
                    output_folder  = "output_folder"):
    pass


""""""
def email_error(traceback, tool_name, error_from_user, subject_line = "EnneadTab Auto Email Error Log"):

    import time
    t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.time())))
    body = "{}\nError happens on {}'s machine when running {}.\n\nDetail below:\n{}'".format(t, error_from_user, tool_name, traceback)
    email(sender_email = None,
            receiver_email_list = ["szhang@ennead.com"],
            subject = subject_line,
            body = body,
            body_folder_link_list = None,
            body_image_link_list = None,
            attachment_list = None,
            schedule_time = None)

""""""
def email(sender_email = None,
        receiver_email_list = None,
        subject = "EnneadTab Auto Email",
        body = None,
        body_folder_link_list = None,
        body_image_link_list = None,
        attachment_list = None,
        schedule_time = None):
    """sender email is not required for outlook approch
    schedule time is the desired time in uni seconds
    """


    if not receiver_email_list:
        return
    if isinstance(receiver_email_list, str):
        print "Prefer list but ok."
        receiver_email_list = receiver_email_list.rstrip().split(";")

    if not body:
        return

    body = body.replace("\n", "<br>")

    data = dict()
    data["sender_email"] = sender_email
    data["receiver_email_list"] = receiver_email_list
    data["subject"] = subject
    data["body"] = body
    data["body_folder_link_list"] = body_folder_link_list
    data["body_image_link_list"] = body_image_link_list
    data["attachment_list"] = attachment_list
    data["schedule_time"] = schedule_time


    file_name = "EA_EMAIL.json"
    dump_folder = get_EA_local_dump_folder()
    file_path = "{}\{}".format(dump_folder, file_name)
    save_dict_to_json(data, file_path)


    exe_location = "L:\\4b_Applied Computing\\03_Rhino\\12_EnneadTab for Rhino\Source Codes\lib\EA_EMAIL\EA_EMAIL.exe"

    try:
        open_file_in_default_application(exe_location)
    except Exception as e:
        print exe_location
        print str(e)

""""""
def old_send_email(contacts = ["address1", "address2"],
                subject = "subject",
                body = "body",
                attachment = "attachment"):




    def send_email_method_1():
        import win32com.client as win32
        outlook = win32.Dispatch('outlook.application')
        mail = outlook.CreateItem(0)
        mail.To = "zsenarchitect@gmail.com"
        mail.Subject = 'Message subject'
        mail.Body = 'Message body'
        mail.HTMLBody = '<h2>HTML Message body</h2>' #this field is optional


        '''
        # To attach a file to the email (optional):
        attachment  = "Path to the attachment"
        mail.Attachments.Add(attachment)
        '''

        mail.Send()


    def send_email_method_2():
        # Import smtplib for the actual sending function
        import smtplib

        # Import the email modules we'll need
        import email
        #from email.message import EmailMessage

        """
        # Open the plain text file whose name is in textfile for reading.
        with open(textfile) as fp:
            # Create a text/plain message
            msg = EmailMessage()
            msg.set_content(fp.read())
        """
        msg = email.message.EmailMessage()
        msg.set_content(body)

        # me == the sender's email address
        # you == the recipient's email address
        msg['Subject'] = subject
        msg['From'] = "szhang@ennead.com"
        msg['To'] = contacts[0]

        # Send the message via our own SMTP server.
        s = smtplib.SMTP('localhost')
        s.send_message(msg)
        s.quit()
        print "email sent"

    def send_email_method_3():
        import smtplib, ssl

        port = 465  # For SSL
        smtp_server = "smtp.gmail.com"
        sender_email = "ennead.tab@gmail.com"  # Enter your address
        receiver_email = contacts[0] # Enter receiver address
        password = "ennead2022"
        message = """\
        Subject: Hi there

        This message is sent from Python."""

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, port) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message)


    def send_email_method_4():
        import smtplib, ssl

        port = 587  # For starttls
        smtp_server = "smtp.gmail.com"
        sender_email = "ennead.tab@gmail.com"
        receiver_email = contacts[0]
        password = "ennead2022"
        message = """\
        Subject: Hi there

        This message is sent from Python."""

        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_server, port) as server:
            server.ehlo()  # Can be omitted
            server.starttls(context=context)
            server.ehlo()  # Can be omitted
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message)

    def send_email_method_5():
        # Import smtplib for the actual sending function
        import smtplib

        # Import the email modules we'll need
        from email.message import EmailMessage

        # # Open the plain text file whose name is in textfile for reading.
        # with open(textfile) as fp:
        #     # Create a text/plain message
        #     msg = EmailMessage()
        #     msg.set_content(fp.read())

        # Open the plain text file whose name is in textfile for reading.

        msg = EmailMessage()
        msg.set_content(body)

        # me == the sender's email address
        # you == the recipient's email address
        msg['Subject'] = subject
        msg['From'] = "ennead.tab@gmail.com"
        msg['To'] = contacts[0]

        # Send the message via our own SMTP server.
        s = smtplib.SMTP('localhost')
        s.send_message(msg)
        s.quit()

    def send_email_method_6():
        import smtplib

        def prompt(prompt):
            return input(prompt).strip()

        fromaddr = "ennead.tab@gmail.com"
        toaddrs  = contacts[0]
        # print("Enter message, end with ^D (Unix) or ^Z (Windows):")

        # Add the From: and To: headers at the start!
        msg = ("From: %s\r\nTo: %s\r\n\r\n"
               % (fromaddr, ", ".join(toaddrs)))

        msg = msg + body

        #print("Message length is", len(msg))

        server = smtplib.SMTP('localhost')
        server.set_debuglevel(1)
        server.sendmail(fromaddr, toaddrs, msg)
        server.quit()


    send_email_method_6()

    print "email sent"
    return False




"""
user names
"""
""""""
def get_real_name():
    from pyrevit import script
    filepath = script.get_bundle_file("EA account.txt")
    filepath = filepath.split(".extension")[0] + ".extension\lib\EA account.txt"
    datas = read_txt_as_list(filepath = filepath, use_encode = True)
    print datas
    user_name = __revit__.Application.Username
    for data in datas:
        if user_name in data:
            break
    return data.split("###")[1]

""""""
def save_autodesk_name(user_name):
    from pyrevit import script
    filepath = script.get_bundle_file("EA account.txt")
    filepath = filepath.split(".extension")[0] + ".extension\lib\EA account.txt"
    datas = read_txt_as_list(filepath = filepath, use_encode = True)
    has_documented = False
    for data in datas:
        if user_name in data:
            has_documented = True
            break
    if has_documented:
        return
    with open(filepath, 'a') as f:
        # f.writelines(list)
        f.write("\n{0}###{0}".format(user_name))
    print read_txt_as_list(filepath = filepath, use_encode = True)


""""""
def is_SZ(pop_toast = False, additional_tester_ID = []):
    try:
        app = __revit__.Application
    except:
        try:
            app = __revit__
        except:
            from os import environ
            #print os.environ["USERPROFILE"]
            if environ["USERPROFILE"] == r"C:\Users\szhang":
                return True
            return False

    if  app.Username == "szhangXNLCX":
        if pop_toast:
            show_toast(message = "", title = "Welcome back! Sen Zhang")
            # print "#####EnneadTab is operated by Sen Zhang"
        return True

    if app.Username in additional_tester_ID:
        print "additional test user found = {}".format(app.Username)
        return True

    return False

""""""
def get_user_name():
    return get_application().Username

""""""
def get_linestyle(doc, linestyle_name):
    line_category = doc.Settings.Categories.get_Item(DB.BuiltInCategory.OST_Lines)
    line_subcs = line_category.SubCategories
    for line_style in line_subcs:
        if line_style.Name == linestyle_name:
            return line_style.GetGraphicsStyle(DB.GraphicsStyleType.Projection)
    return None

""""""
def get_all_linestyles(doc):
    line_category = doc.Settings.Categories.get_Item(DB.BuiltInCategory.OST_Lines)
    line_subcs = line_category.SubCategories
    names = [x.Name for x in line_subcs]
    names.sort()
    return names

""""""
def get_subc(doc, subc_name, in_cate = None):
    """
    in_cate = Detail Items,
    """
    for subc in get_all_subcs(doc, in_cate):
        if subc.Name == subc_name:
            return subc
    return None

""""""
def get_all_subcs(doc, in_cate = None):
    OUT = []
    for cate in doc.Settings.Categories:
        if cate.Name not in in_cate:
            continue
        for subc in cate.SubCategories:
            OUT.append(subc)
    return OUT

"""
unit conversion
"""

""""""
def mm_to_ft(x):
    return x/304.8

""""""
def ft_to_mm(x):

    return (304.8*x)

""""""
def ft_to_fraction_inch(x):
    pass

def ft_to_inch(x):
    return x* 12
""""""
def sqft_to_sqm(x):
    try:
        return DB.UnitUtils.ConvertFromInternalUnits(x, lookup_unit_id("squareMeters"))
    except:
        return DB.UnitUtils.ConvertFromInternalUnits(x, DB.DisplayUnitType.DUT_SQUARE_METERS)
    #return x/10.764
""""""
def sqm_to_internal(x):
    try:
        return DB.UnitUtils.ConvertToInternalUnits(x, lookup_unit_id("squareMeters"))
    except:
        return DB.UnitUtils.ConvertToInternalUnits(x, DB.DisplayUnitType.DUT_SQUARE_METERS)
    #return x/10.764
""""""
def internal_to_mm(x):
    try:
        return DB.UnitUtils.ConvertFromInternalUnits(x, lookup_unit_id("millimeters"))
    except:
        return DB.UnitUtils.ConvertFromInternalUnits(x,DB.DisplayUnitType.DUT_MILLIMETERS)
    #forge_type_id = GetUnitTypeId()
    #return DB.UnitUtils.ConvertFromInternalUnits(x, forge_type_id)
""""""
def mm_to_internal(x):
    try:
        return DB.UnitUtils.ConvertToInternalUnits(x, lookup_unit_id("millimeters"))
    except:
        return DB.UnitUtils.ConvertToInternalUnits (x,DB.DisplayUnitType.DUT_MILLIMETERS)
""""""
def radian_to_degree(radian):
    try:
        return DB.UnitUtils.Convert(radian,
                                    lookup_unit_id("radians"),
                                    lookup_unit_id("degrees"))
    except:
        return DB.UnitUtils.Convert(radian,
                                    DB.DisplayUnitType.DUT_RADIANS,
                                    DB.DisplayUnitType.DUT_DECIMAL_DEGREES)

"""

  // Pre 2021

  DisplayUnitType displayUnitType = fp.DisplayUnitType;
  value = UnitUtils.ConvertFromInternalUnits(
    nullable.Value, displayUnitType ).ToString();

  //2021

  ForgeTypeId forgeTypeId = fp.GetUnitTypeId();
  value = UnitUtils.ConvertFromInternalUnits(
    nullable.Value, forgeTypeId ).ToString();
"""
""""""
def lookup_unit_id(key):
    """
    feet
    inches
    meters
    millimeters

    squareFeet
    squareInches
    squareMeters

    radians
    degrees
    """
    for unit_type_id in DB.UnitUtils.GetAllUnits():
        if key == str(unit_type_id.TypeId).split("-")[0].split("unit:")[1]:
            return unit_type_id


""""""
def lookup_unit_spec_id(key):
    """
    length
    number
    area
    angle
    """
    for spec_type_id in DB.UnitUtils.GetAllMeasurableSpecs ():
        #print spec_type_id.TypeId
        if not "aec:" in str(spec_type_id.TypeId):
            continue
        if key == str(spec_type_id.TypeId).split("-")[0].split("aec:")[1]:
            return spec_type_id




"""
data conversion
"""
""""""
def read_json_as_dict(filepath):
    import json
    # reads it back
    with open(filepath,"r") as f:
      dict = json.load(f)
    return dict

""""""
def save_dict_to_json(dict, filepath):
    import json
    # write to a file
    with open(filepath,"w") as f:
      json.dump(dict, f)






""""""
def read_txt_as_list(filepath = "path", use_encode = False):
    if use_encode:
        import io
        with io.open(filepath, encoding = "utf8") as f:
            lines = f.readlines()
    else:
        with open(filepath) as f: #encoding = "utf8"
            lines = f.readlines()
    return map(lambda x: x.replace("\n",""), lines)

""""""
def save_list_to_txt(list, filepath, end_with_new_line = False, use_encode = False):
    if use_encode:
        import io
        with io.open(filepath, "w", encoding = "utf8") as f:
            f.write('\n'.join(list))
            if end_with_new_line:
                f.write("\n")
    else:
        with open(filepath, 'w') as f:
            # f.writelines(list)
            f.write('\n'.join(list))
            if end_with_new_line:
                f.write("\n")
    pass


""""""
def get_file_name_from_path(file_path):
    import os.path as op
    head, tail = op.split(file_path)
    return tail


""""""
def get_folder_path_from_path(file_path):
    import os.path as op
    head, tail = op.split(file_path)
    return head


""""""
def copy_file_to_folder(original_path, target_folder):
    import shutil
    new_path = original_path.replace(get_folder_path_from_path(original_path), target_folder)
    try:
        shutil.copyfile(original_path, new_path)
    except Exception as e:
        print (e)

""""""
def read_file_safely(original_path, file_name = None):
    #print original_path
    if file_name is None:
        file_name = original_path.rsplit("\\", 1)[1]
    local_folder = get_EA_setting_folder() + "\\" + "Local Copy Dump"
    local_folder = secure_folder(local_folder)
    local_path = "{}\{}".format(local_folder, file_name)
    import shutil
    shutil.copyfile(original_path, local_path)
    #print "###"
    #print local_path
    content = read_txt_as_list(local_path)
    return content


""""""
def get_sticky_longterm(sticky_name, default_value_if_no_sticky):
    folder = get_EA_setting_folder() + "\Longterm Sticky"
    #print folder
    folder = secure_folder(folder)
    file = folder + "\\" + sticky_name + ".STICKY"
    #print file
    #print sticky_name
    #print "***"
    #print get_filenames_in_folder(folder)
    if sticky_name + ".STICKY" not in get_filenames_in_folder(folder):
        print "stickyname not found in folder"
        set_sticky_longterm(sticky_name, default_value_if_no_sticky)
        return default_value_if_no_sticky
    value = read_txt_as_list(file)
    #print "****"
    #print value
    if value is None or len(value) == 0:
        set_sticky_longterm(sticky_name, default_value_if_no_sticky)
        return default_value_if_no_sticky
    else:
        return value[0]

""""""
def set_sticky_longterm(sticky_name, value_to_write):
    folder = get_EA_setting_folder() + "\Longterm Sticky"
    folder = secure_folder(folder)
    file = folder + "\\" + sticky_name + ".STICKY"
    save_list_to_txt([value_to_write], file)

""""""
def get_script_file_folder():
    import os
    return os.path.dirname(__file__)


""""""
def open_file_in_default_application(filepath):

    #subprocess.call('C:\Program Files\Rhino 7\System\Rhino.exe')

    import subprocess, os
    os.startfile(filepath)


""""""
def read_data_from_excel(filepath, worksheet = "Sheet1", by_line = True):
    import sys
    reload(sys)
    # 设定了输出的环境为utf8
    sys.setdefaultencoding('utf-8')
    import sqlalchemy
    import xlrd
    wb = xlrd.open_workbook(filepath)#, encoding_override = "cp1252")#""big5")#"iso2022_jp_2")#"gb18030")#"gbk")#"hz")  #"gb2312")   #"utf8"
    sheet = wb.sheet_by_name(worksheet)
    #print sheet.cell_value(2, 1)
    OUT = []

    for i in range(0, sheet.nrows):
        OUT.append(sheet.row_values(i))
    return OUT


    """
    import csv
    with open(filepath,'rb') as f:
        reader = csv.reader(f)
        for row in reader:
            print row
    return reader
    """

""""""
def list_to_system_list(list, type = "ElementId", use_IList = False):

    import System
    if use_IList:
        if type == "CurveLoop":
            return System.Collections.Generic.IList[DB.CurveLoop](list)

        if type == "TableCellCombinedParameterData":
            return System.Collections.Generic.IList[DB.TableCellCombinedParameterData](list)




    if type == "ElementId":
        return System.Collections.Generic.List[DB.ElementId](list)
    if type == "CurveLoop":
        return System.Collections.Generic.List[DB.CurveLoop](list)
    if type == "Curve":
        return System.Collections.Generic.List[DB.Curve](list)
    if type == "TableCellCombinedParameterData":
        return System.Collections.Generic.List[DB.TableCellCombinedParameterData](list)


    print_note("Things are not right here...type = {}".format(type))

    return False

""""""
def copy_file_to_local_dump_folder(original_path, file_name = None):
    #print original_path
    if file_name is None:
        file_name = original_path.rsplit("\\", 1)[1]
    local_folder = get_EA_setting_folder() + "\\" + "Local Copy Dump"
    local_folder = secure_folder(local_folder)
    local_path = "{}\{}".format(local_folder, file_name)
    import shutil
    shutil.copyfile(original_path, local_path)

    return local_path





"""
folder manipulation
"""
""""""
def cleanup_folder(folder = "folder path",
                    extension = "extension"):
    import os
    filenames = os.listdir(folder)

    count = 0
    for current_file in filenames:
        ext = os.path.splitext(current_file)[1]
        if ext.upper() == extension.upper():
            try:
                os.remove(os.path.join(folder, current_file))
                count += 1
            except Exception as e:
                print_note("Cannot delete file [{}] becasue error: {}".format(current_file, e))
    return count

""""""
def cleanup_name_in_folder(output_folder, desired_name, extension):
    remove_exisitng_file_in_folder(output_folder, desired_name + extension)
    import os
    #print keyword
    keyword = " - Sheet - "
    file_names = get_filenames_in_folder(output_folder)

    for file_name in file_names:
        if desired_name in file_name and extension in file_name.lower():
            #new_name = file_name.split(keyword)[0]
            new_name = desired_name
            #new_name = file_name.split(keyword)[0]

            try:
                os.rename(os.path.join(output_folder, file_name),os.path.join(output_folder, new_name + extension))

            except Exception as e:
                print_note( "B:skip {} becasue: {}".format(file_name, e))

""""""
def rename_file_in_folder(search_file, new_file_name, folder):
    import os
    import os.path as op
    try:
        os.rename(op.join(folder, search_file),op.join(folder, new_file_name))
        return True
    except Exception as e:
        print_note(e)
        return False

""""""
def remove_file_by_keyword_in_folder(folder, keyword, ignore_file_list = None):
    import os
    import os.path as op
    for file_name in os.listdir(folder):
        print_note(file_name)
        if file_name in ignore_file_list:
            continue
        if string_contain_keywords(file_name, [keyword]):
            remove_exisitng_file_in_folder(folder, file_name)

""""""
def remove_exisitng_file_in_folder(folder, file_name):
    import os
    import os.path as op
    if file_name not in os.listdir(folder):
        return
    try:
        os.remove(op.join(folder, file_name))
    except Exception as e:
        print_note( "Cannot remove <{}> becasue of error: {}".format(file_name, e))


""""""
def get_filenames_in_folder(folder):
    import os
    return os.listdir(folder)

""""""
def get_user_folder():
    import os
    return "{}\Documents".format(os.environ["USERPROFILE"])

""""""
def get_EA_setting_folder():
    folder = get_user_folder() + "\EnneadTab Settings"
    return secure_folder(folder)


""""""
def get_EA_local_dump_folder():
    return get_special_folder_in_EA_setting("Local Copy Dump")


""""""
def get_EA_dump_folder_file(file_name):
    """include extension"""
    return "{}\{}".format(get_EA_local_dump_folder(), file_name)


""""""
def get_special_folder_in_EA_setting(folder_name):
    folder = get_EA_setting_folder() + "\{}".format(folder_name)
    return secure_folder(folder)


""""""
def is_file_exist_in_folder(check_file_name, folder):
    import os

    for file_name in os.listdir(folder):
        #print_note(file_name)
        if check_file_name == file_name:
            return True
    return False


""""""
def is_file_with_keywords_exist_in_folder(keyword_list, folder, ignore_file_list = None):
    print_note("search file with keyword in folder")
    import os
    import os.path as op
    for file_name in os.listdir(folder):
        if file_name in ignore_file_list:
            continue
        print_note("-find file: " + file_name)
        for keyword in keyword_list:
            print_note("--try keyword: " + keyword)
            if keyword not in file_name:
                print_note("---keyword not in file_name, not my file, try next file. ")
                break

        else:
            print_note("---search all keywords, keyword not in file_name, not my file, try next file. ")
            continue
        print_note("---return True, find good file: " + file_name)
        return True
    print_note("return False, not any file has all keywords together.")
    return False


""""""
def get_filepath_in_special_folder_in_EA_setting(folder_name, file_name):
    return get_special_folder_in_EA_setting(folder_name) + "\{}".format(file_name)

""""""
def secure_folder(path):
    import os
    try:
        if os.path.exists(path):
            return path
        os.makedirs(path)

    except Exception as e:

        print_note( "folder cannot be secured")
        print_note(e)
        pass
    return path



"""
documents manipulation
"""

def parameter_has_unassigned_value(parameter):
    if parameter.HasValue:
        return False
    return True

""""""
def get_application():
    try:
        app = __revit__.Application
    except:
        app = __revit__
    return app

def is_doc_change_hook_depressed():
    from pyrevit.coreutils import envvars
    if envvars.get_pyrevit_env_var("IS_DOC_CHANGE_HOOK_DEPRESSED"):
        return True
    return False


def try_with_traceback(func_call):
    import traceback
    try:
        return func_call
    except Exception as e:
        print_note("ERROR: " + str(e))
        print_note(traceback.format_exc())

def print_traceback():
    import traceback
    print_note(traceback.format_exc())

def set_doc_change_hook_depressed(is_depressed = True):
    return
    from pyrevit.coreutils import envvars
    from System import EventHandler, Uri
    from Autodesk.Revit.DB.Events import DocumentChangedEventArgs
    # import DOC_CHANGE_EVENT
    import traceback

    if not is_SZ() or True:
        is_depressed = True
    def event_handler_function(sender, args):
        print_note( "inside the handler function: begin")
        try:
            DOC_CHANGE_EVENT.protection_check(args)
        except Exception as e:

            print_note("ERROR: " + str(e))
            print_note(traceback.format_exc())


        print_note("inside the handler function: finish")
        # doc = args.GetDocument()
        # print doc.Title


    app = get_application()
    if is_depressed:
        print_note("going to depress doc change hook")
        try:
            app.DocumentChanged -= EventHandler[DocumentChangedEventArgs ](event_handler_function)
        except:
            pass
    else:
        print_note("going to activate doc change hook")
        try:

            app.DocumentChanged += EventHandler[DocumentChangedEventArgs ](event_handler_function)
        except:
            pass

    envvars.set_pyrevit_env_var("IS_DOC_CHANGE_HOOK_DEPRESSED", is_depressed)


""""""
def is_open_hook_depressed():
    from pyrevit.coreutils import envvars
    if envvars.get_pyrevit_env_var("IS_OPEN_HOOK_DEPRESSED"):
        return True
    return False

""""""
def set_open_hook_depressed(is_depressed = True):
    from pyrevit.coreutils import envvars
    envvars.set_pyrevit_env_var("IS_OPEN_HOOK_DEPRESSED", is_depressed)

""""""
def do_you_want_to_sync_and_close_after_done():
    will_sync_and_close = False
    res = dialogue(main_text = "Sync and Close after done?", options = ["Yes", "No"])
    if res == "Yes":
        will_sync_and_close = True

    return will_sync_and_close


""""""
def sync_and_close(close_others = True, disable_sync_queue = True):

    from pyrevit import revit, script
    from pyrevit.coreutils import envvars
    output = script.get_output()
    killtime = 30
    output.self_destruct(killtime)

    envvars.set_pyrevit_env_var("IS_SYNC_QUEUE_DISABLED", disable_sync_queue)
    if close_others:
        envvars.set_pyrevit_env_var("IS_AFTER_SYNC_WARNING_DISABLED", True)
        # if you descide to close others, they should be no further warning. Only recover that warning behavir in DOC OPENED event


    def get_docs():
        try:
            doc = __revit__.ActiveUIDocument.Document
            docs = doc.Application.Documents
            print_note("get docs using using method 1")
        except:
            docs = __revit__.Documents
            print_note("get docs using using method 2")
        print_note( "[sync and close method, EA UTITLYT]get all docs, inlcuding links and family doc = {}".format(str([x.Title for x in docs])))
        return docs

    print_note("getting docs before sync")
    docs = get_docs()
    logs = []
    for doc in docs:

        if doc.IsLinked or doc.IsFamilyDocument:
            continue
        # print "#####"
        # print ("# {}".format( doc.Title) )
        #with revit.Transaction("Sync {}".format(doc.Title)):
        t_opts = DB.TransactWithCentralOptions()
        #t_opts.SetLockCallback(SynchLockCallBack())
        s_opts = DB.SynchronizeWithCentralOptions()
        s_opts.SetRelinquishOptions(DB.RelinquishOptions(True))

        s_opts.SaveLocalAfter = True
        s_opts.SaveLocalBefore = True
        s_opts.Comment = "EnneadTab Batch Sync"
        s_opts.Compact = True


        try:
            doc.SynchronizeWithCentral(t_opts,s_opts)
            logs.append( "\tSync [{}] Success.".format(doc.Title))
            # resume talkie ability later.
            #speak("Document {} has finished syncing.".format(doc.Title))
        except Exception as e:
            logs.append( "\tSync [{}] Failed.\n{}\t".format(doc.Title, e))

    envvars.set_pyrevit_env_var("IS_SYNC_QUEUE_DISABLED", not(disable_sync_queue))
    for log in logs:
        print log
    if not close_others:
        return

    print_note("getting docs before active safty doc")
    docs = get_docs()
    set_active_doc_as_new_family()
    print_note("active doc set as safety doc")
    for doc in docs:
        if doc is None:
            print_note("doc is None, skip")
            continue
        try:
            if doc.IsLinked:
                print_note("doc {} is a link doc, skip".format(doc.Title))
                continue
        except Exception as e:
            print "Info:"
            print (e)
            print_note(str(doc))
            continue

        title = doc.Title
        try:
            print "Trying to close [{}]".format(title)
            doc.Close(False)
            doc.Dispose()
        except Exception as e:
            print (e)
            try:
                print "skip closing [{}]".format(title)
            except:
                print "skip closing some doc"
        """
        try to open a dummy family rvt file in the buldle folder and switch to that as active doc then close original active doc
        """

""""""
def set_active_doc_as_new_family():
    from pyrevit import script
    filepath = script.get_bundle_file("SAFETY DOC.rfa")
    # doc.Application.NewFamiyDocument(filepath)
    #print filepath
    # "C:\Users\szhang\github\ea-pyRevit\ENNEAD.extension\Ennead.tab\Tailor Shop.panel\misc1.stack\Proj 2135.pulldown\test sync and close.pushbutton\SAFETY DOC.rfa"
    filepath = filepath.split(".extension")[0] + ".extension\lib\SAFETY DOC.rfa"


    # filepath = r"C:\Users\szhang\github\ea-pyRevit\ENNEAD.extension\lib\SAFETY DOC.rfa"
    #print filepath
    print ("show this msg to Sen Zhang. Thank you!")

    open_and_active_project(filepath)

""""""
def open_and_active_project(filepath):

    from Autodesk.Revit import UI
    try:
        app = __revit__
        return UI.UIApplication(app).OpenAndActivateDocument (filepath)
    except:
        pass

    try:
        app = __revit__.ActiveUIDocument.Document.Application
        return UI.UIApplication(app).OpenAndActivateDocument (filepath)
    except:
        pass

    try:
        app = __revit__.ActiveUIDocument.Document.Application
        open_options = DB.OpenOptions()
        return UI.UIApplication(app).OpenAndActivateDocument (filepath, open_options, False)
    except:
        pass

    try:
        app = __revit__
        open_options = DB.OpenOptions()
        return UI.UIApplication(app).OpenAndActivateDocument (filepath, open_options, False)
    except:
        pass

    print "Activate Failed"

""""""
def close_docs_by_name(names = [], close_all = False):

    def safe_close(doc):
        name = doc.Title
        doc.Close(False)
        doc.Dispose()#########################
        print "{} closed".format(name)

    docs = get_top_revit_docs()
    if close_all:
        map(safe_close, docs)
        return

    for doc in docs:
        if doc.Title in names:
            try:
                safe_close(doc)
            except Exception as e:
                print (e)
                print "skip closing [{}]".format(doc.Title)

""""""
def get_top_revit_docs():

    docs = get_application().Documents
    OUT = []
    for doc in docs:
        if doc.IsLinked or doc.IsFamilyDocument:
            continue
        OUT.append(doc)
    return OUT

""""""
def get_all_family_docs(including_current_doc = False):
    docs = get_application().Documents
    OUT = []
    for doc in docs:
        if not doc.IsFamilyDocument:
            continue
        if not including_current_doc:
            if doc.Title == __revit__.ActiveUIDocument.Document.Title:
                continue
        OUT.append(doc)
    return OUT

""""""
def select_family_docs(select_multiple = True, including_current_doc = False):
    from pyrevit import forms
    return forms.SelectFromList.show(get_all_family_docs(including_current_doc = including_current_doc),
                                        name_attr = "Title",
                                        multiselect = select_multiple,
                                        title = "pick family",
                                        button_name='pick family')

""""""
def select_top_level_docs(select_multiple = True):
    from pyrevit import forms
    docs = get_top_revit_docs()
    docs = forms.SelectFromList.show(docs,
                                    name_attr = "Title",
                                    multiselect = select_multiple,
                                    title = "Pick some open revit docs")
    return docs


""""""
def get_revit_link_docs(including_current_doc = False):

    docs = get_application().Documents

    OUT = []
    for doc in docs:
        if doc.IsFamilyDocument:
            continue
        if not including_current_doc:
            if doc.Title == __revit__.ActiveUIDocument.Document.Title:
                continue

        OUT.append(doc)
    OUT.sort(key = lambda x: x.Title)
    return OUT
""""""
def select_revit_link_docs(select_multiple = True, including_current_doc = False):
    from pyrevit import forms
    docs = get_revit_link_docs(including_current_doc = including_current_doc )
    docs = forms.SelectFromList.show(docs,
                                    name_attr = "Title",
                                    multiselect = select_multiple,
                                    title = "Pick some revit links")
    return docs
"""
project setting
"""
def define_new_project_setting():
    # pick a folder in project folder

    # ask for project number and project name

    # save a lot of txt file, each respond to a set of task,

    # setting directory also saved in L drive repo txt----> project_num_project_name--->L drive\xxx\xxx

    pass


def update_project_setting(setting_name):
    # get project setting test, maybe the file is not yet registered

    # if not yet exiting(maybe i am adding a new tool setting that does not exist yet), create it


    # open the txt to user to edit

    pass


def get_project_setting(setting_name):
    # go to L drive repo txt to look for matching name and get directory for where to find settings
    # r"L:\4b_Applied Computing\01_Revit\04_Tools\08_EA Extensions\Project Settings"

    # tool description embed in txt but not readed



    pass



def OLD_get_protected_elementID_from_long_term_ID():
    """
    after doc change event, run this.
    if the remaining
    """
    pass


def log_action_for_protected_element(doc, transcation, missing_elements):
    """
    file at server based on document
    log info: time, user name, filename, action, element involded.



    if people undo, need a way to state that tings are bright back to the file, but UIQUE ID mifght changd
    """
    import time
    user_name = get_application().Username
    localtime = time.asctime( time.localtime(time.time()) ).replace(":","-")

    info = "{  "
    for x in missing_elements:
        info += "{}|".format(x)
    info.replace( info[len(info)-1:],"  }")

    data = "{}| {} | {} | missing: {}".format(localtime, user_name, transcation, info)
    print data
    filepath = get_protection_log_txt(doc)
    with open(filepath, "a") as f:
        f.write(data)
        f.write("\n")


def extract_info(data_item):
    # return category, name, ID with new format [category][name][stabdkle ID]
    category = data_item.split("][")[0].replace("[","")
    name = data_item.split("][")[1]
    ID = data_item.split("][")[2].replace("]","")
    return category, name , ID

def get_protected_elements_from_long_term_ID(doc):
    """
    after doc change event, run this.
    based on QQQ file, retreive as much as it can, item cannot be reteived have been deleted.


    toast warning for modifying protected element
    task dialogue for deleting protected element

    both action is loged
    """



    filepath = get_protection_item_txt(doc)
    data = read_txt_as_list(filepath)
    # print data
    existing = []
    missing = []
    for item in data:
        category, name, stableID = extract_info(item)

        # stableID = item.split("$$$")[1]
        element = doc.GetElement(stableID)
        if element is None:
            # category = item.split("@@@")[0]
            # name = item.split("@@@")[1].split("$$$")[0]
            missing.append("[{}]:{}".format(category, name))
        else:
            existing.append(element)
    return existing, missing

def get_name_changes(doc, existing):
    OUT = []

    # print "inside name change func"
    # print existing

    filepath = get_protection_item_txt(doc)

    datas = read_txt_as_list(filepath)
    # print datas
    for element in existing:
        # print "Q"
        # print element
        current_name = get_unique_name(doc, element)
        # print_note( current_name)
        for data_item in datas:
            category, record_name, stableID = extract_info(data_item)
            if stableID == element.UniqueId:
                # print "find"
                break
        if record_name != current_name:
            OUT.append("[{}] Current Name = {}, Record Name = {}".format(category, current_name, record_name))
    # print OUT
    return OUT


def get_protection_item_txt(doc):


    filepath = r"L:\4b_Applied Computing\01_Revit\04_Tools\08_EA Extensions\Project Settings\Protection Item Setting\Protection Item_{}.txt". format(doc.Title)
    try:
        with open(filepath, "r"):
            pass
    except:
        with open(filepath, "w+"): # if not existing then create
            pass
    return filepath

def get_protection_log_txt(doc):


    filepath = r"L:\4b_Applied Computing\01_Revit\04_Tools\08_EA Extensions\Project Settings\Protected Item History\Protection Log_{}.txt". format(doc.Title)
    try:
        with open(filepath, "r"):
            pass
    except:
        with open(filepath, "w+"): # if not existing then create
            pass
    return filepath

def get_unique_name(doc,x):# x is element

    if x.Category.Name in ["Grids", "Levels", "Scope Boxes"]:
        return x.Name
    if x.Category.Name in ["Floors"]:
        level = doc.GetElement(x.LevelId).Name
        type = x.Name
        return "{}_{}".format(level, type)
    if x.Category.Name in ["Walls"]:
        level = doc.GetElement(x.LevelId).Name
        type = x.Name
        return "{}_{}".format(level, type)
    print "Ask Sen to add this category:{}".format(x.Category.Name)
    return "No Name"

def append_protected_elements_as_long_term_ID(doc, elements, override = False):
    """

    new format:
    [category][name][stabdkle ID]



    check duplicate before overriding it again,
    if name is different, update name with same unique ID??
    """


    filepath = get_protection_item_txt(doc)
    # for item in elements:
    #


    data = ["[{}][{}][{}]".format(x.Category.Name, get_unique_name(doc, x), x.UniqueId) for x in elements]
    data.sort()



    # print data
    if override:
        save_list_to_txt(data, filepath)
    else:
        original_data = read_txt_as_list(filepath)
        for x in data:
            if x not in original_data:
                original_data.append(x)
        #original_data.extend(data)
        original_data.sort()
        save_list_to_txt(original_data, filepath)
        pass

    pass

def OLD_update_protected_elementId_from_long_term_ID():
    """
    after doc opened, and after synced, use this method
    get all elements from the QQQ, convert to a list of short term ID in user local folder
    """
    pass
