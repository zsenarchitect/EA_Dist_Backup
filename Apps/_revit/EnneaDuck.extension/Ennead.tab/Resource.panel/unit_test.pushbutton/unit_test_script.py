#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "Diagnostic validation tool that verifies core EnneadTab modules are functioning correctly. This utility runs a comprehensive series of tests on critical system components to ensure proper operation across the entire extension ecosystem. Perfect for troubleshooting after updates, when experiencing unexpected behavior, or when developing new functionality that depends on core services."
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







