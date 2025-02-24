#! python3

# r: openai
import rhinoscriptsyntax as rs



__title__ = "Text2Script"
__doc__ = """Utility script to convert text to script using AI.

Note: This is Rhino 8 only.

Features:
- Converts natural language to executable Python script
- Automatic error detection and code refinement
- Integrated with Rhino's rhinoscriptsyntax
- Maximum 10 refinement attempts for optimal results
"""
import rhinoscriptsyntax as rs

import sys

for path in rs.SearchPathList():
    sys.path.append(path)

from EnneadTab import FOLDER, SECRET, NOTIFICATION, DATA_FILE, SOUND

import time
import traceback
import os
import subprocess
try:
    from openai import OpenAI
except ImportError:
    pass


from datetime import datetime

class TextToScriptConverter:
    def __init__(self):
        self.max_attempts = 5
        api_key = SECRET.get_api_key("translator_api_key")
        self.client = OpenAI(api_key=api_key)
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
        
        TECHNICAL SPECIFICATIONS:
        - Target Environment: Rhino 8 Python
        - Primary API: Rhino Common (https://developer.rhino3d.com/api/rhinocommon/)
        - Reference Examples: https://github.com/mcneel/rhino-developer-samples/tree/master/rhinopython
        
        COMMON IMPORTS TO CONSIDER:
        - import rhinoscriptsyntax as rs
        - import Rhino
        
        BEST PRACTICES:
        - Include input validation
        - Add error messages for user feedback
        - Implement proper cleanup of resources
        - Structure code in logical functions
        - When asked about using color, use color tuple (r,g,b), and rhinoscriptsyntax will have something to make good color
        
        Remember: Output must be pure Python code only, ready for direct execution.

        When asked about fixing invalid syntax, please provide a corrected version without the wrapper, which means no ```python in the begining, and no``` in the end
        """
   

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
            return generated_code.strip()
        except Exception as e:
            rs.MessageBox("Failed to generate code: {}".format(str(e)))
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
        Original request: {1}
        """.format(str(error), original_request)

    def run(self):
        try:
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
                    
                    # Enhanced execution environment setup
                    import clr
                    clr.AddReference('RhinoCommon')
                    clr.AddReference('System.Drawing')
                    
                    # Create a more comprehensive namespace
                    local_vars = {
                        'rs': __import__('rhinoscriptsyntax'),
                        'Rhino': __import__('Rhino'),
                        'scriptcontext': __import__('scriptcontext'),
                        'System': __import__('System'),
                        'clr': clr,
                        'random': __import__('random'),
                        'math': __import__('math'),
                        'os': __import__('os'),
                        'subprocess': __import__('subprocess'),
                        'time': __import__('time'),
                        'traceback': __import__('traceback'),
                        'System.Drawing': __import__('System.Drawing'),
                    }
                    
                    # Update preset to include common imports
                    self.preset += """
                    REQUIRED IMPORTS TO INCLUDE:
                    import rhinoscriptsyntax as rs
                    import Rhino
                    import System.Drawing
                    """
                    
                    # Execute with enhanced error capture
                    exec(generated_code, local_vars, local_vars)
                    
                    saved_path = self.save_script(generated_code, func_request, is_temporary=False)
                    if saved_path:
                        rs.MessageBox("Script executed successfully and saved to:\n{}".format(saved_path))
                    break
                    
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

if __name__ == "__main__":
    text2script()
