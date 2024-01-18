JSON_KEY = "MESSENGER.json"
TESTING_FLAG = "TEMP_TESTING_MESSENGER.json"


import traceback
import os
import json
import time
import math

def log_error(error):
    error += "\n\n######If you have EnneadTab UI window open, just close the window. Do no more action, otherwise the program might crash.##########\n#########Not sure what to do? Msg Sen Zhang, you have dicovered a important bug and we need to fix it ASAP!!!!!########"
    error_file = "{}\Documents\EnneadTab Settings\Local Copy Dump\error_log.txt".format(
        os.environ["USERPROFILE"])

    with open(error_file, "w") as f:
        f.write(error)

        
try:

    import tkinter as tk
    from tkinter import ttk
    
except:
    error = traceback.format_exc()
    log_error(error)

    




    
def try_catch_error(func):
    def wrapper(*args, **kwargs):
        try:
            out = func(*args, **kwargs)
            return out
        except Exception as e:

            error = traceback.format_exc()

            log_error(error)
            
    return wrapper



def get_file_in_dump_folder( file):
    return "{}\\Documents\\EnneadTab Settings\\Local Copy Dump\\{}".format(os.environ["USERPROFILE"], file)



    
def read_json_as_dict_in_dump_folder(file):
    filepath = get_file_in_dump_folder(file)
    
    # return empty dict if file not exist
    if not os.path.exists(filepath):
        return {}
    
    # reads it back
    with open(filepath,"r") as f:
        try:
            dict = json.load(f)
        except ValueError:
            dict = {}
    return dict

def fake_test_data():
    filepath = get_file_in_dump_folder(JSON_KEY)

    sample = "this is a internal test"
    # sample = "this is a internal test\nABCDEFG"
    # sample = "this is a internal test\nABCDEFG\n12334495"
    sample = "this is a internal test\nABCDEFG\n12334495\noionefono"
    image = "C:\\Users\\szhang\\github\\EnneadTab-for-Revit\\ENNEAD.extension\\lib\\EnneadTab\\images\\surprised_face.png"
    image = None
    image = "C:\\Users\\szhang\\github\\EnneadTab-for-Revit\\ENNEAD.extension\\Ennead.tab\\Utility.panel\\exe_2.stack\\duck_pop\\doraAmon_small.png"
    
    dict = {"main_text":sample,
            "height" : 150 + sample.count("\n") * 40,
            "image":image}
    
    with open(filepath,"w") as f:
        json.dump(dict, f)



class MessageApp:
    # @try_catch_error
    def __init__(self, text,
                 animation_in_duration,
                 animation_stay_duration,
                 animation_fade_duration,
                 width,
                 height,
                 image,
                 x_offset = 0):

        self.window = tk.Tk()
        self.window.iconify()
        # self.window.title("EnneadTab messenger")

        # self.window.attributes("-topmost", True)
        self.window.deiconify()
        self.begining_time = time.time()

        self.window_width = width
        self.window_height = height
        self.x = self.get_screen_width() // 2 - self.window_width//2 + x_offset
        self.y_final = self.get_screen_height() - self.window_height
        self.y_initial = self.get_screen_height()

        # 100x100 size window, location 700, 500. No space between + and numbers
        self.window.geometry("{}x{}+{}+{}".format(self.window_width,
                                                  self.window_height,
                                                  self.x,
                                                  self.y_initial))

        self.style = ttk.Style()
        self.style.configure(
            "Rounded.TLabel",
            background="dark grey",
            borderwidth=60,
            # relief="solid",
            foreground="white",
            font=("Comic Sans MS", 20),
            outline="blue",
            bordercolor="orange",
            padding=20,
            anchor="center",
        )

        if image:
            print (image)
            self.image = tk.PhotoImage(file = image, format="PNG")
            self.image_bubble = tk.Label(self.window, image = self.image, bd = 0)
            self.image_bubble.pack(padx =50)
            self.y_final -= self.image.height()
            self.window_height += self.image.height()

        self.talk_bubble = ttk.Label(
            self.window, text=text, style="Rounded.TLabel"
        )
        # pady ====> pad in Y direction
        self.talk_bubble.pack(pady=5)

        # set the window to have transparent background, only show the label
        self.window.config(background="green")
        self.window.wm_attributes('-transparentcolor', 'green')
        self.window.wm_attributes('-topmost', True)
        self.window.overrideredirect(True)

        self.animation_in_duration = animation_in_duration  # Animation duration in seconds
        # Time to stay visible in seconds
        self.animation_stay_duration = animation_stay_duration
        self.animation_fade_duration = animation_fade_duration  # Fade duration in seconds

        self.window.after(1, self.update)

    # @try_catch_error
    def update(self):
        # kill the app if running for more than total s .
        time_passed = time.time() - self.begining_time
        # print(time_passed)
        if time_passed > (self.animation_in_duration + self.animation_stay_duration + self.animation_fade_duration + 2):
            self.window.destroy()
            return

        if time_passed < self.animation_in_duration:
            progress = time_passed / self.animation_in_duration
            eased_progress = 1 - math.pow(1 - progress, 4)  # Ease-out function
            y = int(self.y_initial - eased_progress *
                    (self.y_initial - self.y_final))

            self.window.geometry("{}x{}+{}+{}".format(self.window_width,
                                                      self.window_height,
                                                      self.x,
                                                      y))

        elif time_passed > self.animation_in_duration + self.animation_stay_duration:
            progress = (time_passed - self.animation_in_duration -
                        self.animation_stay_duration) / self.animation_fade_duration
            opacity = 1.0 - progress
            self.window.attributes("-alpha", opacity)
            # print(opacity)

        self.window.after(1, self.update)

    def run(self):
        self.window.mainloop()

    def get_screen_width(self):
        return self.window.winfo_screenwidth()

    def get_screen_height(self):
        return self.window.winfo_screenheight()


#@try_catch_error-----------------> TO-DO: add silent email error method.
def pop_message():
    print ("working")
    INTERNAL_TEST = os.path.exists(get_file_in_dump_folder(TESTING_FLAG))
    if INTERNAL_TEST:
        fake_test_data()
    
    
    data = read_json_as_dict_in_dump_folder(JSON_KEY)
    if data is None or "main_text" not in data.keys():
        print ("Nothing")
        return
    
    app = MessageApp(text = data["main_text"],
                     animation_in_duration = data.get("animation_in_duration", 0.5),
                     animation_stay_duration = data.get("animation_stay_duration",5),
                     animation_fade_duration = data.get("animation_fade_duration", 2),
                     width = data.get("width", 800),
                     height = data.get("height", 150),
                     image = data.get("image", None),
                     x_offset= data.get("x_offset", 0))
    app.run()
    
    if os.path.exists(get_file_in_dump_folder(JSON_KEY)):
        try:
            os.remove(get_file_in_dump_folder(JSON_KEY))
        except:
            print (traceback.format_exc())

    print ("done")

########################################
if __name__ == "__main__":
    pop_message()
