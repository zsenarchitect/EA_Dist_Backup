
import ENVIRONMENT

import sys
sys.path.append(ENVIRONMENT.DEPENDENCY_FOLDER)
try:
    from termcolor import colored
except:
    pass
from COLOR import TextColor
    

def wrapped_text(text, max_len = 70):

    import textwrap as TW
    wrapper = TW.TextWrapper(width = max_len)
    temp = ""
    for line in wrapper.wrap(text):
        temp += line + "\n"
    return temp



def colored_text(text, color, on_color=None, attrs=None):
    """Colorize text.

    Available text colors:
        red, green, yellow, blue, magenta, cyan, white.

    Available text highlights:
        on_red, on_green, on_yellow, on_blue, on_magenta, on_cyan, on_white.

    Available attributes:
        bold, dark, underline, blink, reverse, concealed.

    Example:
        colored('Hello, World!', 'red', 'on_grey', ['blue', 'blink'])
        colored('Hello, World!', 'green')
    """

    
    if "colored" not in globals():
        # in some terminal run, it cannot read the dependecy folder so cannot load the colored moudle
        return text
    return colored(text, color, on_color, attrs)

def unit_test():
    print(colored_text("hello EnneadTab", TextColor.Red) + " " + colored_text("hello EnneadTab", TextColor.Green))
    print(colored_text("hello EnneadTab", TextColor.Blue))
    print(colored_text("hello EnneadTab", TextColor.Blue, "on_magenta"))
    print(colored_text("hello EnneadTab", TextColor.Yellow))
    print(colored_text("hello EnneadTab", TextColor.Magenta))
    print(colored_text("hello EnneadTab", TextColor.Cyan))
    
    print(colored_text("hello EnneadTab", TextColor.White))


def centered_text(text):
  
    return '<p style="text-align: center;">{}</p>'.format(text)

if __name__ == "__main__":
   
    unit_test()
    

    