__doc__ = "Copy selected view templates to other open models."
__title__ = "Copy Selected Template\nTo Other Open Docs"
#pylint: disable=import-error,invalid-name
from pyrevit import revit
from pyrevit import forms
from Autodesk.Revit import DB # pyright: ignore
import ENNEAD_LOG
doc = __revit__.ActiveUIDocument.Document # pyright: ignore


def copy_view_template():
    selected_viewtemplates = forms.select_viewtemplates(doc = doc)
    if not selected_viewtemplates:
        return
    t = DB.Transaction(doc, "temp")
    t.Start()
    for template in selected_viewtemplates:
        template.Name += "_Transfered from doc_{}".format(doc.Title)

    dest_docs = forms.select_open_docs(title = 'Select Destination Documents')
    if not dest_docs:
        return

    for ddoc in dest_docs:
        with revit.Transaction('Copy View Templates', doc = ddoc):
            revit.create.copy_viewtemplates(selected_viewtemplates,
                                            src_doc = doc,
                                            dest_doc = ddoc)
    t.RollBack()




####################################
if __name__ == "__main__":
    copy_view_template()
    ENNEAD_LOG.use_enneadtab(coin_change = 20, tool_used = __title__.replace("\n", " "), show_toast = True)
