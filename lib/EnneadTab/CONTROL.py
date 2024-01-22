"""This is an idea

How about allowing remote action control: 
    - remote reloading for revit(people keep missing update becasue they do not restart revit everyday)
    - remote register for rhino. Some people keep ignoring the suggestion
    - other ideas?

So i can set a command listener in a data exchange folder(all user has access)
When i post a command for a user. it creates a json file in the data exchange folder, named by user name

any user will periordially looking this exchang folder, if find their name, it extract the commmand and excute
after excution, remove that command from data. If data become empty, delete the json file.


need to figure out what format to use for those command, maybe there are mutiple commands, each has thpse
    timestamp
    command_name
    function_to_run: this may be supplying func as object, or supplying full path of scrtipt and func name and it figure out what func to call
    

"""

class Command:
    RevitReload = "Reload Revit"
    RhinoRegister = "Register Rhino" 

    
class CommandListener:
    pass




class CommandSender:
    """send to one user name
    or send to all known user name


    example:
    self.command(Command.RevitReload)"""
    pass