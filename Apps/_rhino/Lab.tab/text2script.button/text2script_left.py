#! python3

# r: openai
# r: requests
import rhinoscriptsyntax as rs
import sys
from typing import Optional, Tuple
from pathlib import Path
from datetime import datetime
import time
import traceback
import os
import subprocess
import importlib.util
import requests
from openai import OpenAI

def add_path():
    """Add Rhino's Python search paths to sys.path."""
    for path in rs.SearchPathList():
        sys.path.append(path)

add_path()
from EnneadTab import FOLDER, SECRET, NOTIFICATION, DATA_FILE, SOUND

__title__ = "Text2Script"
__doc__ = """Utility script to convert text to script using AI.

Note: This is Rhino 8 only.

Features:
- Converts natural language to executable Python script
- Integrated with Rhino's rhinoscriptsyntax
- Maximum 5 refinement attempts for optimal results
- Always uses main() as the entry function
- Modern error handling and user feedback
"""

class TextToScriptConverter:
    """Converts natural language requests into executable Rhino Python scripts using OpenAI."""
    
    def __init__(self):
        """Initialize the converter with API key and configuration."""
        self.max_attempts = 5
        self.api_key = SECRET.get_api_key("EnneadTabAPI")
        self.client = OpenAI(api_key=self.api_key)
        self.temp_filepath = FOLDER.get_local_dump_folder_file("text2script_TEMP.py")
        self.preset = self._get_system_preset()
        
    def _get_system_preset(self) -> str:
        """Get the system preset for OpenAI API."""
        return """
        You are a specialized Python code generator for Rhino 8, focused on creating executable scripts.
        
        IMPORTANT REQUIREMENTS:
        1. Return ONLY pure Python code - no markdown, no code blocks, no explanations
        2. Code must be complete, self-contained, and immediately executable
        3. Include proper error handling and input validation
        4. Use descriptive variable names and add clear comments
        5. Follow PEP 8 style guidelines
        6. Include docstring for main functions
        7. ALWAYS include a main() function that serves as the entry point
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
        """
    
    def check_api_quota(self) -> bool:
        """Check if OpenAI API key is valid.
        
        Returns:
            bool: True if API key is valid, False otherwise
        """
        try:
            self.client.models.list()
            print("Your API key is valid and ready to use.")
            return True
        except Exception as e:
            error_str = str(e)
            if "401" in error_str or "authentication" in error_str.lower():
                message = "Your API key appears to be invalid or expired."
            else:
                message = f"Error checking API key: {error_str}"
            
            rs.MessageBox(message, title="OpenAI API Status")
            return False

    def get_user_request(self) -> Optional[str]:
        """Get user input for script generation.
        
        Returns:
            Optional[str]: User's request or None if cancelled
        """
        prev_session = DATA_FILE.get_sticky("text2script_session", "Write your dream here.")
        request = rs.StringBox("Enter the function request:", title="Text2Script", default_value=prev_session)
        
        if not request or request.strip() == "":
            rs.MessageBox("No input provided. Operation cancelled.")
            return None
            
        DATA_FILE.set_sticky("text2script_session", request.strip())
        return request.strip()

    def generate_code(self, request: str) -> str:
        """Generate Python code from user request.
        
        Args:
            request (str): User's natural language request
            
        Returns:
            str: Generated Python code
            
        Raises:
            ValueError: If AI returns empty response or quota exceeded
            Exception: For other generation errors
        """
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

            # Clean up code formatting
            generated_code = self._clean_code_formatting(generated_code)
            
            if not generated_code or generated_code.strip() == "":
                raise ValueError("AI returned empty response")
                
            # Ensure proper code structure
            generated_code = self._ensure_code_structure(generated_code)
            
            return generated_code.strip()
            
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "quota" in error_str.lower() or "insufficient_quota" in error_str:
                raise ValueError("OpenAI quota exceeded - Please check your account")
            else:
                rs.MessageBox(f"Failed to generate code: {error_str}")
                raise

    def _clean_code_formatting(self, code: str) -> str:
        """Clean up code formatting by removing markdown wrappers."""
        if "```python" in code:
            code = code.replace("```python", "")
        if "```" in code:
            code = code.replace("```", "")
        return code

    def _ensure_code_structure(self, code: str) -> str:
        """Ensure code has proper structure with main() function and entry point."""
        if "def main(" not in code:
            code = self._add_main_function(code)
            
        if "if __name__ == \"__main__\"" not in code and "if __name__ == '__main__'" not in code:
            code += "\n\nif __name__ == \"__main__\":\n    main()\n"
            
        return code

    def _add_main_function(self, code: str) -> str:
        """Add main function to code if missing."""
        main_function = "\n\ndef main():\n    # Main function added by Text2Script\n    # Your code entry point\n    "
        
        # Find top-level code to move into main
        import re
        function_pattern = r"def\s+\w+\s*\("
        lines = code.split("\n")
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
                code = code.replace(line, "")
            code = code.strip()
        
        return code + main_function

    def save_script(self, script_content: str, request: str, is_temporary: bool = True) -> Optional[Path]:
        """Save script to file and open it in editor.
        
        Args:
            script_content (str): Generated script content
            request (str): Original user request
            is_temporary (bool): If True, saves as temp file and opens in VSCode.
                               If False, saves as timestamped file and opens in default editor.
            
        Returns:
            Optional[Path]: Path to saved file if successful, None if failed
        """
        try:
            if is_temporary:
                filepath = Path(self.temp_filepath)
                header = "Generated from Text2Script (TEMPORARY VERSION)"
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"text2script_{timestamp}.py"
                filepath = Path(FOLDER.get_local_dump_folder_file(filename))
                header = "Generated from Text2Script"

            request_string = "\n".join(f"# {line}" for line in request.split("\n"))
            
            content = f"""# {header}
# Original request: 
{request_string}
# Generated on: {datetime.now()}

{script_content}"""
            
            filepath.write_text(content, encoding='utf-8')
            
            try:
                # Try to open in VSCode first
                vscode_paths = [
                    Path.home() / "AppData" / "Local" / "Programs" / "Microsoft VS Code" / "Code.exe",
                    Path("C:/Program Files/Microsoft VS Code/Code.exe"),
                    Path("C:/Program Files (x86)/Microsoft VS Code/Code.exe")
                ]
                
                vscode_path = next((path for path in vscode_paths if path.exists()), None)
                
                if vscode_path:
                    subprocess.Popen([str(vscode_path), str(filepath)])
                else:
                    os.startfile(str(filepath))
            except Exception:
                os.startfile(str(filepath))
   
            return filepath
        except Exception as e:
            rs.MessageBox(f"Failed to save script: {str(e)}")
            return None

    def create_refinement_request(self, original_request: str, error: Exception) -> str:
        """Create a refined request based on previous error.
        
        Args:
            original_request (str): Original user request
            error (Exception): Error from previous attempt
            
        Returns:
            str: Refined request for next attempt
        """
        if not error:
            return original_request
            
        return f"""
        The previous code generated resulted in the following error:
        {str(error)}
        
        Please fix the code and provide a corrected version.
        IMPORTANT: Make sure to include a main() function as the entry point for the script.
        Original request: {original_request}
        """

    def run(self) -> None:
        """Main execution method for the converter."""
        try:
            if not self.check_api_quota():
                return

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
                    
                    # Execute the script
                    spec = importlib.util.spec_from_file_location("text2script", str(self.temp_filepath))
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    if hasattr(module, 'main'):
                        module.main()
                    else:
                        raise AttributeError("The generated script does not contain a main() function. Please try again.")
                    
                    saved_path = self.save_script(generated_code, func_request, is_temporary=False)
                    if saved_path:
                        rs.MessageBox(f"Script executed successfully and saved to:\n{saved_path}")
                    break
                    
                except ValueError as e:
                    if "OpenAI quota exceeded" in str(e):
                        return
                
                except Exception as e:
                    current_attempt += 1
                    last_error = traceback.format_exc()
                    
                    if current_attempt >= self.max_attempts:
                        NOTIFICATION.messenger(f"Maximum refinement attempts reached.\nLast error: {last_error}")
                        return
                        
                    func_request = self.create_refinement_request(func_request, e)
                    NOTIFICATION.messenger(f"Attempt: {current_attempt} of {self.max_attempts}\nLast error: {last_error}")
                    SOUND.play_error_sound()
                    time.sleep(0.1)
                
        except Exception as e:
            rs.MessageBox(f"Critical error occurred: {str(e)}")
            raise

def text2script() -> None:
    """Main entry point for Text2Script functionality."""
    if rs.ExeVersion() < 8:
        NOTIFICATION.messenger("Please upgrade to Rhino 8 to use Text2Script.")
        return
        
    converter = TextToScriptConverter()
    converter.run()
    SOUND.play_finished_sound()

def check_api_quota() -> None:
    """Standalone function to check OpenAI API key validity."""
    converter = TextToScriptConverter()
    converter.check_api_quota()

if __name__ == "__main__":
    # If run with argument "check_quota", just check quota
    check_api_quota()
