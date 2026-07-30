import streamlit as st
import pandas as pd
import sqlite3
from streamlit_autorefresh import st_autorefresh
import os

DB_PATH = os.getenv("DB_PATH", "predictions.db")


st.title("NIDS — Détection d'intrusion en temps réel")

conn = sqlite3.connect(DB_PATH)
df = pd.read_sql("SELECT * FROM predictions", conn)
conn.close()

total_flux = len(df)
total_attack = df["prediction"].sum()
precision = (df["prediction"] == df["real_value"]).mean()

col1, col2, col3 = st.columns(3)
col1.metric("Flux analysés", total_flux)
col2.metric("Attaques détectées", total_attack)
col3.metric("Précision", f"{precision:.1%}")

st.header("Répartition par type d'attaque")
attack_counts = df[df["label"] != "BENIGN"]["label"].value_counts()
st.bar_chart(attack_counts)

st.header("Détail des détections")
st.dataframe(df)

st_autorefresh(interval=1000, key="refresh")