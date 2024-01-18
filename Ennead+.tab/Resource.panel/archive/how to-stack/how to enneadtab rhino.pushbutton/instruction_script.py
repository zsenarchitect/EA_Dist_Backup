__doc__ = "Instruction on how to get EnneadTab for Rhino on your computer, or your teammate's computer."
__title__ = "How to Install EnneadTab for Rhino"
__context__ = 'zero-doc'

from pyrevit import forms, DB, revit, script



################## main code below #####################
output = script.get_output()
output.close_others()
script.open_url("https://ei.ennead.com/toolbox/BIMManual_01/20.1.9_EnneadTab%20For%20Rhino.aspx")
"""
#print "Follow instruction below to add EnneadTab for Rhino. Loadd it from toolbar layout or..."
image = script.get_bundle_file("instruction4.png")
output.print_image(image)
output.print_md("##Step 1: Just drag and drop the .rui file to your active Rhino window. Please don't dock it elsewhere.")
print "\n\n\n\n"

image = script.get_bundle_file("instruction3.png")
output.print_image(image)
output.print_md("##Step 2: Immediately after drag and drop, use this button 'User: Get Latest EnneadTab' to establish shortcuts and command lines.")
output.print_md("##Step 3: Done. Small updates will happen automatically.")
print "\n\n\n\n"
print "It is a seperate entity from the Revit cousin, and it functions indepedently from Revit, though tools that helps to prepare Rhino before/after Revit are being considered.\n\nLike most python script in Rhino, the first run of any tool in each Rhino session takes slight delay(about 1 second but noticable) so the python is compiled. But after that it will be very very fast to initiate."
print "\n\nNote: Unlike Revit EnneadTab that auto update to L drive, Rhino EnneadTab (after you dock it to with other tabs) will be copied to your local rui. file and lose connection to L drive. So please dont dock it else where.\n\nTo get lastest toolbar, go to the top menu and do 'User: Get Latest', or type 'GetLatestEnneadTab' in Rhino command line."


print "\n\n\n\n"

output.set_width(1000)
output.set_height(800)
output.center()
"""
import ENNEAD_LOG
ENNEAD_LOG.use_enneadtab(coin_change = 99, tool_used = "How to install EnneadTab for Rhino.", show_toast = True)
