#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
root_folder = os.path.abspath((os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(root_folder)
import NOTIFICATION
try:
    import rhinoscriptsyntax as rs
    import Rhino
    import RHINO_OBJ_DATA
except:
    pass

def is_selection_not_valid(obj, note = "Nothing is selected."):
    if not obj:
        NOTIFICATION.messenger(main_text = note, sub_text = "Action Cancelled")
        return False
    return True

def pay_attention(objs, time = 25, visibility = True, selection = True, zoom_selected = True):
    """zoom flash"""

    original_state = rs.EnableRedraw(True)
    if zoom_selected:
        #rs.UnselectAllObjects()
        rs.SelectObjects(objs)
        rs.ZoomSelected()
        rs.UnselectObjects(objs)


    if objs:
        if visibility:
            for i in range(time):
                rs.FlashObject(objs, style = False)
        if selection:
            for i in range(time):
                rs.FlashObject(objs, style = True)
    rs.EnableRedraw(original_state)


def select_subelements(include_face = True, 
                       include_edge = True, 
                       include_vertex = True, 
                       include_edgeloop = True,
                       return_doc_objs = False):
    """Selects sub-objects from a polysurface.

    Args:
        include_face (bool, optional): Include face sub-objects. Defaults to True.
        include_edge (bool, optional): Include edge sub-objects. Defaults to True.
        include_vertex (bool, optional): Include vertex sub-objects. Defaults to True.
        return_obj (bool, optional): Return the selected sub-objects as document objects(with name "TEMP_subelement_selection"), otherwise return as native Rhino geometry. Defaults to False.
    Returns:
        dict: A dictionary containing the selected sub-objects in native Rhino geometry objects.
    """
    # Initialize an empty list to store selected sub-object indices
    selected_subobjects = {"face": [], "edge": [], "vertex": [], "edge_loop":[]}
    
    # Prompt the user to select sub-objects (with sub-object selection enabled)
    go = Rhino.Input.Custom.GetObject()
    note = "Select multiple sub-objects from a polysurface by holding ctrl+shift and click"
    if include_face:
        note += " (faces)"
    if include_edge:
        note += " (edges)"
    if include_vertex:
        note += " (vertices)"
    if include_edgeloop:
        note += " (edgeLoops)"
    go.SetCommandPrompt(note)
    go.SubObjectSelect = True  # Enable sub-object selection


    
    go.GetMultiple(1, 0)  
    # minimumNumber
    # Type: int
    # minimum number of objects to select.
    # maximumNumber
    # Type: int
    # maximum number of objects to select. If 0, then the user must press enter to finish object selection. If -1, then object selection stops as soon as there are at least minimumNumber of object selected. If >0, then the picking stops when there are maximumNumber objects. If a window pick, crossing pick, or Sel* command attempts to add more than maximumNumber, then the attempt is ignored.
        
    if go.CommandResult() != Rhino.Commands.Result.Success:
        print("No sub-objects were selected.")
        return
    
    # Loop through the selected sub-objects
    for obj_ref in go.Objects():
        # Get the sub-object type
        subobject_type = obj_ref.GeometryComponentIndex.ComponentIndexType
        
        if subobject_type == Rhino.Geometry.ComponentIndexType.BrepFace and include_face:
            # Store only face sub-object indices
            selected_subobjects["face"].append(obj_ref.Brep())

        elif subobject_type == Rhino.Geometry.ComponentIndexType.BrepEdge and include_edge:
            selected_subobjects["edge"].append(obj_ref.Curve())

        elif subobject_type == Rhino.Geometry.ComponentIndexType.BrepVertex and include_vertex:
            selected_subobjects["vertex"].append(obj_ref.Point())

        elif subobject_type == Rhino.Geometry.ComponentIndexType.BrepTrim and include_edge:
            selected_subobjects["edge"].append(obj_ref.Edge().ToNurbsCurve())
            
        elif subobject_type == Rhino.Geometry.ComponentIndexType.BrepLoop and include_edgeloop:
            selected_subobjects["edge_loop"].append(obj_ref.Curve().ToNurbsCurve())
        else:
            print ("{} is not a valid sub-object type".format(subobject_type))

    if return_doc_objs:
        for key in selected_subobjects:
            selected_subobjects[key] = [RHINO_OBJ_DATA.geo_to_obj(obj, name = "TEMP_subelement_selection") for obj in selected_subobjects[key]]
    return selected_subobjects


if __name__ == "__main__":
    print (select_subelements(include_face=False, include_edge=True, include_vertex=False))