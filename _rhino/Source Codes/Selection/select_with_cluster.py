import rhinoscriptsyntax as rs
import random
import math
import sys
sys.path.append("..\lib")

import EnneadTab



def random_deselection(object_ids, num_seeds, distance_threshold, outside_leak_rate, inside_fill_rate):
    # Get bounding boxes of all objects
    corners = rs.BoundingBox(object_ids)
    min_pt = corners[0]
    max_pt = corners[6]
    # rs.AddPoint(min_pt)
    # rs.AddPoint(max_pt)
    # return


    # Calculate overall dimensions
    x_dim, y_dim, z_dim = EnneadTab.RHINO.RHINO_OBJ_DATA.get_boundingbox_edge_length(object_ids)


    # Generate seed points...... no, change this to using N random obj center so it is always in group for 3d arrangements.
    sampled_objs = random.sample(object_ids,min(num_seeds, len(object_ids)))
    seed_points = []
    balls = []
    for i, obj in enumerate(sampled_objs):
        """
        x = random.uniform(min_pt[0], max_pt[0])
        y = random.uniform(min_pt[1], max_pt[1])
        z = random.uniform(min_pt[2], max_pt[2])
        seed_points.append(rs.AddPoint(x, y, z))
        """

        seed_points.append(EnneadTab.RHINO.RHINO_OBJ_DATA.get_center(obj))

        balls.append(rs.AddSphere(seed_points[i], distance_threshold))

    # Iterate over all objects
    objs_to_select = []
    for object_id in object_ids:
        # Iterate over the points in the object
        point = EnneadTab.RHINO.RHINO_OBJ_DATA.get_center(object_id)

        min_distance = min(rs.Distance(point, seed_point) for seed_point in seed_points)



        # If the point is within the distance threshold
        if min_distance >= distance_threshold:
            factor = distance_threshold/min_distance
            # deslection 70%--->30% chance to pickup--->outside_leak_rate = 0.7
            if random.random() * factor > 1 - outside_leak_rate:
                objs_to_select.append(object_id)
        else:

            if random.random() < inside_fill_rate:
                objs_to_select.append(object_id)



    rs.SelectObjects(objs_to_select)

    #rs.DeleteObjects(seed_points)
    rs.AddObjectsToGroup(balls, rs.AddGroup())

@EnneadTab.ERROR_HANDLE.try_catch_error
def select_with_cluster():
    object_ids = rs.GetObjects("Select objects")
    if not object_ids:
        return


    a = EnneadTab.DATA_FILE.get_sticky_longterm("SELECTION_CLUSTER_NUM", default_value_if_no_sticky = 5)
    b = EnneadTab.DATA_FILE.get_sticky_longterm("SELECTION_CLUSTER_DIST", default_value_if_no_sticky = 2000)
    c = EnneadTab.DATA_FILE.get_sticky_longterm("SELECTION_CLUSTER_LEAK_RATE", default_value_if_no_sticky = 20)# control how leaky it is to boundary
    d = EnneadTab.DATA_FILE.get_sticky_longterm("SELECTION_CLUSTER_FILL_RATE", default_value_if_no_sticky = 90)# control how much to pickup inside the boundary

    items = ["Number of Cluster(Integer)", "Distance Threshold(File Unit)", "Ouside Leak Rate (%)", "Inside Fill Rate (%)"]
    values = [str(a), str(b), str(c), str(d)]
    res = rs.PropertyListBox(items, values, message="Enter info below.")
    if not res:
        return

    # Parse the input strings into real numbers
    try:
        num_seeds = int(res[0])
        distance_threshold = float(res[1])
        outside_leak_rate = int(res[2])/100.0
        inside_fill_rate =  int(res[3])/100.0
    except ValueError:
        rs.MessageBox("Invalid inputs. Please enter valid numbers.")
        return


    EnneadTab.DATA_FILE.set_sticky_longterm("SELECTION_CLUSTER_NUM", num_seeds)
    EnneadTab.DATA_FILE.set_sticky_longterm("SELECTION_CLUSTER_DIST", int(res[1]))
    EnneadTab.DATA_FILE.set_sticky_longterm("SELECTION_CLUSTER_LEAK_RATE", int(res[2]))
    EnneadTab.DATA_FILE.set_sticky_longterm("SELECTION_CLUSTER_FILL_RATE", int(res[3]))


    rs.EnableRedraw(False)
    random_deselection(object_ids, num_seeds, distance_threshold, outside_leak_rate, inside_fill_rate)

if __name__ == "__main__":
    select_with_cluster()
