import sys
sys.path.append("..\lib")
import EnneadTab



def update_rhino_repo():
    EnneadTab.GIT.update_repo("EnneadTab-for-Rhino")




########################
if __name__ == "__main__":
    update_rhino_repo()
    print("Done")