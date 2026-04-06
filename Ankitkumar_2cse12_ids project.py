import pandas as pd
import numpy as np

url_train = "https://raw.githubusercontent.com/defcom17/NSL_KDD/master/KDDTrain+.txt"
url_test = "https://raw.githubusercontent.com/defcom17/NSL_KDD/master/KDDTest+.txt"

columns = ["duration","protocol_type","service","flag","src_bytes",
    "dst_bytes","land","wrong_fragment","urgent","hot","num_failed_logins",
    "logged_in","num_compromised","root_shell","su_attempted","num_root",
    "num_file_creations","num_shells","num_access_files","num_outbound_cmds",
    "is_host_login","is_guest_login","count","srv_count","serror_rate",
    "srv_serror_rate","rerror_rate","srv_rerror_rate","same_srv_rate",
    "diff_srv_rate","srv_diff_host_rate","dst_host_count","dst_host_srv_count",
    "dst_host_same_srv_rate","dst_host_diff_srv_rate","dst_host_same_src_port_rate",
    "dst_host_srv_diff_host_rate","dst_host_serror_rate","dst_host_srv_serror_rate",
    "dst_host_rerror_rate","dst_host_srv_rerror_rate","label","difficulty"]

print("Downloading and loading data... please wait.")
df_train = pd.read_csv(url_train, header=None, names=columns)
df_test = pd.read_csv(url_test, header=None, names=columns)

df_train.drop(['difficulty'], axis=1, inplace=True)
df_test.drop(['difficulty'], axis=1, inplace=True)

print(f"Training Set Shape: {df_train.shape}")
print(f"Test Set Shape: {df_test.shape}")
print("\nFirst 5 rows of your data:")
df_train.head()


def convert_label(label):
    if label == 'normal':
        return 0
    else:
        return 1

df_train['label'] = df_train['label'].apply(convert_label)
df_test['label'] = df_test['label'].apply(convert_label)

# 2. CONVERT TEXT COLUMNS TO NUMBERS (One-Hot Encoding)
# This turns "protocol_type" into columns like "protocol_type_tcp", "protocol_type_udp", etc.
# We use a pandas function called 'get_dummies' to do this automatically.

# Identify the columns that are text (categorical)
categorical_cols = ['protocol_type', 'service', 'flag']

# Apply the encoding
df_train = pd.get_dummies(df_train, columns=categorical_cols)
df_test = pd.get_dummies(df_test, columns=categorical_cols)

# IMPORTANT: Ensure both train and test sets have the exact same columns
# Sometimes the test set might be missing a rare protocol, so we align them.
# This adds any missing columns to the test set and fills them with 0.
train_cols = df_train.columns
df_test = df_test.reindex(columns=train_cols, fill_value=0)

print(f"New Training Shape: {df_train.shape}")
print(f"New Test Shape: {df_test.shape}")
print("Data is now strictly numeric and ready for the 'Brain'.")


from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score, classification_report

# 1. SPLIT DATA INTO X (Features) AND y (Labels)
# X is everything except the label
X_train = df_train.drop('label', axis=1)
y_train = df_train['label']

X_test = df_test.drop('label', axis=1)
y_test = df_test['label']

# 2. DEFINE THE NEURAL NETWORK (The "Baseline" Model)
# hidden_layer_sizes=(100,): This means 1 layer with 100 neurons.
# max_iter=100: We give it 100 chances to learn from the data.
print("Training the Neural Network... (This might take 1-2 minutes)")
mlp = MLPClassifier(hidden_layer_sizes=(100,), max_iter=50, random_state=42)

# 3. TRAIN
mlp.fit(X_train, y_train)

# 4. TEST
predictions = mlp.predict(X_test)

# 5. SCORE
print("Baseline Accuracy:", accuracy_score(y_test, predictions))
print("\nDetailed Report:\n", classification_report(y_test, predictions))


from sklearn.ensemble import RandomForestClassifier

# 1. TRAIN A RANDOM FOREST TO FIND IMPORTANT FEATURES
# We use Random Forest because it's very good at ranking variables.
print("Ranking features... (This might take a minute)")
rf = RandomForestClassifier(n_estimators=50, random_state=42)
rf.fit(X_train, y_train)

# 2. GET THE IMPORTANCE SCORES
importances = rf.feature_importances_
feature_names = X_train.columns

# 3. CREATE A DATAFRAME TO VIEW THEM
feature_importance_df = pd.DataFrame({
    'Feature': feature_names,
    'Importance': importances
})

# 4. SORT BY IMPORTANCE AND PICK THE TOP 20
top_20_features = feature_importance_df.sort_values(by='Importance', ascending=False).head(20)

print("\nTop 20 Most Important Features:")
print(top_20_features)

# 5. CREATE THE "OPTIMIZED" DATASETS (only keeping these 20 columns)
# We get the list of names
selected_columns = top_20_features['Feature'].tolist()

# We verify that these columns exist in our dataframe
# (This step prevents errors if indices got messed up)
X_train_opt = X_train[selected_columns]
X_test_opt = X_test[selected_columns]

print(f"\nNew Optimized Shape: {X_train_opt.shape}")
print("We have reduced the data from 123 columns to just 20!")


# 1. TRAIN THE OPTIMIZED NEURAL NETWORK
# Notice we are using X_train_opt and X_test_opt (the 20-column versions)
print("Training the Optimized Neural Network... (This should be faster)")
mlp_opt = MLPClassifier(hidden_layer_sizes=(100,), max_iter=50, random_state=42)

mlp_opt.fit(X_train_opt, y_train)

# 2. TEST
predictions_opt = mlp_opt.predict(X_test_opt)

# 3. SCORE
print("Optimized Accuracy:", accuracy_score(y_test, predictions_opt))
print("\nDetailed Report:\n", classification_report(y_test, predictions_opt))

# 4. FINAL COMPARISON
print("--- FINAL RESULT ---")
# We assume you still have the 'predictions' variable from Step 3
baseline_acc = accuracy_score(y_test, predictions)
opt_acc = accuracy_score(y_test, predictions_opt)

print(f"Baseline Accuracy (123 features): {baseline_acc:.4f}")
print(f"Optimized Accuracy (20 features):  {opt_acc:.4f}")

if opt_acc > baseline_acc:
    print("SUCCESS: The optimized model is MORE accurate!")
elif opt_acc == baseline_acc:
    print("SUCCESS: The optimized model is JUST AS accurate (but faster)!")
else:
    print("Result: The optimized model lost some accuracy, but is much simpler.")
    
    
    
from sklearn.preprocessing import StandardScaler

# 1. SET UP THE SCALER
# StandardScaler shifts the data so the average is 0.
scaler = StandardScaler()

# 2. "FIT" THE SCALER (Learn the math from the training data)
# We only fit on training data to avoid "cheating" (data leakage)
scaler.fit(X_train_opt)

# 3. TRANSFORM THE DATA
X_train_scaled = scaler.transform(X_train_opt)
X_test_scaled = scaler.transform(X_test_opt)

# 4. TRAIN THE OPTIMIZED MODEL ON SCALED DATA
print("Training the Scaled Optimized Neural Network... (Final Attempt)")
mlp_opt_scaled = MLPClassifier(hidden_layer_sizes=(100,), max_iter=50, random_state=42)
mlp_opt_scaled.fit(X_train_scaled, y_train)

# 5. TEST AND SCORE
predictions_scaled = mlp_opt_scaled.predict(X_test_scaled)
scaled_acc = accuracy_score(y_test, predictions_scaled)

print(f"Baseline Accuracy:       {baseline_acc:.4f}")
print(f"Optimized (Unscaled):    {opt_acc:.4f}")
print(f"Optimized (SCALED):      {scaled_acc:.4f}")

if scaled_acc > baseline_acc:
    print("\n WE DID IT! The optimized model is now smarter AND faster.")
    
    
    
# INCREASE ITERATIONS TO FIX THE WARNING
print("Training with more time (200 iterations)...")

# We changed max_iter from 50 to 200
mlp_final = MLPClassifier(hidden_layer_sizes=(100,), max_iter=200, random_state=42)

mlp_final.fit(X_train_scaled, y_train)

# TEST
predictions_final = mlp_final.predict(X_test_scaled)
final_acc = accuracy_score(y_test, predictions_final)

print(f"Baseline Accuracy:       {baseline_acc:.4f}")
print(f"Final Optimized Accuracy:{final_acc:.4f}")

if final_acc > baseline_acc:
    print("\n🏆 SUCCESS: We beat the baseline with less data!")
else:
    print("\nRESULT: Still close, but the Baseline wins on pure accuracy.")
    
    
import matplotlib.pyplot as plt
import numpy as np

# DATA FROM OUR EXPERIMENT
# (Replace these with your exact final numbers if they differ slightly)
models = ['Baseline (All Features)', 'Optimized (Top 20)']
accuracies = [baseline_acc, final_acc] # Uses the variables we created earlier
feature_counts = [123, 20]

# --- CHART 1: ACCURACY COMPARISON ---
plt.figure(figsize=(8, 5))
bars = plt.bar(models, accuracies, color=['#4287f5', '#fcba03']) # Blue and Yellow

# Add the actual numbers on top of the bars
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, yval + 0.01, f'{yval:.4f}', ha='center', fontweight='bold')

plt.title('Detection Accuracy: Baseline vs. Optimized', fontsize=14)
plt.ylabel('Accuracy Score (0-1)', fontsize=12)
plt.ylim(0, 1.0) # Set limit to 1.0 to show the full scale
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.show()

# --- CHART 2: COMPLEXITY COMPARISON (The "Wow" Factor) ---
plt.figure(figsize=(8, 5))
bars = plt.bar(models, feature_counts, color=['#ff6b6b', '#1dd1a1']) # Red and Green

# Add numbers
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, yval + 2, f'{int(yval)} Features', ha='center', fontweight='bold')

plt.title('Computational Complexity (Number of Features)', fontsize=14)
plt.ylabel('Count of Input Features', fontsize=12)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.show()


import xgboost as xgb
from sklearn.metrics import accuracy_score

# 1. INITIALIZE THE XGBOOST MODEL
# XGBoost is often stronger than Random Forest and faster than ANN
print("Training XGBoost on Optimized Features...")
xgb_model = xgb.XGBClassifier(n_estimators=100, learning_rate=0.1, max_depth=6, random_state=42)

# 2. TRAIN
xgb_model.fit(X_train_opt, y_train)

# 3. PREDICT
xgb_preds = xgb_model.predict(X_test_opt)
xgb_acc = accuracy_score(y_test, xgb_preds)

print(f"Optimized ANN Accuracy:     {final_acc:.4f}")
print(f"Optimized XGBoost Accuracy: {xgb_acc:.4f}")

if xgb_acc > final_acc:
    print("\n🚀 XGBoost outperformed the Neural Network!")
    
    
from sklearn.ensemble import VotingClassifier
from sklearn.ensemble import RandomForestClassifier

# 1. DEFINE THE THREE EXPERTS
# We use the scaled data because the ANN needs it
clf1 = MLPClassifier(hidden_layer_sizes=(100,), max_iter=200, random_state=42)
clf2 = xgb.XGBClassifier(n_estimators=100, random_state=42)
clf3 = RandomForestClassifier(n_estimators=100, random_state=42)

# 2. CREATE THE VOTING CLASSIFIER
# 'hard' voting means they vote on the final label (0 or 1)
voted_model = VotingClassifier(
    estimators=[('ann', clf1), ('xgb', clf2), ('rf', clf3)],
    voting='hard'
)

print("Training the Voting Classifier... (This takes a bit longer)")
voted_model.fit(X_train_scaled, y_train)

# 3. TEST AND SCORE
voted_preds = voted_model.predict(X_test_scaled)
voted_acc = accuracy_score(y_test, voted_preds)

print(f"Final Voting Accuracy: {voted_acc:.4f}")


