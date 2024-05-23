import sys
sys.path.append("..\lib")
import EnneadTab


@EnneadTab.ERROR_HANDLE.try_catch_error
def main():


    EnneadTab.VERSION_CONTROL.publish_Rhino_python_file()



if  __name__ == "__main__" :

    main()
