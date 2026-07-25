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

## Limites et travaux futurs

**Limites :**
- Entraînement sur échantillon (300k lignes) pour RF/XGBoost — contrainte mémoire
- Split temporel très sévère (types d'attaques disjoints train/test)
- Isolation Forest : precision faible, non déployable seul

**Travaux futurs :**
- Détection temps réel (Kafka + Spark Streaming)
- Déploiement conteneurisé (Docker + k3s)
- Mapping MITRE ATT&CK

## Stack technique

Python · pandas · NumPy · scikit-learn · XGBoost · Jupyter · Parquet
