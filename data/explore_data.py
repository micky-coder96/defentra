import pandas as pd
import urllib.request

# Stable direct raw link to a cleaned NSL-KDD 20% training subset CSV
DATA_URL = "https://raw.githubusercontent.com/SABDULLAHJ/Anomaly-Detection-on-NSL-KDD-dataset/master/1%20-%2020%20Percent%20Training%20Set.csv"
file_path = "data/nsl_kdd_sample.csv"

print("[*] Downloading NSL-KDD sample dataset for Defentra...")
try:
    urllib.request.urlretrieve(DATA_URL, file_path)
    print("[+] Download complete!")

    # Load and inspect rows
    df = pd.read_csv(file_path)
    print(f"\n[📊] Dataset Shape (Rows, Columns): {df.shape}")
    print("\n[👀] First 3 rows of raw network traffic data:")
    print(df.head(3))

except Exception as e:
    print(f"[-] Error downloading dataset: {e}")
