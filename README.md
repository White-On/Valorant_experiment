# 🎮 Valorant Match Prediction - Projet d'Analyse et Classification

## 📋 Aperçu du Projet

Ce projet vise à développer un système de prédiction des résultats de matchs Valorant en utilisant des techniques d'apprentissage automatique. L'objectif principal est d'atteindre une précision de prédiction de 60-70% en enrichissant significativement les données des joueurs et des équipes.

## 🎯 Objectifs

- **Collecte de données enrichies** : Rassembler des statistiques détaillées sur les joueurs et les matchs via l'API Valorant
- **Prédiction de résultats** : Développer des modèles de classification pour prédire l'issue des matchs
- **Analyse exploratoire** : Comprendre les facteurs qui influencent les performances des équipes
- **Dashboard interactif** : Visualiser et suivre l'évolution des données collectées

## 🔬 Historique des Approches de Classification

À l'heure actuelle, j'ai déjà fait plusieurs tentatives de classification autour des parties de Valorant :

### 📊 Première Approche - MLP Simple
- **Modèle** : Multi-Layer Perceptron (MLP)
- **Données** : Informations pré-match (rang de chaque joueur principalement)
- **Résultat** : Échec - La donnée manquait très clairement de richesse

### 🎯 Deuxième Tentative - Données Post-Match
- **Approche** : Test avec des informations post-partie pour valider le potentiel
- **Objectif** : Voir si en "trichant" je pouvais booster les résultats
- **Résultat** : Sans succès malgré l'accès aux données complètes

### ⚙️ Troisième Approche - SGD Classifier
- **Modèle** : Stochastic Gradient Descent (SGD) de sklearn
- **Données pré-match** : Sans succès
- **Données post-match** : Bons résultats obtenus

### 💡 Approche Actuelle - Enrichissement des Données
**Hypothèse** : En enrichissant fortement la donnée côté joueur/équipe, j'ai une chance d'au moins approcher les 60-70% de précision.

Cette nouvelle stratégie se concentre sur :
- Collecte exhaustive des statistiques historiques des joueurs
- Analyse des performances par agent/rôle
- Métriques d'équipe et synergies
- Facteurs contextuels (cartes, compositions, méta)

## 🏗️ Architecture du Projet

```
Valorant_experiment/
├── 📊 data/                          # Données collectées
│   ├── player_stats.db              # Base de données SQLite des joueurs
│   ├── matchs.csv                   # Matchs collectés de base
│   ├── matchs_enhanced.csv          # Matchs avec données enrichies
│   └── ...                         # Autres fichiers de données
├── 🔧 src/                          # Code source principal
│   ├── api_utils.py                 # Utilitaires pour l'API Valorant
│   ├── config.py                    # Configuration du projet
│   ├── database_utils.py            # Gestion de la base de données
│   ├── matchs_collect.py            # Collecte des matchs
│   ├── matchs_enhanced.py           # Enrichissement des données
│   ├── player_stats_collector.py    # Collecte des stats joueurs
│   ├── data_summary.py              # Résumé des données (CLI)
│   └── db_manager.py                # Gestionnaire de base de données
├── 🧪 exploration_work/             # Notebooks d'exploration
│   ├── Valorant_data_Analyze.ipynb  # Analyse des données
│   ├── sklearn_attempt.ipynb        # Tentatives avec sklearn
│   └── ...                         # Autres explorations
├── 📱 valorant_dashboard.py         # Dashboard Streamlit
└── 🚀 Scripts de lancement
```

## 🔧 Installation et Configuration

### Prérequis
- Python 3.9+
- Clé API Henrik Dev (https://api.henrikdev.xyz/)
- Environnement virtuel recommandé

### Installation

1. **Cloner le projet**
```bash
git clone <repository-url>
cd Valorant_experiment
```

2. **Créer un environnement virtuel**
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
# ou
source .venv/bin/activate  # Linux/Mac
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
pip install streamlit plotly  # Pour le dashboard
```

4. **Configuration de l'API**
Créer un fichier `.env` à la racine :
```env
API_KEY=YOUR_HENRIK_API_KEY_HERE
```

## 🚀 Utilisation

### 📊 Dashboard Interactif (Recommandé)
```bash
# Lancement du dashboard Streamlit
streamlit run valorant_dashboard.py
```

Le dashboard offre une interface web complète pour :
- 📈 Visualiser l'état des données en temps réel
- 🎮 Analyser les matchs collectés
- 👥 Gérer les joueurs en base
- 🔧 Effectuer des actions de maintenance

### 🖥️ Ligne de Commande

#### Collecte de Données
```bash
cd src

# Collecter les statistiques des joueurs
python player_stats_collector.py

# Collecter les matchs
python matchs_collect.py

# Enrichir les données de matchs
python matchs_enhanced.py

# Résumé des données
python data_summary.py
```

#### Gestion de la Base de Données
```bash
cd src

# Informations sur la base de données
python db_manager.py --info

# Nettoyer la base de données
python db_manager.py --clean
```


## 🔍 Notebooks d'Exploration

Le dossier `exploration_work/` contient les Jupyter Notebooks pour :
- **`Valorant_data_Analyze.ipynb`** : Analyse exploratoire des données
- **`sklearn_attempt.ipynb`** : Tentatives de classification avec sklearn
- **`Valorant_data_generation.ipynb`** : Génération et préparation des données


## 🛠️ Technologies Utilisées

- **Python 3.9+** : Langage principal
- **Pandas** : Manipulation des données
- **Scikit-learn** : Modèles de machine learning
- **SQLite** : Base de données locale
- **Streamlit** : Interface web interactive
- **Plotly** : Visualisations interactives
- **Rich** : Interface CLI améliorée
- **Requests** : Appels API
- **Henrik Dev API** : Accès aux données Valorant

*Projet développé dans le cadre d'une formation en Machine Learning et analyse de données esports.*
