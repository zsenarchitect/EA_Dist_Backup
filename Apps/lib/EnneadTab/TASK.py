import subprocess

class TaskScheduler:


    def add_scheduled_task(self, task_name, exe_path):
        # Format the command to add to the Task Scheduler
        command = 'schtasks /create /tn "{}" /tr "{}" /sc daily /st 00:00'.format(task_name, exe_path)
        
        try:
            # Run the command
            subprocess.check_call(command, shell=True)
            print ("Task scheduled successfully: {}".format(task_name))
        except subprocess.CalledProcessError as e:
            print ("Failed to schedule task:", e)

    def remove_scheduled_task(self, task_name):
        # Format the command to delete the task from the Task Scheduler
        command = 'schtasks /delete /tn "{}" /f'.format(task_name)
        
        try:
            # Run the command
            subprocess.check_call(command, shell=True)
            print ("Task '{}' removed successfully.".format(task_name))
        except subprocess.CalledProcessError as e:
            print ("Failed to remove scheduled task:", e)


