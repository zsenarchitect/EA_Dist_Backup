#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Go get a drink!"
__title__ = "Beer\nTab"
__context__ = "zero-doc"


import proDUCKtion # pyright: ignore

<<<<<<< HEAD
from EnneadTab import UNIT_TEST, USER
=======
from  EnneadTab import UNIT_TEST, USER
>>>>>>> 76e3fd102b014b1662a1e1b3ba697ce7e40c1030

def beer_tab():
    print (USER.USER_NAME)
    UNIT_TEST.test_core_module()

    print ("ok")

################## main code below #####################


if __name__ == "__main__":
    beer_tab()
