import configparser
import os




def main():
    # Get the current user's profile directory
    user_profile = os.path.expanduser("~")

    # Path to the .ini file
    file_path = os.path.join(user_profile, 'AppData', 'Roaming', 'pyRevit', 'pyRevit_config.ini')

    # Create a ConfigParser object
    config = configparser.ConfigParser()

    # Read the .ini file
    config.read(file_path)

    # Construct the new path for userextensions
    new_userextensions_path = os.path.join(user_profile, 'Documents', 'EnneadTab Ecosystem', 'EA_Dist', '_revit')

    # Modify the userextensions in the [core] section
    if 'core' in config:
        config.set('core', 'userextensions', '["{}"]'.format(new_userextensions_path))

    # Write the changes back to the .ini file
    with open(file_path, 'w') as configfile:
        config.write(configfile)

    print("The userextensions item has been updated.")


if __name__ == "__main__":
    main()