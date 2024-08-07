
import DATA_FILE
import FOLDER
import USER

from CONFIG import GLOBAL_SETTING_FILE

@FOLDER.backup_data(GLOBAL_SETTING_FILE , "setting")
def update_money(coin_change):
    with DATA_FILE.update_data(GLOBAL_SETTING_FILE) as data:
        
        if "money" not in data.keys():
            data["money"] = 100
        data["money"] += coin_change
        return data["money"]
    
def get_money():
    return update_money(0)


def daily_reward():
    pass


def print_leader_board():
    pass

def print_history():
    pass

def manual_transaction():
    pass


def get_data_by_name():
    pass

def set_data_by_name():
    pass