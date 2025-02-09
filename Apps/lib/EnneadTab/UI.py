

DATA_FILE_NAME = "progressbar.sexyDuck"

import DATA_FILE
import EXE



class ProgressBarManager:
    def __init__(self, items=None, title="Processing...", label_func = None):
        self.items = items if items is not None else []
        self.title = title
        self.total = len(self.items) if items is not None else 100
        self.current_progress = 0
        self.label_func = label_func

        

    def update(self, amount=1):
        self.current_progress += amount

        progress = (self.current_progress / self.total) * 100
        if self.label_func is not None:
            label = self.label_func(self.current_progress)
        else:
            label = f"Processing item {self.current_progress}"
        data = {
            "progress": progress,
            "is_active": True,
            "label": label
        }

        DATA_FILE.set_data(data,DATA_FILE_NAME)



    def __enter__(self):
        # Start the progress bar in a separate process
        EXE.try_open_app("ProgressBar")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Clean up
        kill_progressbar()
  





def progress_bar(items, func, label_func = None, title="Iterating through items"):
    """Process items with the given function while showing a progress bar.
    
    Args:
        items: Iterable of items to process
        func: Function to apply to each item
        title: Title to display on the progress bar
        label_func: Function to generate a label for each item

    Example:
    def test_func(item):
        time.sleep(random.randint(1,10)/10)
        print(item)

    def label_func(item):
        return ("Processing item {}".format(item))


    progress_bar(items, func, label_func = label_func, title = "Iternating through items")

    
    """
    with ProgressBarManager(items=items, title=title, label_func=label_func) as progress:

        for item in items:
            func(item)
            progress.update()

def kill_progressbar():
    DATA_FILE.set_data({"is_active":False}, DATA_FILE_NAME)


def unit_test():
    import time
    import random
    items = list(range(1000))
    def test_func(item):
        time.sleep(random.randint(1,10)/10)
        print(item)

    def label_func(item):
        return ("Processing item {}".format(item))
    progress_bar(items, test_func, label_func = label_func, title = "Iternating through items")
    






# Example usage
if __name__ == "__main__":
    # unit_test()
    kill_progressbar()
