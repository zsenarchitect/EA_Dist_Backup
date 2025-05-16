"""
Modern chat interface for EnneadTabAgent

This module handles:
- Chat UI with tkinter
- Message rendering and history
- Suggested queries and interactive elements
"""

import os
import sys
import json
import logging
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import webbrowser
from datetime import datetime
import re
import queue
from typing import List, Dict, Callable, Any, Optional

# Import local modules
from . import constants
from . import utils
from . import models
from openai import OpenAI

# Setup logger
logger = logging.getLogger("EnneadTabAgent.ui")

class ModernChatUI:
    def __init__(self, agent_instance):
        """Initialize the chat UI with a reference to the agent."""
        self.agent = agent_instance
        self.root = None
        self.messages_frame = None
        self.messages_canvas = None
        self.input_entry = None
        self.send_button = None
        self.status_label = None
        self.message_queue = queue.Queue()
        self.conversation = models.Conversation()
        self.username = utils.find_username()
        self.suggested_questions_shown = False
        
        self.setup_ui()
        
    def setup_ui(self):
        """Create and configure the user interface."""
        # Create the main window
        self.root = tk.Tk()
        self.root.title(constants.WINDOW_TITLE)
        self.root.geometry(f"{constants.WINDOW_WIDTH}x{constants.WINDOW_HEIGHT}")
        self.root.minsize(constants.WINDOW_MIN_WIDTH, constants.WINDOW_MIN_HEIGHT)
        
        # Configure style
        style = ttk.Style()
        style.configure('TFrame', background=constants.BACKGROUND_COLOR)
        style.configure('TLabel', background=constants.BACKGROUND_COLOR, foreground=constants.TEXT_COLOR)
        style.configure('TButton', background=constants.PRIMARY_COLOR, foreground='white')
        style.configure('Status.TLabel', foreground='gray')
        style.configure('Error.TLabel', foreground='red')
        
        # Create main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create messages area
        messages_container = ttk.Frame(main_frame)
        messages_container.pack(fill='both', expand=True, padx=0, pady=(0, 10))
        
        # Canvas and scrollbar for messages
        self.messages_canvas = tk.Canvas(
            messages_container, 
            background=constants.BACKGROUND_COLOR,
            highlightthickness=0
        )
        scrollbar = ttk.Scrollbar(
            messages_container, 
            orient='vertical', 
            command=self.messages_canvas.yview
        )
        self.messages_canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side='right', fill='y')
        self.messages_canvas.pack(side='left', fill='both', expand=True)
        
        # Frame to hold messages inside canvas
        self.messages_frame = ttk.Frame(self.messages_canvas)
        messages_window = self.messages_canvas.create_window(
            (0, 0), 
            window=self.messages_frame, 
            anchor='nw', 
            width=self.messages_canvas.winfo_reqwidth()
        )
        
        # Configure canvas scrolling
        def on_frame_configure(event):
            self.messages_canvas.configure(scrollregion=self.messages_canvas.bbox('all'))
            
        def on_canvas_configure(event):
            width = event.width
            self.messages_canvas.itemconfig(messages_window, width=width)
            
        self.messages_frame.bind('<Configure>', on_frame_configure)
        self.messages_canvas.bind('<Configure>', on_canvas_configure)
        
        # Mouse wheel scrolling
        def on_mousewheel(event):
            if sys.platform.startswith('win'):
                self.messages_canvas.yview_scroll(int(-1 * (event.delta / 120)), 'units')
            else:  # For macOS and Linux
                self.messages_canvas.yview_scroll(int(-1 * event.delta), 'units')
                
        self.messages_canvas.bind_all('<MouseWheel>', on_mousewheel)  # Windows and macOS
        self.messages_canvas.bind_all('<Button-4>', lambda e: self.messages_canvas.yview_scroll(-1, 'units'))  # Linux
        self.messages_canvas.bind_all('<Button-5>', lambda e: self.messages_canvas.yview_scroll(1, 'units'))   # Linux
        
        # Create bottom area for input
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill='x', pady=(0, 5))
        
        # Create status bar
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill='x')
        
        self.status_label = ttk.Label(
            status_frame, 
            text="Ready", 
            anchor='w',
            style='Status.TLabel',
            font=(constants.FONT_FAMILY, constants.FONT_SIZE_SMALL)
        )
        self.status_label.pack(side='left', fill='x', expand=True)
        
        kb_status = utils.get_vector_store_age()
        kb_text = f"Knowledge last updated: {kb_status} days ago" if kb_status else "Knowledge base not found"
        
        self.kb_status_label = ttk.Label(
            status_frame, 
            text=kb_text,
            anchor='e',
            style='Status.TLabel',
            font=(constants.FONT_FAMILY, constants.FONT_SIZE_SMALL)
        )
        self.kb_status_label.pack(side='right')
        
        # Create input entry and send button
        input_style = {
            'font': (constants.FONT_FAMILY, constants.FONT_SIZE_NORMAL),
            'bg': 'white',
            'fg': constants.TEXT_COLOR,
            'insertbackground': constants.TEXT_COLOR,
            'relief': 'solid',
            'borderwidth': 1
        }
        
        self.input_entry = tk.Text(
            input_frame, 
            height=3, 
            wrap='word',
            **input_style
        )
        self.input_entry.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Placeholder text
        self.input_entry.insert('1.0', "Type your message here...")
        self.input_entry.config(fg='gray')
        
        def on_entry_focus_in(event):
            if self.input_entry.get('1.0', 'end-1c') == "Type your message here...":
                self.input_entry.delete('1.0', 'end')
                self.input_entry.config(fg=constants.TEXT_COLOR)
                
        def on_entry_focus_out(event):
            if not self.input_entry.get('1.0', 'end-1c').strip():
                self.input_entry.delete('1.0', 'end')
                self.input_entry.insert('1.0', "Type your message here...")
                self.input_entry.config(fg='gray')
                
        self.input_entry.bind('<FocusIn>', on_entry_focus_in)
        self.input_entry.bind('<FocusOut>', on_entry_focus_out)
        
        # Handle Enter and Shift+Enter
        self.input_entry.bind('<Return>', self.handle_return)
        self.input_entry.bind('<Shift-Return>', self.handle_shift_return)
        
        # Send button
        self.send_button = ttk.Button(
            input_frame, 
            text="Send", 
            command=self.send_message,
            style='TButton'
        )
        self.send_button.pack(side='right', pady=5)
        
        # Welcome message and suggested questions
        self.add_system_message("Welcome to EnneadAssistant! I can help you with information about Ennead Architects. What would you like to know?")
        self.show_suggested_questions()
        
        # Start message processing loop
        self.process_messages()
        
    def process_messages(self):
        """Process messages from the queue to avoid blocking the UI."""
        try:
            while not self.message_queue.empty():
                func, args, kwargs = self.message_queue.get_nowait()
                func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error processing messages: {e}")
        finally:
            self.root.after(100, self.process_messages)
            
    def queue_function(self, func, *args, **kwargs):
        """Queue a function to be executed in the UI thread."""
        self.message_queue.put((func, args, kwargs))
        
    def show_suggested_questions(self):
        """Display suggested questions that the user can click on."""
        if self.suggested_questions_shown:
            return
            
        suggestions_frame = ttk.Frame(self.messages_frame, style='TFrame')
        suggestions_frame.pack(fill='x', pady=10)
        
        # Label for suggestions
        ttk.Label(
            suggestions_frame,
            text="Suggested questions:",
            font=(constants.FONT_FAMILY, constants.FONT_SIZE_SMALL, 'bold'),
            style='TLabel'
        ).pack(anchor='w', pady=(0, 5))
        
        # Create buttons for suggested questions
        for i, question in enumerate(constants.SUGGESTED_QUERIES[:5]):  # Limit to first 5 questions
            suggestion_btn = tk.Button(
                suggestions_frame,
                text=question,
                relief='flat',
                bg=constants.BACKGROUND_COLOR,
                fg=constants.PRIMARY_COLOR,
                activebackground=constants.BACKGROUND_COLOR,
                activeforeground=constants.SECONDARY_COLOR,
                font=(constants.FONT_FAMILY, constants.FONT_SIZE_NORMAL),
                anchor='w',
                cursor="hand2",
                bd=0,
                padx=5,
                pady=2,
                highlightthickness=0
            )
            
            def create_command(q):
                return lambda: self.ask_suggested_question(q)
                
            suggestion_btn.config(command=create_command(question))
            suggestion_btn.pack(fill='x', pady=1)
            
            # Hover effect
            suggestion_btn.bind("<Enter>", lambda e, btn=suggestion_btn: btn.config(
                bg=constants.BACKGROUND_COLOR,
                fg=constants.SECONDARY_COLOR
            ))
            suggestion_btn.bind("<Leave>", lambda e, btn=suggestion_btn: btn.config(
                bg=constants.BACKGROUND_COLOR,
                fg=constants.PRIMARY_COLOR
            ))
            
        self.suggested_questions_shown = True
        
        # Scroll to see suggestions
        self.messages_canvas.update_idletasks()
        self.messages_canvas.yview_moveto(0.0)
        
    def ask_suggested_question(self, question):
        """Process a suggested question when clicked."""
        # Set the question in the input field
        self.input_entry.delete('1.0', 'end')
        self.input_entry.insert('1.0', question)
        self.input_entry.config(fg=constants.TEXT_COLOR)
        
        # Send the message
        self.send_message()
        
    def handle_return(self, event):
        """Handle Enter key press to send message."""
        if not event.state & 0x1:  # No Shift key
            self.send_message()
            return "break"  # Prevent default behavior
        return None
        
    def handle_shift_return(self, event):
        """Handle Shift+Enter to add newline."""
        return None  # Allow default behavior (newline)
        
    def set_status(self, status, is_error=False):
        """Update the status bar text."""
        self.status_label.config(
            text=status,
            style='Error.TLabel' if is_error else 'Status.TLabel'
        )
        
    def update_kb_status(self):
        """Update the knowledge base status display."""
        kb_age = utils.get_vector_store_age()
        if kb_age is not None:
            self.kb_status_label.config(text=f"Knowledge last updated: {kb_age} days ago")
        else:
            self.kb_status_label.config(text="Knowledge base not found")
        
    def add_system_message(self, message):
        """Add a system message to the chat."""
        # Create message frame
        msg_frame = ttk.Frame(
            self.messages_frame,
            style='TFrame'
        )
        msg_frame.pack(fill='x', pady=5)
        
        # Message content frame
        content_frame = ttk.Frame(
            msg_frame,
            style='TFrame'
        )
        content_frame.pack(fill='x')
        
        # System message has a different style
        message_label = tk.Label(
            content_frame,
            text=message,
            wraplength=constants.WINDOW_WIDTH - 100,
            justify='left',
            bg='#e0e0e0',
            fg=constants.TEXT_COLOR,
            pady=8,
            padx=10,
            relief='flat',
            font=(constants.FONT_FAMILY, constants.FONT_SIZE_NORMAL)
        )
        message_label.pack(fill='x')
        
        # Scroll to see new message
        self.messages_canvas.update_idletasks()
        self.messages_canvas.yview_moveto(1.0)
        
    def add_message(self, sender, message):
        """Add a user or assistant message to the chat."""
        # Create message frame
        msg_frame = ttk.Frame(
            self.messages_frame,
            style='TFrame'
        )
        msg_frame.pack(fill='x', pady=5)
        
        is_user = sender.lower() == 'user'
        
        # Label for sender
        sender_name = self.username if is_user else "EnneadAssistant"
        timestamp = utils.format_timestamp()
        sender_label = ttk.Label(
            msg_frame,
            text=f"{sender_name} • {timestamp}",
            font=(constants.FONT_FAMILY, constants.FONT_SIZE_SMALL),
            style='TLabel'
        )
        sender_label.pack(anchor='w' if is_user else 'e')
        
        # Message content frame
        content_frame = ttk.Frame(
            msg_frame,
            style='TFrame'
        )
        content_frame.pack(fill='x')
        
        # Create the message bubble
        message_bg = constants.USER_MESSAGE_COLOR if is_user else constants.AI_MESSAGE_COLOR
        message_anchor = 'w' if is_user else 'e'
        
        # Process message text for URLs
        message_text = message
        urls = self.extract_urls(message)
        has_urls = len(urls) > 0
        
        # Create message label
        message_label = tk.Label(
            content_frame,
            text=message_text,
            wraplength=constants.WINDOW_WIDTH - 100,
            justify='left',
            bg=message_bg,
            fg=constants.TEXT_COLOR,
            pady=8,
            padx=10,
            relief='flat',
            font=(constants.FONT_FAMILY, constants.FONT_SIZE_NORMAL)
        )
        message_label.pack(anchor=message_anchor)
        
        # Add URL buttons if URLs found
        if has_urls and not is_user:
            url_frame = ttk.Frame(content_frame, style='TFrame')
            url_frame.pack(anchor='e', pady=(5, 0), padx=10)
            
            for url in urls[:3]:  # Limit to first 3 URLs
                url_btn = tk.Button(
                    url_frame,
                    text=f"🔗 {url[:30]}..." if len(url) > 30 else f"🔗 {url}",
                    relief='flat',
                    bg='#f0f0f0',
                    fg=constants.PRIMARY_COLOR,
                    activebackground='#e0e0e0',
                    activeforeground=constants.PRIMARY_COLOR,
                    font=(constants.FONT_FAMILY, constants.FONT_SIZE_SMALL),
                    cursor="hand2",
                    command=lambda u=url: utils.open_url(u),
                    padx=5,
                    pady=2
                )
                url_btn.pack(anchor='e', pady=2)
        
        # Add to conversation model
        self.conversation.add_message(
            role="user" if is_user else "assistant",
            content=message
        )
        
        # Scroll to see new message
        self.messages_canvas.update_idletasks()
        self.messages_canvas.yview_moveto(1.0)
        
    def extract_urls(self, text):
        """Extract URLs from text."""
        # URL regex pattern
        url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+(?:/[^\\s]*)?'
        return re.findall(url_pattern, text)
        
    def send_message(self):
        """Send the user's message and get a response."""
        # Get message text
        message = self.input_entry.get('1.0', 'end-1c')
        
        # Don't send empty messages or the placeholder
        if not message.strip() or message.strip() == "Type your message here...":
            return
            
        # Clear input field
        self.input_entry.delete('1.0', 'end')
        self.input_entry.focus_set()
        
        # Add user message to chat
        self.add_message("user", message)
        
        # Get AI response
        self.set_status("Thinking...")
        self.send_button.config(state='disabled')
        
        threading.Thread(
            target=self.get_ai_response,
            args=(message,),
            daemon=True
        ).start()
        
    def get_ai_response(self, message):
        """Get a response from the AI agent."""
        try:
            # Get response from agent
            response = self.agent.get_response(message)
            
            # Update UI in main thread
            self.queue_function(self.add_message, "assistant", response)
            self.queue_function(self.set_status, "Ready")
            self.queue_function(lambda: self.send_button.config(state='normal'))
            
        except Exception as e:
            logger.error(f"Error getting AI response: {e}")
            error_msg = f"Sorry, I encountered an error: {str(e)}"
            self.queue_function(self.add_message, "assistant", error_msg)
            self.queue_function(self.set_status, "Error occurred", True)
            self.queue_function(lambda: self.send_button.config(state='normal'))
            
    def run(self):
        """Run the UI main loop."""
        self.root.mainloop() 