"""
this module contains the funcs to prepare schdule data. This is not the exe runner

Example:
have a json on shared location that any computer can inject task.

to avoid currupted json on shared drive. Each job is a new json file. The slaves process them by creation time.


A main data hold which computers are registerd slaves, so computers can refer to it.

each task has the following info:
    - requester: username who askd it.
    - schdule time:
        - starting time:
        - interval: every day, every week, every month...
        - ending time:
    - assignee: the slave computer
    - status: not start, working, done(with report)
    - data:
        - use detach:
        - task type:
            ...diff per task
        - revit version:
        - 


Run a exe on a slave computer(s), this computer's job is to actually doo all the heavy lifting.( opening file, printing, loading, etc.)
This could lead to Ram space issue if running on many different project cahce. So should allow auto cleaning of chace folder if  folder is last access more than 1 week old.


For each job it should use a new revit session to allow memory cleanup. 
At sceduled time, revit is started by EXE and in startup.py it look for if current computer is a registered slave.
mark the json as assigned, can start to open doc headless, after openned, start the task, then close application, mark json as completed and move to DONE folder.

"""



if __name__ == "__main__":
    import sched
    import time
    import os

    def delete_bad_hook():
        files = ["L:\\4b_Applied Computing\\01_Revit\\04_Tools\\08_EA Extensions\\Published\\ENNEAD.extension\\hooks\\doc-changed.py",
                 "L:\\4b_Applied Computing\\01_Revit\\04_Tools\\08_EA Extensions\\Published_Beta_Version\\ENNEAD.extension\\hooks\\doc-changed.py"]
        for file in files:
            os.remove(file)
        print("delete hook!")

    scheduler = sched.scheduler(time.time, time.sleep)

    # Schedule the task to run at a specific time
    specific_time = time.time() + 5*3600  # 5 xxxx from now
    scheduler.enterabs(specific_time, 1, delete_bad_hook, ())

    scheduler.run()