
import sys



sys.path.append("..\lib")
import EnneadTab

sys.path.append(EnneadTab.ENVIRONMENT.DEPENDENCY_FOLDER_LEGACY)





@EnneadTab.ERROR_HANDLE.try_catch_error
def temp():
    unicode_string = u'\u8fd0\u8425\u6b66\u6c49\u4e1a\u52a1\u4e2d\u5fc3'
    print (unicode_string)
    print (unicode_string.encode('utf-8'))
    print(EnneadTab.UNICODE.convert_unicode_to_string(unicode_string.encode('utf-8')))


######################  main code below   #########
if __name__ == "__main__":

    temp()
