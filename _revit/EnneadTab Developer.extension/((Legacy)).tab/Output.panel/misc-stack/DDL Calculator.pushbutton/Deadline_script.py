
__doc__ = "calculator ddl."
__title__ = "DDL\nCalculator"

from pyrevit import forms, script
from datetime import date

ddl_date = forms.ask_for_date(title = "When is your deadline??")
if not ddl_date:
    script.exit()

diff_date = -( date.today() - ddl_date ).days
display_text = "There is {} days until the deadline.".format(diff_date)
if diff_date < 0:
    display_text = "Deadline Passed."
elif diff_date == 0:
    display_text = "Today!!!!"
elif diff_date == 1:
    display_text = "There is less than 24 hours until the deadline."
elif 1 < diff_date <= 3:
    display_text += "\nAHHH!!!!!"

forms.alert(display_text)
