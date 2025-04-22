"""
Image-based Auto Clicker
------------------------
Automatically searches for and clicks on a specified image on screen.
Requires an image file in the same directory as the script.

Dependencies:
    - pyautogui
    - mouse
    - tkinter (included in Python standard library)

Usage:
    Place target image in script directory
    Use the control window's Terminate button to stop
"""

import time
import sys
import os
import traceback
from pathlib import Path
import tkinter as tk
from tkinter import messagebox

try:
    import pyautogui
    import mouse
except ImportError:
    print("Please install required packages:")
    print("pip install pyautogui mouse")
    sys.exit(1)

class MinimalGUI:
    """Minimal GUI window with terminate button"""
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Auto Clicker Control")
        self.root.geometry("200x50")
        self.running = True
        
        # Create terminate button
        self.terminate_btn = tk.Button(
            self.root, 
            text="Terminate", 
            command=self.terminate_program
        )
        self.terminate_btn.pack(pady=10)
        
        # Minimize window on start
        self.root.iconify()
    
    def terminate_program(self):
        """Handle terminate button click"""
        if messagebox.askyesno("Confirm Exit", "Are you sure you want to exit?"):
            self.running = False
            self.root.quit()
    
    def start(self):
        """Start GUI event loop"""
        self.root.protocol("WM_DELETE_WINDOW", self.terminate_program)
        self.root.mainloop()

def auto_clicker():
    print("Image-based auto-clicker started. Use control window to stop.")
    
    # Create and start GUI
    gui = MinimalGUI()
    import threading
    gui_thread = threading.Thread(target=gui.start, daemon=True)
    gui_thread.start()
    
    try:
        while gui.running:
            # Get script directory and all button images
            script_dir = Path(__file__).parent
            button_images = list(script_dir.glob("button_*.png"))
            
            if not button_images:
                print("Waiting for images to appear in script directory...")
                time.sleep(5)
                continue
            
            # Look for each image on screen
            for button_image in button_images:
                if not gui.running:  # Check if termination was requested
                    break
                try:
                    button_pos = pyautogui.locateOnScreen(str(button_image), confidence=0.9)
                    
                    if button_pos:
                        center_x, center_y = pyautogui.center(button_pos)
                        mouse.move(center_x, center_y)
                        mouse.click('left')
                        print("Image {} found and clicked".format(button_image.name))
                        break  # Exit loop after first match is found and clicked
                except Exception as e:
                    print("Error processing {}: {}".format(button_image.name, str(e)))
                    continue
            
            time.sleep(5)  # Wait 5 seconds before next search

    except Exception as e:
        print("Error: " + traceback.format_exc())
    finally:
        print("Auto-clicker stopped.")

if __name__ == "__main__":
    print("Starting in 3 seconds...")
    time.sleep(3)
    auto_clicker()
