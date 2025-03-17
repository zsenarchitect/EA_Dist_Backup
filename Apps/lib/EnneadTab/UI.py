DATA_FILE_NAME = "progressbar.sexyDuck"

import DATA_FILE
import EXE
import NOTIFICATION
import time
import SOUND

class ProgressBarManager:
    def __init__(self, items=None, title="Processing...", label_func = None):
        self.items = items if items is not None else []
        self.title = title
        self.total = len(self.items) if items is not None else 100
        self.counter = 0
        self.current_item = None
        self.label_func = label_func
        self.start_time = time.time()
        

    def update(self, amount=1):
        self.counter += amount

        progress = (float(self.counter) / float(self.total)) * 100
  
        if self.label_func is not None:
            label = self.label_func(self.current_item)
        else:
            label = "Processing item {}".format(self.counter)
        data = {
            "progress": progress,
            "is_active": True,
            "label": label,
            "start_time": self.start_time,
            "counter": self.counter,
            "total": self.total
        }

        DATA_FILE.set_data(data,DATA_FILE_NAME)



    def __enter__(self):
        # Start the progress bar in a separate process
        start_progressbar()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Clean up
        kill_progressbar()
        SOUND.play_finished_sound()
  





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
            progress.current_item = item
            func(item)
            progress.update()




def kill_progressbar():
    DATA_FILE.set_data({"is_active":False}, DATA_FILE_NAME)


def start_progressbar():
    EXE.try_open_app("ProgressBar", safe_open=True)

def unit_test():
    import time
    import random
    test_products = [
        "UltraGlow Pro X1000",
        "QuickSlice Master",
        "DreamWeaver Elite",
        "PowerFlex 360",
        "SmartHome Hub Plus",
        "EcoClean Supreme",
        "TechMaster 2000",
        "ComfortZone Deluxe",
        "SpeedBrew Max",
        "FitTracker Prime",
        "AquaPure Filter",
        "SoundWave Elite",
        "ChefMate Pro",
        "LuxLight Diamond",
        "GreenThumb Helper",
        "CloudSync Station",
        "VitaBlend Master",
        "SafeGuard Plus",
        "EnergyBoost Ultra",
        "CleanAir Premium",
        "WorkFlow Elite",
        "HomeGuard Pro",
        "SleepMaster Deluxe",
        "SmartScale Connect",
        "PetCare Premium",
        "GardenPro Tools",
        "BrainBoost Focus",
        "FreshKeep Elite",
        "TimeSaver Pro",
        "BeautyGlow Max",
        "KidSafe Guardian",
        "SportsFlex Ultra",
        "CoolBreeze Plus",
        "MindCalm Essential",
        "TravelMate Pro",
        "EasyClean Master",
        "HealthTrack Elite",
        "SmartCook Helper",
        "PowerBank Ultra",
        "HomeFit Studio",
        "WaterWise Plus",
        "NightGuard Pro",
        "StudyBuddy Max",
        "EcoFresh Prime",
        "WorkStation Elite",
        "SafeSleep Plus",
        "QuickCharge Pro",
        "MealPrep Master",
        "SmartView Display",
        "PetPlay Premium",
        "GymMaster Pro",
        "BabyGuard Elite",
        "CleanBot 3000",
        "SoundPod Ultra",
        "CareCraft Plus",
        "EasyLife Helper",
        "SmartLock Pro",
        "FitnessFuel Max",
        "HomeStyle Elite",
        "TechGuard Plus",
        "EcoSmart Prime",
        "WorkPro Station",
        "LifeTrack Master",
        "CoolComfort Pro",
        "SmartBrew Elite",
        "SafeSpace Plus",
        "PowerTool Ultra",
        "HealthMate Pro",
        "EasyOrganize Max",
        "SmartWatch Prime",
        "PetCare Deluxe",
        "GardenMaster Elite",
        "BrainTrain Plus",
        "FreshFood Pro",
        "TimeKeeper Ultra",
        "BeautyPro Master",
        "KidPlay Premium",
        "SportsMaster Elite",
        "CoolZone Plus",
        "MindFocus Pro",
        "TravelPro Elite",
        "EasyClean Ultra",
        "HealthGuard Max",
        "SmartHome Premium",
        "PowerMax Elite",
        "HomeFit Plus",
        "WaterPure Pro",
        "NightRest Ultra",
        "StudyMaster Elite",
        "EcoClean Prime",
        "WorkSpace Plus",
        "SafeGuard Ultra",
        "QuickFix Pro",
        "MealMaster Elite",
        "SmartScreen Plus",
        "PetCare Ultra",
        "GymPro Elite",
        "Babycare Premium",
        "CleanMaster Pro",
        "SoundBox Ultra",
        "CareKit Elite",
        "EasyLife Plus",
        "SmartSecurity Pro",
        "FitnessMax Ultra",
        "HomeStyle Premium"
    ]
    def test_func(item):
        run_time = random.randint(1,10)/10.0
        time.sleep(run_time)
        print("simluate running product [{}] took {:.1f}s".format(item, run_time))


    def label_func(item):
        return ("Dummy Processing item [{}]".format(item))
    progress_bar(test_products, test_func, label_func = label_func, title = "Iternating through items")
    






# Example usage
if __name__ == "__main__":
    NOTIFICATION.messenger("See terminal option")
    print("\nWhat would you like to do?")
    print("1. Run unit test")
    print("2. Kill progress bar")
    print ("3. Start Dummy progress bar")
    

    choice = input("Enter 1 or 2 or 3: ").strip()
    
    if choice == "1":
        unit_test()
        kill_progressbar()
    elif choice == "2":
        kill_progressbar()
    elif choice == "3":
        start_progressbar()
    else:
        print("Invalid choice. Please enter 1 or 2.")
