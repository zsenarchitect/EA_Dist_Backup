#!/usr/bin/python
# -*- coding: utf-8 -*-
import NOTIFICATION


def is_selection_not_valid(obj, note = "Nothing is selected."):
    if not obj:
        NOTIFICATION.toast(main_text = note, sub_text = "Action Cancelled")
        return False
    return True
