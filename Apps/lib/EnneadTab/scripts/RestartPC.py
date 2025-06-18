import os
import time
import sys

# Warn the user
print("Your computer will restart in 5 minutes. Press Ctrl+C to cancel.")
try:
    for remaining in range(300, 0, -1):
        mins, secs = divmod(remaining, 60)
        timeformat = f"{mins:02d}:{secs:02d}"
        print(f"Restarting in: {timeformat}", end='\r', flush=True)
        time.sleep(1)
    print()  # Move to next line after countdown
except KeyboardInterrupt:
    print("\nRestart cancelled.")
    sys.exit(0)

# Restart the computer (Windows)
os.system("shutdown /r /t 0")
