
import Rhino # pyright: ignore
import System # pyright: ignore.Drawing
import scriptcontext as sc
import rhinoscriptsyntax as rs
import sys
sys.path.append("..\lib")
import EnneadTab
####################### below are new thing#######

class EA_SEATING_Conduit(Rhino.Display.DisplayConduit):
    def __init__(self):

        self.BAKE_STICKY_KEY = "EA_SEATING_IS_BAKING"
        if not sc.sticky.has_key(self.BAKE_STICKY_KEY):
            sc.sticky[self.BAKE_STICKY_KEY] = False

        self.layer_key = "EA_SEATING_BAKING_LAYERS"
        if not sc.sticky.has_key(self.layer_key):
            sc.sticky[self.layer_key] = []



        pass


    def PreDrawObjects  (self, e):#PostDrawObjects,, PreDrawObjects,,DrawOverlay ,,DrawForeground
        self.is_baking = sc.sticky[self.BAKE_STICKY_KEY]
        self.bake_layers = sc.sticky[self.layer_key]
        self.data = dict()


        for layer in get_seat_crv_layers():

            base_crvs = get_crvs_in_layer(layer)
            if len(base_crvs) == 0:
                continue


            block_name = layer.split("<")[1].split(">")[0]
            block = sc.doc.InstanceDefinitions.Find(block_name)
            if not block:
                continue
            #print "Block find: {}".format(block_name)



            spacing = float(layer.split("{")[1].split("}")[0])
            if not spacing:
                continue

            #print "Spacing find: {}".format(spacing)
            if block_name not in self.data.keys():
                self.data[block_name] = 0


            for base_crv in base_crvs:
                transform_list = get_transforms_from_base_crv(base_crv, spacing)
                self.data[block_name] += len(transform_list)
                #print transform_list
                """
                for transform in transform_list:
                    #print block
                    #print transform
                    #transform = Rhino.Geometry.Transform.Identity
                    #print transform
                    e.Display.DrawInstanceDefinition(block, transform)

                    #print e.Display.DrawDot (Rhino.Geometry.Point3d(0,0,200), "test")
                """
                map(lambda transform: e.Display.DrawInstanceDefinition(block, transform), transform_list)

                if layer in self.bake_layers and self.is_baking:
                    bake_blocks(block_name, transform_list, spacing)
                #print "AA"
            #print "BB"




        if sc.sticky[self.BAKE_STICKY_KEY]:
            print("finish baking")
            sc.sticky[self.BAKE_STICKY_KEY] = False
            self.is_baking = False





    def DrawForeground(self, e):
        text = "Ennead Seat Study Mode"
        color = rs.CreateColor([87, 85, 83])
        #color = System.Drawing.Color.Red
        position_X_offset = 20
        position_Y_offset = 40
        size = 40
        bounds = e.Viewport.Bounds
        pt = Rhino.Geometry.Point2d(bounds.Left + position_X_offset, bounds.Top + position_Y_offset)
        e.Display.Draw2dText(text, color, pt, False, size)
        pt = Rhino.Geometry.Point2d(pt[0], pt[1] + 35)
        e.Display.Draw2dText("Include bracket [SEAT_CRVS] in layer name to allow picking.", color, pt, False, 20)
        pt = Rhino.Geometry.Point2d(pt[0], pt[1] + 25)
        e.Display.Draw2dText("Include angle bracket <YourBlockName> in layer name to allow assigning.", color, pt, False, 20)
        pt = Rhino.Geometry.Point2d(pt[0], pt[1] + 25)
        e.Display.Draw2dText("Include curly bracket {Spacing} in layer name to allow assigning.", color, pt, False, 20)
        pt = Rhino.Geometry.Point2d(pt[0], pt[1] + 25)
        e.Display.Draw2dText("Flip crv to flip seat orientation, Right click to bake seats.", color, pt, False, 20)
        """
        pt = Rhino.Geometry.Point2d(pt[0], pt[1] + 25)
        e.Display.Draw2dText("So far, this prototype has only been tested in millimeter file units.", color, pt, False, 20)
        """

        pt = Rhino.Geometry.Point2d(pt[0], pt[1] + 25)
        pt0 = System.Drawing.Point(pt[0], pt[1] )
        pt1 = System.Drawing.Point(pt[0] + 500, pt[1] )
        #print "A"
        e.Display.Draw2dLine(pt0, pt1, color, 5)
        #print "B"
        for key in sorted(self.data.keys()):
            pt = Rhino.Geometry.Point2d(pt[0], pt[1] + 20)
            text = "Total seats for <{}> = {}".format(key, self.data[key])
            e.Display.Draw2dText(text, color, pt, False, 20)
        #print "drawingsssss finish"




        #print "Done"
        #True = text center around thge define pt, Flase = lower-left


def bake_blocks(block_name, transform_list, spacing):
    blocks = [rs.InsertBlock2(block_name, xform) for xform in transform_list]
    group_name = "<{}>_[{}]".format(block_name, spacing)
    rs.AddObjectsToGroup(blocks, rs.AddGroup(group_name))
    bake_layer = rs.AddLayer("EA_Seating_Bake::{}".format(group_name))
    map(lambda x: rs.ObjectLayer(x, bake_layer), blocks)
    #rs.EnableRedraw(True)
    #EnneadTab.RHINO.RHINO_SELECTION.pay_attention(blocks)
    #rs.EnableRedraw(False)

    pass


def get_seat_crv_layers():
    #print "geting good layers"
    layers = sorted(rs.LayerNames())
    good_layers = filter(lambda x:"[SEAT_CRVS]" in x, layers)
    def layer_name_syntax(x):
        if "{" in x and "}" in x and "<" in x and ">" in x:
            return True
        return False
    good_layers = filter(layer_name_syntax, layers)

    #print good_layers
    return good_layers

    pass


def get_crvs_in_layer(layer):
    objs = rs.ObjectsByLayer(layer)
    objs = filter(lambda x: rs.IsCurve(x), objs)
    return objs


@EnneadTab.ERROR_HANDLE.try_catch_error
def toggle_seating_display():


    conduit = None
    key = "EA_SEATING_display_Conduit"
    if sc.sticky.has_key(key):
        conduit = sc.sticky[key]
    else:
        # create a conduit and place it in sticky
        conduit = EA_SEATING_Conduit()
        sc.sticky[key] = conduit

    # Toggle enabled state for conduit. Every time this script is
    # run, it will turn the conduit on and off
    conduit.Enabled = not conduit.Enabled
    if conduit.Enabled: print "conduit enabled"
    else: print "conduit disabled"
    sc.doc.Views.Redraw()

    print("Tool Finished")


def get_transforms_from_base_crv(base_crv, spacing):

    block_name, insert_pt, ref_pt = get_dummy_seating()
    temp_block = rs.InsertBlock(block_name, insert_pt)
    directional_ref = [0,1,0]
    block_reference = [insert_pt, ref_pt, directional_ref]


    crv_segs = rs.ExplodeCurves(base_crv)

    #temporartyly set project osnap on to prevent flipping on X axis base line
    #original_project_osnap_status = rs.ProjectOsnaps()
    #rs.ProjectOsnaps(enable = True)

    collection = []
    #print crv_segs
    for seg in crv_segs:
        count = rs.CurveLength(seg) / spacing
        pts_on_seg = rs.DivideCurve(seg, count, create_points = False)
        if rs.IsCurveClosed(seg):
            pts_on_seg.append(pts_on_seg[0])


        for i in range(len(pts_on_seg)):
            x0 = pts_on_seg[i]
            #print x0

            param = rs.CurveClosestPoint(seg, x0)
            tangent = rs.CurveTangent(seg, param)


            #print "tagent = {}".format(tangent)
            side_vector = rs.VectorRotate(tangent, 90, [0,0,1])
            #print "side vector tagent = {}".format(side_vector)
            directional_ref_temp = x0 + side_vector
            #rs.AddPoint(directional_ref_temp)
            target_reference = [x0, x0 + tangent, directional_ref_temp]
            #print "target_reference = {}".format(target_reference)
            #target_reference = [x0, x1]
            temp_placed_block = rs.OrientObject( temp_block, block_reference, target_reference, flags = 1 )
            collection.append(rs.BlockInstanceXform(temp_placed_block))
            rs.DeleteObject(temp_placed_block)


    rs.DeleteObjects(crv_segs)
    rs.DeleteObject(temp_block)
    return collection

def get_dummy_seating():
    if rs.IsBlock("seating dummy"):
        return "seating dummy", [0,0,0], [500 , 0, 0]
    else:
        return create_dummy_seating()


def create_dummy_seating():
    name = "seating dummy"
    W = 1000
    H = 1000

    pt0 = [0,0,0]
    pt2 = [-W/2,0,0]
    pt1 = [W/2, W, H]
    pts = [pt1, pt2]
    ref_pt_coord = [W/2 , 0, 0]

    box_corners = rs.BoundingBox(pts)
    box = rs.AddBox(box_corners)
    dot = rs.AddText("Sample Panel\n<{}>\nReplace block with better design.".format(name),
                    EnneadTab.RHINO.RHINO_OBJ_DATA.get_center(box),
                    height = 0.5,
                    font = "Arial",
                    font_style = 0,
                    justification = 2 + 131072 )
    #dot = rs.AddTextDot("Sample Panel <{}>\nReplace Me".format(name), EnneadTab.RHINO.RHINO_OBJ_DATA.get_center(box))
    insert_pt = rs.AddPoint(pt0)
    ref_pt = rs.AddPoint(ref_pt_coord)
    ref_line_start_pt = pt0
    ref_line_end_pt = [0, -W, 0]

    ref_line = rs.AddLine(ref_line_start_pt, ref_line_end_pt)
    block_contents = [box, insert_pt, ref_pt, ref_line, dot]
    block_name = rs.AddBlock(block_contents, insert_pt, name = name, delete_input = True)
    return block_name, pt0, ref_pt_coord


def testing():
    rs.EnableRedraw(False)
    for layer in  get_seat_crv_layers():
        area, crvs = get_area_and_crv_geo_from_layer(layer)
        if area == 0:
            continue
        print("#")
        text = convert_area_to_good_unit(area)

        color = rs.LayerColor(layer)
        print(text)
        print(color)


if __name__=="__main__":
    #showinscript()
    #showafterscript()
    toggle_seating_display()
    #testing()




    """
    ideas:
    right click to set desired GFA to each layer name, save to external text. and live compare how much is off from target.
    """
