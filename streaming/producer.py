import pandas as pd
from kafka import KafkaProducer
from time import sleep
import json

df = pd.read_parquet("../data/processed/cicids_clean.parquet").sample(n=10000, random_state=42)

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

for i , row in df.iterrows():
    message = row.to_dict()
    producer.send("network-flows", message)
    sleep(0.01)
    print(f"Flux #{i} envoyé — is_attack={row['is_attack']}")

producer.flush()