#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
EnneadTab REVIT Export Module

This module provides comprehensive export functionality for Revit documents, supporting:
- PDF export with configurable color and paper size settings
- DWG export with customizable export settings
- Image export (JPG) with resolution control
- Batch export capabilities with file organization

Key Features:
- Smart print setting detection based on sheet properties
- Multiple export methods for PDF to handle different scenarios
- Support for view-on-sheet exports
- Automatic file naming and organization
- PDF combination utilities
- Robust error handling and retry mechanisms

Dependencies:
    - pyrevit
    - Autodesk.Revit.DB
    - EnneadTab modules: FOLDER, IMAGE, DATA_CONVERSION, PDF, ERROR_HANDLE

Note:
    This module is part of the EnneadTab toolkit and requires Revit API access.
"""

import os
import sys
root_folder = os.path.abspath((os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(root_folder)

import FOLDER
import IMAGE
import DATA_CONVERSION
import PDF
import ERROR_HANDLE

try:
    from pyrevit import script # pyright: ignore
    from Autodesk.Revit import DB # pyright: ignore

except :

    pass

def print_time(title, time_end, time_start, use_minutes = False):
    output = script.get_output()
    if not use_minutes:
        foot_note = "{} seconds".format( time_end - time_start)
        output.print_md("{} takes **{}** seconds".format(title, time_end - time_start))
        return foot_note
    mins = int((time_end - time_start)/60)
    output.print_md("{} takes **{}** mins".format(title, mins))
    foot_note = "{} mins".format( mins)
    return foot_note


def get_print_setting(doc, is_color_by_sheet, is_color = True, is_A1_paper = True):
    """Retrieves appropriate print settings based on color and paper size preferences.

    Args:
        doc (DB.Document): Active Revit document
        is_color_by_sheet (bool): Whether to use sheet-specific color settings
        is_color (bool, optional): Use color printing. Defaults to True.
        is_A1_paper (bool, optional): Use A1 paper size. Defaults to True.

    Returns:
        DB.PrintSetting: Selected print setting matching the specified criteria
    """


    all_print_settings = DB.FilteredElementCollector(doc).OfClass(DB.PrintSetting)

    if is_color_by_sheet:
        is_color = False

    if is_color:
        all_print_settings = filter(lambda x: "COLOR" in x.Name, all_print_settings)
    else:
        all_print_settings = filter(lambda x: "GRAYSCALE" in x.Name, all_print_settings)

    if is_A1_paper:
        all_print_settings = filter(lambda x: "A1" in x.Name, all_print_settings)
    else:
        all_print_settings = filter(lambda x: "A0" in x.Name, all_print_settings)

    #print all_print_settings[0].Name
    if len(all_print_settings) > 0:
        return all_print_settings[0]
    print ("!!!Cannot find print setting that has 'COLOR/GRAYSCALE' or 'A1/A0' in it. Use default")
    return DB.FilteredElementCollector(doc).OfClass(DB.PrintSetting).FirstElement()

def export_pdf(view_or_sheet, file_name, output_folder, is_color_by_sheet):
    """Exports a view or sheet to PDF using optimal export method.

    The function attempts multiple export methods to ensure successful export:
    - Method 1: Uses PrintManager with Bluebeam PDF printer
    - Method 2: Uses native PDF export with custom naming rules

    Args:
        view_or_sheet (DB.View | DB.ViewSheet): View or sheet to export
        file_name (str): Target filename (without .pdf extension)
        output_folder (str): Output directory path
        is_color_by_sheet (bool): Whether to use sheet-specific color settings

    Returns:
        str: Name of exported PDF file
    """
    doc = view_or_sheet.Document


    def override_blue_lines():
        pass

    def dry_transaction_decorator(f):
        def warper():
            t = DB.Transaction(doc, "dry T")
            t.Start()
            f()
            t.RollBack()
        return warper



    def pdf_method_1():
        #  ----- method 1 -----
        print ("$$$ Trying method 1")
        t = DB.Transaction(doc, "temp")
        t.Start()


        titleBlock = DB.FilteredElementCollector(doc, view_or_sheet.Id).OfCategory(DB.BuiltInCategory.OST_TitleBlocks).FirstElement()
        #print titleBlock.Symbol.Family.Name


        print_manager = doc.PrintManager
        print_manager.PrintToFile = True
        #print_manager.IsVirtual = True
        print_manager.SelectNewPrintDriver("Bluebeam PDF")
        # print_manager.Apply()

        if view_or_sheet.LookupParameter("Print_In_Color"):
            sheet_use_color = view_or_sheet.LookupParameter("Print_In_Color").AsInteger()
        else:
            sheet_use_color = 0
            print ("Cannot find 'Print_In_Color' in sheet para...Use NO color as default.")
        print_manager.PrintSetup.CurrentPrintSetting = get_print_setting(doc,
                                                                        is_color_by_sheet,
                                                                        is_color = sheet_use_color,
                                                                        is_A1_paper = "A1" in titleBlock.Symbol.Family.Name)
        # print_manager.Apply()
        #t.Commit()
        #"""
        print ("Print Setting Name = [{}]".format(print_manager.PrintSetup.CurrentPrintSetting.Name))
        print_manager.PrintToFileName = r"{}\{}.pdf".format(output_folder, file_name)
        print_manager.PrintRange = DB.PrintRange.Select
        view_set = DB.ViewSet()
        view_set.Insert(view_or_sheet)
        try:
            print_manager.ViewSheetSetting.InSession.Views = view_set
        except:
            print ("InSession ViewSheetSet failed, trying with CurrentViewSheetSet...")
            print_manager.ViewSheetSetting.CurrentViewSheetSet.Views = view_set
        # print_manager.Apply()
        # t.Commit()
        #print print_manager.PrintToFileName

        """might be important again"""
        #reactivate_output()

        while True:
            try:
                try:
                    print_manager.SubmitPrint(view_or_sheet)
                except:
                    print ("2nd method")
                    print_manager.SubmitPrint()
                print ("PDF export succesfully")
                break
            except Exception as e:
                if  "The files already exist!" in e:
                    raw_name = file_name + "_same name"
                    new_name = print_manager.PrintToFileName = r"{}\{}.pdf".format(output_folder, file_name)
                    print ("------**There is a file existing with same name, will attempt to save as {}**".format(new_name))

                elif "no views/sheets selected" in e:
                    print (e)
                    print ("...")
                    print (print_manager.PrintToFileName)
                    print ("problem sheet = {}".format(view_or_sheet.Name))
                    has_non_print_sheet = True
                else:
                    print (e)
                    print (print_manager.PrintToFileName)
                    print ("problem sheet = {}".format(view_or_sheet.Name))
                break

        t.RollBack()
        #print t.GetStatus()

        """might be important again"""
        #cleanup_pdf_name()
        FOLDER.secure_filename_in_folder(output_folder, file_name, ".pdf")

        print ("$$$ end method 1")

    def pdf_method_2():
        #  ----- method 2 -----
        #print "$$$ Trying method 2"

        sheet_list = DATA_CONVERSION.list_to_system_list([view_or_sheet.Id])


        pdf_options = DB.PDFExportOptions ()
        pdf_options.Combine = False



        name_rule = pdf_options.GetNamingRule ()
        #print name_rule

        sheet_num_para_data = DB.TableCellCombinedParameterData.Create()
        sheet_num_para_data.ParamId = DB.ElementId(DB.BuiltInParameter.SHEET_NUMBER)
        if len(file_name.split(view_or_sheet.SheetNumber)) == 1:
            sheet_num_para_data.Prefix = ""
        else:
            sheet_num_para_data.Prefix = file_name.split(view_or_sheet.SheetNumber)[0]
        sheet_num_para_data.Separator = " - "

        sheet_name_para_data = DB.TableCellCombinedParameterData.Create()
        sheet_name_para_data.ParamId = DB.ElementId(DB.BuiltInParameter.SHEET_NAME)

        # IList<TableCellCombinedParameterData> GetNamingRule()
        new_rule = [sheet_num_para_data, sheet_name_para_data]
        new_rule = DATA_CONVERSION.list_to_system_list(new_rule, type = "TableCellCombinedParameterData", use_IList = False)
        pdf_options.SetNamingRule(new_rule)

        if view_or_sheet.LookupParameter("Print_In_Color"):
            sheet_color_setting = view_or_sheet.LookupParameter("Print_In_Color").AsInteger()
        else:
            sheet_color_setting = 0

        if not is_color_by_sheet:
            sheet_color_setting = 0
        if sheet_color_setting:
            pdf_options.ColorDepth = DB.ColorDepthType.Color
        else:
            pdf_options.ColorDepth = DB.ColorDepthType.GrayScale

        #pdf_options.ExportPaperFormat = DB.ExportPaperFormat.Default


        doc.Export(output_folder, sheet_list, pdf_options)
        #print "$$$ end method 2"


    pdf_method_2()
    return file_name + ".pdf"




def export_dwg(view_or_sheet, file_name, output_folder, dwg_setting_name, is_export_view_on_sheet = False):
    """Exports views or sheets to DWG format with specified settings.

    Features:
    - Supports both individual view/sheet export and view-on-sheet export
    - Automatic file naming based on sheet information
    - Retry mechanism for failed exports
    - Cleanup of temporary files

    Args:
        view_or_sheet (DB.View | DB.ViewSheet): View or sheet to export
        file_name (str): Target filename (without .dwg extension)
        output_folder (str): Output directory path
        dwg_setting_name (str): Name of DWG export settings to use
        is_export_view_on_sheet (bool, optional): Export individual views from sheets. Defaults to False.

    Returns:
        list: List of exported DWG filenames
    """
    files_exported = []
    doc = view_or_sheet.Document

    if is_export_view_on_sheet and view_or_sheet.ViewType.ToString() == "DrawingSheet":
        view_ids = view_or_sheet.GetAllPlacedViews()
        #useful_sheet_count = 0
        for view_id in view_ids:
            view = doc.GetElement(view_id)

            if view.ViewType.ToString() in [ "Legend","Schedule", "Rendering"]:
                continue

            if "{3D" in view.Name:
                continue

            #useful_sheet_count += 1
            detail_num_para_id = DB.BuiltInParameter.VIEWPORT_DETAIL_NUMBER
            detail_num = view.Parameter[detail_num_para_id].AsString() #get view detail num
            title_para_id = DB.BuiltInParameter.VIEW_DESCRIPTION
            title = view.Parameter[title_para_id].AsString() #get view title

            # prefix is that [2]_123_
            if len(file_name.split(view_or_sheet.SheetNumber)) == 1:
                prefix = ""
            else:
                prefix = file_name.split(view_or_sheet.SheetNumber)[0]

            view_file_name = "{}{}_{}_{}_[View On Sheet]".format(prefix, view_or_sheet.SheetNumber, detail_num, title)

            print ("Exporting view on sheet: {}.dwg".format(view_file_name))
            dwg_file = export_dwg(view, view_file_name, output_folder, dwg_setting_name, is_export_view_on_sheet)
            files_exported.extend(dwg_file)

    #DWG_export_setting = get_export_setting(doc, export_setting_name)
    DWG_option = DB.DWGExportOptions().GetPredefinedOptions(doc, dwg_setting_name)
    view_as_collection = DATA_CONVERSION.list_to_system_list([view_or_sheet.Id])
    max_attempt = 10
    attempt = 0
    while True:
        if attempt > max_attempt:
            print  ("Give up on <{}>, too many failed attempts, see reason above.".format(file_name))
            #global failed_export
            #failed_export.append(file_name)
            break
        attempt += 1
        try:
            doc.Export(output_folder, r"{}".format(file_name), view_as_collection, DWG_option)
            #print "DWG export succesfully: " + file_name
            break
        except Exception as e:
            if  "The files already exist!" in e:
                file_name = file_name + "_same name"
                #new_name = print_manager.PrintToFileName = r"{}\{}.pdf".format(output_folder, file_name)
                print("------**There is a file existing with same name, will attempt to save as {}**".format(file_name))

            else:
                print (e)
    FOLDER.cleanup_folder_by_extension(folder = output_folder, extension = ".pcp")
    files_exported.append(file_name + ".dwg")
    return files_exported



def export_image(view_or_sheet, file_name_naked, output_folder, is_thumbnail = False, resolution = 6000, is_color_by_sheet = True):
    """Exports views or sheets to JPG format with configurable settings.

    Features:
    - Configurable resolution for both thumbnails and full-size exports
    - Support for color/grayscale conversion based on sheet settings
    - Automatic file management and cleanup
    - Retry mechanism for failed exports

    Args:
        view_or_sheet (DB.View | DB.ViewSheet): View or sheet to export
        file_name (str): Target filename (without .jpg extension)
        output_folder (str): Output directory path
        is_thumbnail (bool, optional): Create smaller thumbnail version. Defaults to False.
        resolution (int, optional): Image resolution in pixels. Defaults to 6000.
        is_color_by_sheet (bool, optional): Use sheet-specific color settings. Defaults to True.

    Returns:
        str: Name of exported JPG file if successful, False otherwise
    """
    
    doc = view_or_sheet.Document



    opts = DB.ImageExportOptions()
    try:
        opts.FilePath = output_folder + '\\{}.jpg'.format(file_name_naked)
    except:
        print ("Error in export_image: {}".format(file_name_naked))
        return False
    

        
    opts.ImageResolution = DB.ImageResolution.DPI_300
    opts.ExportRange = DB.ExportRange.SetOfViews
    opts.ZoomType = DB.ZoomFitType.FitToPage

    opts.PixelSize = 1200 if is_thumbnail else resolution

    opts.SetViewsAndSheets(DATA_CONVERSION.list_to_system_list([view_or_sheet.Id]))

    attempt = 0
    max_attempt = 5
    if os.path.exists(opts.FilePath):
        try:
            os.remove(opts.FilePath)
        except:
            pass
        
        
    while True:
        if attempt > max_attempt:
            print  ("Give up on <{}>, too many failed attempts, see reason above.".format(file_name_naked))
            return False
            
        attempt += 1

        try:

            doc.ExportImage(opts)
            # print ("Image export succesfully")

            break
        except Exception as e:
            if  "The files already exist!" in str(e):
                file_name_naked = file_name_naked + "_same name"
                opts.FilePath = output_folder + '\\{}.jpg'.format(file_name_naked)
                #new_name = print_manager.PrintToFileName = r"{}\{}.pdf".format(output_folder, file_name)
                print("------**There is a file existing with same name, will attempt to save as {}**".format(file_name_naked))

            else:
                print( e.message)

                
    # FOLDER.secure_filename_in_folder(output_folder, file_name_naked, ".jpg")
    # import time
    # while True:
    #     if os.path.exists(opts.FilePath):
    #         try:
    #             with open(opts.FilePath, "rb") as f:
    #                 pass
    #             break
    #         except:
    #             pass
    #     time.sleep(0.5)
 

    if view_or_sheet.LookupParameter("Print_In_Color"):
        sheet_is_colored = view_or_sheet.LookupParameter("Print_In_Color").AsInteger() == 1
    else:
        sheet_is_colored = False

    if not is_color_by_sheet:
        sheet_is_colored = False
    if not sheet_is_colored:
        file_path = "{}\\{}.jpg".format(output_folder, file_name_naked)
        try:
            IMAGE.convert_image_to_greyscale(file_path)
        except:
            bw_file = "{}\\{}_BW.jpg".format(output_folder, file_name_naked)
            try:
                IMAGE.convert_image_to_greyscale(file_path, bw_file)
                os.remove(file_path)
                os.rename(bw_file, file_path)
            except:
                import traceback
                ERROR_HANDLE.print_note(traceback.format_exc())
                return "{}_BW.jpg".format(file_name_naked)
        
    return file_name_naked + ".jpg"


                    
def combine_final_pdf(output_folder, files_exported_for_this_issue, combined_pdf_name, copy_folder = None):
    """Combines multiple PDFs into a single document with optional backup.

    Args:
        output_folder (str): Directory containing source PDFs
        files_exported_for_this_issue (list): List of PDF filenames to combine
        combined_pdf_name (str): Name for combined PDF file
        copy_folder (str, optional): Backup directory path. Defaults to None.
    """

    list_of_filepaths = []
    files = os.listdir(output_folder)

    for file in files:
        if ".pdf" not in file.lower():
            continue

        if file in files_exported_for_this_issue:
            file_path = os.path.join(output_folder, file)
            print ("--combining PDF: {}".format(file_path))
            list_of_filepaths.append(file_path)

    combined_pdf_file_path = "{}\{}.pdf".format(output_folder, combined_pdf_name)
    PDF.pdfs2pdf(combined_pdf_file_path, list_of_filepaths, reorder = True)
    if copy_folder:
        FOLDER.copy_file_to_folder(combined_pdf_file_path, copy_folder)


def dump_exported_files_to_copy_folder(output_folder, files_exported_for_this_issue, file_id_dict, copy_folder):
    """Organizes exported files into a structured directory hierarchy.

    Creates a organized directory structure based on file types and plot IDs:
    - PDFs/[plot_id]/
    - DWGs/[plot_id]/
    - JPGs/[plot_id]/

    Args:
        output_folder (str): Source directory containing exported files
        files_exported_for_this_issue (list): List of files to organize
        file_id_dict (dict): Mapping of filenames to plot IDs
        copy_folder (str): Root directory for organized file structure
    """


    for file in os.listdir(output_folder):
        if file in files_exported_for_this_issue:
            file_path = os.path.join(output_folder, file)


            try:
                plot_id = file_id_dict[file]
            except:
                plot_id = "Missing"



            if ".pdf" in file.lower():
                if plot_id:
                    new_folder = "{}\{}\PDFs".format(copy_folder, plot_id)
                else:
                    new_folder = "{}\PDFs".format(copy_folder)
                new_folder = FOLDER.secure_folder(new_folder)

            elif ".dwg" in file.lower():
                if plot_id:
                    new_folder = "{}\{}\DWGs".format(copy_folder, plot_id)
                else:
                    new_folder = "{}\DWGs".format(copy_folder)
                new_folder = FOLDER.secure_folder(new_folder)

            elif ".jpg" in file.lower():
                if plot_id:
                    new_folder = "{}\{}\JPGs".format(copy_folder, plot_id)
                else:
                    new_folder = "{}\JPGs".format(copy_folder)
                new_folder = FOLDER.secure_folder(new_folder)

            else:
                new_folder = copy_folder[:]

            FOLDER.copy_file_to_folder(file_path, new_folder, handle_BW_file = True)