"""Remove selected revisions from selected sheets."""

from pyrevit import revit, DB
from pyrevit import forms
from pyrevit import script
from pyrevit.framework import List
from pyrevit.revit.db import query



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



if __name__== "__main__":
    logger = script.get_logger()


    revisions = forms.select_revisions(button_name='Select Revision',
                                    multiple=True)

    logger.debug(revisions)


    if revisions:
        sheets = forms.select_sheets(button_name='Remove Revisions',
                                    include_placeholder=True)
        if sheets:
            with revit.Transaction('Remove Revision from Sheets'):

                updated_sheets = update_sheet_revisions(revisions,
                                                        sheets,
                                                        state=False)
            if updated_sheets:
                print('SELECTED REVISION REMOVED FROM THESE SHEETS:')
                print('-' * 100)
                cloudedsheets = []
                for s in sheets:
                    if s in updated_sheets:
                        revit.report.print_sheet(s)
                    else:
                        cloudedsheets.append(s)
            else:
                cloudedsheets = sheets

            if len(cloudedsheets) > 0:
                print('\n\nSELECTED REVISION IS CLOUDED ON THESE SHEETS '
                    'AND CAN NOT BE REMOVED.')
                print('-' * 100)

                for s in cloudedsheets:
                    revit.report.print_sheet(s)
