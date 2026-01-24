import time
import joblib
import xgboost as xgb
import numpy as np
import os
import subprocess
from pynput import keyboard
from collections import deque

# --- CONFIGURATION ---
MODEL_FOLDER = "models"
BAT_FILE = "enx.bat"
BUFFER_SIZE = 15  # Keys to analyze at once
BLOCK_THRESHOLD = 0.45 # If score drops below this -> TRIGGER

def run_sentinel():
    print("=======================================")
    print("    REAL-TIME SECURITY SENTINEL        ")
    print("=======================================")
    username = input("Enter Username to Protect: ").strip()
    model_path = os.path.join(MODEL_FOLDER, f"{username}_brain.pkl")

    if not os.path.exists(model_path):
        print("[!] Model not found. Build it first.")
        return

    print("[+] Loading Brain...")
    brain = joblib.load(model_path)
    scaler = brain['scaler']
    xgb_model = brain['xgb']
    svm_model = brain['svm']
    hmm_model = brain['hmm']

    print(f"[+] System Armed. protecting {username}...")
    
    # Real-time buffers
    active_keys = {}
    key_buffer = deque(maxlen=BUFFER_SIZE)

    def on_press(key):
        try:
            k_code = key.vk if hasattr(key, 'vk') else key.value.vk
            if k_code not in active_keys:
                active_keys[k_code] = time.perf_counter() * 1000
        except:
            pass

    def on_release(key):
        try:
            k_code = key.vk if hasattr(key, 'vk') else key.value.vk
            
            if k_code in active_keys:
                press_time = active_keys.pop(k_code)
                release_time = time.perf_counter() * 1000
                
                # 1. Add raw timings to buffer
                key_buffer.append({
                    'p': press_time, 
                    'r': release_time
                })

                # 2. Only check if buffer is full
                if len(key_buffer) == BUFFER_SIZE:
                    analyze_buffer()

        except:
            pass

    def analyze_buffer():
        # Convert list of dicts to DataFrame-like array
        data = list(key_buffer)
        
        # Calculate features on the fly
        feats = []
        for i in range(1, len(data)):
            dwell = data[i]['r'] - data[i]['p']
            flight = data[i]['p'] - data[i-1]['r'] # Flight from PREVIOUS release
            feats.append([dwell, flight])
        
        if len(feats) == 0: return

        # Scale Data
        X_live = scaler.transform(feats)

        # --- THE ENSEMBLE VOTE ---
        
        # 1. XGBoost Vote
        dtest = xgb.DMatrix(X_live)
        p_xgb = np.mean(xgb_model.predict(dtest))

        # 2. SVM Vote
        p_svm = np.mean(svm_model.predict_proba(X_live)[:, 1])

        # 3. HMM Vote (Normalized Score)
        hmm_score = hmm_model.score(X_live)
        p_hmm = 1.0 if hmm_score > -500 else 0.3 # Simple threshold normalization

        # Weighted Average
        final_score = (p_xgb * 0.5) + (p_svm * 0.3) + (p_hmm * 0.2)
        
        # Visualization output (Optional)
        status = "SAFE" if final_score > BLOCK_THRESHOLD else "THREAT"
        print(f"[{status}] Score: {final_score:.2f} (XGB:{p_xgb:.2f} SVM:{p_svm:.2f})")

        # --- TRIGGER LOGIC ---
        if final_score < BLOCK_THRESHOLD:
            print("!!! UNAUTHORIZED USER DETECTED !!!")
            trigger_defense()

    def trigger_defense():
        # Executes the BAT file and kills this script so it doesn't loop
        try:
            subprocess.Popen([BAT_FILE], shell=True)
            print("[!] Countermeasures deployed.")
            os._exit(1) # Kill the python script immediately
        except Exception as e:
            print(f"Error triggering BAT: {e}")

    # Start Listener
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

if __name__ == "__main__":
    run_sentinel()