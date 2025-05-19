#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
EnneadTab Notification System

A sophisticated notification system providing customizable user alerts through
various channels including popups, sounds, and animated notifications. This module
offers both standard message notifications and fun, interactive notifications like
the signature duck popup.

Key Features:
    - Customizable popup notifications with animations
    - Fun, interactive duck notifications with sound effects
    - User preference management for notification styles
    - Rich text formatting with custom fonts
    - Animation timing control
    - Position and size customization
    - Background and font color customization

Note:
    All notifications respect user preferences and can be disabled through
    configuration settings.
"""

import SOUND
import DATA_FILE
import EXE
import IMAGE
import CONFIG

def is_hate_messenger():
    """Check if standard notifications are disabled.
    
    Retrieves user preference for minimal popup notifications from configuration.

    Returns:
        bool: True if user has opted for minimal notifications
    """
    return  CONFIG.get_setting("radio_bt_popup_minimal", False) 

def is_hate_duck_pop():
    """Check if duck notifications are disabled.
    
    Retrieves user preference for duck popup notifications from configuration.

    Returns:
        bool: True if duck notifications are disabled
    """
    return not CONFIG.get_setting("toggle_bt_is_duck_allowed", False)

FUNFONTS = [
    "Berlin Sans FB"
    "Ravie", 
    "Small Fonts",
    "Snap ITC",
    "Viner Hand ITC",
    "BankGothic Lt BT",
    "Bauhaus 93",
    "Bradley Hand ITC",
    "Broadway",
    "Chiller",
    "CityBlueprint",
    "Comic Sans MS",
    "CountryBlueprint"
    ]

def get_random_font():
    """Select a random decorative font.
    
    Chooses from a curated list of fun, decorative fonts suitable for
    notifications.

    Returns:
        str: Name of randomly selected font
    """
    import random
    return random.choice(FUNFONTS)

def messenger(main_text,
             width=None,
             height=None,
             image=None,
             animation_in_duration=None,
             animation_stay_duration=None,
             animation_fade_duration=None,
             x_offset=None,
             background_color=None,
             font_size=None,
             font_color=None,
             font_family=None):
    """Display a customizable popup notification.
    
    Creates an animated notification window with rich customization options
    for appearance and timing. Notifications automatically fade after display.

    Args:
        main_text (str): Message to display (supports line breaks)
        width (int, optional): Maximum width in pixels. Defaults to 1200.
        height (int, optional): Maximum height in pixels. Defaults to 150.
        image (str, optional): Path to image to display
        animation_in_duration (int, optional): Fade-in duration in milliseconds
        animation_stay_duration (int, optional): Display duration in milliseconds
        animation_fade_duration (int, optional): Fade-out duration in milliseconds
        x_offset (int, optional): Horizontal position offset
        background_color (str, optional): Background color in hex or RGB format
        font_size (int, optional): Text size in points
        font_color (str, optional): Text color in hex or RGB format
        font_family (str, optional): Font name from FUNFONTS or system fonts

    Note:
        If notifications are disabled via user preferences, this function
        returns without action.
    """

    if is_hate_messenger():
        return
    
    if not isinstance(main_text, str):
        main_text = str(main_text)

    data = {}
    data["main_text"] = main_text
    if animation_in_duration is not None:
        data["animation_in_duration"] = animation_in_duration
    if animation_stay_duration is not None:
        data["animation_stay_duration"] = animation_stay_duration
    if animation_fade_duration is not None:
        data["animation_fade_duration"] = animation_fade_duration
    if width is not None:
        data["width"] = width
    if height is not None:
        data["height"] = height 
    if image is not None:
        data["image"] = image
    if x_offset is not None:
        data["x_offset"] = x_offset
    if font_color:
        data["font_color"] = font_color
    if font_family:
        data["font_family"] = font_family
    if font_size:
        data["font_size"] = font_size
    if background_color:
        data["background_color"] = background_color



    DATA_FILE.set_data(data, "messenger_data")

    if not EXE.try_open_app("Messenger"):
        print (main_text)


def duck_pop(main_text=None):
    """Display an animated duck notification with sound.
    
    Creates a fun, interactive notification featuring an animated duck
    with sound effects. Falls back to standard notification if duck
    notifications are disabled.

    Args:
        main_text (str, optional): Message to display. Defaults to "Quack!"

    Note:
        - Uses randomly selected duck images and sounds
        - Includes explosion animation effect
        - Falls back to messenger() if duck notifications are disabled
    """
    if is_hate_duck_pop():
   
        messenger(main_text)
        return
    
    if not main_text:
        main_text = "Quack!"

    data = {}
    data["main_text"] = main_text

    # when the ranking is ready, can progress to make better ranked duck
    data["duck_image"] = IMAGE.get_one_image_path_by_prefix("duck_pop")
    data["explosion_gif"] = IMAGE.get_image_path_by_name("duck_explosion.gif")
    data["audio"] = SOUND.get_one_audio_path_by_prefix("duck")
    DATA_FILE.set_data(data, "DUCK_POP") 

    EXE.try_open_app("DuckPop")
  

def unit_test():
    """Run comprehensive tests of notification system.
    
    Tests both standard and duck notifications with default settings.
    """
    duck_pop("Hello, Ennead!")
    messenger("Hello Ennead!")

def window_msg(title, message, image=None, duration=10):
    """Display a Windows 10 style toast notification in the corner.
    
    Creates a non-blocking toast notification that appears in the corner
    of the screen similar to native Windows 10 notifications.
    
    Args:
        title (str): Title text displayed at top of notification
        message (str): Main message text (supports line breaks)
        image (str, optional): Path to image or predefined type:
            None = Information icon
            "info" = Information icon
            "warning" = Warning icon
            "error" = Error icon
            Any other string = Custom icon path
        duration (int, optional): How long toast notifications stay visible (seconds)
    
    Note:
        Designed for compatibility with both IronPython and CPython environments.
        Uses Windows 10 toast notification APIs for a modern user experience.
        See: https://learn.microsoft.com/en-us/windows/apps/design/shell/tiles-and-notifications/toast-notifications-overview
    """
    print("Showing notification: {} - {}".format(title, message))
    
    # Use toast notification style (Windows 10 corner popup)
    try:
        # Try Windows 10 toast notifications via win10toast
        try:
            # For CPython with win10toast package
            from win10toast import ToastNotifier
            
            toaster = ToastNotifier()
            toaster.show_toast(
                title,
                message,
                icon_path=image if image and image not in ["info", "warning", "error"] else None,
                duration=duration,
                threaded=True  # Non-blocking
            )
            print("Notification sent via win10toast")
            return
        except ImportError:
            print("win10toast not available, trying next method")
            pass
        
        # Try Windows Forms notification (IronPython or alternative approach)
        try:
            import clr
            clr.AddReference("System.Windows.Forms")
            from System.Windows.Forms import NotifyIcon, ToolTipIcon, Form, Application
            from System.Drawing import Icon, SystemIcons
            
            form = Form()
            form.ShowInTaskbar = False
            
            notify_icon = NotifyIcon()
            notify_icon.Visible = True
            notify_icon.Text = title  # Tooltip text
            
            # Set appropriate icon
            if image == "error":
                notify_icon.Icon = SystemIcons.Error
            elif image == "warning":
                notify_icon.Icon = SystemIcons.Warning
            elif image == "info" or image is None:
                notify_icon.Icon = SystemIcons.Information
            else:
                # Try to load custom icon if path provided
                try:
                    notify_icon.Icon = Icon(image)
                except Exception:
                    notify_icon.Icon = SystemIcons.Information
            
            # Show balloon tip (toast notification)
            notify_icon.BalloonTipTitle = title
            notify_icon.BalloonTipText = message
            # Use longer duration for visibility
            notify_icon.ShowBalloonTip(duration * 1000)  # Convert to milliseconds
            print("Notification sent via Windows Forms")
            
            # Keep application running to show notification
            import threading
            def cleanup():
                import time
                time.sleep(duration)
                notify_icon.Visible = False
                notify_icon.Dispose()
                
            threading.Thread(target=cleanup).start()
            return
        except Exception as e:
            print("Windows Forms notification failed:", str(e))
            pass
            
        # If all else fails, use ctypes for basic Windows notification
        try:
            import ctypes
            from ctypes import wintypes
            import time
            
            # Load shell32.dll
            shell32 = ctypes.WinDLL('shell32.dll')
            user32 = ctypes.WinDLL('user32.dll')
            
            # Find an existing window or create a dummy one
            hwnd = user32.GetForegroundWindow()
            if not hwnd:
                hwnd = user32.GetDesktopWindow()
            
            # Define notification flag constants
            NIF_INFO = 0x00000010
            NIF_ICON = 0x00000002
            NIF_TIP = 0x00000004
            NIF_MESSAGE = 0x00000001
            NIIF_INFO = 0x00000001
            NIIF_WARNING = 0x00000002
            NIIF_ERROR = 0x00000003
            NIM_ADD = 0x00000000
            NIM_MODIFY = 0x00000001
            NIM_DELETE = 0x00000002
            
            # Determine icon type
            icon_flag = NIIF_INFO
            if image == "warning":
                icon_flag = NIIF_WARNING
            elif image == "error":
                icon_flag = NIIF_ERROR
            
            # Create notification data structure
            class NOTIFYICONDATA(ctypes.Structure):
                _fields_ = [
                    ("cbSize", wintypes.DWORD),
                    ("hWnd", wintypes.HWND),
                    ("uID", wintypes.UINT),
                    ("uFlags", wintypes.UINT),
                    ("uCallbackMessage", wintypes.UINT),
                    ("hIcon", wintypes.HANDLE),
                    ("szTip", ctypes.c_char * 128),
                    ("dwState", wintypes.DWORD),
                    ("dwStateMask", wintypes.DWORD),
                    ("szInfo", ctypes.c_char * 256),
                    ("uVersion", wintypes.UINT),
                    ("szInfoTitle", ctypes.c_char * 64),
                    ("dwInfoFlags", wintypes.DWORD),
                ]
            
            # Initialize notification data
            nid = NOTIFYICONDATA()
            nid.cbSize = ctypes.sizeof(nid)
            nid.hWnd = hwnd
            nid.uID = 0
            nid.uFlags = NIF_INFO | NIF_TIP | NIF_ICON
            nid.dwInfoFlags = icon_flag
            nid.szInfo = message.encode('utf-8')
            nid.szInfoTitle = title.encode('utf-8')
            nid.szTip = (title + ": " + message[:60]).encode('utf-8')
            
            # Show notification
            try:
                # Add notification icon first
                shell32.Shell_NotifyIconA(NIM_ADD, ctypes.byref(nid))
                print("Notification sent via ctypes")
                
                # Keep it visible for the specified duration
                time.sleep(duration)
                
                # Remove notification icon
                shell32.Shell_NotifyIconA(NIM_DELETE, ctypes.byref(nid))
            except Exception as e:
                print("Error showing notification:", str(e))
            
            return
        except Exception as e:
            print("Ctypes notification failed:", str(e))
            pass
            
    except Exception as e:
        # Fall back to console output if all toast methods fail
        print("Toast notification: {} - {}".format(title, message))
        print("(Note: Windows toast notification failed, displaying text instead)")
        print("Error: {}".format(str(e)))
        if image:
            print("Icon type: {}".format(image))

def test_window_msg():
    """Run tests of Windows 10 style toast notifications.
    
    Tests different notification styles with various icons and durations.
    """
    print("Testing toast notifications...")
    
    # Test standard notifications
    window_msg("Information", "This is an information message")
    window_msg("Warning", "This is a warning message", "warning")
    window_msg("Error", "This is an error message", "error")
    
    # Test with different durations
    window_msg("Quick Notification", "This notification disappears quickly", None, 3)
    window_msg("Long Notification", "This notification stays longer", None, 7)
    
    print("Toast notification tests complete!")

if __name__ == "__main__":
    duck_pop("Hello, Ennead!")
    # Test random font messenger
    font = get_random_font()
    messenger("Hello world with bigger text\nUsing [{}]".format(font), font_size=30, font_family=font)
    for font_name    in FUNFONTS:
        messenger("rapid fire test："+font_name, font_family=font_name)
        # import time 
        # time.sleep(0.2)
    