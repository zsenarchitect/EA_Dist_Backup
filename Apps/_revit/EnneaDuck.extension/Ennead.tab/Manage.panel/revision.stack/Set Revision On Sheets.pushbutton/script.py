"""Set selected revisions on selected sheets."""

from pyrevit import revit, DB
from pyrevit import forms
from pyrevit import script
from pyrevit.framework import List
from pyrevit.revit.db import query

revisions = forms.select_revisions(button_name='Select Revision',
                                   multiple=True)


def update_sheet_revisions(revisions, sheets=None, state=True):
    doc = revit.doc
    # make sure revisions is a list
    if not isinstance(revisions, list):
        revisions = [revisions]

    updated_sheets = []
    if revisions:
        # get sheets if not available
        for sheet in sheets or query.get_sheets(doc=doc):
            addrevs = set([x.IntegerValue
                           for x in sheet.GetAdditionalRevisionIds()])
            for rev in revisions:
                # skip issued revisions

                if state:
                    addrevs.add(rev.Id.IntegerValue)
                elif rev.Id.IntegerValue in addrevs:
                    addrevs.remove(rev.Id.IntegerValue)

            rev_elids = [DB.ElementId(x) for x in addrevs]
            sheet.SetAdditionalRevisionIds(List[DB.ElementId](rev_elids))
            updated_sheets.append(sheet)

    return updated_sheets

if revisions:
    sheets = forms.select_sheets(button_name='Set Revision',
                                 include_placeholder=True)
    if sheets:
        with revit.Transaction('Set Revision on Sheets'):
            updated_sheets = update_sheet_revisions(revisions,
                                                    sheets)
        if updated_sheets:
            print('SELECTED REVISION ADDED TO THESE SHEETS:')
            print('-' * 100)
            for s in updated_sheets:
                snum = s.Parameter[DB.BuiltInParameter.SHEET_NUMBER]\
                        .AsString().rjust(10)
                sname = s.Parameter[DB.BuiltInParameter.SHEET_NAME]\
                         .AsString().ljust(50)
                print('NUMBER: {0}   NAME:{1}'.format(snum, sname))


if __name__== "__main__":
    pass