"""Modern GUI for ViewPrettifier.

This module provides a sophisticated, dark-themed GUI for the ViewPrettifier tool,
with real-time progress tracking, model selection, and image customization.
"""

import os
import sys
import time
import threading
import tkinter as tk
from tkinter import ttk, filedialog, StringVar, DoubleVar, BooleanVar
from PIL import Image, ImageTk
import image_generator
import importlib

# Check if ttkthemes is available for better dark theme support
try:
    from ttkthemes import ThemedTk
    HAS_THEMED_TK = True
except ImportError:
    HAS_THEMED_TK = False
    pass

# Models that can be selected (model_id: display_name)
AVAILABLE_MODELS = {
    "runwayml/stable-diffusion-v1-5": "Stable Diffusion v1.5 (Default)",
    "stabilityai/stable-diffusion-2-1": "Stable Diffusion v2.1",
    "CompVis/stable-diffusion-v1-4": "Stable Diffusion v1.4",
    "SG161222/Realistic_Vision_V4.0": "Realistic Vision v4.0",
    "dreamlike-art/dreamlike-photoreal-2.0": "Dreamlike Photoreal 2.0"
}

# Control nets that can be selected
AVAILABLE_CONTROLNETS = {
    "lllyasviel/sd-controlnet-canny": "Canny Edge (Default)",
    "lllyasviel/sd-controlnet-depth": "Depth",
    "lllyasviel/sd-controlnet-hed": "HED Boundary",
    "lllyasviel/sd-controlnet-mlsd": "MLSD Lines",
    "lllyasviel/sd-controlnet-normal": "Normal Map"
}

class ToolTip:
    """Create tooltips for a given widget."""
    
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)
    
    def show_tooltip(self, event=None):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        
        # Create a toplevel window
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        
        label = ttk.Label(self.tooltip, text=self.text, wraplength=250,
                         background="#2d2d30", foreground="#e0e0e0", relief="solid", borderwidth=1)
        label.pack(padx=5, pady=5)
    
    def hide_tooltip(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

class ProgressBar(ttk.Frame):
    """Custom progress bar with step indicator."""
    
    def __init__(self, parent, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        
        # Create variables for tracking progress
        self.current_step = StringVar(value="0")
        self.total_steps = StringVar(value="5")
        self.progress_var = DoubleVar(value=0.0)
        self.status_text = StringVar(value="Ready")
        
        # Create UI elements
        self.create_widgets()
    
    def create_widgets(self):
        """Create the progress bar and step indicator."""
        # Progress bar
        style = ttk.Style()
        style.configure("Custom.Horizontal.TProgressbar", 
                       background='#007acc', troughcolor='#252526')
        
        self.progress = ttk.Progressbar(self, style="Custom.Horizontal.TProgressbar", 
                                        orient="horizontal", length=400,
                                        mode="determinate", variable=self.progress_var)
        self.progress.pack(pady=5, fill=tk.X)
        
        # Step indicator frame
        step_frame = ttk.Frame(self)
        step_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Step counter (x/y)
        self.step_label = ttk.Label(step_frame, 
                                   text="Step:", 
                                   foreground="#e0e0e0")
        self.step_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.step_counter = ttk.Label(step_frame, 
                                     textvariable=tk.StringVar(value=f"{self.current_step.get()}/{self.total_steps.get()}"),
                                     foreground="#007acc")
        self.step_counter.pack(side=tk.LEFT)
        
        # Status text
        self.status_label = ttk.Label(step_frame, 
                                     textvariable=self.status_text,
                                     foreground="#e0e0e0")
        self.status_label.pack(side=tk.RIGHT)
    
    def update_progress(self, value, step=None, total=None, status=None):
        """Update progress bar and step indicator."""
        self.progress_var.set(value)
        
        if step is not None:
            self.current_step.set(str(step))
        
        if total is not None:
            self.total_steps.set(str(total))
        
        if status is not None:
            self.status_text.set(status)
        
        # Update the step counter text
        self.step_counter.configure(text=f"{self.current_step.get()}/{self.total_steps.get()}")
        
        # Force update
        self.update_idletasks()

class ViewPrettifierGUI:
    """Main GUI class for ViewPrettifier."""
    
    def __init__(self, root=None):
        """Initialize the GUI."""
        self.setup_root(root)
        self.setup_styles()
        self.create_variables()
        self.create_widgets()
        self.setup_updater()
        
        # Reference to the generator
        self.generator = image_generator.generator
        
        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_root(self, root):
        """Setup the root window."""
        if root is None:
            # Use themed Tk if available for better dark theme
            if HAS_THEMED_TK:
                self.root = ThemedTk(theme="equilux")
            else:
                self.root = tk.Tk()
        else:
            self.root = root
        
        self.root.title("ViewPrettifier")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        # Set dark theme colors
        self.root.configure(bg="#252526")
        
        # Try to set taskbar icon
        try:
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.png")
            if os.path.exists(icon_path):
                self.root.iconphoto(True, tk.PhotoImage(file=icon_path))
        except:
            pass
    
    def setup_styles(self):
        """Setup custom styles for widgets."""
        self.style = ttk.Style()
        
        # Configure dark theme
        self.style.configure("TFrame", background="#252526")
        self.style.configure("TLabel", background="#252526", foreground="#e0e0e0")
        self.style.configure("TButton", background="#3c3c3c", foreground="#e0e0e0", 
                            font=("Segoe UI", 10))
        self.style.configure("TCheckbutton", background="#252526", foreground="#e0e0e0")
        self.style.configure("TRadiobutton", background="#252526", foreground="#e0e0e0")
        self.style.configure("TEntry", fieldbackground="#3c3c3c", foreground="#e0e0e0")
        self.style.configure("TCombobox", fieldbackground="#3c3c3c", foreground="#e0e0e0")
        
        # Button styles
        self.style.configure("Primary.TButton", background="#007acc", foreground="white")
        self.style.map("Primary.TButton",
                     background=[("active", "#1f8ad2"), ("disabled", "#555555")])
        
        # Header style
        self.style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"), foreground="#e0e0e0")
        
        # Section header style
        self.style.configure("Section.TLabel", font=("Segoe UI", 12, "bold"), foreground="#007acc")
        
        # Configure the comboboxes
        self.root.option_add("*TCombobox*Listbox.background", "#3c3c3c")
        self.root.option_add("*TCombobox*Listbox.foreground", "#e0e0e0")
    
    def create_variables(self):
        """Create variables for storing user input."""
        # Get the current folder
        self.current_folder = os.path.dirname(os.path.abspath(__file__))
        
        # Input image paths
        self.base_image_path = StringVar(value=os.path.join(self.current_folder, "image_base.jpg"))
        self.style_image_path = StringVar(value=os.path.join(self.current_folder, "image_ref.jpg"))
        self.output_image_path = StringVar(value=os.path.join(self.current_folder, "image_output.jpg"))
        
        # Prompt variables
        self.prompt = StringVar(value="modern architecture with natural material")
        self.negative_prompt = StringVar(value="ugly, deformed, watermark, signature, text")
        
        # Model selection
        self.selected_model = StringVar(value=list(AVAILABLE_MODELS.keys())[0])
        self.selected_controlnet = StringVar(value=list(AVAILABLE_CONTROLNETS.keys())[0])
        
        # Advanced options
        self.use_gpu = BooleanVar(value=True)
        self.steps = StringVar(value="30")
        self.guidance_scale = StringVar(value="7.5")
        self.use_online_compute = BooleanVar(value=False)
        
        # Processing status
        self.is_processing = False
        self.progress_value = 0
        self.current_step = 0
        self.total_steps = 5
        self.status_text = "Ready"
        
        # Step mapping for progress tracking
        self.step_mapping = {
            "Starting": 1,
            "Detecting edges": 2,
            "Loading models": 3,
            "Preparing images": 3,
            "Generating image": 4,
            "Processing final image": 4,
            "Complete": 5,
            "Failed": 5,
            "Error": 5,
            "Terminated": 5
        }
    
    def create_widgets(self):
        """Create GUI widgets."""
        # Main container with padding
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title and description
        self.create_header()
        
        # Create a notebook with tabs
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Create tabs
        self.create_main_tab()
        self.create_advanced_tab()
        
        # Progress section
        self.create_progress_section()
        
        # Action buttons
        self.create_action_buttons()
        
        # Status bar at the bottom
        self.create_status_bar()
    
    def create_header(self):
        """Create header with title and description."""
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        title = ttk.Label(header_frame, text="ViewPrettifier", style="Header.TLabel")
        title.pack(anchor="w")
        
        description = ttk.Label(header_frame, 
                              text="Generate AI renderings from architectural images using Stable Diffusion",
                              wraplength=700)
        description.pack(anchor="w")
    
    def create_main_tab(self):
        """Create the main configuration tab."""
        main_tab = ttk.Frame(self.notebook)
        self.notebook.add(main_tab, text="Main Settings")
        
        # Two columns layout
        left_frame = ttk.Frame(main_tab)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        right_frame = ttk.Frame(main_tab)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Left column - Image selection
        self.create_image_selection(left_frame)
        
        # Right column - Prompt settings
        self.create_prompt_settings(right_frame)
    
    def create_advanced_tab(self):
        """Create the advanced settings tab."""
        advanced_tab = ttk.Frame(self.notebook)
        self.notebook.add(advanced_tab, text="Advanced Settings")
        
        # Model selection
        model_frame = ttk.LabelFrame(advanced_tab, text="AI Model Settings", padding=10)
        model_frame.pack(fill=tk.X, pady=5)
        
        # Model
        model_label = ttk.Label(model_frame, text="Stable Diffusion Model:")
        model_label.grid(row=0, column=0, sticky="w", pady=5)
        
        model_combo = ttk.Combobox(model_frame, textvariable=self.selected_model, state="readonly")
        model_combo['values'] = list(AVAILABLE_MODELS.keys())
        model_combo.grid(row=0, column=1, sticky="we", padx=5, pady=5)
        
        model_name = ttk.Label(model_frame, textvariable=StringVar(value=""))
        model_name.grid(row=0, column=2, sticky="w", padx=5, pady=5)
        
        # Update model name when selection changes
        def update_model_name(*args):
            model_id = self.selected_model.get()
            model_name.configure(text=AVAILABLE_MODELS.get(model_id, ""))
        
        self.selected_model.trace_add("write", update_model_name)
        update_model_name()  # Initialize
        
        # ControlNet
        controlnet_label = ttk.Label(model_frame, text="ControlNet Type:")
        controlnet_label.grid(row=1, column=0, sticky="w", pady=5)
        
        controlnet_combo = ttk.Combobox(model_frame, textvariable=self.selected_controlnet, state="readonly")
        controlnet_combo['values'] = list(AVAILABLE_CONTROLNETS.keys())
        controlnet_combo.grid(row=1, column=1, sticky="we", padx=5, pady=5)
        
        controlnet_name = ttk.Label(model_frame, textvariable=StringVar(value=""))
        controlnet_name.grid(row=1, column=2, sticky="w", padx=5, pady=5)
        
        # Update controlnet name when selection changes
        def update_controlnet_name(*args):
            controlnet_id = self.selected_controlnet.get()
            controlnet_name.configure(text=AVAILABLE_CONTROLNETS.get(controlnet_id, ""))
        
        self.selected_controlnet.trace_add("write", update_controlnet_name)
        update_controlnet_name()  # Initialize
        
        # GPU checkbox
        gpu_check = ttk.Checkbutton(model_frame, text="Use GPU acceleration (if available)", 
                                  variable=self.use_gpu)
        gpu_check.grid(row=2, column=0, columnspan=3, sticky="w", pady=5)
        
        # Generation settings
        generation_frame = ttk.LabelFrame(advanced_tab, text="Generation Settings", padding=10)
        generation_frame.pack(fill=tk.X, pady=5)
        
        # Steps
        steps_label = ttk.Label(generation_frame, text="Inference Steps:")
        steps_label.grid(row=0, column=0, sticky="w", pady=5)
        
        steps_entry = ttk.Entry(generation_frame, textvariable=self.steps, width=10)
        steps_entry.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        ToolTip(steps_entry, "Higher values give better quality but take longer. Range: 20-50")
        
        # Guidance Scale
        guidance_label = ttk.Label(generation_frame, text="Guidance Scale:")
        guidance_label.grid(row=1, column=0, sticky="w", pady=5)
        
        guidance_entry = ttk.Entry(generation_frame, textvariable=self.guidance_scale, width=10)
        guidance_entry.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        ToolTip(guidance_entry, "How closely to follow the prompt. Higher values are more accurate but less creative. Range: 5-15")
        
        # Online compute
        online_frame = ttk.LabelFrame(advanced_tab, text="Compute Options", padding=10)
        online_frame.pack(fill=tk.X, pady=5)
        
        online_check = ttk.Checkbutton(online_frame, 
                                     text="Use online compute (requires API key)", 
                                     variable=self.use_online_compute)
        online_check.pack(anchor="w", pady=5)
        
        # API Key
        api_key_label = ttk.Label(online_frame, text="API Key:")
        api_key_label.pack(anchor="w", pady=(5, 0))
        
        api_key_entry = ttk.Entry(online_frame, width=40, show="*")
        api_key_entry.pack(anchor="w", pady=(0, 5), fill=tk.X)
        
        # For now, disable online compute since it's not implemented
        online_check.configure(state="disabled")
        api_key_entry.configure(state="disabled")
        
        # Add a note about future feature
        note_label = ttk.Label(online_frame, 
                             text="Online compute option will be available in a future update.",
                             foreground="#aaaaaa")
        note_label.pack(anchor="w", pady=5)
        
        # Configure grid
        model_frame.columnconfigure(1, weight=1)
        generation_frame.columnconfigure(1, weight=1)
    
    def create_image_selection(self, parent):
        """Create image selection widgets."""
        image_frame = ttk.LabelFrame(parent, text="Image Selection", padding=10)
        image_frame.pack(fill=tk.BOTH, expand=True)
        
        # Base image
        base_label = ttk.Label(image_frame, text="Base Image:", style="Section.TLabel")
        base_label.pack(anchor="w", pady=(0, 5))
        
        base_preview_frame = ttk.Frame(image_frame)
        base_preview_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.base_preview = ttk.Label(base_preview_frame, text="Preview not available")
        self.base_preview.pack(fill=tk.BOTH, expand=True)
        
        base_path_frame = ttk.Frame(image_frame)
        base_path_frame.pack(fill=tk.X, pady=(0, 10))
        
        base_path_entry = ttk.Entry(base_path_frame, textvariable=self.base_image_path)
        base_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        base_browse_btn = ttk.Button(base_path_frame, text="Browse...",
                                   command=lambda: self.browse_file(self.base_image_path, "Select Base Image", 
                                                                  [("Image files", "*.jpg;*.jpeg;*.png")]))
        base_browse_btn.pack(side=tk.RIGHT)
        
        # Style reference image
        style_label = ttk.Label(image_frame, text="Style Reference Image:", style="Section.TLabel")
        style_label.pack(anchor="w", pady=(0, 5))
        
        style_preview_frame = ttk.Frame(image_frame)
        style_preview_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.style_preview = ttk.Label(style_preview_frame, text="Preview not available")
        self.style_preview.pack(fill=tk.BOTH, expand=True)
        
        style_path_frame = ttk.Frame(image_frame)
        style_path_frame.pack(fill=tk.X)
        
        style_path_entry = ttk.Entry(style_path_frame, textvariable=self.style_image_path)
        style_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        style_browse_btn = ttk.Button(style_path_frame, text="Browse...",
                                    command=lambda: self.browse_file(self.style_image_path, "Select Style Reference Image", 
                                                                   [("Image files", "*.jpg;*.jpeg;*.png")]))
        style_browse_btn.pack(side=tk.RIGHT)
        
        # Update previews when paths change
        self.base_image_path.trace_add("write", lambda *args: self.update_preview(self.base_image_path.get(), self.base_preview))
        self.style_image_path.trace_add("write", lambda *args: self.update_preview(self.style_image_path.get(), self.style_preview))
        
        # Initialize previews
        self.update_preview(self.base_image_path.get(), self.base_preview)
        self.update_preview(self.style_image_path.get(), self.style_preview)
    
    def create_prompt_settings(self, parent):
        """Create prompt settings widgets."""
        prompt_frame = ttk.LabelFrame(parent, text="Prompt Settings", padding=10)
        prompt_frame.pack(fill=tk.BOTH, expand=True)
        
        # Positive prompt
        positive_label = ttk.Label(prompt_frame, text="Positive Prompt:", style="Section.TLabel")
        positive_label.pack(anchor="w", pady=(0, 5))
        
        positive_prompt_frame = ttk.Frame(prompt_frame)
        positive_prompt_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        positive_entry = tk.Text(positive_prompt_frame, height=5, bg="#3c3c3c", fg="#e0e0e0", 
                                wrap=tk.WORD, relief=tk.FLAT, padx=5, pady=5)
        positive_entry.pack(fill=tk.BOTH, expand=True)
        positive_entry.insert(tk.END, self.prompt.get())
        
        # Update StringVar when text changes
        def update_prompt(*args):
            self.prompt.set(positive_entry.get("1.0", "end-1c"))
        
        positive_entry.bind("<KeyRelease>", update_prompt)
        
        # Negative prompt
        negative_label = ttk.Label(prompt_frame, text="Negative Prompt:", style="Section.TLabel")
        negative_label.pack(anchor="w", pady=(0, 5))
        
        negative_prompt_frame = ttk.Frame(prompt_frame)
        negative_prompt_frame.pack(fill=tk.BOTH, expand=True)
        
        negative_entry = tk.Text(negative_prompt_frame, height=5, bg="#3c3c3c", fg="#e0e0e0", 
                                wrap=tk.WORD, relief=tk.FLAT, padx=5, pady=5)
        negative_entry.pack(fill=tk.BOTH, expand=True)
        negative_entry.insert(tk.END, self.negative_prompt.get())
        
        # Update StringVar when text changes
        def update_negative_prompt(*args):
            self.negative_prompt.set(negative_entry.get("1.0", "end-1c"))
        
        negative_entry.bind("<KeyRelease>", update_negative_prompt)
        
        # Output settings
        output_frame = ttk.LabelFrame(parent, text="Output Settings", padding=10)
        output_frame.pack(fill=tk.X, pady=(10, 0))
        
        output_label = ttk.Label(output_frame, text="Output Image Path:")
        output_label.pack(anchor="w", pady=(0, 5))
        
        output_path_frame = ttk.Frame(output_frame)
        output_path_frame.pack(fill=tk.X)
        
        output_path_entry = ttk.Entry(output_path_frame, textvariable=self.output_image_path)
        output_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        output_browse_btn = ttk.Button(output_path_frame, text="Browse...",
                                     command=lambda: self.browse_file(self.output_image_path, "Save Output Image As", 
                                                                    [("JPEG files", "*.jpg")], save=True))
        output_browse_btn.pack(side=tk.RIGHT)
    
    def create_progress_section(self):
        """Create progress bar and status section."""
        progress_frame = ttk.LabelFrame(self.main_frame, text="Progress", padding=10)
        progress_frame.pack(fill=tk.X, pady=10)
        
        self.progress_bar = ProgressBar(progress_frame)
        self.progress_bar.pack(fill=tk.X)
    
    def create_action_buttons(self):
        """Create action buttons."""
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.generate_btn = ttk.Button(button_frame, text="Generate Image",
                                    style="Primary.TButton",
                                    command=self.start_generation)
        self.generate_btn.pack(side=tk.RIGHT, padx=5)
        
        self.cancel_btn = ttk.Button(button_frame, text="Cancel",
                                   command=self.cancel_generation,
                                   state="disabled")
        self.cancel_btn.pack(side=tk.RIGHT, padx=5)
    
    def create_status_bar(self):
        """Create status bar at the bottom."""
        status_frame = ttk.Frame(self.root, relief=tk.SUNKEN, style="Status.TFrame")
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.style.configure("Status.TFrame", background="#007acc")
        self.style.configure("Status.TLabel", background="#007acc", foreground="white")
        
        self.status_label = ttk.Label(status_frame, text="Ready", style="Status.TLabel")
        self.status_label.pack(side=tk.LEFT, padx=5, pady=2)
    
    def browse_file(self, path_var, title, filetypes, save=False):
        """Open a file browser dialog and update the path variable."""
        initial_dir = os.path.dirname(path_var.get())
        
        if not os.path.exists(initial_dir):
            initial_dir = self.current_folder
        
        if save:
            filename = filedialog.asksaveasfilename(
                title=title,
                initialdir=initial_dir,
                filetypes=filetypes,
                defaultextension=".jpg"
            )
        else:
            filename = filedialog.askopenfilename(
                title=title,
                initialdir=initial_dir,
                filetypes=filetypes
            )
        
        if filename:
            path_var.set(filename)
    
    def update_preview(self, image_path, preview_label):
        """Update the image preview."""
        if os.path.exists(image_path):
            try:
                # Open and resize image
                img = Image.open(image_path)
                img.thumbnail((200, 200))
                photo = ImageTk.PhotoImage(img)
                
                # Update label
                preview_label.configure(image=photo, text="")
                preview_label.image = photo  # Keep a reference
            except Exception as e:
                preview_label.configure(image="", text=f"Error loading image: {str(e)}")
        else:
            preview_label.configure(image="", text="Image not found")
    
    def setup_updater(self):
        """Setup a timer to update progress."""
        def update_progress():
            if hasattr(self, 'generator') and self.is_processing:
                progress, status, _ = self.generator.get_progress_status()
                
                # Map status to steps
                step = self.step_mapping.get(status, 0)
                
                # Update progress bar
                self.progress_bar.update_progress(progress, step=step, total=5, status=status)
                
                # Update status bar
                self.status_label.configure(text=f"Status: {status} - {progress}%")
            
            # Schedule next update
            self.root.after(500, update_progress)
        
        # Start updater
        self.root.after(500, update_progress)
    
    def start_generation(self):
        """Start the image generation process."""
        # Check if paths are valid
        if not os.path.exists(self.base_image_path.get()):
            tk.messagebox.showerror("Error", "Base image not found. Please select a valid image.")
            return
        
        # Disable UI during processing
        self.is_processing = True
        self.generate_btn.configure(state="disabled")
        self.cancel_btn.configure(state="normal")
        
        # Get parameters
        base_image = self.base_image_path.get()
        style_image = self.style_image_path.get()
        prompt = self.prompt.get()
        negative_prompt = self.negative_prompt.get()
        output_path = self.output_image_path.get()
        
        # Custom parameters
        model_id = self.selected_model.get()
        controlnet_id = self.selected_controlnet.get()
        use_gpu = self.use_gpu.get()
        steps = int(self.steps.get())
        guidance_scale = float(self.guidance_scale.get())
        
        # Update status
        self.status_label.configure(text="Status: Starting generation...")
        
        # Update generator settings if available
        try:
            self.generator.model_id = model_id
            self.generator.controlnet_id = controlnet_id
            self.generator.use_gpu = use_gpu
            self.generator.steps = steps
            self.generator.guidance_scale = guidance_scale
        except:
            pass
        
        # Start generation
        thread = image_generator.generate_image(base_image, style_image, prompt, negative_prompt, output_path)
        
        # Setup completion check
        def check_completion():
            if not self.is_processing:
                return
                
            progress, status, _ = self.generator.get_progress_status()
            
            if status in ["Complete", "Failed", "Error", "Terminated"]:
                self.is_processing = False
                self.generate_btn.configure(state="normal")
                self.cancel_btn.configure(state="disabled")
                
                # Update final status
                self.status_label.configure(text=f"Status: {status}")
                
                # Show result if successful
                if status == "Complete":
                    if os.path.exists(output_path):
                        tk.messagebox.showinfo("Success", f"Image generated successfully and saved to:\n{output_path}")
                        
                        # Try to display the image
                        try:
                            if os.name == 'nt':  # Windows
                                os.startfile(output_path)
                            else:
                                import subprocess
                                subprocess.call(('xdg-open', output_path))
                        except:
                            pass
                elif status == "Failed" or status == "Error":
                    tk.messagebox.showerror("Error", "Image generation failed. Check the terminal for more information.")
                elif status == "Terminated":
                    tk.messagebox.showwarning("Cancelled", "Image generation was cancelled.")
            else:
                # Check again after 500ms
                self.root.after(500, check_completion)
        
        # Start completion check
        self.root.after(500, check_completion)
    
    def cancel_generation(self):
        """Cancel the generation process."""
        if self.is_processing:
            # Update status
            self.status_label.configure(text="Status: Cancelling...")
            
            # Terminate generation
            self.generator.terminate()
            
            # Reset UI
            self.is_processing = False
            self.generate_btn.configure(state="normal")
            self.cancel_btn.configure(state="disabled")
    
    def on_closing(self):
        """Handle window close event."""
        if self.is_processing:
            if tk.messagebox.askyesno("Quit", "Image generation is in progress. Are you sure you want to quit?"):
                self.generator.terminate()
                self.root.destroy()
        else:
            self.root.destroy()
    
    def run(self):
        """Start the main event loop."""
        self.root.mainloop()

def launch_gui():
    """Launch the GUI."""
    # Install dependencies if needed
    try:
        import importlib
        import subprocess
        import sys
        
        # Try to import ttkthemes
        try:
            importlib.import_module('ttkthemes')
        except ImportError:
            print("Installing ttkthemes for better UI...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "ttkthemes"])
            
            # Reimport
            importlib.invalidate_caches()
    except:
        pass
    
    # Create and run GUI
    app = ViewPrettifierGUI()
    app.run()

if __name__ == "__main__":
    launch_gui() 