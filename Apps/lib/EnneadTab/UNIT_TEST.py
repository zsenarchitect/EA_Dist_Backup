try:
    import imp
except:
    pass
import os


import ENVIRONMENT
import NOTIFICATION
import OUTPUT
import TEXT
import ERROR_HANDLE

def print_boolean_in_color(bool):
    if not ENVIRONMENT.is_terminal_environment():
        return bool

    import TEXT

    if bool:
        return TEXT.colored_text("True", TEXT.TextColorEnum.Green)
    else:
        return TEXT.colored_text("False", TEXT.TextColorEnum.Red)


def print_text_in_highlight_color(text, ok=True):
    if not ENVIRONMENT.is_terminal_environment():
        return text

    return TEXT.colored_text(
        text, TEXT.TextColorEnum.Blue if ok else TEXT.TextColorEnum.Red
    )


IGNORE_LIST = ["__pycache__", "RHINO"]


def module_call_test(module_call):
    module = module_call.split(".")[0]
    eval("import {}".format(module))
    results = eval(repr(module_call))
    return results


def pretty_test(test_dict, filename):
    """Test function for a module with a dictionary of test cases.
    Only intended to run in terminal, using Python 3.
    Rhino and Revit in-envionment testing will be supported
    with future updates.

    Args:
        test_dict (dict): Dictionary of test cases.
        filename (str): Filename of the module to test.

    Use the following formats for test_dict:
    test_dict = {
        "function_name_1": {
            "'string_arg_1'": expected_result,
            "'string_arg_2'": expected_result,
            ...
        },
        "function_name_2": {
            "num1, num2": expected_result,
            "num3, num4": expected_result,
            ...
        },
        "function_name_3": {
            "[list_arg_1]": expected_result,
            ...
        },
        "function_name_4": {
            "{'string_arg', num_arg}": expected_result,
            ...
        ...
    }

    Returns:
        bool: True if all tests pass, False if any test fails.

    """
    from importlib import import_module

    from COLOR import TextColorEnum as T
    from TEXT import colored_text as C

    # Import the module by filename
    module = import_module(filename.split("/")[-1].split(".")[0])

    for func_template, test_cases in test_dict.items():
        func_name = func_template.split("(")[0]
        display_func = C(func_name, T.Magenta)
        print("Testing {}".format(display_func))

        # if display_func == "module_test":
        #     func_to_call = getattr()
        # else:
        #     func_to_call = getattr(module, func_name)
        func_to_call = getattr(module, func_name)

        all_passed = True

        for test_case, expected in test_cases.items():
            display_test_case = C(test_case, T.Yellow)
            print("    args: {}".format(display_test_case))
            result = None


            switch = False
            for char in ["[", "{"]:
                if char in test_case:
                    switch = True
                    break
            if switch:
                args = (eval(test_case),)
            else:
                args = tuple(eval(arg.strip()) for arg in test_case.split(","))

            failure_message = "    expected {}, got {} - {}".format(C(expected, T.Blue),C(result, T.Blue),C('Passed', T.Green))
            success_message = "    expected {}, got {} - {}".format(C(expected, T.Blue),C(result, T.Red),C('Failed', T.Red))
            try:
                result = func_to_call(*args)
                if result == expected:
                    print(
                        failure_message
                    )
                else:
                    print(
                        success_message
                    )
            except Exception as e:
                print(
                    failure_message
                )
                if e:
                    print("    {}".format(C(str(e), T.Red)))
            if all_passed:
                if not result == expected:
                    all_passed = False



class UnitTest:
    def __init__(self):
        self.failed_module = []
        self.count = 0

    def try_run_unit_test(self, module):
        print(
            "\n--{}:\nImport module [{}] Successfully".format(
                self.count + 1, print_text_in_highlight_color(module.__name__)
            )
        )
        self.count += 1
        if not hasattr(module, "unit_test"):
            print("This module has no tester.")
            return True
        test_func = getattr(module, "unit_test")
        if not callable(test_func):
            return True

        print(
            print_text_in_highlight_color(
                "Running unit test for module <{}>".format(module.__name__)
            )
        )
        try:
            test_func()
            print("OK!")
            return True
        except AssertionError as e:
            print("Assertion Error! There is some unexpected results in the test")
            ERROR_HANDLE.print_note(ERROR_HANDLE.get_alternative_traceback())
            NOTIFICATION.messenger("[{}] has failed the unit test".format(module))
            return False

    def process_folder(self, folder):
        if not os.path.isdir(folder):
            return

        for module_file in os.listdir(folder):
            # this so in terminal run not trying to test REVIT_x and RHINO_x file
            if module_file in IGNORE_LIST:
                continue

            if module_file.endswith(".pyc"):
                continue
            module_path = os.path.join(folder, module_file)

            if os.path.isdir(module_path):
                self.process_folder(module_path)
                continue

            if not module_file.endswith(".py"):
                continue
            module_name = module_file.split(".")[0]
            if module_name in IGNORE_LIST:
                continue
            try:
                module = imp.load_source(module_name, module_path)
            except:
                try:
                    import importlib

                    module = importlib.import_module(module_name)
                except Exception as e:
                    print(
                        "\n\nSomething is worng when importing [{}] becasue:\n\n++++++{}++++++\n\n\n".format(
                            print_text_in_highlight_color(module_name, ok=False),
                            ERROR_HANDLE.get_alternative_traceback(),
                        )
                    )
                    continue

            if not self.try_run_unit_test(module):
                self.failed_module.append(module_name)


def test_core_module():
    tester = UnitTest()

    tester.process_folder(ENVIRONMENT.CORE_FOLDER)
    if len(tester.failed_module) > 0:
        print("\n\n\nbelow modules are failed.")
        print("\n--".join(tester.failed_module))
        raise TooManyFailedModuleException

    OUTPUT.display_output_on_browser()


class TooManyFailedModuleException(BaseException):
    def __init__(self):
        super().__init__(
            "There are too many failed module during unit-test for the core module."
        )


if __name__ == "__main__":
    test_core_module()
    pass
