"""base class for setting up display conduit"""


try:
    import Rhino
    import rhinoscriptsyntax as rs
    import System
    import traceback
    
    REF_CLASS = Rhino.Display.DisplayConduit
except:
    REF_CLASS = object


def try_catch_conduit_error(func):
    def wrapper(*args, **kwargs):
        try:
            out = func(*args, **kwargs)
            return out
        except Exception as e:
            error = traceback.format_exc()
            print (error)
    return wrapper

class ConduitTextSize:
    Title = 20
    Normal = 10
    Footnote = 5

class RhinoConduit(REF_CLASS):
    default_color = rs.CreateColor([87, 85, 83])

    
    def display_text(self, e, text, size, color = None, is_middle_justified = False):
        """this is the shared method to display on screen text. 
        After each line diplsay, the pointer get to new line position.

        Args:
            e (_type_): _description_
            text (_type_): _description_
            size (ConduitTextSize): _description_
            color (_type_, optional): _description_. Defaults to None.
            is_middle_justified (bool, optional): _description_. Defaults to False.
        """
        if not isinstance(size, ConduitTextSize):
            raise Exception("size should be ConduitTextSize")
        if not hasattr(self, 'pointer_2d'):
            initial_x = 100
            initial_y = 100
            bounds = e.Viewport.Bounds
            self.pointer_2d = Rhino.Geometry.Point2d(bounds.Left + initial_x, bounds.Top + initial_y)
        
        if not color:
            color = RhinoConduit.default_color
        e.Display.Draw2dText(text, color, self.pointer_2d, is_middle_justified, size)
        self.pointer_2d += Rhino.Geometry.Vector2d(0, size )


    def display_space(self, space = ConduitTextSize.Normal):
        self.pointer_2d += Rhino.Geometry.Vector2d(0, space)

    def display_seperation_line(self, e):        
        pt0 = System.Drawing.Point(self.pointer_2d[0], self.pointer_2d[1] )
        pt1 = System.Drawing.Point(self.pointer_2d[0] + 500, self.pointer_2d[1] )
        e.Display.Draw2dLine(pt0, pt1, self.default_color, 5)
        self.display_space()