import os
import subprocess
try:
    import winreg
except ImportError:
    import _winreg as winreg  # IronPython 2.7 compatibility
import tempfile
import uuid
from datetime import datetime, timedelta

import ENVIRONMENT

# Compatibility for IronPython 2.7 - define DEVNULL if not available
try:
    DEVNULL = subprocess.DEVNULL
except AttributeError:
    DEVNULL = open(os.devnull, 'wb')

# Compatibility helper for subprocess.run (not available in IronPython 2.7)
def _run_command(cmd, capture_output=False, text=False, check=False):
    """
    Compatibility function for subprocess.run that works in IronPython 2.7
    """
    try:
        if capture_output:
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
            stdout, stderr = proc.communicate()
            if text and hasattr(stdout, 'decode'):
                stdout = stdout.decode('utf-8', errors='ignore')
                stderr = stderr.decode('utf-8', errors='ignore')
            
            # Create a simple result object
            class Result:
                def __init__(self, returncode, stdout, stderr):
                    self.returncode = returncode
                    self.stdout = stdout
                    self.stderr = stderr
                    
            result = Result(proc.returncode, stdout, stderr)
            
            if check and proc.returncode != 0:
                raise subprocess.CalledProcessError(proc.returncode, cmd, output=stdout, stderr=stderr)
            
            return result
        else:
            returncode = subprocess.call(cmd, shell=False)
            if check and returncode != 0:
                raise subprocess.CalledProcessError(returncode, cmd)
            return returncode
    except Exception as e:
        if check:
            raise
        return None

def run_powershell_script(script_name, no_wait = True):
    full_path = os.path.join(ENVIRONMENT.SCRIPT_FOLDER, script_name)
    if not os.path.exists(full_path):
        print("Script not found: {}".format(full_path))
        return

    try:
        if no_wait:
            # Use Popen for non-blocking execution with hidden window and no output
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            
            subprocess.Popen(["powershell", 
                            "-ExecutionPolicy", "Bypass",
                            "-NoProfile",
                            "-NonInteractive",
                            "-WindowStyle", "Hidden",
                            "-File", full_path],
                           startupinfo=startupinfo,
                           stdout=DEVNULL,
                           stderr=DEVNULL)
        else:
            # Use call for blocking execution - compatible with IronPython 2.7
            subprocess.call(["powershell", 
                          "-ExecutionPolicy", "Bypass",
                          "-NoProfile",
                          "-NonInteractive",
                          "-File", full_path], 
                            shell=True)
    except subprocess.CalledProcessError as e:
        print("Error running script: {}".format(e))
        return
    except Exception as e:
        print("Error running script: {}".format(e))
        return

class RegisterMethod:
    def __init__(self, enabled=True):
        self.enabled = enabled

class RegisterDaily(RegisterMethod):
    def __init__(self, time="00:00", enabled=True):
        super(RegisterDaily, self).__init__(enabled)
        self.time = time

class RegisterInterval(RegisterMethod):
    def __init__(self, interval=45, enabled=True):
        super(RegisterInterval, self).__init__(enabled)
        self.interval = interval  # in minutes

class RegisterStartup(RegisterMethod):
    def __init__(self, enabled=True):
        super(RegisterStartup, self).__init__(enabled)

def _create_scheduled_task_xml(task_name, script_path, trigger_xml):
    """Create XML for Windows Task Scheduler"""
    xml_template = '''<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Date>{date}</Date>
    <Author>EnneadTab</Author>
    <Description>Auto-registered PowerShell script: {task_name}</Description>
  </RegistrationInfo>
  <Triggers>
    {trigger_xml}
  </Triggers>
  <Principals>
    <Principal id="Author">
      <UserId>S-1-5-32-545</UserId>
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>LeastPrivilege</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
    <IdleSettings>
      <StopOnIdleEnd>false</StopOnIdleEnd>
      <RestartOnIdle>false</RestartOnIdle>
    </IdleSettings>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>false</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT1H</ExecutionTimeLimit>
    <Priority>7</Priority>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>PowerShell.exe</Command>
      <Arguments>-ExecutionPolicy Bypass -NoProfile -NonInteractive -WindowStyle Hidden -File "{script_path}"</Arguments>
    </Exec>
  </Actions>
</Task>'''
    return xml_template.format(
        date=datetime.now().isoformat(),
        task_name=task_name,
        trigger_xml=trigger_xml,
        script_path=script_path
    )

def _find_existing_registrations(script_path, method):
    """Find existing registrations for a script with the same method type"""
    script_name = os.path.splitext(os.path.basename(script_path))[0]
    method_name = method.__class__.__name__
    pattern = "EnneadTab_{}_{}".format(script_name, method_name)
    
    existing = []
    
    # Check startup registry entries
    if isinstance(method, RegisterStartup):
        try:
            key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ)
            
            i = 0
            while True:
                try:
                    name, value, _ = winreg.EnumValue(key, i)
                    if name.startswith(pattern):
                        existing.append(name)
                    i += 1
                except WindowsError:
                    break
            
            winreg.CloseKey(key)
        except Exception as e:
            print("Error reading startup registry: {}".format(e))
    
    # Check scheduled tasks
    elif isinstance(method, (RegisterDaily, RegisterInterval)):
        try:
            cmd = ["schtasks", "/query", "/fo", "csv"]
            result = _run_command(cmd, capture_output=True, text=True, check=True)
            
            for line in result.stdout.split('\n')[1:]:  # Skip header
                if line.strip() and pattern in line:
                    parts = line.split(',')
                    if len(parts) > 0:
                        task_name = parts[0].strip('"')
                        if task_name.startswith(pattern):
                            existing.append(task_name)
        except Exception as e:
            print("Error listing scheduled tasks: {}".format(e))
    
    return existing

def _register_startup_registry(script_path, task_name):
    """Register script to run at startup via Windows Registry"""
    try:
        # Open the registry key for startup programs
        key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
        
        # Create the command to run the PowerShell script
        command = 'PowerShell.exe -ExecutionPolicy Bypass -NoProfile -NonInteractive -WindowStyle Hidden -File "{}"'.format(script_path)
        
        # Set the registry value
        winreg.SetValueEx(key, task_name, 0, winreg.REG_SZ, command)
        winreg.CloseKey(key)
        
        print("Successfully registered '{}' for startup execution".format(task_name))
        return True
        
    except Exception as e:
        print("Error registering startup script: {}".format(e))
        return False

def _register_scheduled_task(script_path, task_name, method):
    """Register script as a Windows scheduled task"""
    try:
        # Generate appropriate trigger XML based on method type
        if isinstance(method, RegisterDaily):
            # Parse time (format: "HH:MM")
            hour, minute = method.time.split(":")
            trigger_xml = '''<TimeTrigger>
      <StartBoundary>{date}T{hour}:{minute}:00</StartBoundary>
      <Enabled>true</Enabled>
      <Repetition>
        <Interval>P1D</Interval>
        <StopAtDurationEnd>false</StopAtDurationEnd>
      </Repetition>
    </TimeTrigger>'''.format(
                date=datetime.now().strftime("%Y-%m-%d"),
                hour=hour,
                minute=minute
            )
            
        elif isinstance(method, RegisterInterval):
            # Convert minutes to ISO 8601 duration format
            interval_minutes = method.interval
            trigger_xml = '''<TimeTrigger>
      <StartBoundary>{date}</StartBoundary>
      <Enabled>true</Enabled>
      <Repetition>
        <Interval>PT{interval}M</Interval>
        <StopAtDurationEnd>false</StopAtDurationEnd>
      </Repetition>
    </TimeTrigger>'''.format(
                date=datetime.now().isoformat(),
                interval=interval_minutes
            )
        else:
            raise ValueError("Unsupported method type for scheduled task")
        
        # Create task XML
        task_xml = _create_scheduled_task_xml(task_name, script_path, trigger_xml)
        
        # Write XML to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as temp_file:
            temp_file.write(task_xml)
            temp_xml_path = temp_file.name
        
        try:
            # Create the scheduled task using schtasks command
            cmd = [
                "schtasks", "/create",
                "/tn", task_name,
                "/xml", temp_xml_path,
                "/f"  # Force creation (overwrite if exists)
            ]
            
            result = _run_command(cmd, capture_output=True, text=True, check=True)
            print("Successfully registered scheduled task '{}'".format(task_name))
            return True
            
        finally:
            # Clean up temporary XML file
            try:
                os.unlink(temp_xml_path)
            except:
                pass
                
    except subprocess.CalledProcessError as e:
        print("Error creating scheduled task: {}".format(e.stderr))
        return False
    except Exception as e:
        print("Error registering scheduled task: {}".format(e))
        return False

def register_powershell_script(script_path, method=None):
    """
    Register a PowerShell script to run with the specified method.
    
    Args:
        script_path (str): Path to the PowerShell script file
        method (RegisterMethod): Registration method (RegisterStartup, RegisterDaily, or RegisterInterval)
    
    Returns:
        bool: True if registration was successful, False otherwise
    """
    if method is None:
        method = RegisterStartup()
    
    # Get absolute path for consistency
    if os.path.exists(script_path):
        script_path = os.path.abspath(script_path)
    
    # Check if registration is disabled - if so, unregister existing ones
    if not method.enabled:
        print("Registration is disabled for method: {}. Looking for existing registrations to remove...".format(method.__class__.__name__))
        
        # Find and remove existing registrations
        existing_registrations = _find_existing_registrations(script_path, method)
        if existing_registrations:
            print("Found {} existing registration(s) to remove".format(len(existing_registrations)))
            removed_count = 0
            for reg_name in existing_registrations:
                if unregister_powershell_script(reg_name):
                    removed_count += 1
            print("Successfully removed {} registration(s)".format(removed_count))
            return removed_count > 0
        else:
            print("No existing registrations found to remove")
            return True
    
    # Validate script path for registration
    if not os.path.exists(script_path):
        print("Script not found: {}".format(script_path))
        return False
    
    # Generate task name based on script name and method
    script_name = os.path.splitext(os.path.basename(script_path))[0]
    method_name = method.__class__.__name__
    task_name = "EnneadTab_{}_{}_{}".format(script_name, method_name, str(uuid.uuid4())[:8])
    
    print("Registering script: {}".format(script_path))
    print("Method: {}".format(method_name))
    print("Task name: {}".format(task_name))
    
    # Register based on method type
    if isinstance(method, RegisterStartup):
        return _register_startup_registry(script_path, task_name)
    elif isinstance(method, (RegisterDaily, RegisterInterval)):
        return _register_scheduled_task(script_path, task_name, method)
    else:
        print("Unsupported registration method: {}".format(type(method)))
        return False

def unregister_powershell_script(task_name):
    """
    Unregister a previously registered PowerShell script.
    
    Args:
        task_name (str): Name of the task to unregister
    
    Returns:
        bool: True if unregistration was successful, False otherwise
    """
    try:
        # Try to delete as scheduled task first
        try:
            cmd = ["schtasks", "/delete", "/tn", task_name, "/f"]
            _run_command(cmd, capture_output=True, text=True, check=True)
            print("Successfully unregistered scheduled task '{}'".format(task_name))
            return True
        except subprocess.CalledProcessError:
            pass
        
        # Try to delete from startup registry
        try:
            key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
            winreg.DeleteValue(key, task_name)
            winreg.CloseKey(key)
            print("Successfully unregistered startup script '{}'".format(task_name))
            return True
        except FileNotFoundError:
            pass
        
        print("Task '{}' not found in scheduled tasks or startup registry".format(task_name))
        return False
        
    except Exception as e:
        print("Error unregistering script: {}".format(e))
        return False

def list_registered_scripts():
    """
    List all registered EnneadTab PowerShell scripts.
    
    Returns:
        dict: Dictionary with 'startup' and 'scheduled' lists
    """
    registered = {'startup': [], 'scheduled': []}
    
    # Check startup registry entries
    try:
        key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ)
        
        i = 0
        while True:
            try:
                name, value, _ = winreg.EnumValue(key, i)
                if name.startswith("EnneadTab_"):
                    registered['startup'].append({'name': name, 'command': value})
                i += 1
            except WindowsError:
                break
        
        winreg.CloseKey(key)
    except Exception as e:
        print("Error reading startup registry: {}".format(e))
    
    # Check scheduled tasks
    try:
        cmd = ["schtasks", "/query", "/fo", "csv"]
        result = _run_command(cmd, capture_output=True, text=True, check=True)
        
        for line in result.stdout.split('\n')[1:]:  # Skip header
            if line.strip() and "EnneadTab_" in line:
                parts = line.split(',')
                if len(parts) > 0:
                    task_name = parts[0].strip('"')
                    if task_name.startswith("EnneadTab_"):
                        registered['scheduled'].append({'name': task_name})
    except Exception as e:
        print("Error listing scheduled tasks: {}".format(e))
    
    return registered

if __name__ == "__main__":
    # Example usage
    run_powershell_script("Get-InstalledSoftware.ps1")
    
    # Example registrations:
    register_powershell_script("path/to/script.ps1", RegisterStartup())  # enabled by default
    register_powershell_script("path/to/script.ps1", RegisterDaily("09:30"))
    register_powershell_script("path/to/script.ps1", RegisterInterval(60))
    
    # Example with disabled registration (will unregister existing):
    register_powershell_script("path/to/script.ps1", RegisterStartup(enabled=False))  # will unregister existing
    register_powershell_script("path/to/script.ps1", RegisterDaily("09:30", enabled=False))
    register_powershell_script("path/to/script.ps1", RegisterInterval(60, enabled=False))