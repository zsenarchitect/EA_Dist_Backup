#!/usr/bin/python
# -*- coding: utf-8 -*-

import ENVIRONMENT

def notification(title = ENVIRONMENT.PLUGIN_NAME + " For Rhino",
                main_text = "sample header",
                sub_text = "",
                self_destruct = None,
                button_name = "Sure...",
                width = 500,
                height = 150):
    """Display a notification dialog in Rhino.

    Args:
        title (str, optional): Dialog window title. Defaults to ENVIRONMENT.PLUGIN_NAME + " For Rhino".
        main_text (str, optional): Primary message text. Defaults to "sample header".
        sub_text (str, optional): Secondary message text. Defaults to "".
        self_destruct (int, optional): Auto-close time in seconds. Defaults to None.
        button_name (str, optional): Text for the confirmation button. Defaults to "Sure...".
        width (int, optional): Dialog width in pixels. Defaults to 500.
        height (int, optional): Dialog height in pixels. Defaults to 150.

    Returns:
        bool: True if confirmed, False if canceled.
    """



    import _RHINO_FORMS_NOTIFICATION as FORMS_NTF
    return FORMS_NTF.show_NotificationDialog(title,
                                            main_text,
                                            sub_text,
                                            self_destruct,
                                            button_name,
                                            width,
                                            height)

def select_from_list(options,
                    title = ENVIRONMENT.PLUGIN_NAME + " For Rhino",
                    message = "test message",
                    button_names = ["Select"],
                    width = 500,
                    height = 500,
                    multi_select = True):
    """Display a list selection dialog with single or multiple selection options.

    Args:
        options (list): List of items to choose from.
        title (str, optional): Dialog window title. Defaults to ENVIRONMENT.PLUGIN_NAME + " For Rhino".
        message (str, optional): Instructions for user. Defaults to "test message".
        button_names (list, optional): List of button labels. Defaults to ["Select"].
        width (int, optional): Dialog width in pixels. Defaults to 500.
        height (int, optional): Dialog height in pixels. Defaults to 500.
        multi_select (bool, optional): Allow multiple selections. Defaults to True.

    Returns:
        list: Selected items from the options list.
    """



    import _RHINO_FORMS_LIST_SELECTION as FORMS_L
    return FORMS_L.show_ListSelectionDialog(options,
                                            title,
                                            message,
                                            multi_select,
                                            button_names,
                                            width,
                                            height)




def select_from_list2list(options_A,
                        options_B,
                        title = ENVIRONMENT.PLUGIN_NAME + " For Rhino",
                        message = "",
                        search_A_text = "search AAA",
                        search_B_text = "search BBB",
                        multi_select_A = True,
                        multi_select_B = True,
                        button_names = ["Select"],
                        width = 300,
                        height = 200):
    """Display a dual-list selection dialog allowing transfers between two lists.

    Args:
        options_A (list): Items in the first list.
        options_B (list): Items in the second list.
        title (str, optional): Dialog window title. Defaults to ENVIRONMENT.PLUGIN_NAME + " For Rhino".
        message (str, optional): Instructions for user. Defaults to "".
        search_A_text (str, optional): Placeholder for first list search. Defaults to "search AAA".
        search_B_text (str, optional): Placeholder for second list search. Defaults to "search BBB".
        multi_select_A (bool, optional): Allow multiple selections in first list. Defaults to True.
        multi_select_B (bool, optional): Allow multiple selections in second list. Defaults to True.
        button_names (list, optional): List of button labels. Defaults to ["Select"].
        width (int, optional): Dialog width in pixels. Defaults to 300.
        height (int, optional): Dialog height in pixels. Defaults to 200.

    Returns:
        tuple: Selected items from both lists (list_A_selection, list_B_selection).
    """



    import _RHINO_FORMS_LIST2LIST_SELECTION as FORMS_L2L
    return FORMS_L2L.ShowList2ListSelectionDialog(options_A,
                                                options_B,
                                                title,
                                                message,
                                                search_A_text,
                                                search_B_text,
                                                multi_select_A,
                                                multi_select_B,
                                                button_names,
                                                width,
                                                height)
