
import sys
sys.path.append("..\lib")
import EnneadTab

@EnneadTab.ERROR_HANDLE.try_catch_error
def tell_a_joke():


    main_text = "Dad Joke of the day..."
    EnneadTab.RHINO.RHINO_FORMS.notification(main_text = main_text, sub_text = EnneadTab.FUN.JOKES.give_me_a_joke(talk = True), height = 200)

######################  main code below   #########
if __name__ == "__main__":

    tell_a_joke()

