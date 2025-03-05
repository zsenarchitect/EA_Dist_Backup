#! python3

# r: openai
# r: requests
import rhinoscriptsyntax as rs
def add_path():
    # need this because in Rhino 8 py3 it cannot find the path by default
    for path in rs.SearchPathList():
        sys.path.append(path)

__title__ = "Text2Script"
__doc__ = """Utility script to convert text to script using AI.

Note: This is Rhino 8 only.

Features:
- Converts natural language to executable Python script
- Integrated with Rhino's rhinoscriptsyntax
- Maximum 5 refinement attempts for optimal results
- Always uses main() as the entry function
- API quota usage checking
"""
import sys

add_path()
from EnneadTab import FOLDER, SECRET, NOTIFICATION, DATA_FILE, SOUND
import time
import traceback
import os
import subprocess
import importlib.util
from datetime import datetime
import requests
from datetime import datetime, timedelta

try:
    from openai import OpenAI
except ImportError:
    pass

class TextToScriptConverter:
    def __init__(self):
        self.max_attempts = 5
        self.api_key = SECRET.get_api_key("EnneadTabAPI")
        self.client = OpenAI(api_key=self.api_key)
        self.temp_filepath = FOLDER.get_EA_dump_folder_file("text2script_TEMP.py")
        self.preset = """
        You are a specialized Python code generator for Rhino 8, focused on creating executable scripts.
        
        IMPORTANT REQUIREMENTS:
        1. Return ONLY pure Python code - no markdown, no code blocks, no explanations
        2. Code must be complete, self-contained, and immediately executable
        3. Include proper error handling and input validation
        4. Use descriptive variable names and add clear comments
        5. Follow PEP 8 style guidelines
        6. Include docstring for main functions
        7. ALWAYS include a main() function that serves as the entry point for the script
        8. At the end of your code, include: if __name__ == "__main__": main()
        
        TECHNICAL SPECIFICATIONS:
        - Target Environment: Rhino 8 Python
        - Primary API: Rhino Common (https://developer.rhino3d.com/api/rhinocommon/)
        - Reference Examples: https://github.com/mcneel/rhino-developer-samples/tree/master/rhinopython
        
        COMMON IMPORTS TO CONSIDER:
        - import rhinoscriptsyntax as rs
        - import Rhino
        - import System.Drawing
        
        BEST PRACTICES:
        - Include input validation
        - Add error messages for user feedback
        - Implement proper cleanup of resources
        - Structure code in logical functions
        - When asked about using color, use color tuple (r,g,b), and rhinoscriptsyntax will have something to make good color
        - ALWAYS use a main() function as the entry point
        
        Remember: Output must be pure Python code only, ready for direct execution.

        When asked about fixing invalid syntax, please provide a corrected version without the wrapper, which means no ```python in the beginning, and no``` in the end
        """
   
    def check_api_quota(self):
        """Check OpenAI API quota usage and display results.
        
        This function attempts to:
        1. Check API key validity with a minimal API call
        2. Check usage limits via the dashboard API if possible
        3. Provide a diagnostic message to the user
        """
        try:
            # First, try a minimal API call to check if key is valid/active
            response = self.client.models.list()
            
            # If we get here, the key is at least valid
            message = "Your API key appears to be valid. "
            
            # Try to get quota information using billing API
            try:
                # Get usage for current month
                now = datetime.now()
                start_date = datetime(now.year, now.month, 1).strftime("%Y-%m-%d")
                end_date = (datetime(now.year, now.month, 1) + timedelta(days=32)).replace(day=1).strftime("%Y-%m-%d")
                
                headers = {
                    "Authorization": f"Bearer {self.api_key}"
                }
                
                url = f"https://api.openai.com/v1/dashboard/billing/usage?start_date={start_date}&end_date={end_date}"
                response = requests.get(url, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    total_usage = data.get("total_usage", 0) / 100  # Convert from cents to dollars
                    
                    message += f"\n\nCurrent month usage: ${total_usage:.2f}"
                    
                    # Try to get subscription info
                    subscription_url = "https://api.openai.com/v1/dashboard/billing/subscription"
                    sub_response = requests.get(subscription_url, headers=headers)
                    
                    if sub_response.status_code == 200:
                        sub_data = sub_response.json()
                        hard_limit = sub_data.get("hard_limit_usd", "Unknown")
                        
                        if hard_limit != "Unknown":
                            message += f"\nMonthly limit: ${hard_limit:.2f}"
                            
                            if hard_limit > 0:
                                remaining = hard_limit - total_usage
                                message += f"\nRemaining: ${remaining:.2f}"
                                
                                if remaining <= 0:
                                    message += "\n\nYou have reached or exceeded your usage limit for this month."
                else:
                    message += "\n\nCould not retrieve detailed usage information."
                    if response.status_code == 401:
                        message += "\nAuthentication error when checking quota - API key may be invalid for billing checks."
                    else:
                        message += f"\nStatus code: {response.status_code}"
                        message += f"\nResponse: {response.text}"
            
            except Exception as e:
                message += f"\n\nCould not check detailed quota information: {str(e)}"
                message += "\nYour key appears valid but we couldn't determine usage limits."
            
            # Show information to user
            rs.MessageBox(message, title="OpenAI API Status")
            return True
            
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "quota" in error_str.lower() or "insufficient_quota" in error_str:
                message = "Your API key appears to have exceeded its quota limit."
            elif "401" in error_str or "authentication" in error_str.lower():
                message = "Your API key appears to be invalid or expired."
            else:
                message = f"Error checking API key: {error_str}"
            
            rs.MessageBox(message, title="OpenAI API Status")
            return False

    def get_user_request(self):
        prev_session = DATA_FILE.get_sticky("text2script_session", "Write your dream here.")
        request = rs.StringBox("Enter the function request:", title="Text2Script", default_value=prev_session)
        if not request or request.strip() == "":
            rs.MessageBox("No input provided. Operation cancelled.")
            return None
        DATA_FILE.set_sticky("text2script_session", request.strip())
        return request.strip()

    def generate_code(self, request):
        try:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": self.preset},
                    {"role": "user", "content": request}
                ],
                temperature=0.2
            )
            generated_code = response.choices[0].message.content

            if "```python" in generated_code:
                generated_code = generated_code.replace("```python", "")
            if "```" in generated_code:
                generated_code = generated_code.replace("```", "")
                
            if not generated_code or generated_code.strip() == "":
                raise ValueError("AI returned empty response")
                
            # Ensure the generated code has a main() function
            if "def main(" not in generated_code:
                main_function = "\n\ndef main():\n    # Main function added by Text2Script\n    # Your code entry point\n    "
                
                # Find if there's any code outside of function definitions
                import re
                function_pattern = r"def\s+\w+\s*\("
                lines = generated_code.split("\n")
                execution_lines = []
                
                for i, line in enumerate(lines):
                    if re.match(function_pattern, line.strip()):
                        # Skip until end of function
                        indentation = len(line) - len(line.lstrip())
                        j = i + 1
                        while j < len(lines) and (not lines[j].strip() or len(lines[j]) - len(lines[j].lstrip()) > indentation):
                            j += 1
                        i = j - 1
                    elif line.strip() and not line.strip().startswith("#") and not line.strip().startswith("import") and not line.strip().startswith("from"):
                        execution_lines.append(line)
                
                if execution_lines:
                    main_function += "\n    # Incorporating top-level code into main function\n    " + "\n    ".join(execution_lines)
                    # Remove the top-level code from the original code
                    for line in execution_lines:
                        generated_code = generated_code.replace(line, "")
                    generated_code = generated_code.strip()
                
                # Add the main function and the entry point
                generated_code += main_function
                
            # Ensure there's a proper entry point
            if "if __name__ == \"__main__\"" not in generated_code and "if __name__ == '__main__'" not in generated_code:
                generated_code += "\n\nif __name__ == \"__main__\":\n    main()\n"
            
            return generated_code.strip()
        except Exception as e:
            error_str = str(e)
            # Check for OpenAI quota exceeded errors
            if "429" in error_str or "quota" in error_str.lower() or "insufficient_quota" in error_str:
                message = """OpenAI API quota exceeded.

This means your OpenAI account has reached its usage limit.

To fix this issue:
1. Check your OpenAI account at platform.openai.com
2. Verify your billing details
3. Consider upgrading your plan if needed

Would you like to check your current quota status?"""
                check_quota = rs.MessageBox(message, title="OpenAI Quota Error", buttons=4)
                if check_quota == 6:  # Yes button
                    self.check_api_quota()
                raise ValueError("OpenAI quota exceeded - Please check your account")
            else:
                rs.MessageBox("Failed to generate code: {}".format(error_str))
                raise

    def save_script(self, script_content, request, is_temporary=True):
        """Save script to file and open it in editor.
        
        Args:
            script_content (str): Generated script content
            request (str): Original user request
            is_temporary (bool): If True, saves as temp file and opens in VSCode.
                               If False, saves as timestamped file and opens in default editor.
            
        Returns:
            str or None: Path to saved file if successful, None if failed
        """
        try:
            if is_temporary:
                filepath = self.temp_filepath
                header = "Generated from Text2Script (TEMPORARY VERSION)"
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = "text2script_{}.py".format(timestamp)
                filepath = FOLDER.get_EA_dump_folder_file(filename)
                header = "Generated from Text2Script"

            request_string = "\n".join("# {}".format(line) for line in request.split("\n"))
            
            content = """# {}
# Original request: 
{}
# Generated on: {}

{}""".format(header, request_string, datetime.now(), script_content)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            try:
                # Check common VSCode installation paths
                vscode_paths = [
                    r"C:\Users\{}\AppData\Local\Programs\Microsoft VS Code\Code.exe".format(os.getenv("USERNAME")),
                    r"C:\Program Files\Microsoft VS Code\Code.exe",
                    r"C:\Program Files (x86)\Microsoft VS Code\Code.exe"
                ]
                
                vscode_path = next((path for path in vscode_paths if os.path.exists(path)), None)
                
                if vscode_path:
                    subprocess.Popen([vscode_path, filepath])
                else:
                    os.startfile(filepath)
            except Exception:
                # Fallback to default handler if any error occurs
                os.startfile(filepath)
   
            return filepath
        except Exception as e:
            rs.MessageBox("Failed to save script: {}".format(str(e)))
            return None

    def create_refinement_request(self, original_request, error):
        if not error:
            return original_request
            
        return """
        The previous code generated resulted in the following error:
        {0}
        
        Please fix the code and provide a corrected version.
        IMPORTANT: Make sure to include a main() function as the entry point for the script.
        Original request: {1}
        """.format(str(error), original_request)

    def run(self):
        try:
            # Add option to check quota first
            check_first = rs.MessageBox("Would you like to check your API quota before proceeding?", 
                                      title="OpenAI API Quota Check", 
                                      buttons=4)  # Yes/No buttons
            if check_first == 6:  # Yes button
                self.check_api_quota()
            
            func_request = self.get_user_request()
            if not func_request:
                return

            current_attempt = 0
            last_error = None
            
            while current_attempt < self.max_attempts:
                try:
                    generated_code = self.generate_code(func_request)
                    # Save and open temporary version
                    self.save_script(generated_code, func_request, is_temporary=True)
                    
                    # Execute the script by loading it as a module using importlib
                    spec = importlib.util.spec_from_file_location("text2script", self.temp_filepath)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # Check if main function exists in the generated code
                    if hasattr(module, 'main'):
                        module.main()
                    else:
                        raise AttributeError("The generated script does not contain a main() function. Please try again.")
                    
                    saved_path = self.save_script(generated_code, func_request, is_temporary=False)
                    if saved_path:
                        rs.MessageBox("Script executed successfully and saved to:\n{}".format(saved_path))
                    break
                except ValueError as e:
                    # Check if this is an OpenAI quota error
                    if "OpenAI quota exceeded" in str(e):
                        return  # Exit without retrying
                
                except Exception as e:
                    current_attempt += 1
                    last_error = traceback.format_exc()
                    
                    if current_attempt >= self.max_attempts:
                        NOTIFICATION.messenger("Maximum refinement attempts reached.\nLast error: {}".format(last_error))
                        return
                        
                    func_request = self.create_refinement_request(func_request, e)

                    NOTIFICATION.messenger("Attempt: {} of {}\nLast error: {}".format(current_attempt, self.max_attempts, last_error))
                    SOUND.play_error_sound()
                    time.sleep(0.1)
                
                    
        except Exception as e:
            rs.MessageBox("Critical error occurred: {}".format(str(e)))
            raise

def text2script():
    if rs.ExeVersion() < 8:
        NOTIFICATION.messenger("Please upgrade to Rhino 8 to use Text2Script.")
        return
    converter = TextToScriptConverter()
    converter.run()
    SOUND.play_finished_sound()

def check_api_quota():
    """Standalone function to check OpenAI API quota without running the full script"""
    converter = TextToScriptConverter()
    converter.check_api_quota()

if __name__ == "__main__":
    # If run with argument "check_quota", just check quota
    check_api_quota()
