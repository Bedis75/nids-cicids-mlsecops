import pandas as pd
from kafka import KafkaConsumer
import joblib
import json
import sqlite3
from datetime import datetime



conn = sqlite3.connect("predictions.db")
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        prediction INTEGER,
        real_value INTEGER,
        label TEXT
    )
""")
conn.commit()

model = joblib.load("rf_model.pkl")

consumer = KafkaConsumer(
    "network-flows",
    bootstrap_servers="localhost:9092",
    value_deserializer=lambda v: json.loads(v.decode('utf-8')),
    auto_offset_reset='earliest'
)

for message in consumer:
    data = message.value
    df_row = pd.DataFrame([data])
    features = df_row.drop(columns=["Label","is_attack","source_day"])
    prediction = model.predict(features)
    timestamp_value = datetime.now().isoformat()
    print("le modèle a prédit :", prediction[0], " | réel :", data["is_attack"], " | ", data["Label"])
    cursor.execute(
    "INSERT INTO predictions (timestamp, prediction, real_value, label) VALUES (?, ?, ?, ?)",
    (timestamp_value, int(prediction[0]), int(data["is_attack"]), data["Label"])
    )
    conn.commit()
