# Keyboard Biometrics Security System

## System Overview
This system uses AI/ML to authenticate users based on their unique typing patterns (keystroke dynamics). It consists of three main components:

### Files:
1. **1_data_collector.py** - Collects keystroke timing data
2. **2_model_builder.py** - Trains AI models on collected data
3. **3_sentinel.py** - Real-time monitoring and threat detection
4. **enx.bat** - Security countermeasure script

## Setup Complete! ✓

All required packages are installed:
- ✓ pynput (keyboard monitoring)
- ✓ pandas (data processing)
- ✓ numpy (numerical operations)
- ✓ scikit-learn (machine learning)
- ✓ xgboost (gradient boosting)
- ✓ hmmlearn (Hidden Markov Models)
- ✓ joblib (model serialization)

## How to Use:

### Step 1: Collect Training Data
```powershell
python 1_data_collector.py
```
- Enter your username when prompted
- Type naturally for 2-5 minutes (at least 200-300 keystrokes)
- Press ESC when done
- Data saved in `user_data/<username>_raw.csv`

### Step 2: Build Your AI Model
```powershell
python 2_model_builder.py
```
- Enter the same username
- The system will train 3 AI models (XGBoost, SVM, HMM)
- Model saved in `models/<username>_brain.pkl`

### Step 3: Activate Protection
```powershell
python 3_sentinel.py
```
- Enter your username
- System monitors your typing in real-time
- If someone else types, it triggers `enx.bat` security response

## How It Works:

**Data Collection:** Measures two key metrics:
- Dwell time: How long each key is held down
- Flight time: Time between releasing one key and pressing the next

**AI Models:** Uses ensemble learning with 3 models:
- XGBoost: Gradient boosting for pattern recognition
- SVM: Support Vector Machine for geometric separation
- HMM: Hidden Markov Model for rhythm analysis

**Detection:** Real-time scoring:
- Score > 0.45: Legitimate user (SAFE)
- Score < 0.45: Unauthorized access (THREAT → triggers enx.bat)

## Tips:
- Collect data while typing normally (not hunt-and-peck)
- More training data = better accuracy
- The system adapts to your unique typing rhythm
- False positives can be reduced by lowering BLOCK_THRESHOLD in 3_sentinel.py

## Security Note:
The `enx.bat` file creates popup alerts when unauthorized access is detected. Customize it for your specific security needs.
