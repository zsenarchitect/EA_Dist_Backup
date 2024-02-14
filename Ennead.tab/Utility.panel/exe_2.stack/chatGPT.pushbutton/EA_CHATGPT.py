#### this has to run in python 3.x
import traceback
import os
import sys
sys.path.append(r'L:\4b_Applied Computing\03_Rhino\12_EnneadTab for Rhino\Source Codes\lib')
sys.path.append(r'L:\4b_Applied Computing\03_Rhino\12_EnneadTab for Rhino\Dependency Modules')

#import EnneadTab
#sys.path.append(EnneadTab.ENVIRONMENT.DEPENDENCY_FOLDER_LEGACY)


#from pyChatGPT import ChatGPT
import openai


def secure_folder(path):
    from os import makedirs as OS_MAKEDIRS
    try:
        OS_MAKEDIRS(path)

    except Exception as e:

        #print_note( "folder cannot be secured")
        #print_note(e)
        pass
    return path

def get_user_folder():
    from os import environ as OS_ENV
    #print OS_ENV["USERPROFILE"]
    return "{}\Documents".format(OS_ENV["USERPROFILE"])

def get_EA_setting_folder():
    folder = get_user_folder() + "\EnneadTab Settings"
    #print folder
    return secure_folder(folder)


def get_special_folder_in_EA_setting(folder_name):
    folder = get_EA_setting_folder() + "\{}".format(folder_name)
    return secure_folder(folder)

def get_EA_local_dump_folder():
    return get_special_folder_in_EA_setting("Local Copy Dump")


def read_json_as_dict(filepath):
    import json
    # reads it back
    with open(filepath,"r") as f:
      dict = json.load(f)
    return dict


def save_dict_to_json(dict, filepath):
    import json
    # write to a file
    with open(filepath,"w") as f:
      json.dump(dict, f)

def is_file_exist_in_folder(check_file_name, folder):
    import os

    for file_name in os.listdir(folder):
        #print_note(file_name)
        if check_file_name == file_name:
            return True
    return False


class PromptData:

    def __init__(self):
        file_name = "EA_COPILOT.json"
        dump_folder = get_EA_local_dump_folder()
        file_path = "{}\{}".format(dump_folder, file_name)
        if not is_file_exist_in_folder(file_name, dump_folder):
            return

        data = read_json_as_dict(file_path)
        if data["direction"] != "input":
            return
        self.session_token = data["session_token"]
        # Extract the recipient, sender email, and email content from the JSON data
        self.conversation_history = data["conversation_history"]
        #"The following is a conversation with an AI assistant for problems in Rhino and Revit. The assistant is helpful, creative, clever, friendly and very funny.\n\nYou: How do I create a sheet in Revit\nEnneadTab Copilot:"
        self.ai_name = data["ai_name"]
        self.human_name = data["human_name"]
        self.key_prompt = data["key_prompt"]

    def store(self):
        file_name = "EA_COPILOT.json"
        dump_folder = get_EA_local_dump_folder()
        file_path = "{}\{}".format(dump_folder, file_name)
        data = read_json_as_dict(file_path)
        """
        if self.ai_name in self.response:
            self.conversation_history += "{}".format(self.response)
        else:
            self.conversation_history += "\n{}{}".format(self.ai_name, self.response)
        """
        self.conversation_history += "{}".format( self.response)

        self.conversation_history += "\n\n"
        data["conversation_history"] = self.conversation_history
        data["direction"] = "output"
        print (self.conversation_history)
        """
        for attr in dir(self):
            if "__" in attr:
                continue
            data[attr] = getattr(self, attr)
        """


        save_dict_to_json(data, file_path)

    def process(self):



        openai.api_key =  self.session_token

        response = openai.Completion.create(model = "text-davinci-003",
                                            prompt = self.conversation_history,
                                            temperature = 0.9,
                                            max_tokens = 500,
                                            top_p = 1,
                                            frequency_penalty = 0.0,
                                            presence_penalty = 0.6,
                                            stop = ["Bye bye" ]# stop means when conversation encounter those items, it will stop generating .
                                            )
        print (response)
        self.response = response["choices"][0]["text"]



def main():
    data = PromptData()
    if not hasattr(data, "ai_name"):
        return
    data.process()
    data.store()


if __name__ == "__main__":
    try:
        main()
    except:
        error = traceback.format_exc()
        error_file = "{}\error_log.txt".format(get_EA_local_dump_folder())
        with open(error_file, "w") as f:
            f.write(error)
        import subprocess, os
        os.startfile(error_file)
