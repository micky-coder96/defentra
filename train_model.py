import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import joblib
import os

print("[*] Loading NSL-KDD dataset for training...")
file_path = "data/nsl_kdd_sample.csv"

if not os.path.exists(file_path):
    print("[-] Dataset file not found! Please check your data folder.")
    exit()

# Load dataset with low_memory=False to handle mixed types cleanly
df = pd.read_csv(file_path, header=None, low_memory=False)

# Extract core features and convert types safely
# Col 4: protocol_type, Col 5: src_bytes, Col 6: dst_bytes, Col 41: label
sub_df = df[[4, 5, 6, 41]].copy()
sub_df.columns = ["protocol_type", "src_bytes", "dst_bytes", "label"]

# Force protocol_type to string to prevent mixed int/str type errors
sub_df["protocol_type"] = sub_df["protocol_type"].astype(str)

# Force src_bytes and dst_bytes to numeric, turning bad/corrupted rows into NaN
sub_df["src_bytes"] = pd.to_numeric(sub_df["src_bytes"], errors="coerce")
sub_df["dst_bytes"] = pd.to_numeric(sub_df["dst_bytes"], errors="coerce")

# Drop rows with missing values that resulted from type conversions
sub_df = sub_df.dropna()

# Preprocess categorical features
le = LabelEncoder()
sub_df["protocol_type"] = le.fit_transform(sub_df["protocol_type"])

# Convert attack labels into categorical targets (Normal vs Attack)
sub_df["target"] = sub_df["label"].apply(
    lambda x: "Normal" if str(x).strip() == "normal" else "Attack"
)

X = sub_df[["protocol_type", "src_bytes", "dst_bytes"]]
y = sub_df["target"]

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print("[*] Training Random Forest Intrusion Detection Model...")
model = RandomForestClassifier(n_estimators=50, random_state=42)
model.fit(X_train, y_train)

# Evaluate accuracy
accuracy = model.score(X_test, y_test)
print(f"[+] Model trained successfully! Test Accuracy: {accuracy * 100:.2f}%")

# Save the trained model and label encoder
os.makedirs("models", exist_ok=True)
joblib.dump(model, "models/defentra_rf_model.pkl")
joblib.dump(le, "models/protocol_encoder.pkl")
print("[+] Model saved to models/defentra_rf_model.pkl")
