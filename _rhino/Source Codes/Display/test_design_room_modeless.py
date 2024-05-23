"""
try this
can timer tryigger display conduit to update.

"""


import threading


import Rhino # pyright: ignore
import rhinoscriptsyntax as rs
import scriptcontext as sc
import System # pyright: ignore
import sys
sys.path.append("..\lib")
from EnneadTab.ENVIRONMENT import get_EnneadTab_For_Rhino_root
sys.path.append(r'{}\Source Codes\lib'.format(get_EnneadTab_For_Rhino_root()))
import EnneadTab
"""
class EA_DESIGN_ROOM_Conduit(Rhino.Display.DisplayConduit):
    def __init__(self):
        
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

        if self.counter % self.counter_max < 0 and not sc.sticky[IS_UPDTAE_KEY]:# add 'and not' here becasue the force update is done thru the right click action
            self.sync()


        if self.counter % 2 == 0 or sc.sticky[IS_UPDTAE_KEY]:
            self.show_mouse_on_screen(e)

        if self.counter < 0:
            self.counter = self.counter_max




    def show_text_with_pointer(self, e, text, size, color = None, is_middle_justified = False):
        if not color:
            color = self.default_color


        e.Display.Draw2dText(text, color, self.pointer_2d, is_middle_justified, size)

        self.pointer_2d += Rhino.Geometry.Vector2d(0, size )


"""


class AutoTimer(Rhino.Display.DisplayConduit):
    def __init__(self, life_span, show_progress = False, interval = 1):
        """
        args:
        """
        self.life_span = life_span
        self.max_repetition = life_span / interval
        self.current_count = self.max_repetition
        self.timer = None
        self.interval = interval
        self.show_progress = show_progress


        self.default_color = rs.CreateColor([87, 85, 83])


    @EnneadTab.ERROR_HANDLE.try_catch_error
    def on_timed_event(self):
        if self.show_progress:
            print ("{}/{}".format(int(self.current_count), int(self.max_repetition )))

        # if hasattr(self, 'e'):
            #print self.e
            #self.show_text_with_pointer(self.e, "A::::showing  " + str(self.current_count), 20)
            # self.DrawOverlay(self.e)
       
        self.current_count -= 1
        # print("The Elapsed event was raised at", datetime.datetime.now())

        if self.current_count > 0:

            self.timer = threading.Timer(self.interval, self.on_timed_event)
            self.timer.start()
        else:
            print("Timer stopped after", self.life_span, "seconds")
            self.stop_timer()
            timer_example.Enabled = False

    def stop_timer(self):
        if self.timer:
            self.timer.cancel()

    def begin(self):
        print("Timer begins!")
        self.timer = threading.Timer(self.interval, self.on_timed_event)
        self.timer.start()
        #print(self.timer.is_alive())

    @EnneadTab.ERROR_HANDLE.try_catch_error
    def show_text_with_pointer(self, e, text, size, color = None, is_middle_justified = False):
        if not color:
            color = self.default_color

        position_X_offset = 500
        position_Y_offset = 100
        bounds = e.Viewport.Bounds
        if not hasattr(self, 'pointer_2d'):
            self.pointer_2d = Rhino.Geometry.Point2d(bounds.Left + position_X_offset, bounds.Top + position_Y_offset)
        
        e.Display.Draw2dText(text, color, self.pointer_2d, is_middle_justified, size)
        self.pointer_2d += Rhino.Geometry.Vector2d(0, size*0.1 )

    @EnneadTab.ERROR_HANDLE.try_catch_error
    def myDrawOverlay(self, e):

        #print self.e
        self.show_text_with_pointer(e, "B showing{}".format(int(self.current_count)), 20)

        
        

if __name__ == "__main__":
    timer_example = AutoTimer(life_span=10,
                              show_progress=True,
                              interval= 1)
    timer_example.Enabled = True
    timer_example.begin()