#!/usr/bin/python
# -*- coding: utf-8 -*-
import ENVIRONMENT

import sys
sys.path.append(r'{}\Dependency Modules'.format(ENVIRONMENT.PUBLISH_FOLDER_FOR_RHINO))


def merge_pdfs(combined_pdf_file_path, list_of_filepaths, reorder = False):
    """merge multiple pdfs to single pdf.

    Args:
        combined_pdf_file_path (str): path for final product
        list_of_filepaths (list): list of l=path for the input pdfs
        reorder (bool, optional): reorder the pdf alphabetically. Defaults to False.
    """
    try:
        from PyPDF2 import PdfFileMerger
    except:
        pass
    merger = PdfFileMerger()

    if reorder:
        list_of_filepaths.sort()

    for filepath in list_of_filepaths:
        merger.append(filepath)

    merger.write(combined_pdf_file_path)
    merger.close()



#############
if __name__ == "__main__":
    print(__file__ + "   -----OK!")