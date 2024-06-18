
import sys
sys.path.append("..\lib")
import EnneadTab
################################################################################
# SampleEtoViewports.py
# MIT License - Copyright (c) 2017 Robert McNeel & Associates.
# See License.md in the root of this repository for details.
################################################################################
import Rhino # pyright: ignore
import Eto # pyright: ignore

################################################################################
# Viewports dialog class
################################################################################
class ViewportsDialog(Eto.Forms.Dialog[bool]):

    # Initializer
    def __init__(self):
        # Initialize dialog box
        self.Title = 'Rhino Viewport in an Eto Control'
        self.Padding = Eto.Drawing.Padding(5)
        #self.Resizable = True
        #self.Height = 500
        self.Width = 1000
        # Create viewport controls
        m_viewport_control = Rhino.UI.Controls.ViewportControl
        print(Rhino.UI.Controls.ViewportControl.Viewport.Info)
        mode = Rhino.Display.DisplayModeDescription.ShadedId
        #m_viewport_control.Viewport.DisplayMode = mode;
        #m_viewport_control.Refresh()
        viewport0 = Rhino.UI.Controls.ViewportControl(Size = Eto.Drawing.Size(2000, 400))
        viewport1 = Rhino.UI.Controls.ViewportControl(Size = Eto.Drawing.Size(4000, 200))
        """
        if isolate object, then this viewport will zoom exltent around, make it more usefule.
        """
        
        # Create layout
        layout = Eto.Forms.StackLayout()
        layout.Padding = Eto.Drawing.Padding(5)
        layout.Spacing = 5
        layout.HorizontalContentAlignment = Eto.Forms.HorizontalAlignment.Stretch
        layout.Items.Add(viewport0)
        layout.Items.Add(viewport1)
        layout.Items.Add(None)
        layout.Items.Add(self.CloseButton())
        # Set the dialog content
        self.Content = layout
        
        EnneadTab.RHINO.RHINO_UI.apply_dark_style(self)

    # Close button click handler
    def OnCloseButtonClick(self, sender, e):
        self.Close(True)

    # Create button control
    def CloseButton(self):
        # Create the default button
        self.DefaultButton = Eto.Forms.Button(Text = 'Close')
        self.DefaultButton.Click += self.OnCloseButtonClick
        return self.DefaultButton

################################################################################
# Function to test the viewport dialog
################################################################################
@EnneadTab.ERROR_HANDLE.try_catch_error
def TestViewportsDialog():
    dlg = ViewportsDialog()
    dlg.ShowModal(Rhino.UI.RhinoEtoApp.MainWindow)

################################################################################
# Check to see if this file is being executed as the "main" python
# script instead of being used as a module by some other python script
# This allows us to use the module which ever way we want.
################################################################################
if __name__ == "__main__":
    TestViewportsDialog()
