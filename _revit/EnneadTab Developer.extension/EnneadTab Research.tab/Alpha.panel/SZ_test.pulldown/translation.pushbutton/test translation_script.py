__doc__ = "xxxxxxxxx"
__title__ = "test translation"

names= ["bulding level 14 floor plan","east elevation","enlarge plans", "enlarged east elevation","ns site section","north south elevations","east west section"]


#make all name low cap
print("---")

def find_num(string):
    temp = ""
    start_recording = False

    for charactor in string:
        if charactor.isdigit():
            temp += charactor

            start_recording = True
        if charactor == " " and start_recording == True:
            break

    return int(temp)


def num_to_cn(num):
    if num == 1:
        return "yi"
    elif num == 2:
        return "er"
    elif num == 4:
        return "si"
    else:
        return "jiu"

def add(original, symbol, text):
    i = original.find(symbol)
    return  original[:i]+text+original[i:]

def convert_level(name):
    if "roof"  in name:
        return "wudingjifang"
    i = name.find("level")
    for chara in name[i:]:
        print(chara)
    #print name.split("level")[1]
    num = find_num(name.split("level")[1])
    print(num)

    first_digit = num/10
    second_digit = num%10
    print(first_digit,second_digit)
    if first_digit == 0:
        pass



        #find number contaied by space
    #num%10=last diagit
    #num\10 if >0 = firstdigit
    #if lastdigit = 1, then yi
    #if first digit = 3, then sanshi
    return "xxxxceng"




def trans(name):
    translation = "@&$~"

    if "level" in name:
        level_name = convert_level(name)
        translation =add (translation, "&",level_name)

    if "plan" in name:
        translation =add (translation, "$","pingmiantu")
    elif "section" in name:
        translation =add (translation, "$","pomiantu")
    elif "elevation" in name:
        translation =add (translation, "$","limiantu")


    if "east" in name and "elevation" in name:
        translation =add (translation, "@","dong")
    elif "ns " in name or "north south" in name:
        translation =add (translation, "@","nanbeixiang")
    elif "ew " in name or "west east" in name or "east west" in name:
        translation =add (translation, "@","dongxixiang")



    if "site" in name:
        translation =add (translation, "&","changdi")

    if "enlarge" in name:
        translation =add (translation, "~","dayang")

    print(name + " = " + translation)



for name in names:
    trans(name)
