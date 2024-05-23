import sys
sys.path.append("..\lib")
import EnneadTab
import webbrowser


def open_slope_calculator():
    path = r"https://rechneronline.de/slope/"
    webbrowser.open(path)


if __file__ == "__main__":
    open_slope_calculator()
