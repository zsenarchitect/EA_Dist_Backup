#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
sys.path.append("..\lib")
import EnneadTab
import rhinoscriptsyntax as rs
from scriptcontext import doc
import Rhino # pyright: ignore

"""
### TO-DO:
- Change into two buttons: one for displaying block names, one for displaying block usage summary
#### Assigned to: **CM**
"""

def get_center(obj):
    corners = rs.BoundingBox(obj)
    min = corners[0]
    max = corners[6]
    center = (min + max)/2
    return center


def create_block_name_textdots():

    rs.EnableRedraw(False)
    blocks = rs.ObjectsByType(4096, select = False, state = 0)

    bounding_box_centers = [get_center(x) for x in blocks]
    dot_texts = [ rs.BlockInstanceName(x) for x in blocks]
    dots = [rs.AddTextDot(text,pt) for text, pt in zip(dot_texts,bounding_box_centers)]
    group_name = "block_names_display_dots"
    rs.AddGroup(group_name = group_name)
    rs.AddObjectsToGroup(dots, group_name)


def summary_of_block_usage():
    block_names = rs.BlockNames(sort = False)
    OUT = ""
    for block_name in block_names:
        OUT += "\n[{}] status:".format(block_name)
        top_level_count = rs.BlockInstanceCount(block_name, where_to_look = 0)
        OUT += "\n• {} instances as top level block".format(rs.BlockInstanceCount(block_name,where_to_look = 0))
        OUT += "\n• {} instances in nested block".format(rs.BlockInstanceCount(block_name,where_to_look = 1) - top_level_count)
        OUT += "\n• {} instances in block definition type".format(rs.BlockInstanceCount(block_name,where_to_look = 2))

        parent_blocks = rs.BlockContainers(block_name)
        if len(parent_blocks) != 0:
            plural_upper = "s" if len(parent_blocks) > 1 else ""
            OUT += "\n• {} parent block{}:".format(len(parent_blocks), plural_upper)
            for item in parent_blocks:
                OUT += "\n\t\t[{}]".format(item)

        block_definition = doc.InstanceDefinitions.Find(block_name)
        objs = block_definition.GetObjects()
        
        child_blocks = filter(lambda x: rs.IsBlockInstance(x), objs)
        child_blocks.sort(key = lambda x: rs.BlockInstanceName(x))
        if len(child_blocks) != 0:
            plural_inner = "s" if len(child_blocks) > 1 else ""
            OUT += "\n• {} nested block{}:".format(len(child_blocks), plural_inner)
            for item in child_blocks:
                OUT += "\n\t\t[{}]".format(rs.BlockInstanceName(item))


        OUT += "\n"

    rs.TextOut(message = OUT, title = "Summary of all block instances")


@EnneadTab.ERROR_HANDLE.try_catch_error
def display_block_names():
    create_block_name_textdots()
    summary_of_block_usage()


#######################################
if __name__ == "__main__":
    display_block_names()
