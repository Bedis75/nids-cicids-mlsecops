import pandas as pd
from kafka import KafkaProducer
from time import sleep
import json
import os

KAFKA_SERVER = os.getenv("KAFKA_SERVER", "localhost:29092")
PARQUET_PATH = os.getenv("PARQUET_PATH", "../data/processed/cicids_clean.parquet")

df = pd.read_parquet(PARQUET_PATH).sample(n=10000, random_state=42)

producer = KafkaProducer(
    bootstrap_servers=KAFKA_SERVER,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

for i , row in df.iterrows():
    message = row.to_dict()
    producer.send("network-flows", message)
    sleep(0.01)
    print(f"Flux #{i} envoyé — is_attack={row['is_attack']}")

producer.flush()