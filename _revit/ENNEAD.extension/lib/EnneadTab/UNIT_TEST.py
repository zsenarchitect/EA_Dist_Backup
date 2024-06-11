try:
    import imp
except:
    pass
import os
import traceback

import ENVIRONMENT_CONSTANTS
import NOTIFICATION
import USER
import ENVIRONMENT


IGNORE_LIST = ["desktop_pet",
               "desktop_pet_V2",
               "desktop_pet_V3",
               "desktop pet_V2_failed",
               "GIT_UPDATER"]

class UnitTest:
    def __init__(self):

        self.count = 0
        
        
    def try_run_unit_test(self, module):
        import TEXT
        print ("\n--{}:\nImport module [{}] Successfully".format(self.count,
                                                                 print_text_in_highlight_color(module.__name__)))
        self.count += 1
        if not hasattr(module, 'unit_test'):
            return
        test_func = getattr(module, 'unit_test')
        if not callable(test_func):
            return
        
        print(print_text_in_highlight_color('Running unit test for module <{}>'.format(module.__name__)))
        try:
            test_func()
            print ("OK!")
        except AssertionError as e:
            print ("Assertion Error! There is some unexpected results in the test")
            print (traceback.format_exc())
        
    def process_folder(self, folder):
        if not os.path.isdir(folder):
            return

        

        
        for module_file in os.listdir(folder):
            module_path = os.path.join(folder, module_file)
            if "archive" in module_path.lower():
                return
            
            if os.path.isdir(module_path):
                self.process_folder(module_path)
                continue
            if not module_file.endswith('.py'):
                continue
            module_name = module_file.split('.')[0]
            if module_name in IGNORE_LIST:
                continue
            try:
                module = imp.load_source(module_name, module_path)
                # module_spec = importlib.util.spec_from_file_location(module_name, module_path)
                # module = importlib.util.module_from_spec(module_spec)
                # module_spec.loader.exec_module(module)
            except Exception as e:
                NOTIFICATION.messenger(main_text = "Something is worng when importing [{}]".format(module_name))
                print ("\n\nSomething is worng when importing [{}] becasue:\n\n++++++{}++++++\n\n\n".format(module_name,
                                                                                            traceback.format_exc()))
                
                continue
            
            self.try_run_unit_test(module)

def print_boolean_in_color(bool):
    if not ENVIRONMENT_CONSTANTS.is_terminal_environment():
        return bool
    
    import TEXT
    if bool:
        return TEXT.colored_text("True", TEXT.TextColor.Green)
    else:
        return TEXT.colored_text("False", TEXT.TextColor.Red)  

def print_text_in_highlight_color(text):
    if not ENVIRONMENT_CONSTANTS.is_terminal_environment():
        return text
    import TEXT
    return TEXT.colored_text(text, TEXT.TextColor.Blue)
        
def test_core_module():
    tester = UnitTest()
    # CORE_MODULE_FOLDER_FOR_RHINO
    # CORE_MODULE_FOLDER_FOR_PUBLISHED_RHINO
    address = "RHINO" if ENVIRONMENT_CONSTANTS.is_Rhino_environment() else "REVIT"

    if not USER.is_enneadtab_developer():
        address = "PUBLISHED_" + address
    
    attr_name = "CORE_MODULE_FOLDER_FOR_{}".format(address)
    value = getattr(ENVIRONMENT, attr_name)
    print (value)


    if ENVIRONMENT_CONSTANTS.is_Rhino_environment():
        tester.process_folder(value)
        
    elif ENVIRONMENT_CONSTANTS.is_Revit_environment():
        tester.process_folder(value)
    
    else:
        print ("Testing in terminal environment, using rhino and revit folder for now...")
        tester.process_folder(ENVIRONMENT.CORE_MODULE_FOLDER_FOR_REVIT)
        tester.process_folder(ENVIRONMENT.CORE_MODULE_FOLDER_FOR_RHINO)
    

    NOTIFICATION.duck_pop(main_text = "All unit tests finished!")
    print ("\n\n\nAll unit tests finished!")
    
    
if __name__ == '__main__':
    test_core_module()