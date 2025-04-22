"""example on overload handling

import System.Collections.Generic.IEnumerable as IEnumerable


for srf in srfs:
    splitBrep = srf.Split.Overloads[IEnumerable[Rhino.Geometry.Curve], System.Double](cutters, tol)



wrong example.....
if you have a out parameter, iron python will return as tuple instead using it in args
success, family_ref = project_doc.LoadFamily.Overloads[str, DB.IFamilyLoadOptions](temp_path, loading_opt, family_ref)
"""

import os
