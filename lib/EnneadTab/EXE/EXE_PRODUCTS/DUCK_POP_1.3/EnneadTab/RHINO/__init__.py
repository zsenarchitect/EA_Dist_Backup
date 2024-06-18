#!/usr/bin/python
# -*- coding: utf-8 -*-


import os
for module in os.listdir(os.path.dirname(__file__)):
    #print (module)
    if module == '__init__.py':
        continue

    if module[-3:] != '.py':
        continue
    try:
        __import__(module[:-3], locals(), globals())
    except Exception as e:
        pass
        #print (e)
        #print ("Cannot import {}".format(module))
del module# delete this varible becaue it is refering to last item on the for loop
