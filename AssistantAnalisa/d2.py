import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
import matplotlib.pyplot as plt
import seaborn as sns

# Fungsi untuk memuat dataset transaksi
def load_data():
    # Gantilah dengan path ke file transaksi yang sebenarnya
    data = pd.read_csv('data/tx_training.csv')
    return data

# Fungsi untuk melatih model Isolation Forest dan mendeteksi anomali
def detect_anomalies(data):
    # Memilih fitur-fitur yang akan digunakan untuk pelatihan
    features = ['nominaltx', 'txtimestamp']  # Gantilah dengan fitur yang sesuai

    # Konversi fitur txtimestamp ke format numerik (Unix timestamp)
    data['txtimestamp'] = pd.to_datetime(data['txtimestamp'])
    data['txtimestamp'] = data['txtimestamp'].astype(np.int64) // 10**9  # Konversi ke detik

    X = data[features]

    # Melatih model Isolation Forest
    model = IsolationForest(contamination=0.05, random_state=42)
    data['anomaly_score'] = model.fit_predict(X)

    # Menambahkan kolom anomaly dengan nilai True jika anomali, selain itu False
    data['anomaly'] = data['anomaly_score'] == -1

    return data, model

# Fungsi utama untuk menjalankan aplikasi
def main():
    # Memuat data
    data = load_data()

    data_with_anomalies, model = detect_anomalies(data)

    # Menampilkan hasil deteksi anomali
    anomalies = data_with_anomalies[data_with_anomalies['anomaly'] == True]
    print("Anomalous transactions:")
    print(anomalies)

    # Plot hasil deteksi
    fig, ax = plt.subplots()
    sns.scatterplot(data=data_with_anomalies, x='nominaltx', y='txtimestamp', hue='anomaly', ax=ax)
    plt.title("Transaction Anomalies Detection")
    plt.xlabel("Transaction Amount")
    plt.ylabel("Transaction Timestamp (Unix)")
    plt.show()

if __name__ == "__main__":
    main()
