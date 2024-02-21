"""base class for setting up display conduit"""


try:
    import Rhino
    REF_CLASS = Rhino.Display.DisplayConduit
except:
    REF_CLASS = object

class RhinoConduit(REF_CLASS):
    pass