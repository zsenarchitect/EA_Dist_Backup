import sys
sys.path.append("..\lib")
import EnneadTab
#!/usr/bin/python
# -*- coding: utf-8 -*-




def validating_jokes():
    with open("dad_jokes.txt", "r") as f:
    #import io
    #with io.open("dad_jokes.txt", encoding = "utf8") as f:
        lines = f.readlines()


    OUT = []
    for line in lines:
        #print "\n#######################"
        #print line
        if r"â€™" in line:
            print(line)
            print("find a bad string" + "*" * 50)
            line = line.replace(r"â€™", r"\'")
        if r"â??" in line:
            print(line)
            print("find a bad string" + "*" * 50)
            line = line.replace(r"â??", r"\"")
        if r".â" in line:
            print(line)
            print("find a bad string" + "*" * 50)
            line = line.replace(r".â", r"\"")
        if line.endswith("?"):
            print("find a questiong ending:" + "*" * 100)
            print(line)
        OUT.append(line)

    with open("dad_jokes.txt", "w") as f:
        f.writelines(OUT)




def random_joke():
    import random
    with open(r'L:\4b_Applied Computing\03_Rhino\12_EnneadTab for Rhino\Source Codes\Fun\jokes\dad_jokes.txt', "r") as f:
        lines = f.readlines()


    random.shuffle(lines)
    return lines[0].replace("\n", "")


@EnneadTab.ERROR_HANDLE.try_catch_error
def main():
    validating_jokes()
    print (random_joke())


############################################
if __name__ == "__main__":
    main()