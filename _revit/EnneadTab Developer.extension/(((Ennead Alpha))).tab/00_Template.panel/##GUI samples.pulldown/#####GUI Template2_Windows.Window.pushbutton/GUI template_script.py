__doc__ = "Sen Zhang has not writed documentation for this tool, but he should!"
__title__ = "GUI\ntemplate_esthan method"
# dependencies
import clr
clr.AddReference('System.Windows.Forms')
clr.AddReference('IronPython.Wpf')

# find the path of ui.xaml
from pyrevit import UI
from pyrevit import script
xamlfile = script.get_bundle_file('GUI temp_UI.xaml')

# import WPF creator and base Window
import wpf
from System import Windows

class MyWindow(Windows.Window):
    def __init__(self):
        wpf.LoadComponent(self, xamlfile)

    @property
    def user_name(self):
        return self.textbox.Text

    def function_1(self, sender, args):
        UI.TaskDialog.Show(
            "Hello World",
            "Hello {}".format(self.user_name or 'World')
            )


# let's show the window (modal)
MyWindow().ShowDialog()
