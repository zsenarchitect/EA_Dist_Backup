#!/usr/bin/python
# -*- coding: utf-8 -*-
try:
    import rhinoscriptsyntax as rs
except:
    pass

def get_center(obj):
    corners = rs.BoundingBox(obj)
    min = corners[0]
    max = corners[6]
    center = (min + max)/2
    return center

def get_obj_h(obj):
    corners = rs.BoundingBox(obj)
    min = corners[0]
    max = corners[6]
    z_diff = (max.Z - min.Z)
    return z_diff

def get_boundingbox_edge_length(obj):
    corners = rs.BoundingBox(obj)
    X = rs.Distance(corners[0], corners[1])
    Y = rs.Distance(corners[1], corners[2])
    Z = rs.Distance(corners[0], corners[5])
    return X, Y, Z


def get_obj_min_center_pt(obj):
    pts = rs.BoundingBox(obj)
    pt0 = pts[0]
    pt1 = pts[2]
    return (pt0 + pt1)/2
