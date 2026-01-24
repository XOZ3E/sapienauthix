import time
import csv
import os
from pynput import keyboard

# CONFIGURATION
DATA_FOLDER = "user_data"
if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

def start_logging():
    print("=======================================")
    print("   KEYSTROKE DYNAMICS DATA COLLECTOR   ")
    print("=======================================")
    username = input("Enter Username to Train: ").strip()
    filename = os.path.join(DATA_FOLDER, f"{username}_raw.csv")
    
    # Check if file exists, write headers if not
    file_exists = os.path.isfile(filename)
    
    print(f"[+] Logging to: {filename}")
    print("[+] Press ESC to stop logging.")
    
    # Dictionary to track currently pressed keys
    active_keys = {}

    # Open file in append mode
    with open(filename, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["key_code", "press_timestamp", "release_timestamp"])
        
        def on_press(key):
            try:
                # Handle standard keys (a, b, c) and special keys (shift, ctrl)
                k_code = key.vk if hasattr(key, 'vk') else key.value.vk
            except:
                return # Ignore unrecognizable keys

            if key == keyboard.Key.esc:
                return False # Stop listener

            if k_code not in active_keys:
                active_keys[k_code] = time.perf_counter()

        def on_release(key):
            try:
                k_code = key.vk if hasattr(key, 'vk') else key.value.vk
            except:
                return

            if k_code in active_keys:
                press_time = active_keys.pop(k_code)
                release_time = time.perf_counter()
                
                # Convert to milliseconds for easier math later
                p_ms = press_time * 1000
                r_ms = release_time * 1000
                
                # Write RAW data immediately
                writer.writerow([k_code, p_ms, r_ms])
                f.flush() # Ensure data is saved even if crash

        # Start the Listener
        with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
            listener.join()

    print(f"\n[+] Session Saved. Data stored in {filename}")

if __name__ == "__main__":
    start_logging()