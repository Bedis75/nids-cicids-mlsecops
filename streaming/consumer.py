import pandas as pd
from kafka import KafkaConsumer
import joblib
import json

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
    print("le modèle a prédit :", prediction[0], " | réel :", data["is_attack"], " | ", data["Label"])
