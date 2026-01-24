import pandas as pd
import numpy as np
import joblib
import xgboost as xgb
import os
from sklearn.linear_model import SGDClassifier
from sklearn.preprocessing import RobustScaler
from hmmlearn import hmm

# CONFIGURATION
DATA_FOLDER = "user_data"
MODEL_FOLDER = "models"
if not os.path.exists(MODEL_FOLDER):
    os.makedirs(MODEL_FOLDER)

def build_model():
    print("=======================================")
    print("      AI MODEL TRAINING ENGINE         ")
    print("=======================================")
    username = input("Enter Username to Build Model For: ").strip()
    raw_path = os.path.join(DATA_FOLDER, f"{username}_raw.csv")
    model_path = os.path.join(MODEL_FOLDER, f"{username}_brain.pkl")

    if not os.path.exists(raw_path):
        print(f"[!] Error: No data found for {username}. Run collector first.")
        return

    print("[1/5] Loading and Cleaning Data...")
    df = pd.read_csv(raw_path)
    
    # --- FEATURE ENGINEERING ---
    # Dwell = Release - Press
    df['dwell'] = df['release_timestamp'] - df['press_timestamp']
    # Flight = Press - Previous_Release
    df['flight'] = df['press_timestamp'] - df['release_timestamp'].shift(1)
    
    # Clean NaN (First row has no previous release)
    df = df.dropna()
    
    # Filter Impossible Outliers (Machine errors or distractions)
    df = df[(df['dwell'] > 10) & (df['dwell'] < 1000)]
    df = df[(df['flight'] > 0) & (df['flight'] < 3000)]

    X = df[['dwell', 'flight']].values

    print("[2/5] Generating Synthetic Intruder Data...")
    # We create fake 'bad' typing to teach the model what NOT to accept
    # Gaussian noise injection
    noise = np.random.normal(0, 15, X.shape)
    X_intruder = X + noise * 1.5 # Shifted and messy
    
    # Labels: 1 = Owner, 0 = Intruder
    X_train = np.vstack([X, X_intruder])
    y_train = np.hstack([np.ones(len(X)), np.zeros(len(X_intruder))])

    print("[3/5] Training Scaler & XGBoost...")
    scaler = RobustScaler()
    X_scaled = scaler.fit_transform(X_train)

    # XGBoost for Logic
    dtrain = xgb.DMatrix(X_scaled, label=y_train)
    params = {
        'objective': 'binary:logistic',
        'max_depth': 6,
        'eta': 0.3,
        'eval_metric': 'logloss'
    }
    xgb_model = xgb.train(params, dtrain, num_boost_round=50)

    print("[4/5] Training SVM & HMM...")
    # SVM (SGD) for Geometry
    svm_model = SGDClassifier(loss='log_loss', warm_start=True)
    svm_model.fit(X_scaled, y_train)

    # HMM for Rhythm (Only trains on Owner data)
    hmm_model = hmm.GaussianHMM(n_components=3, covariance_type="full", n_iter=100)
    hmm_model.fit(scaler.transform(X))

    print("[5/5] Saving Brain...")
    # Bundle everything into one object
    brain = {
        'scaler': scaler,
        'xgb': xgb_model,
        'svm': svm_model,
        'hmm': hmm_model,
        'user': username
    }
    joblib.dump(brain, model_path)
    print(f"[+] Model Successfully Built: {model_path}")

if __name__ == "__main__":
    build_model()