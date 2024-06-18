#!/usr/bin/python
# -*- coding: utf-8 -*-

def notification(main_text = "",
                sub_text = "",
                window_title = "EnneadTab",
                button_name = "Close",
                self_destruct = 0,
                window_width = 500,
                window_height = 500):
    """simple window that do not take any resonse from user.

    Args:
        main_text (str, optional): _description_. Defaults to "".
        sub_text (str, optional): _description_. Defaults to "".
        window_title (str, optional): _description_. Defaults to "EnneadTab".
        button_name (str, optional): _description_. Defaults to "Close".
        self_destruct (int, optional): if value other than 0, will close after that many secs. Defaults to 0.
        window_width (int, optional): _description_. Defaults to 500.
        window_height (int, optional): _description_. Defaults to 500.
    """

    
    import REVIT_FORMS_NOTIFICATION

    #xmal_template = remap_filepath_between_folder(xmal_template, new_folder_after_dot_extension = "lib")
    REVIT_FORMS_NOTIFICATION.ModelessForm(main_text,
                                        sub_text,
                                        button_name,
                                        window_title,
                                        self_destruct,
                                        window_width,
                                        window_height)


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
    Basic windows that take up to 4 user selection option.
    
    extra check box appear before commands options
    verification_check_box_text appear after commands options
    is activaed, the result of dialogue will return a tuple of two values.

    options = [["opt 1","description long long long long"], ["opt 2"]]   if options is a string, then used as main text, but if it is a list of two strings, the second string will be used as description. In either case, the command link will return main text


    TaskDialogIconNone,	No icon.
    TaskDialogIconShield,	Shield icon.
    TaskDialogIconInformation,	Information icon.
    TaskDialogIconError,	Error icon.
    TaskDialogIconWarning, Warning icon

    Args:
        title (str, optional): _description_. Defaults to "EnneadTab".
        main_text (str, optional): _description_. Defaults to "main_text".
        sub_text (_type_, optional): _description_. Defaults to None.
        options (_type_, optional): _description_. Defaults to None.
        footer_link (str, optional): _description_. Defaults to "http://www.ennead.com".
        footer_text (str, optional): _description_. Defaults to "EnneadTab".
        use_progress_bar (bool, optional): _description_. Defaults to False.
        expended_content (_type_, optional): _description_. Defaults to None.
        extra_check_box_text (_type_, optional): _description_. Defaults to None.
        verification_check_box_text (_type_, optional): _description_. Defaults to None.
        icon (str, optional): _description_. Defaults to "shield".
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
