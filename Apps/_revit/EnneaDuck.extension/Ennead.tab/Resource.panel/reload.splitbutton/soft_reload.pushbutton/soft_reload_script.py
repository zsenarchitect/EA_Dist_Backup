#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "Just download the new repo and unzip. This will not reload the Reevit for UI change."
__title__ = "Soft\nReload"
__context__ = "zero-doc"
__tip__ = True

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

from EnneadTab import ERROR_HANDLE, LOG, VERSION_CONTROL



@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def soft_reload():
    VERSION_CONTROL.update_EA_dist()


################## main code below #####################
if __name__ == "__main__":
    soft_reload()







