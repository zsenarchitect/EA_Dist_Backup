input_list = [("Width", "Number", "Room width."),
              ("Length", "Number", "Room length."),
              ("Height", "Number", "Room height.")]
output_list = [("Model", "Model", "HBJson Model.")]


basic_doc = """This script shows how to:

    1. create a room from a box
    2. add a single aperture to the south wall
    3. add the room to a model
    4. create a sensor grid and add it to the room
    5. save the room as an HBJSON file
    
"""


########################################### internal setup
import _utility
__doc__ = _utility.generate_doc_string(basic_doc, input_list, output_list)
# default_value_map = _utility.generate_default_value_map()

# print dir(_utility)
# use this to trick GH that all varibale is defined.
globals().update(_utility.validate_input_list(globals(), input_list))



################ input below ###########################
width = Width
length = Length
height = Height

import Rhino # pyright: ignore
import rhinoscriptsyntax as rs
import scriptcontext as sc

import Grasshopper
sc.doc = Grasshopper.Instances.ActiveCanvas.Document

import os
import sys
sys.path.append("L:\\4b_Applied Computing\\03_Rhino\\12_EnneadTab for Rhino\\Dependency Modules")
from honeybee.room import Room, Vector3D
from honeybee.model import Model

from honeybee_radiance.sensorgrid import SensorGrid
############## main design below #######################

def create_room(width, length, height):
    # width = 4
    # height = 3.6
    # depth = 6

    wwr = 0.6

    grid_size = 0.5  # every half a meter
    grid_offset = 0.8  # 80 cms from the floor

    # initiate a room
    room = Room.from_box(identifier='single_room', width=width, depth=length, height=height)

    # get south facing wall using wall face normal angle.
    south_vector = Vector3D(0, -1, 0)
    south_face = [face for face in room.faces if south_vector.angle(face.normal) <= 0.01][0]
    # create an aperture by ratio
    # alternatively one can use other methods like `aperture_by_width_height`
    # see here for docs: https://www.ladybug.tools/honeybee-core/docs/honeybee.face.html#honeybee.face.Face.aperture_by_width_height
    south_face.apertures_by_ratio(ratio=wwr)

    # create a model and add the room to it
    model = Model('EnneadTab-test-model', rooms=[room], units='Meters')

    # create a sensor grid - this is only required if you want to run grid-based studies
    # use generate_grid method to create a sensor grid from room floor
    grid_mesh = room.generate_grid(x_dim=grid_size, y_dim=grid_size, offset=grid_offset)
    # create a sensor grid using the generated mesh
    sensor_grid = SensorGrid.from_mesh3d(identifier='room', mesh=grid_mesh)

    model.properties.radiance.add_sensor_grid(sensor_grid)

    if not os.path.exists('.\Honeybee_Data'):
        os.mkdir('.\Honeybee_Data')
    model.to_hbjson(name=model.identifier, folder='.\Honeybee_Data')
    
    
    print(type(model))
    
    return [model]


if _utility.is_all_input_valid(globals(), input_list):
    result = create_room(width, length, height)



    ################ output below ######################
    for i,item in enumerate(output_list):
        output_name = item[0]
        globals()[output_name] = result[i]
    


else:
    print ("There are missing valid input")

sc.doc = Rhino.RhinoDoc.ActiveDoc