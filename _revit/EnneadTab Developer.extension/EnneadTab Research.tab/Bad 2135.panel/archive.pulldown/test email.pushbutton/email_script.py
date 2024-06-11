__doc__ = "Send email to me. DO NOT USE."
__title__ = "Test email"

from pyrevit import script #


import EA_UTILITY
import EnneadTab




"""
from pyrevit import HOST_APP
doc = HOST_APP.doc
uidoc = HOST_APP.uidoc
"""

################## main code below #####################
output = script.get_output()
output.close_others()

body = "test body test"

EA_UTILITY.send_email(contacts = ["szhang@ennead.com"],
                        body = body)
