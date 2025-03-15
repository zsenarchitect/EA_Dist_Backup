from __future__ import print_function, division, absolute_import


# r: cv2
# r: numpy
# r: torch
# r: diffusers
# r: transformers
# r: Pillow
# r: tkinter
# r: ttkthemes
__title__ = "ViewPrettifier"
__doc__ = """Generate AI renderings from architectural images.
Features:
- Processes existing architectural images
- Detects edges in the image to preserve model structure
- Allows use of style reference images
- Modern dark-themed GUI for configuration
- Model and ControlNet selection
- Progress tracking with step indicators
- Generates AI renderings using Stable Diffusion with ControlNet
- Shows real-time progress during generation
- Automatically installs required dependencies
- Monitors for stalled processes and provides diagnostics
"""

import os
import time
import sys
import subprocess
import logging
import psutil
import threading
try:
    from queue import Queue  # Python 3
except ImportError:
    from Queue import Queue  # Python 2
try:
    import tkinter as tk
    from tkinter import ttk, messagebox
except ImportError:
    import Tkinter as tk
    import ttk
    import tkMessageBox as messagebox

# Configure logging with more detailed formatting
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('viewprettifier_debug.log', mode='w')  # 'w' mode to start fresh each run
    ]
)
logger = logging.getLogger('ViewPrettifier')

# Add memory monitoring
def log_memory_usage():
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    logger.debug(f"Memory usage - RSS: {memory_info.rss / 1024 / 1024:.1f}MB, VMS: {memory_info.vms / 1024 / 1024:.1f}MB")

# Progress queue for inter-thread communication
progress_queue = Queue()

def update_progress_bar():
    """Update progress bar and status label in GUI mode."""
    try:
        while True:
            progress, status = progress_queue.get_nowait()
            if hasattr(sys, '_progress_bar'):
                sys._progress_bar['value'] = progress
                sys._status_label['text'] = status
                sys._root.update()
            progress_queue.task_done()
    except:
        pass
    if hasattr(sys, '_root'):
        sys._root.after(100, update_progress_bar)

def show_progress(progress, status):
    """Show progress in both CLI and GUI modes."""
    progress_queue.put((progress, status))
    if not hasattr(sys, '_root'):
        # CLI mode progress
        sys.stdout.write(f"\rProgress: [{('=' * int(progress/2)).ljust(50)}] {progress}% - {status}")
        sys.stdout.flush()
        if progress >= 100:
            print()

# Import our modules with better error handling
try:
    import image_generator
    logger.info("Successfully imported image generator module")
except Exception as e:
    logger.error(f"Failed to import image generator: {str(e)}")
    raise

def check_system_resources():
    """Check if system has sufficient resources to run."""
    memory = psutil.virtual_memory()
    cpu_percent = psutil.cpu_percent()
    
    logger.info(f"System check - Available RAM: {memory.available/1024/1024:.1f}MB, CPU Usage: {cpu_percent}%")
    
    if memory.available < 2 * 1024 * 1024 * 1024:  # Less than 2GB available
        logger.warning("Low memory available, performance may be affected")
        return False, "Low memory available"
    
    if cpu_percent > 90:
        logger.warning("High CPU usage, performance may be affected")
        return False, "High CPU usage"
        
    return True, "System resources OK"

def check_image_exists(image_path):
    """Check if an image exists and is a valid file."""
    exists = os.path.isfile(image_path) and os.path.exists(image_path)
    logger.debug(f"Checking image path: {image_path} - Exists: {exists}")
    return exists

def install_dependencies():
    """Install required dependencies if they are missing."""
    logger.info("Starting dependency installation...")
    
    # Monitor initial memory usage
    log_memory_usage()
    
    # List of required packages - adding GUI dependencies
    required_packages = [
        "torch", "diffusers", "transformers", "opencv-python", "pillow", 
        "psutil", "accelerate", "ttkthemes"
    ]
    
    show_progress(0, "Installing dependencies...")
    total_packages = len(required_packages)
    
    # Install each package if not already installed
    for i, package in enumerate(required_packages):
        try:
            __import__(package.replace("-", "_"))
            logger.info(f"{package} is already installed.")
        except ImportError:
            logger.info(f"Installing {package}...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                logger.info(f"{package} installed successfully.")
            except Exception as e:
                logger.error(f"Failed to install {package}: {str(e)}")
                # Continue with other packages
        
        # Update progress
        progress = int((i + 1) / total_packages * 100)
        show_progress(progress, f"Installing dependencies ({i+1}/{total_packages})")
    
    # Check final memory usage
    log_memory_usage()
    logger.info("Dependency installation complete.")
    return True

def launch_gui_mode():
    """Launch the GUI interface for ViewPrettifier."""
    logger.info("Launching GUI mode...")
    try:
        import gui
        
        # Create progress bar window
        root = tk.Tk()
        root.title("ViewPrettifier Progress")
        root.geometry("400x150")
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Horizontal.TProgressbar", thickness=25)
        
        # Add progress bar
        progress_frame = ttk.Frame(root, padding="10")
        progress_frame.pack(fill=tk.X, expand=True)
        
        progress_bar = ttk.Progressbar(
            progress_frame,
            orient="horizontal",
            mode="determinate",
            style="Horizontal.TProgressbar"
        )
        progress_bar.pack(fill=tk.X, pady=10)
        
        # Add status label
        status_label = ttk.Label(progress_frame, text="Initializing...", wraplength=380)
        status_label.pack(fill=tk.X, pady=5)
        
        # Store references for update_progress_bar
        sys._root = root
        sys._progress_bar = progress_bar
        sys._status_label = status_label
        
        # Start progress updates
        root.after(100, update_progress_bar)
        
        # Launch GUI
        gui.launch_gui()
        
    except Exception as e:
        logger.error(f"Error launching GUI: {str(e)}", exc_info=True)
        raise

def cli_mode():
    """Run ViewPrettifier in command-line interface mode."""
    logger.info("Starting CLI mode...")
    
    # Check system resources
    resources_ok, message = check_system_resources()
    if not resources_ok:
        logger.warning(f"Resource check warning: {message}")
        print(f"Warning: {message}")
    
    current_folder = os.path.dirname(os.path.abspath(__file__))
    logger.debug(f"Current folder: {current_folder}")
    
    base_image = os.path.join(current_folder, "image_base.jpg")
    style_image = os.path.join(current_folder, "image_ref.jpg")
    prompt = "modern architecture with natural material"
    negative_prompt = "ugly, deformed, watermark, signature, text"
    output_path = os.path.join(current_folder, "image_output.jpg")
    
    # Verify input image exists
    if not check_image_exists(base_image):
        error_msg = "Base image not found. Please place an image named 'image_base.jpg' in the script folder."
        logger.error(error_msg)
        print(f"Error: {error_msg}")
        return
    
    # Create ImageGenerator instance with progress callback
    generator = image_generator.create_image_generator()
    
    # Monitor memory usage
    log_memory_usage()
    
    try:
        # Start generation with progress reporting
        logger.info("Starting image generation...")
        thread = generator.generate_image(base_image, style_image, prompt, negative_prompt, output_path)
        
        # Monitor progress
        while thread.is_alive():
            progress, status, _ = generator.get_progress_status()
            show_progress(progress, status)
            
            # Check if process is stuck
            is_stuck, reason = generator.check_if_stuck()
            if is_stuck:
                logger.warning(f"Process appears stuck: {reason}")
                print(f"\nWarning: {reason}")
                break
            
            # Monitor resource usage
            log_memory_usage()
            time.sleep(0.5)
        
        # Final progress update
        progress, status, _ = generator.get_progress_status()
        show_progress(progress, status)
        
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        print("\nProcess interrupted by user")
        generator.terminate()
    except Exception as e:
        logger.error(f"Error during generation: {str(e)}", exc_info=True)
        print(f"\nError: {str(e)}")
    finally:
        # Final memory usage check
        log_memory_usage()

def view_prettifier():
    """Generate AI rendering from an architectural image."""
    logger.info("Starting ViewPrettifier...")
    
    # Check if we should run in CLI mode
    cli_mode_flag = "--cli" in sys.argv
    logger.debug(f"CLI mode flag: {cli_mode_flag}")
    
    try:
        # Install dependencies if needed
        install_dependencies()
        
        if cli_mode_flag:
            logger.info("Running in CLI mode")
            cli_mode()
        else:
            logger.info("Running in GUI mode")
            try:
                launch_gui_mode()
            except Exception as e:
                logger.error(f"Error launching GUI: {str(e)}")
                logger.info("Falling back to command-line mode")
                cli_mode()
                
    except Exception as e:
        logger.error(f"Unexpected error in view_prettifier: {str(e)}", exc_info=True)
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    try:
        logger.info("ViewPrettifier script started")
        view_prettifier()
    except Exception as e:
        logger.error(f"Fatal error in main: {str(e)}", exc_info=True)
        print(f"Fatal error: {str(e)}")
