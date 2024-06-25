import Rhino # pyright: ignore
import rhinoscriptsyntax as rs
import scriptcontext as sc
import System # pyright: ignore

import sys
sys.path.append("..\lib")
from EnneadTab.ENVIRONMENT import get_EnneadTab_For_Rhino_root
sys.path.append(r'{}\Source Codes\lib'.format(get_EnneadTab_For_Rhino_root()))
import EnneadTab


ROOM_ROOT_FOLDER = r"L:\4b_Applied Computing\03_Rhino\12_EnneadTab for Rhino\Design Room"

KEY = "EA_DESIGN_ROOM_display_Conduit"
IS_UPDATE_KEY = "EA_DESIGN_ROOM_IS_UPDATING"

class EA_DESIGN_ROOM_Conduit(Rhino.Display.DisplayConduit):
    def __init__(self):
        self.default_color = rs.CreateColor([87, 85, 83])
        self.session_links = dict()
        self.room_name = None
        self.counter = 300
        self.counter_max = self.counter
        self.color_lookup = dict()


        if sc.sticky.has_key(IS_UPDATE_KEY):
            sc.sticky[IS_UPDATE_KEY] = False



        # KEY = "EA_DESIGN_ROOM_NAME"
        # if sc.sticky.has_key(KEY):
        #     self.room_name = sc.sticky[KEY]

        #self.main_folder = "{}\{}".format(ROOM_ROOT_FOLDER, self.room_name)


        #print "#######initiation"
    #
    # @property
    # def room_name(self):
    #     return COMMON_DATA["room_name"]

    @property
    def main_folder(self):
        return "{}\{}".format(ROOM_ROOT_FOLDER, self.room_name)


    #@EnneadTab.ERROR_HANDLE.try_catch_error
    def DrawOverlay  (self, e):#PostDrawObjects,, PreDrawObjects,,DrawOverlay ,,DrawForeground
        if not self.room_name:
            return


        if self.counter % 5 == 0:
            export_mouse_data(self.main_folder)


        for path in collect_session_files(self.main_folder):

            user = EnneadTab.FOLDER.get_file_name_from_path(path)
            self.session_links[user] = path



        self.counter -= 1

        if self.counter % self.counter_max < 0 and not sc.sticky[IS_UPDATE_KEY]:# add 'and not' here becasue the force update is done thru the right click action
            self.sync()


        if self.counter % 2 == 0 or sc.sticky[IS_UPDATE_KEY]:
            self.show_mouse_on_screen(e)

        if sc.sticky[IS_UPDATE_KEY]:
            sc.sticky[IS_UPDATE_KEY] = False

        if self.counter < 0:
            self.counter = self.counter_max


    def sync(self):
        export_layer_data(self.main_folder)
        if self.session_links:
            rs.Command("-WorkSession  Refresh Enter", echo = False)
        self.counter = self.counter_max


    def show_mouse_on_screen(self, e):
        datas = read_mouse_data(self.main_folder)
        #becareful about unit, that replate to how mouse are drawn
        for data in datas:
            self.color_lookup[data["user"]] = EnneadTab.COLOR.tuple_to_color(data["color"])
            try:
                pt_x, pt_y, pt_z = data["mouse_position"]
                e.Display.DrawDot (text = data["user"],
                                    dotColor = EnneadTab.COLOR.tuple_to_color(data["color"]),
                                    textColor = EnneadTab.COLOR.BLACK,
                                    worldPosition = Rhino.Geometry.Point3d(pt_x, pt_y, pt_z)
                                    )
            except KeyError:
                print("Need to restart")


    def show_text_with_pointer(self, e, text, size, color = None, is_middle_justified = False):
        if not color:
            color = self.default_color


        e.Display.Draw2dText(text, color, self.pointer_2d, is_middle_justified, size)
        #self.pointer_2d = Rhino.Geometry.Point2d(self.pointer_2d[0], self.pointer_2d[0] + size - 5)
        self.pointer_2d += Rhino.Geometry.Vector2d(0, size )


    #@EnneadTab.ERROR_HANDLE.try_catch_error
    def DrawForeground(self, e):
        if not self.room_name:
            return

        #color = System.Drawing.Color.Red
        position_X_offset = 20
        position_Y_offset = 40
        bounds = e.Viewport.Bounds
        self.pointer_2d = Rhino.Geometry.Point2d(bounds.Left + position_X_offset, bounds.Top + position_Y_offset)


        title = "Ennead Design Room Mode"
        if self.room_name != "":
            title += ": {}".format(self.room_name)
        self.show_text_with_pointer(e,
                                    text = title,
                                    size = 30)
        """
        self.show_text_with_pointer(e,
                                    text = "Only objects under the <EnneadTab Design Room> parent layer will be interchanged.",
                                    size = 20)
        """
        self.show_text_with_pointer(e,
                                    text = "Other geo files refreshed in {} frames.".format(self.counter),
                                    size = 15)
        self.show_text_with_pointer(e,
                                    text = "You can also sync immediately by right clicking the icon.",
                                    size = 15)
        self.show_text_with_pointer(e,
                                    text = "The smaller file size, the quick it sync.",
                                    size = 15)
        self.show_text_with_pointer(e,
                                    text = "Mouse updates whenever you pan/zoom/move camera, or you are modeling.",
                                    size = 15)
        self.show_text_with_pointer(e,
                                    text = "Left click icon again to leave room.",
                                    size = 15)
        self.show_text_with_pointer(e,
                                    text = "Very important that the team agree on the same unit used.",
                                    size = 15)

        self.pointer_2d += Rhino.Geometry.Vector2d(0, 20)
        pt0 = System.Drawing.Point(self.pointer_2d[0], self.pointer_2d[1] )
        pt1 = System.Drawing.Point(self.pointer_2d[0] + 500, self.pointer_2d[1] )
        #print "A"
        e.Display.Draw2dLine(pt0, pt1, self.default_color, 5)
        #print "B"

        #print self.session_links.keys()
        self.pointer_2d += Rhino.Geometry.Vector2d(0, 20)
        for file in sorted(self.session_links.keys()):
            #file_size = "2mb"
            user = file.replace(".3dm", "")
            self.show_text_with_pointer(e,
                                        text = user,
                                        size = 15,
                                        color = self.color_lookup[user] )




def initiate_room():


    current_rooms = EnneadTab.FOLDER.get_filenames_in_folder(ROOM_ROOT_FOLDER)
    current_rooms.insert(0, "<Create New Room>")
    room_name = EnneadTab.RHINO.RHINO_FORMS.select_from_list(current_rooms,
                                                            title = "EnneadTab Pick Design Room",
                                                            message = "Use a unique room so you and your team can see each other.",
                                                            button_names = ["Pick Room"],
                                                            width = 500,
                                                            height = 500,
                                                            multi_select = False)




    if room_name == "<Create New Room>":
        room_name = rs.StringBox(message = "Enter Your Room Name", title = "Design Room Name")

    if not room_name:
        return

    main_folder = "{}\{}".format(ROOM_ROOT_FOLDER, room_name)
    EnneadTab.FOLDER.secure_folder(main_folder)

    """
    user_mouses_datas = []
    user_geo_datas = []
    for file in EnneadTab.FOLDER.get_filenames_in_folder(main_folder):

        # do not process self file
        if EnneadTab.USER.get_user_name() in file:
            continue

        if ".mouse" in file:
            #print "this is user mouse data"
            user_mouses_datas.append(file)
        if ".3dm" in file:
            #print "this is user geo file"
            user_geo_datas.append(file)
    """

    # put my self to the same folder

    export_mouse_data(main_folder)


    # set_layer_structure()

    # get_my_output_data and save to "user.3dm"
    export_layer_data(main_folder)
    create_worksession_file(main_folder)
    EnneadTab.DATA_FILE.set_sticky_longterm("EA_DESIGN_ROOM_NAME", room_name)

    conduit = sc.sticky[KEY]
    conduit.room_name = room_name
    conduit.session_links = dict()

def set_layer_structure():
    # if dont have Ennead Design Room layer, it shoudlinitate it with one sub layer
    base_layers = ["<EnneadTab Design Room>", "<EnneadTab Design Room>::Sample Layer"]
    for layer in base_layers:
        if not rs.IsLayer(layer):
            #print layer
            rs.AddLayer(name = layer)

    rs.CurrentLayer(layer = layer)
    #for layer in base_layers:
        #rs.RenameLayer(layer, layer.replace("EnneadTab Design Room", "[EnneadTab Design Room]"))

def export_mouse_data(main_folder):
    mouse_position = rs.GetCursorPos()[0] #[0]  cursor position in world coordinates
    #print mouse_position
    file = "{}\{}.mouse".format(main_folder, EnneadTab.USER.get_user_name())
    mouse_dict = dict()
    mouse_dict["mouse_position"] = (mouse_position.X,
                                    mouse_position.Y,
                                    mouse_position.Z)
    key = "DESIGN_ROOM_USER_COLOR"
    if sc.sticky.has_key(key):
        mouse_dict["color"] = sc.sticky["DESIGN_ROOM_USER_COLOR"]
    else:
        mouse_dict["color"] = EnneadTab.COLOR.get_random_color()
        sc.sticky[key] = mouse_dict["color"]
    mouse_dict["user"] = EnneadTab.USER.get_user_name()
    EnneadTab.DATA_FILE.save_dict_to_json(mouse_dict, file)

def read_mouse_data(main_folder):
    files = [x for x in EnneadTab.FOLDER.get_filenames_in_folder(main_folder) if '.mouse' in x]
    files = [x for x in files if EnneadTab.USER.get_user_name() not in x]
    files = ["{}\{}".format(main_folder, x) for x in files]
    datas = [EnneadTab.DATA_FILE.read_json_file_safely(x) for x in files]
    return datas


def export_layer_data(main_folder, use_key_parent_layer = False):
    #layers = filter(lambda x:"[EnneadTab Design Room]" in x, rs.LayerNames())
    if use_key_parent_layer:
        layers = [x for x in rs.LayerNames() if "<EnneadTab Design Room>" in x]
        objs = [rs.ObjectsByLayer(x, select = True) for x in layers]
        file = "{}\{}.3dm".format(main_folder, EnneadTab.USER.get_user_name())
        sc.doc.ExportSelected(file)
        return

    file = "{}\{}.3dm".format(main_folder, EnneadTab.USER.get_user_name())
    sc.doc.Export(file)


def collect_session_files(main_folder):
    def is_other_3dm_file(file):
        if  ".3dmbak" in file:
            return False
        if not ".3dm" in file:
            return False
        if EnneadTab.USER.get_user_name() in file:
            return False
        return True
    files = [x for x in EnneadTab.FOLDER.get_filenames_in_folder(main_folder) if is_other_3dm_file(x)]

    return files


def create_worksession_file(main_folder):

    files = collect_session_files(main_folder)

    if not files:
        return

    files = ["{}\{}".format(main_folder, x) for x in files]

    file_string_link = ""
    for file in files:
        file_string_link += " Attach \"{}\"".format(file)

    session_file_path = "{}\design_room".format(EnneadTab.FOLDER.get_EA_local_dump_folder())
    #print "%%%%%%%%%%%%%%%%%%%%%%%%%"
    #print session_file_path
    #print files
    rs.Command("-WorkSession  {} Saveas \"{}\" Enter".format(file_string_link, session_file_path), echo = False)


def detach_worksession_file(main_folder):
    files = collect_session_files(main_folder)

    if not files:
        return

    files = ["{}\{}".format(main_folder, x) for x in files]

    file_string_link = ""
    for file in files:
        file_string_link += " Detach \"{}\"".format(file)

    session_file_path = "{}\design_room".format(EnneadTab.FOLDER.get_EA_local_dump_folder())
    #print "%%%%%%%%%%%%%%%%%%%%%%%%%"
    #print session_file_path
    #print files
    rs.Command("-WorkSession  {} Saveas \"{}\" Enter".format(file_string_link, session_file_path), echo = False)




def design_room():


    conduit = None

    if sc.sticky.has_key(KEY):
        conduit = sc.sticky[KEY]
    else:
        # create a conduit and place it in sticky
        conduit = EA_DESIGN_ROOM_Conduit()
        sc.sticky[KEY] = conduit

    # Toggle enabled state for conduit. Every time this script is
    # run, it will turn the conduit on and off
    conduit.Enabled = not conduit.Enabled
    if conduit.Enabled:
        print("conduit enabled")
        initiate_room()
        if not conduit.room_name:
            del sc.sticky[KEY]

    else:

        print("conduit disabled")
        if conduit.room_name:
            main_folder = "{}\{}".format(ROOM_ROOT_FOLDER, conduit.room_name)
            detach_worksession_file(main_folder)


    sc.doc.Views.Redraw()

    print("Design Room Finished")



######################  main code below   #########
if __name__ == "__main__":
    rs.EnableRedraw(False)
    design_room()
