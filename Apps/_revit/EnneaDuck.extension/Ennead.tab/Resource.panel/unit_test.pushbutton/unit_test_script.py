#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "Test the core modules"
__title__ = "Unit Test"
__context__ = "zero-doc"


import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

from EnneadTab import ERROR_HANDLE, UNIT_TEST, LOG


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def unit_test():
    UNIT_TEST.test_core_module()



################## main code below #####################
if __name__ == "__main__":
    unit_test()







