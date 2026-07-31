# NIDS-CICIDS-MLSecOps

NIDS-CICIDS-MLSecOps est un système de détection d'intrusion réseau basé sur le machine learning, entraîné sur le dataset CICIDS2017 (trafic réseau contenant plusieurs types d'attaques).

Le projet compare des approches supervisées et non-supervisées — Random Forest, XGBoost, Isolation Forest — et met en évidence comment les performances chutent face à des attaques inédites (zero-day).

## Contexte

Les attaques réseau augmentent en volume et en variété, et surveiller manuellement le trafic n'est plus tenable. Le machine learning permet d'automatiser la détection d'intrusion, libérant l'analyste des tâches répétitives.

Mais un modèle ML n'est pas infaillible : ce projet examine notamment ses limites face à des attaques qu'il n'a jamais vues à l'entraînement — un enjeu central en sécurité, où les menaces évoluent constamment.

## Résultat principal

Les résultats ci-dessous illustrent l'écart de performance entre les différentes approches d'évaluation :


| Approche | Recall (attaques) | Ce que ça révèle |
|----------|-------------------|------------------|
| Supervisé, split aléatoire | 1.00 | Score illusoire (mémorisation) |
| Supervisé, split temporel | 0.08 | Échec sur attaques inédites |
| Isolation Forest (non-supervisé) | 0.45 | Généralise mieux au zero-day |

Le score parfait obtenu en split aléatoire est trompeur : il reflète la mémorisation de flux redondants, pas une vraie capacité de détection. Le split temporel le confirme — face à des attaques inédites, le modèle supervisé ne détecte quasiment rien (recall 0.08). Dans ce contexte, l'approche non-supervisée se révèle nettement plus robuste.

## Structure du projet

- `01_data_preparation.ipynb` — nettoyage des données, gestion des valeurs Inf/NaN, création de la target binaire, export Parquet
- `02_baseline_models.ipynb` — modèles supervisés (Logistic Regression, Random Forest, XGBoost) et analyse critique du score parfait
- `03_temporal_split.ipynb` — réévaluation XGBoost avec un découpage temporel (par jour) révélant l'effondrement du score sur attaques inédites
- `04_anomaly_detection.ipynb` — détection non-supervisée (Isolation Forest) apprenant la normalité, plus robuste face aux attaques inédites
- `streaming/docker-compose.yml` — infrastructure Kafka (mode KRaft)
- `streaming/producer.py` — rejoue les flux CICIDS2017 dans Kafka (JSON)
- `streaming/consumer.py` — scoring temps réel, persistance SQLite
- `streaming/dashboard.py` — dashboard Streamlit (métriques live)
- `k8s/kafka.yaml` — Deployment et Service Kafka
- `k8s/producer.yaml` — Deployment du producer
- `k8s/consumer.yaml` — Deployment du consumer (volume partagé)
- `k8s/dashboard.yaml` — Deployment et Service NodePort du dashboard
- `k8s/storage.yaml` — PersistentVolumeClaim pour la base de prédictions

## Pipeline temps réel

Le pipeline analyse les flux réseau au fil de leur arrivée : chaque flux est
scoré par le modèle Random Forest dès réception, puis les résultats sont
affichés sur un dashboard live.

Le flux est simulé : un producer rejoue le dataset CICIDS2017 ligne par ligne
(une ligne toutes les 10 ms, configurable) pour reproduire l'arrivée continue
de trafic. En production, la source serait une sonde réseau alimentée par un
outil type CICFlowMeter.

```producer.py → Kafka (network-flows) → consumer.py (scoring) → SQLite → dashboard```

- **Kafka 3.9 en mode KRaft** (sans ZooKeeper), topic à 3 partitions
- **Consumer** : charge le modèle sérialisé avec joblib — l'entraînement
  (notebooks) et l'inférence (streaming) sont ainsi découplés
- **Dashboard Streamlit** : métriques live, répartition des attaques détectées

## Déploiement

Le déploiement se fait à deux niveaux. Chaque composant (producer, consumer,
dashboard) est conteneurisé via son propre Dockerfile. Docker Compose orchestre
l'ensemble pour le développement local ; Kubernetes prend le relais pour
l'orchestration.

Lancement en une commande :

```
docker compose up -d        # Docker Compose
kubectl apply -f k8s/       # Kubernetes
```

- **Configuration externalisée** : adresse Kafka, chemins de fichiers et taille
  d'échantillon passent par variables d'environnement — le même code tourne en
  local, en Compose et en Kubernetes
- **Modèle et données embarqués dans les images** : garantit qu'une image donnée
  contient exactement le modèle avec lequel elle a été construite
- **Volume partagé** (PersistentVolumeClaim) entre consumer et dashboard pour la
  base de prédictions
- **Exposition** : le dashboard est accessible via un Service NodePort

## Mapping MITRE ATT&CK

Les étiquettes du dataset (DoS Hulk, PortScan, FTP-Patator) sont propres à
CICIDS2017. Les traduire en identifiants MITRE ATT&CK les relie au vocabulaire
opérationnel de la sécurité.

Chaque détection se situe alors dans une étape connue du cycle d'attaque, avec
ses mitigations documentées — un analyste sait immédiatement à quelle phase
il fait face.

| Classe CICIDS2017 | Tactique ATT&CK | Technique |
|-------------------|-----------------|-----------|
| PortScan | Reconnaissance (TA0043) | T1046 — Network Service Discovery |
| FTP-Patator, SSH-Patator | Credential Access (TA0006) | T1110.001 — Password Guessing |
| Web Attack (SQLi, XSS, Brute Force) | Initial Access (TA0001) | T1190 — Exploit Public-Facing Application |
| Infiltration | Lateral Movement (TA0008) | T1021 — Remote Services |
| Bot | Command and Control (TA0011) | T1071 — Application Layer Protocol |
| DoS Hulk, GoldenEye, slowloris, Slowhttptest | Impact (TA0040) | T1499 — Endpoint Denial of Service |
| DDoS | Impact (TA0040) | T1498 — Network Denial of Service |
| Heartbleed | Credential Access (TA0006) | T1040 — Network Sniffing |

## Limites et travaux futurs

**Limites :**

- Entraînement sur échantillon (300k lignes) pour RF/XGBoost — contrainte mémoire
- Split temporel très sévère (types d'attaques disjoints train/test)
- Isolation Forest : precision faible, non déployable seul

**Travaux futurs :**

- Agrégations sur fenêtres temporelles via Spark Structured Streaming
  (taux d'attaques par intervalle, pics par port) pour capter des patterns
  invisibles au niveau du flux isolé
- Durcissement des conteneurs : exécution en utilisateur non-privilégié
- Réentraînement périodique du modèle et versionnement des artefacts

## Stack technique

Python · pandas · NumPy · scikit-learn · XGBoost · Parquet · Apache Kafka · Docker · Kubernetes · Streamlit · SQLite · Jupyter
