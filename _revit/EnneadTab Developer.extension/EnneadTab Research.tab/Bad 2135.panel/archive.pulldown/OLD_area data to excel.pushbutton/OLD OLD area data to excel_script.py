OTHERS__doc__ = "DO NOT USE, use newer data to excel tool."
__title__ = "OLD_DO NOT USE_area to excel"

from pyrevit import forms, DB, revit, script
import xlsxwriter as xw
import EA_UTILITY
import EnneadTab



def find_level_row_in_excel(level):
    level_num = level.Name.split("LEVEL")[1].replace("(REFUGE)","")
    initial_row = 7
    return initial_row + int(level_num) - 1


def find_area_definition_column_in_excel(area):
    department_name = area.LookupParameter("Area Department").AsString()
    area_name = area.LookupParameter("Name").AsString()




    bad_area_found = False
    if department_name == "RETAIL":
        column =  0
    elif department_name == "OFFICE":
        column = 1
    elif department_name == "VISITOR CENTER":
        column = 2
        if area_name == "VISITOR LOBBY":
            column += 0
        elif area_name == "VISITOR IMAGE DISPLAY":
            column += 1
        elif area_name == "VISITOR CONFERENCE":
            column += 2
        elif area_name == "VISITOR TRAINING":
            column += 3
        elif area_name == "VISITOR FRIENDS RECEPTION":
            column += 4
        elif area_name == "VISITOR ROUND THEATER":
            column += 5
        elif area_name == "VIP/GR LOBBY":
            column += 6
        elif area_name == "VIP/GR MEETING":
            column += 7
        else:
            bad_area_found = True
    elif department_name == "SUPPORT":
        column = 10
        if area_name == "TRAINING":
            column += 0
        elif  area_name in ["MULTIFUNCTION HALL", "MULTIFUNCTION HALL DOUBLE HEIGHT"]:
            column += 1
        elif area_name == "SERVICE CENTER":
            column += 2
        elif area_name == "GYM":
            column += 3
        elif area_name == "LEISURE SPACE":
            column += 4
        else:
            bad_area_found = True
    elif department_name == "PUBLIC CIRCULATION":
        column = 15
    elif department_name == "OTHERS":
        column = 16
    else:
        bad_area_found = True
        column = 20

    if bad_area_found:
        print("area department:area name = '{}':'{}'.  Not found in chart".format(department_name, area_name))

    initial_column = 2
    return initial_column + column



class data_item():
    def __init__(self, area):
        self.area_num = area.Area * area.LookupParameter("MC_$Discount Ratio").AsDouble()
        self.area_obj = area
        self.row = find_level_row_in_excel(area.Level)
        self.column = find_area_definition_column_in_excel(area)

    def update_data_item_area(self, new_area):
        #print "$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$adding more area to data item-----------"
        self.area_num += new_area.Area * new_area.LookupParameter("MC_$Discount Ratio").AsDouble()

    def print_data_detail(self):
        print("data item detail:{};{}:{}..row:{}...column:{} ---{}".format(self.area_obj.Level.Name,
                                                    self.area_obj.LookupParameter("Area Department").AsString(),
                                                    self.area_obj.LookupParameter("Name").AsString(),
                                                    self.row,
                                                    self.column,
                                                    EA_UTILITY.sqft_to_sqm(self.area_num)))





def get_all_areas_in_GFA_scheme(doc = revit.doc):
    all_areas = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Areas).WhereElementIsNotElementType().ToElements()
    return filter(lambda x: x.AreaScheme.Name == "Gross Building", all_areas)

def not_in_use_get_areas_by_department_by_doc(department_name, doc = revit.doc):
    GFA_scheme_areas = get_all_areas_in_GFA_scheme(doc)
    """
    for area in GFA_scheme_areas:
        print(area.LookupParameter("Area Department").AsString())
    """
    return filter(lambda x: x.LookupParameter("Area Department").AsString() == department_name, GFA_scheme_areas)

def alert_bad_areas(department_name_checklist, area_name_checklist, area_name_exception, doc = revit.doc):

    area_name_checklist.extend(area_name_exception)
    GFA_scheme_areas = get_all_areas_in_GFA_scheme(doc)
    bad_area_count = 0
    for area in GFA_scheme_areas:

        if area.LookupParameter("Area Department").AsString() not in department_name_checklist or area.LookupParameter("Name").AsString() not in area_name_checklist:
            print("------------This are item below cannot find place in chart -------------")
            print_area_detail(area)
            bad_area_count += 1
    if bad_area_count != 0 :
        forms.alert("There are {} area with department name or area name not defined. See output window for details".format(bad_area_count))



def is_area_similar_to_data_item(area, data):

    if data.area_obj.Level.Name != area.Level.Name:
        return False
    if data.area_obj.LookupParameter("Area Department").AsString() != area.LookupParameter("Area Department").AsString():
        return False

    if data.area_obj.LookupParameter("Area Department").AsString() not in ["RETAIL", "OFFICE", "PUBLIC CIRCULATION", "OTHERS"]:
        if data.area_obj.LookupParameter("Name").AsString() != area.LookupParameter("Name").AsString():
            return False
    #print "----------------------------------------------------------find similar"
    return True

def print_area_detail(area):
    print("area detail: {};{}:{}--{}".format(area.Level.Name, area.LookupParameter("Area Department").AsString(), area.LookupParameter("Name").AsString(), EA_UTILITY.sqft_to_sqm(area.Area * area.LookupParameter("MC_$Discount Ratio").AsDouble())))



def not_in_use_get_color_format(data):
    cell_format_retail = workbook.add_format({'bg_color' : '#FFC000'})
    cell_format_office = workbook.add_format({'bg_color' : '#DDEBF7'})
    cell_format_visitorcenter = workbook.add_format({'bg_color' : '#F8CBAD'})
    cell_format_support = workbook.add_format({'bg_color' : '#FFE699'})
    cell_format_extra = workbook.add_format({'bg_color' : '#DC9090'})
    cell_format_bad = workbook.add_format({'bg_color' : '#f44336'})

    department = data.area_obj.LookupParameter("Area Department")
    if department == "OFFICE":
        return cell_format_office
    elif department == "RETAIL":
        return cell_format_retail
    elif department == "VISITOR CENTER":
        return cell_format_visitorcenter
    elif department == "SUPPORT":
        return cell_format_support
    elif department == "OTHERS":
        return cell_format_extra
    else:
        return cell_format_bad


def write_data_item(worksheet, data):

    #cell_format = get_color_format(data)
    worksheet.write(data.row,
                    data.column,
                    float("{:.2f}".format(EA_UTILITY.sqft_to_sqm(data.area_num))))

def write_header(worksheet, area_name_checklist):
    header = area_name_checklist
    for i in range(len(header)):
        if i == 0:
            format = workbook.add_format({'bg_color' : '#FFC000'})
        elif i == 1:
            format = workbook.add_format({'bg_color' : '#DDEBF7'})
        elif i <= 9:
            format = workbook.add_format({'bg_color' : '#F8CBAD'})
        elif i <= 14:
            format = workbook.add_format({'bg_color' : '#FFE699'})
        elif i <= 15:
            format = workbook.add_format({'bg_color' : '#b5c6ba'})
        else:
            format = workbook.add_format({'bg_color' : '#DC9090'})

        worksheet.write(6, i + 2, header[i], format)
        worksheet.set_column(i +2,i+2, 1.3 * max( len(header[i]), 5))



def write_levels(worksheet):
    cell_format = workbook.add_format()
    cell_format.set_bg_color('#808080')
    for i in range(1, 33):
        worksheet.write(i+6, 1 ,  "level {}".format(i), cell_format)
################## main code below #####################
output = script.get_output()
output.close_others()

area_name_checklist = ["RETAIL",
                        "OFFICE",
                        "VISITOR LOBBY",##
                        "VISITOR IMAGE DISPLAY",
                        "VISITOR CONFERENCE",
                        "VISITOR TRAINING",
                        "VISITOR FRIENDS RECEPTION",
                        "VISITOR ROUND THEATER",
                        "VIP/GR LOBBY",
                        "VIP/GR MEETING",
                        "TRAINING",##
                        "MULTIFUNCTION HALL",
                        "SERVICE CENTER",
                        "GYM",
                        "LEISURE SPACE",
                        "PUBLIC CIRCULATION",##
                        "OTHERS"]##
department_name_checklist =  ["RETAIL", "OFFICE", "VISITOR CENTER", "SUPPORT", "OTHERS","PUBLIC CIRCULATION"]
area_name_exception = ["MULTIFUNCTION HALL DOUBLE HEIGHT", "OFFICE CORE"]
"""
for department in area_departments:
    print(get_areas_by_department_by_doc(department))
    print("*"*20)
"""
data_collection = []
safety = 0
for area in get_all_areas_in_GFA_scheme():
    safety += 1
    if safety > 1500:
        break


    #print_area_detail(area)
    #print "---"
    '''
    if area.LookupParameter("Name").AsString() in area_name_exception:
        continue
    '''
    if len(data_collection) == 0:
        data_collection.append(data_item(area))
        continue

    found_similar = False
    for data in data_collection:
        #data.print_data_detail()
        if is_area_similar_to_data_item(area, data):
            #print "find similar"
            data.update_data_item_area(area)
            found_similar = True
            break
        else:
            #print "data item not similar, keep looking"
            #keep looking
            pass
    if not found_similar:
        #print "no similar data found, adding to collection"
        data_collection.append(data_item(area))




# Create a workbook and add a worksheet.
#forms.save_excel_file()
file_location = forms.save_excel_file()
workbook = xw.Workbook(file_location)
worksheet = workbook.add_worksheet("N3 AREA CHART")

#print data_collection
print("*"*50)
for data in data_collection:
    data.print_data_detail()
    write_data_item(worksheet, data)



write_levels(worksheet)
write_header(worksheet, area_name_checklist)
try:
    workbook.close()
    forms.alert("Excel saved at '{}'".format(file_location))
except:
    forms.alert("the excel file you picked is still open, cannot override. Writing cancelled.")


alert_bad_areas(department_name_checklist, area_name_checklist, area_name_exception)






"""
# Some data we want to write to the worksheet.
expenses = (['Rent', 1000],
            ['Gas',   100],
            ['Food',  300],
            ['Gym',    50])

# Start from the first cell. Rows and columns are zero indexed.
row = 0
col = 0

# Iterate over the data and write it out row by row.
for item, cost in (expenses):
    worksheet.write(row, col,     item)
    worksheet.write(row, col + 1, cost)
    row += 1

# Write a total using a formula.
worksheet.write(row, 0, 'Total')
worksheet.write(row, 1, '=SUM(B1:B4)')

workbook.close()

print("done")
"""
