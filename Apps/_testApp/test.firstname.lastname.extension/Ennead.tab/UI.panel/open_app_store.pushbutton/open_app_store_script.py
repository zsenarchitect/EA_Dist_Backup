#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "Sen Zhang has not writed documentation for this tool, but he should!"
__title__ = "Open App Store"

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

from EnneadTab import ERROR_HANDLE, LOG, EXE



@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def open_app_store():

    EXE.try_open_app("AppStore")


################## main code below #####################
if __name__ == "__main__":
    open_app_store()







