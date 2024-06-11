__doc__ = "DO NOT USE, use new exporter tool."
__title__ = "[obsolete]19_PDF and DWG exporter"

from pyrevit import forms, DB, revit, script
import os
import os.path as op
import time
import System



def remove_extra_dot():
    file_names = os.listdir(fix_folder)
    for file_name in file_names:
        if ".." in file_name:
            try:
                os.rename(op.join(fix_folder, file_name),op.join(fix_folder, file_name.replace("..", ".")))
            except:
                print("skip {}".format(file_name))


def delete_extra_file(basefolder, key_ext):
    filenames = os.listdir(basefolder)
    PCP_file_found = False
    count = 0
    for current_file in filenames:
        ext = op.splitext(current_file)[1].upper()
        if ext == key_ext:
            os.remove(op.join(basefolder, current_file))
            count+=1
    return count


def get_export_setting(doc, setting_name = "Empty"):
    existing_dwg_settings = DB.FilteredElementCollector(doc)\
                                .OfClass(DB.ExportDWGSettings)\
                                .WhereElementIsNotElementType()\
                                .ToElements()


    def pick_from_setting():
        sel_setting = None
        while sel_setting == None:
            sel_setting = forms.SelectFromList.show(existing_dwg_settings, \
                                                    name_attr = "Name", \
                                                    button_name='always use setting with this name for this export job', \
                                                    title = "Select existing Export Setting.")
            if sel_setting == None:
                forms.alert("You didn't select any export setting. Try again.")
            else:
                break

        return sel_setting



    if setting_name == "Empty":##trying to defin the setting for the first time
        sel_setting = pick_from_setting()

    else:####trying to match a setting name from input
        sel_setting = None
        for setting in existing_dwg_settings:
            if setting.Name == setting_name:
                sel_setting = setting
                break
        if sel_setting == None:
            forms.alert("Cannot find setting with same name to match [{}], please manual select".format(setting_name))
            sel_setting = pick_from_setting()


    return sel_setting


def export_DWG_from_sheet(sheet, doc):
    print("-----")
    time_start = time.time()

    file_name = "{} - {}".format(sheet.SheetNumber, sheet.Name)
    if has_index:
        file_name = index_dict[sheet.SheetNumber] + "_" + file_name


    print("preparing [{}].dwg".format(file_name))

    #print_manager.PrintToFileName = r"{}\{}.dwg".format(output_folder, file_name)
    #print print_manager.PrintToFileName


    sheet_as_collection = System.Collections.Generic.List[DB.ElementId]([sheet.Id])



    while True:
        try:
            doc.Export(output_folder, file_name, sheet_as_collection, DWG_option)
            print("ok")
            break
        except Exception as e:
            if  "The files already exist!" in e:
                file_name = file_name + "_same name"
                #new_name = print_manager.PrintToFileName = r"{}\{}.pdf".format(output_folder, file_name)
                output.print_md("------**There is a file existing with same name, will attempt to save as {}**".format(new_name))

            else:
                print (e)
    time_end = time.time()
    print_time("sheet to DWG", time_end, time_start)


def print_PDF_from_sheet(sheet, print_manager):
    #global print_manager
    print("-----")
    time_start = time.time()

    file_name = "{} - {}".format(sheet.SheetNumber, sheet.Name)
    if has_index:
        file_name = index_dict[sheet.SheetNumber] + "_" + file_name


    print("preparing [{}].pdf".format(file_name))
    print_manager.PrintToFileName = r"{}\{}.pdf".format(output_folder, file_name)
    #print_manager.Apply()
    #print print_manager.PrintToFileName
    while True:
        try:
            print_manager.SubmitPrint(sheet)
            print("ok")
            break
        except Exception as e:
            if  "The files already exist!" in e:
                file_name = file_name + "_same name"
                new_name = print_manager.PrintToFileName = r"{}\{}.pdf".format(output_folder, file_name)
                output.print_md("------**There is a file existing with same name, will attempt to save as {}**".format(new_name))

            else:
                print (e)
    time_end = time.time()
    print_time("sheet to PDF", time_end, time_start)


def print_time(title, time_end, time_start, use_minutes = False):
    if not use_minutes:
        output.print_md("{} takes **{}** seconds".format(title, time_end - time_start))
        return
    mins = int((time_end - time_start)/60)
    output.print_md("{} takes **{}** mins".format(title, mins))


def is_sheet_in_current_issue_para(sheet):

    #print key_para
    #print sheet.Name
    #print sheet.LookupParameter(key_para).AsString()
    if sheet.LookupParameter("Sheet Note").AsString() == "Not Shared":
        return False
    if sheet.LookupParameter("Sheet Note").AsString() == "DD":
        return False


    try:
        if sheet.LookupParameter(key_para).AsString() == u"\u25A0":
            #print "qqqq"
            return True
        else:
            return False
    except Exception as e:
        print (e)
        return False


def get_sheets_from_doc(doc):

    sheets = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Sheets).WhereElementIsNotElementType().ToElements()
    return filter(is_sheet_in_current_issue_para, sheets)


def export_content_in_doc(doc):

    time_start = time.time()
    output.print_md("##Currently printing from {}".format(doc.Title))
    sheets = get_sheets_from_doc(doc)

    global sheet_count
    sheet_count += len(sheets)
    #sheets.extend(get_sheets_from_doc(doc))

    """
    for sheet in sheets:
        print(sheet.Name)
    """


    #test sheets
    #sheets = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_Sheets).WhereElementIsNotElementType().ToElements()
    #sheets = list(sheets)[10:15]
    print("*"*20)
    print("Below are sheets that will be printed.....")
    for sheet in sheets:
        print("\t{} - {}".format(sheet.SheetNumber, sheet.Name))
    print("*"*20)
    #script.exit()


    #get print setting
    if export_pdf:
        #global print_manager
        print_manager = doc.PrintManager
        print_manager.PrintToFile = True
        print_manager.SelectNewPrintDriver("Bluebeam PDF")
        #print_manager.Apply()

    if export_dwg:
        global DWG_option
        DWG_export_setting = get_export_setting(doc, export_setting_name)
        DWG_option = DB.DWGExportOptions().GetPredefinedOptions(doc, DWG_export_setting.Name)

    counter = 0
    total = len(sheets)
    if export_dwg and export_pdf:
        total *= 2


    pb_title = "Working on {}......".format(doc.Title)
    with forms.ProgressBar(title = "exporting sheet....{value} of {max_value}", step = 1, cancellable = True) as pb:
        for sheet in sheets:
            if pb.cancelled:
                break
            if export_pdf:
                print_PDF_from_sheet(sheet, print_manager)
                counter += 1
                pb.update_progress(counter, total)
            if export_dwg:
                export_DWG_from_sheet(sheet, doc)
                counter += 1
                pb.update_progress(counter, total)


    time_end = time.time()
    print_time("print {} ".format(doc.Title), time_end, time_start, use_minutes = True)




    #script.exit()


def show_setting_helper():
    output.print_md( "open your **bluebeam administrator**(not the bluebeam viewer)")
    print("on the printer tab, \n\t-disable 'prompt for file name'\n\t-disable 'open in viewer'\n\nShould look like this below.")
    img_path = script.get_bundle_file("bluebeam admin setting.png")
    output.set_height(1000)
    output.print_image(img_path)
    print(r"The pdf will likely to print to a default location regardless the output folder you picker earlier, but that is ok, let it run by it self and come back later. On most cases they will populate at the 'User/Documents' folder")


def index_all_sheets(docs):
    sheets = []
    for doc in docs:
        sheets.extend( get_sheets_from_doc(doc) )

    """
    sheets.sort(key = lambda x: x.LookupParameter("MC_$PlotID").AsString(), reverse = False)
    sheets.sort(key = lambda x: x.LookupParameter("Sheet_$Order").AsString(), reverse = False)
    sheets.sort(key = lambda x: x.SheetNumber, reverse = False)
    """

    sheets.sort(key = lambda x: (x.LookupParameter("MC_$PlotID").AsString() ,
                                x.LookupParameter("Sheet_$Order").AsInteger(),
                                x.SheetNumber), reverse = False)

    """
    for sheet in sheets:
        print("******")
        print(sheet.LookupParameter("MC_$PlotID").AsString(), sheet.LookupParameter("Sheet_$Order").AsInteger(), sheet.SheetNumber)
    """

    global index_dict
    for i, sheet in enumerate(sheets):
        index_dict[sheet.SheetNumber] = "{0:03}".format(i + 1)


    print("--------indexing all the sheets including file not printing now.--------")
    sorted_dict = sorted(index_dict.items(), key = lambda x: x[1])
    #print sorted_dict
    for key, value in sorted_dict:
        print("[{}] ---> {}".format(key, value))
    print("-------- end of index--------")

    #script.exit()
    return index_dict




def proceed_all_sheets():
    #select from linked docs, including my main doc
    revit_links = DB.FilteredElementCollector(revit.doc).OfClass(DB.RevitLinkInstance).WhereElementIsNotElementType().ToElements()
    #for link in revit_links:
        #print link
    open_docs = revit.doc.Application.Documents
    for open_doc in open_docs:
        #print "***"
        #print open_doc.Title
        #print open_doc.IsLinked
        if not open_doc.IsLinked:
            main_doc = open_doc

    """
    for revit_link in revit_links:
        print("----")
        print(revit_link.Name)
        print(revit.doc.GetElement(revit_link.GetTypeId()).IsNestedLink)
    #script.exit()
    """



    all_docs = [x.GetLinkDocument() for x in revit_links]#.insert(0, revit.doc)
    all_docs.insert(0, revit.doc)
    for doc in all_docs:
        if not hasattr(doc, "Title"):
            forms.alert("there are revit link not loaded. This action will cancel.")
            script.exit()


    """
    class MyOption(forms.TemplateListItem):
        @property
        def name(self):
            if self.Title == main_doc.Title:
                return self.Title
            else:
                return "{} _ limited graphic, no inner link graphic".format(self.Title)

    all_docs = [MyOption(x) for x in all_docs]
    docs = forms.SelectFromList.show(all_docs, multiselect = True)

    for x in docs:
        print(doc)
    """

    temp_list = []
    for doc in all_docs:
        if doc.Title == main_doc.Title:
            temp_list.append(doc.Title)
        else:
            temp_list.append("{} _ limited graphic, no inner link graphic".format(doc.Title))

    docs_names = forms.SelectFromList.show(temp_list, multiselect = True)
    #print docs_names
    docs_names = [x.split(" _ ")[0] for x in docs_names]
    #print docs_names
    docs = []
    for doc in all_docs:
        #print doc.Title
        if doc.Title in docs_names:
            docs.append(doc)
    """
    for doc in docs:
        print(doc)
    """

    """
    docs = forms.SelectFromList.show(all_docs, name_attr = "Title", multiselect = True)
    for x in docs:
        print(doc)
    """



    global key_para
    #select the sheets by which issue black squere satus?
    para_names = [r"Issue 2021/12/31",\
                    r"Issue 2022/01/15",\
                    r"Issue 2022/02/25",\
                    r"Issue 2022/03/10"]
    key_para = forms.ask_for_one_item(para_names, default=para_names[-1], prompt = "pick a issue", title = None)




    global output_folder
    #get save folder
    output_folder = forms.pick_folder(title = "folder for the output PDF, best if you can create a empty folder")
    #print output_folder


    global has_index
    index_options = ["Index_SheetNum - SheetName", "SheetNum - SheetName"]
    index_opt = forms.alert("Do you want to add index prefix to PDF name so you when you combine they go by order?", options = index_options)
    if index_opt == index_options[0]:
        has_index = True
        index_all_sheets(all_docs)
    else:
        has_index = False



    global export_dwg
    global export_pdf
    file_types = ["pdf Only", "dwg Only", "pdf + dwg"] ### maybe add image as export option
    file_export_type = forms.alert("What to export", options = file_types)
    if "pdf" in file_export_type:
        export_pdf = True
    if "dwg" in file_export_type:
        export_dwg = True
        global export_setting_name
        export_setting_name = get_export_setting(revit.doc, export_setting_name).Name



    time_start = time.time()



    for doc in docs:
        t = DB.Transaction(doc, "temp change")
        t.Start()

        #testing to force make inner link as attachment

        print("---epxanding the inner link in the document {}, will temperorily make attachement link".format(doc.Title))
        inner_links = DB.FilteredElementCollector(doc).OfClass(DB.RevitLinkInstance).WhereElementIsNotElementType().ToElements()
        for inner_link in inner_links:

            print("nesting link = {}".format(inner_link.Name))
            link_type = doc.GetElement(inner_link.GetTypeId())
            print(link_type.AttachmentType)
            link_type.AttachmentType = DB.AttachmentType.Attachment
            print(link_type.AttachmentType)
            print(link_type.GetLinkedFileStatus())
            print(link_type.IsNestedLink)
            #print inner_link.

            #linktype = doc.GetElement(inner_link.GetTypeId())
            #if linktype.IsNestedLink:
            try:
                link_type.Reload()
                print("reload finish")
            except Exception as e:

                print (e)
        print("--------------")

        export_content_in_doc(doc)
        print("finish temp transaction: overlay --> attached link")
        t.RollBack()


    time_end = time.time()
    print("#"*20)
    print("all sheets from selected revit files have been printed.")
    print_time("print {} sheets".format(sheet_count), time_end, time_start, use_minutes = True)

    if "yes" == forms.alert("end of printing. \nSave a print log?", options = ["yes", "no"]):

        output.save_contents(forms.save_file( file_ext = "html"))


################## main code below #####################
output = script.get_output()
output.close_others()
key_para = "temp"
sheet_count = 0
output_folder = "temp"
has_index = False
index_dict = {}
export_pdf = False
export_dwg = False
export_setting_name = "Empty"
DWG_option = ""
#print_manager = ""

action_options = [ "print sheets from all models, (by clicking this it is assumed you have recently reload link to lastest info)",
                    "delete .PS and .PCP files",
                    "tell me how to prevent bluebeam file name dialog from showing up on every file",
                    "cancel action"]
action = forms.alert("pick a action:", options = action_options, sub_msg = "if the views contains nested link as overlay, the inner link will not be loaded.\n\nWHICH MEANS LINK WILL SHOW ON EXPORT, BUT NESTING LINK WILL NOT.\n\nThis is a becasue overlay link does not load initlaly, and cannot be loaded by API when opended to multiple doucments.\nFor best reseult, I suggest only output from actual file instead of from link. But the index name is still a helpful feature.")



if action == action_options[0]:
    proceed_all_sheets()

elif action == action_options[1]:
    fix_folder = forms.pick_folder(title = "folder to fix extra dot")
    remove_extra_dot()
    pcp_count = delete_extra_file(fix_folder,".PCP") #if self.clearPCP else 0
    ps_count = delete_extra_file(fix_folder,".PS") #if self.clearPS else 0
    script.exit()
elif action == action_options[2]:
    show_setting_helper()
    script.exit()
else:
    script.exit()
