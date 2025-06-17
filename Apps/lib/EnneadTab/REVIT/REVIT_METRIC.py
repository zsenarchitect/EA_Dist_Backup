# -*- coding: utf-8 -*-
from datetime import datetime
import traceback
import os
import sys
import time
import json
import logging

# ------------------------------------------------------------------
# Compatibility: IronPython 2.7 (Revit) does not have FileNotFoundError
# ------------------------------------------------------------------
try:
    FileNotFoundError
except NameError:  # Define fallback for IronPython
    class FileNotFoundError(IOError):
        """Fallback FileNotFoundError for IronPython <3."""
        pass

# Setup imports
root_folder = os.path.abspath((os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(root_folder)


import DATA_FILE,  ENVIRONMENT, MODULE_HELPER
from pyrevit import forms



PREFIX = "REVIT_METRIC"

class RevitMetric:
    def __init__(self, doc):
        self.doc = doc
        self.tasks = []
        self.debug_mode = True  # Enable debug mode for better debugging
        
        # Load tasks from configuration, fallback to sample tasks if no config exists
        config_tasks = load_tasks_from_config(doc.Title)
        if config_tasks:
            self.tasks = config_tasks
            self.log_debug("Loaded {} tasks from configuration for document: {}".format(len(self.tasks), doc.Title))
        else:
            # Fallback sample tasks for testing/development
            self.log_debug("No configuration found, using sample tasks for document: {}".format(doc.Title))
        self.tasks.append(MetricTask("sample_task", 
                                     "XX.tab\\YY.panel\\ZZ.pulldown", 
                                     "run_task", 
                                     enabled = True))
        self.tasks.append(MetricTask("sample_task2", 
                                "XX2.tab\\YY2.panel\\ZZ2.pulldown", 
                                "run_task2", 
                                enabled = False))

        
    def log_debug(self, message):
        """Enhanced logging function for debugging"""
        if self.debug_mode:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            print("[DEBUG {}] {}".format(timestamp, message))
            
    def log_error(self, message, exception=None):
        """Enhanced error logging function"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        print("[ERROR {}] {}".format(timestamp, message))
        if exception:
            print("[ERROR {}] Exception details: {}".format(timestamp, str(exception)))
            print("[ERROR {}] Traceback: {}".format(timestamp, traceback.format_exc()))

    def reload_tasks_from_config(self):
        """Reload tasks from configuration file"""
        self.log_debug("Reloading tasks from configuration for document: {}".format(self.doc.Title))
        config_tasks = load_tasks_from_config(self.doc.Title)
        if config_tasks:
            self.tasks = config_tasks
            self.log_debug("Reloaded {} tasks from configuration".format(len(self.tasks)))
            return True
        else:
            self.log_debug("No configuration found, keeping existing tasks")
            return False

        
    def update_metric(self):
        """Update metrics for the current document"""
        try:
            # Get task configuration
            config_file = os.path.join(os.path.dirname(__file__), "metric_tasks.json")
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    tasks = json.load(f)
            else:
                logging.debug("No configuration found, using sample tasks for document: {}".format(self.doc.Title))
                tasks = {
                    "sample_task": {
                        "enabled": True,
                        "script_path": "C:\\Users\\szhang\\Documents\\EnneadTab Ecosystem\\EA_Dist\\Apps\\_revit\\XX.tab\\YY.panel\\ZZ.pulldown",
                        "function": "run_task"
                    },
                    "sample_task2": {
                        "enabled": False,
                        "script_path": "path/to/script2",
                        "function": "run_task2"
                    }
                }

            # Update timestamp
            self.data["last_update"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Run tasks
            success_count = 0
            total_tasks = len(tasks)
            logging.debug("Starting metric update for document: {}".format(self.doc.Title))
            logging.debug("Using data file: {}".format(self.data_file))
            logging.debug("Added update time: {}".format(self.data["last_update"]))
            
            for i, (task_name, task_config) in enumerate(tasks.items(), 1):
                if not task_config.get("enabled", True):
                    logging.debug("Skipping task {} - disabled".format(task_name))
                    continue
                    
                logging.debug("Running task {}/{}: {}".format(i, total_tasks, task_name))
                logging.debug("Executing task: {}".format(task_name))
                
                try:
                    task = MetricTask(task_name, task_config)
                    start_time = time.time()
                    task.run(self.doc)
                    duration = time.time() - start_time
                    logging.debug("Task {} duration: {:.3f} seconds".format(task_name, duration))
                    success_count += 1
                except Exception as e:
                    logging.error("Error running task {}".format(task_name))
                    logging.error("Exception details: {}".format(str(e)))
                    logging.error("Traceback: {}".format(traceback.format_exc()))
                    
            logging.debug("Metric update completed. Success: {}/{}".format(success_count, total_tasks))
            return success_count > 0
            
        except Exception as e:
            logging.error("Error in update_metric: {}".format(str(e)))
            return False



class MetricTask:
    def __init__(self, task_name, script_path, func_name, enabled):
        self.task_name = task_name
        self.script_path = script_path
        self.func_name = func_name
        self.enabled = enabled
        
    def validate(self):
        """Validate task configuration"""
        if not self.task_name:
            raise ValueError("Task name cannot be empty")
        if not self.script_path:
            raise ValueError("Script path cannot be empty")
        if not self.func_name:
            raise ValueError("Function name cannot be empty")
        

    def run(self, doc):
        if not self.enabled:
            print("[WARNING] Skipping task {} - disabled".format(self.task_name))
            return
        
        if self.script_path == "":
            print("[WARNING] Skipping task {} - empty script path".format(self.task_name))
            return
        
        # Validate task before running
        self.validate()
        
        script_path = os.path.join(ENVIRONMENT.REVIT_FOLDER, self.script_path)
        print("[DEBUG] Running task: {}".format(self.task_name))
        print("[DEBUG] Script path: {}".format(script_path))
        print("[DEBUG] Function: {}".format(self.func_name))
        print("[DEBUG] Document: {}".format(doc.Title if hasattr(doc, 'Title') else 'Unknown'))
        
        # Verify script file exists
        if not os.path.exists(script_path):
            raise FileNotFoundError("Script file not found: {}".format(script_path))
            
        MODULE_HELPER.run_revit_script(script_path, self.func_name, doc)
        print("[DEBUG] Task {} execution completed".format(self.task_name))

        

def setup_task():
    """Setup task configuration for REVIT metric collection using pyrevit.forms"""
    
    print("Starting REVIT Metric Task Configuration...")
    

    # Step 1: Find all existing REVIT_METRIC_ data files
    print("Finding existing metric data files...")
    try:
        dump_folder = ENVIRONMENT.DUMP_FOLDER
        all_files = os.listdir(dump_folder)
        metric_files = [f for f in all_files if f.startswith(PREFIX + "_") and f.endswith(ENVIRONMENT.PLUGIN_EXTENSION)]
        doc_titles = [f[len(PREFIX + "_"):-len(ENVIRONMENT.PLUGIN_EXTENSION)] for f in metric_files]
        print("Found {} existing documents: {}".format(len(doc_titles), doc_titles))
    except Exception as e:
        print("Error finding data files: {}".format(e))
        doc_titles = []
    
    # Step 2: Define all possible tasks
    available_tasks = [
        {
            "task_name": "model_health_check",
            "script_path": "Model Health.tab\\Model Health.panel\\Model Health Check.pulldown\\Model Health Check.pushbutton\\Model Health Check_script.py",
            "func_name": "main",
            "description": "Performs comprehensive model health analysis"
        },
        {
            "task_name": "element_count",
            "script_path": "Model Health.tab\\Model Health.panel\\Element Count.pushbutton\\Element Count_script.py", 
            "func_name": "main",
            "description": "Counts various element types in the model"
        },
        {
            "task_name": "warning_check",
            "script_path": "Model Health.tab\\Model Health.panel\\Warning Check.pushbutton\\Warning Check_script.py",
            "func_name": "main", 
            "description": "Checks for model warnings and issues"
        },
        {
            "task_name": "view_audit",
            "script_path": "Model Health.tab\\Model Health.panel\\View Audit.pushbutton\\View Audit_script.py",
            "func_name": "main",
            "description": "Audits views and view templates"
        },
        {
            "task_name": "workset_analysis", 
            "script_path": "Model Health.tab\\Model Health.panel\\Workset Analysis.pushbutton\\Workset Analysis_script.py",
            "func_name": "main",
            "description": "Analyzes workset usage and distribution"
        }
    ]
    
    # Step 3: Document selection
    doc_title = None
    
    if doc_titles:

   
        doc_title = forms.SelectFromList.show(
            doc_titles,
            title="Select Document",
            width=400,
            height=300,
            message="Select an existing document"
        )
        
        
    
    
    if not doc_title:
        print("No document selected")
        return
    
    print("Selected document: {}".format(doc_title))
    
    # Step 4: Task configuration
    data_file_name = "{}_{}".format(PREFIX, doc_title)
    
    try:
        with DATA_FILE.update_data(data_file_name, is_local=True) as data_file:
            # Load existing config or create default
            existing_config = data_file.get("config", {})
            
            # Create task selection list with current status
            task_options = []
            selected_tasks = []
            
            for task in available_tasks:
                task_name = task["task_name"]
                current_enabled = existing_config.get(task_name, {}).get("enabled", True)
                description = task["description"]
                
                # Create display string
                
                display_text = "{} - {}".format(task_name, description)
                task_options.append(display_text)
                
                # Pre-select if currently enabled
                if current_enabled:
                    selected_tasks.append(display_text)
            
            # Show multi-selection dialog
            selected_task_displays = forms.SelectFromList.show(
                task_options,
                title="Configure Tasks for: {}".format(doc_title),
                width=600,
                height=400,
                message="Select tasks to ENABLE (unselected tasks will be DISABLED):",
                multiselect=True,
                default=selected_tasks
            )
            
            if selected_task_displays is None:
                print("No tasks selected")
                return
            
            # Build new configuration
            new_config = {}
            enabled_count = 0
            
            for i, task in enumerate(available_tasks):
                task_name = task["task_name"]
                display_text = task_options[i]
                enabled = display_text in selected_task_displays
                
                if enabled:
                    enabled_count += 1
                
                new_config[task_name] = {
                    "enabled": enabled,
                    "script_path": task["script_path"],
                    "func_name": task["func_name"],
                    "description": task["description"]
                }
            
            # Show confirmation
            summary_lines = [
                "Configuration Summary:",
                "",
                "Document: {}".format(doc_title),
                "Tasks enabled: {}/{}".format(enabled_count, len(available_tasks)),
                ""
            ]
            
            for task_name, task_config in new_config.items():
                status = "ENABLED" if task_config["enabled"] else "DISABLED"
                summary_lines.append("• {}: {}".format(task_name, status))
            
            summary_lines.append("")
            summary_lines.append("Save this configuration?")
            
            if forms.alert("\n".join(summary_lines), title="Confirm Configuration", ok=False, yes=True, no=True):
                data_file["config"] = new_config
                data_file["config_last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                forms.alert("Configuration saved successfully!", title="Success")
                print("Configuration saved for document: {}".format(doc_title))
            else:
                forms.alert("Configuration not saved.", title="Cancelled")
                
    except Exception as e:
        forms.alert("Error configuring tasks: {}".format(e), title="Error")
        traceback.print_exc()








def load_tasks_from_config(doc_title):
    """Load task configuration from data file and return list of MetricTask objects"""
    data_file_name = "{}_{}".format(PREFIX, doc_title)
    
    try:
        with DATA_FILE.get_data(data_file_name, is_local=True) as data_file:
            if "config" not in data_file:
                print("No configuration found for document: {}".format(doc_title))
                return []
            
            config = data_file["config"]
            tasks = []
            
            for task_name, task_config in config.items():
                task = MetricTask(
                    task_name=task_name,
                    script_path=task_config["script_path"],
                    func_name=task_config["func_name"],
                    enabled=task_config["enabled"]
                )
                tasks.append(task)
            
            print("Loaded {} tasks from configuration".format(len(tasks)))
            return tasks
            
    except Exception as e:
        print("Error loading task configuration: {}".format(e))
        return []

if __name__ == "__main__":
    pass