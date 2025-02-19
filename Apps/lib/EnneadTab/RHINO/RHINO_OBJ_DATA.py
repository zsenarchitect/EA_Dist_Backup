#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
root_folder = os.path.abspath((os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(root_folder)
import ENVIRONMENT


if ENVIRONMENT.IS_RHINO_ENVIRONMENT:
    import rhinoscriptsyntax as rs
    import scriptcontext as sc


def sort_pts_by_Z(pts):
    """Sort points by their Z coordinate in ascending order.

    Parameters
    ----------
    pts : list
        List of Rhino.Geometry.Point3d objects to sort

    Returns
    -------
    list
        Points sorted by ascending Z coordinate value
    """
    pts = sorted(pts, key=lambda x: x.Z)
    return pts

def sort_pts_along_crv(pts, crv):
    """Sort points by their parameter values along a curve.

    Parameters
    ----------
    pts : list
        List of Rhino.Geometry.Point3d objects to sort
    crv : Rhino.Geometry.Curve
        Reference curve to sort points along

    Returns
    -------
    list
        Points sorted by ascending parameter value along the curve
    """
    pts = sorted(pts, key=lambda x: rs.CurveClosestPoint(crv, x))
    return pts

def sort_AB_along_crv(pt0, pt1, crv):
    """Sort two points along a curve in ascending parameter order.

    Parameters
    ----------
    pt0 : Rhino.Geometry.Point3d
        First point to sort
    pt1 : Rhino.Geometry.Point3d
        Second point to sort
    crv : Rhino.Geometry.Curve
        Reference curve to sort points along

    Returns
    -------
    tuple
        (pt0, pt1) sorted so that pt0's parameter value is less than pt1's.
        For closed curves, points are sorted to minimize the parameter distance
        between them across the seam.

    Notes
    -----
    - Uses normalized curve parameters for comparison
    - Handles both open and closed curves
    - For closed curves, checks if sorting across the seam gives shorter parameter distance
    """
    t0 = rs.CurveClosestPoint(crv,pt0)
    t1 = rs.CurveClosestPoint(crv,pt1)
    t0 = rs.CurveNormalizedParameter(crv, t0)
    t1 = rs.CurveNormalizedParameter(crv, t1)


    if t1 < t0:
        t0, t1 = t1, t0
        pt0, pt1 = pt1, pt0

    if not rs.IsCurveClosed(crv):
        return pt0, pt1

    if abs(t1 - t0) > abs(t0) + abs(1-t1):
        pt0, pt1 = pt1, pt0

    return pt0, pt1



def get_center(obj):
    """Get the center point of an object's bounding box.

    Parameters
    ----------
    obj : Guid
        Object ID to calculate center for

    Returns
    -------
    Rhino.Geometry.Point3d
        Center point of the object's bounding box
    """
    corners = rs.BoundingBox(obj)
    min = corners[0]
    max = corners[6]
    center = (min + max)/2
    return center

def get_obj_h(obj):
    """Get the height (Z dimension) of an object's bounding box.

    Parameters
    ----------
    obj : Guid
        Object ID to calculate height for

    Returns
    -------
    float
        Height of the object's bounding box
    """
    corners = rs.BoundingBox(obj)
    min = corners[0]
    max = corners[6]
    z_diff = (max.Z - min.Z)
    return z_diff

def get_boundingbox_edge_length(obj):
    """Get the lengths of bounding box edges in X, Y, and Z directions.

    Parameters
    ----------
    obj : Guid
        Object ID to calculate bounding box dimensions for

    Returns
    -------
    tuple
        (X_length, Y_length, Z_length) of the bounding box edges
    """
    corners = rs.BoundingBox(obj)
    X = rs.Distance(corners[0], corners[1])
    Y = rs.Distance(corners[1], corners[2])
    Z = rs.Distance(corners[0], corners[5])
    return X, Y, Z


def get_obj_min_center_pt(obj):
    """Get the center point of the minimum face of an object's bounding box.

    Parameters
    ----------
    obj : Guid
        Object ID to calculate minimum face center for

    Returns
    -------
    Rhino.Geometry.Point3d
        Center point of the minimum (bottom) face of the bounding box
    """
    pts = rs.BoundingBox(obj)
    pt0 = pts[0]
    pt1 = pts[2]
    return (pt0 + pt1)/2


def get_instance_geo(block_instance):
    """Get all geometry objects from a block instance, including nested instances.

    Parameters
    ----------
    block_instance : Guid
        Block instance ID to extract geometry from

    Returns
    -------
    list
        All geometry objects contained in the block instance, transformed to 
        world coordinates

    Notes
    -----
    - Recursively processes nested block instances
    - Applies block instance transformation to all geometry
    - Returns actual geometry objects, not references
    """
    block_name = rs.BlockInstanceName(block_instance)
    non_block_objs, block_instance_objs = [], []

    for x in rs.BlockObjects(block_name):
        (block_instance_objs if rs.IsBlockInstance(x) else non_block_objs).append(x)
        
    non_block_geos = [sc.doc.Objects.Find(x).Geometry for x in non_block_objs]
    block_geos = []
    for x in block_instance_objs:
        block_geos.extend(get_instance_geo(x))
    geo_contents = non_block_geos + block_geos
    
    transform = rs.BlockInstanceXform(block_instance)
    [x.Transform(transform) for x in geo_contents]
    return geo_contents

