"""note to self:
it is important to use type hint for GH input.
Only consider process it with rhino common, do not use rhinoscriptsyntax as it cannot process gh guid correctly to the funcs.
"""
__title__ = "2419_Facade move"
__doc__ = "xxxxxxxxxxxxxxxxxxxxx"

import Rhino # pyright: ignore
import rhinoscriptsyntax as rs
import scriptcontext as sc


import Grasshopper # pyright: ignore
sc.doc = Grasshopper.Instances.ActiveCanvas.Document



import os
import sys
tab_folder = os.path.dirname(os.path.dirname(__file__))
apps_folder = os.path.dirname(os.path.dirname(tab_folder))
sys.path.append("{}\\lib".format(apps_folder))
import EnneadTab


def main(crv_set_1, crv_set_2):
    OUT = []
    

    for curve in crv_set_2:
        domain = curve.Domain
        print (domain)
        t1 = (domain[1]-domain[0])*0.2 + domain[0]
        t2 = (domain[1]-domain[0])*0.8 + domain[0]
        print (t1, t2)
        start_point, end_point = curve.PointAt(t1), curve.PointAt(t2)
        OUT.append(start_point)
    


   

    return OUT

if is_run: # pyright: ignore
    a = main(crv_set_1, crv_set_2) # pyright: ignore

sc.doc = Rhino.RhinoDoc.ActiveDoc