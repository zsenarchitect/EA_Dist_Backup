#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Toast Notification Test Script

A standalone test script that demonstrates Windows 10 toast notifications
without any dependencies on the EnneadTab modules.

This script can be used to verify that the Windows 10 notification system
is working properly on your machine.
"""

def test_toast_notification():
    """Test Windows 10 toast notifications with win10toast library."""
    try:
        print("Testing toast notifications with win10toast...")
        from win10toast import ToastNotifier
        
        toaster = ToastNotifier()
        toaster.show_toast(
            "EnneadTab Notification",
            "This is a Windows 10 toast notification test!",
            duration=5,
            threaded=True  # Non-blocking
        )
        
        print("Toast notification sent. You should see it in the bottom right corner.")
        print("Waiting for notification to complete...")
        
        # Wait a moment to make sure notification appears
        import time
        time.sleep(6)
        
        print("Test completed!")
        return True
    except ImportError:
        print("win10toast package not found. Run 'pip install win10toast' to install it.")
        return False
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def test_system_notification():
    """Test Windows notifications using ctypes directly."""
    print("Testing notifications with Windows API via ctypes...")
    try:
        import ctypes
        from ctypes import wintypes
        import time
        
        # Load shell32.dll
        shell32 = ctypes.WinDLL('shell32.dll')
        user32 = ctypes.WinDLL('user32.dll')
        
        # Find an existing window
        hwnd = user32.GetForegroundWindow()
        if not hwnd:
            hwnd = user32.GetDesktopWindow()
        
        # Define notification constants
        NIF_INFO = 0x00000010
        NIF_ICON = 0x00000002
        NIF_TIP = 0x00000004
        NIIF_INFO = 0x00000001
        NIM_ADD = 0x00000000
        NIM_DELETE = 0x00000002
        
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
        nid.uID = 1
        nid.uFlags = NIF_INFO | NIF_TIP | NIF_ICON
        nid.dwInfoFlags = NIIF_INFO
        
        # Set notification content
        title = "Windows API Notification"
        message = "This is a test using Windows API directly!"
        
        nid.szInfo = message.encode('utf-8')
        nid.szInfoTitle = title.encode('utf-8')
        nid.szTip = (title + ": " + message[:60]).encode('utf-8')
        
        # Show notification
        shell32.Shell_NotifyIconA(NIM_ADD, ctypes.byref(nid))
        print("Native Windows notification sent. You should see it now.")
        
        # Keep it visible
        time.sleep(5)
        
        # Remove notification icon
        shell32.Shell_NotifyIconA(NIM_DELETE, ctypes.byref(nid))
        print("Ctypes notification test completed!")
        return True
    except Exception as e:
        print(f"Ctypes notification failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("Windows 10 Toast Notification Test")
    print("==================================")
    print("")
    
    # Test win10toast notifications
    toast_success = test_toast_notification()
    
    print("\n")
    
    # Test ctypes notifications
    ctypes_success = test_system_notification()
    
    print("\n")
    print("Test Results:")
    print(f"- win10toast notification: {'SUCCESS' if toast_success else 'FAILED'}")
    print(f"- Windows API notification: {'SUCCESS' if ctypes_success else 'FAILED'}") 