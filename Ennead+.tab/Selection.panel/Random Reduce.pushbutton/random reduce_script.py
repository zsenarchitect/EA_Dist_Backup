
from pyrevit import revit, DB
from pyrevit import script
from pyrevit import forms

import random

__title__ = "Randomly Reduce\nPanel Selection"
__doc__ = 'Randomly deselect from selection input. Most likely to be used in curtain panels.\n\nUse shift click to randomly reduce all kinds of elements.'


'''
list = [1,2,3,4,5,6]
print list[:len(list)]
'''


if __name__== "__main__":
	selection = list(revit.get_selection())
	if not selection:
		forms.alert("Please selection some elements first.")
		script.exit()
	if __shiftclick__:
		pass
	else:
		selection = [x for x in selection if x.Category.Name == "Curtain Panels"]

	keep_rate = forms.ask_for_string( default = "75", prompt = "The percentage that will remain afterward.", title = "Keeping Rate")

	try:
		keep_rate = int(keep_rate)
	except:
		forms.alert("Please use integer value.\nFor example, input 75 means keep 75% by the end.")
		script.exit()

	'''
	if isinstance(keep_rate, int) == False:
	'''


	limit = int( (keep_rate / 100.0) * len(selection)  )
	random.shuffle(selection)

	selection_reduced = selection[:limit]

	revit.get_selection().set_to(selection_reduced)






	'''

	selection = revit.get_selection()
	selected_id = [x.Id.IntegerValue for x in selection]

	keep_rate = 70# in percetage
	limit = int( (keep_rate / 100.0) * len(selection)  )
	random.shuffle(selected_id)


	selection_id_reduced = selected_id[:limit]

	elements = [DB.ElementId(item) for item in selection_id_reduced]

	revit.get_selection().set_to(elements)
	'''
