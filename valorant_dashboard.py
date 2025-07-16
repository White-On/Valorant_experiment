"""
Dashboard Streamlit pour le suivi des données Valorant
Application web interactive pour visualiser et suivre l'état des données collectées.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sqlite3
from pathlib import Path
import json
import os

# Configuration Streamlit
st.set_page_config(
    page_title="Valorant Data Dashboard",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import des modules locaux
import sys
sys.path.append('src')
from database_utils import DatabaseManager
from config import MATCHS_FILE, PLAYER_DB_PATH, MATCHS_ENHANCED_FILE

def load_custom_css():
    """Charge les styles CSS personnalisés."""
    st.markdown("""
    <style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 0.5rem 0;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: white;
        margin: 0;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: rgba(255, 255, 255, 0.8);
        margin: 0;
    }
    
    .status-good {
        color: #28a745;
    }
    
    .status-warning {
        color: #ffc107;
    }
    
    .status-error {
        color: #dc3545;
    }
    
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 1rem;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=300)  # Cache pendant 5 minutes
def load_database_stats():
    """Charge les statistiques de la base de données."""
    db_manager = DatabaseManager()
    
    stats = {
        'exists': db_manager.database_exists(),
        'player_count': 0,
        'last_updated': None
    }
    
    if stats['exists']:
        stats['player_count'] = db_manager.get_player_count()
        
        # Obtenir la date de dernière modification
        if PLAYER_DB_PATH.exists():
            mtime = PLAYER_DB_PATH.stat().st_mtime
            stats['last_updated'] = datetime.fromtimestamp(mtime)
    
    return stats

@st.cache_data(ttl=300)
def load_matches_data():
    """Charge les données des matchs."""
    matches_data = {
        'exists': False,
        'count': 0,
        'size_mb': 0,
        'last_updated': None,
        'df': None
    }
    
    if MATCHS_FILE.exists():
        try:
            df = pd.read_csv(MATCHS_FILE)
            matches_data.update({
                'exists': True,
                'count': len(df),
                'size_mb': MATCHS_FILE.stat().st_size / (1024 * 1024),
                'last_updated': datetime.fromtimestamp(MATCHS_FILE.stat().st_mtime),
                'df': df
            })
        except Exception as e:
            st.error(f"Erreur lors du chargement des matchs: {e}")
    
    return matches_data

@st.cache_data(ttl=300)
def load_enhanced_matches_data():
    """Charge les données des matchs enrichis."""
    enhanced_data = {
        'exists': False,
        'count': 0,
        'size_mb': 0,
        'last_updated': None,
        'df': None
    }
    
    if MATCHS_ENHANCED_FILE.exists():
        try:
            df = pd.read_csv(MATCHS_ENHANCED_FILE)
            enhanced_data.update({
                'exists': True,
                'count': len(df),
                'size_mb': MATCHS_ENHANCED_FILE.stat().st_size / (1024 * 1024),
                'last_updated': datetime.fromtimestamp(MATCHS_ENHANCED_FILE.stat().st_mtime),
                'df': df
            })
        except Exception as e:
            st.error(f"Erreur lors du chargement des matchs enrichis: {e}")
    
    return enhanced_data

def display_metric_card(title, value, status_color=""):
    """Affiche une carte de métrique personnalisée."""
    status_class = f"status-{status_color}" if status_color else ""
    
    st.markdown(f"""
    <div class="metric-card">
        <p class="metric-label">{title}</p>
        <p class="metric-value {status_class}">{value}</p>
    </div>
    """, unsafe_allow_html=True)

def main_dashboard():
    """Page principale du dashboard."""
    st.title("🎮 Dashboard Valorant - Suivi des Données")
    st.markdown("---")
    
    # Charger les données
    db_stats = load_database_stats()
    matches_data = load_matches_data()
    enhanced_data = load_enhanced_matches_data()
    
    # Métriques principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        status_color = "good" if db_stats['player_count'] > 0 else "error"
        st.metric(
            label="👥 Joueurs en BDD",
            value=db_stats['player_count'],
            help="Nombre total de joueurs dans la base de données"
        )
    
    with col2:
        status_color = "good" if matches_data['count'] > 0 else "warning"
        st.metric(
            label="🎮 Matchs Collectés",
            value=matches_data['count'],
            help="Nombre total de matchs dans le fichier CSV"
        )
    
    with col3:
        status_color = "good" if enhanced_data['count'] > 0 else "warning"
        st.metric(
            label="⭐ Matchs Enrichis",
            value=enhanced_data['count'],
            help="Nombre de matchs avec données enrichies"
        )
    
    with col4:
        total_size = matches_data['size_mb'] + enhanced_data['size_mb']
        if PLAYER_DB_PATH.exists():
            total_size += PLAYER_DB_PATH.stat().st_size / (1024 * 1024)
        
        st.metric(
            label="💾 Espace Utilisé",
            value=f"{total_size:.1f} MB",
            help="Espace total utilisé par tous les fichiers de données"
        )
    
    # Graphiques et analyses
    st.markdown("---")
    
    # Onglets pour différentes vues
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Vue d'ensemble", "🎮 Analyse des Matchs", "👥 Gestion des Joueurs", "🔧 Maintenance"])
    
    with tab1:
        overview_tab(db_stats, matches_data, enhanced_data)
    
    with tab2:
        matches_analysis_tab(matches_data, enhanced_data)
    
    with tab3:
        players_management_tab(db_stats)
    
    with tab4:
        maintenance_tab(db_stats, matches_data, enhanced_data)

def overview_tab(db_stats, matches_data, enhanced_data):
    """Onglet vue d'ensemble."""
    st.subheader("📊 Vue d'ensemble des données")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Évolution des données")
        
        # Graphique en secteurs de la répartition des données
        labels = ['Joueurs BDD', 'Matchs Standard', 'Matchs Enrichis']
        values = [db_stats['player_count'], matches_data['count'], enhanced_data['count']]
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=.3,
            marker_colors=colors
        )])
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(
            title="Répartition des Données Collectées",
            showlegend=True,
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🕒 État des fichiers")
        
        # Tableau d'état des fichiers
        file_status = []
        
        files_info = [
            ("Base de données joueurs", PLAYER_DB_PATH, db_stats['last_updated'], db_stats['exists']),
            ("Fichier matchs", MATCHS_FILE, matches_data['last_updated'], matches_data['exists']),
            ("Matchs enrichis", MATCHS_ENHANCED_FILE, enhanced_data['last_updated'], enhanced_data['exists'])
        ]
        
        for name, path, last_update, exists in files_info:
            if exists and last_update:
                time_diff = datetime.now() - last_update
                if time_diff.days == 0:
                    last_update_str = f"Il y a {time_diff.seconds // 3600}h"
                else:
                    last_update_str = f"Il y a {time_diff.days}j"
                status = "✅ Actif"
            else:
                last_update_str = "Jamais"
                status = "❌ Inexistant"
            
            file_status.append({
                "Fichier": name,
                "État": status,
                "Dernière modification": last_update_str
            })
        
        df_status = pd.DataFrame(file_status)
        st.dataframe(df_status, use_container_width=True, hide_index=True)

def matches_analysis_tab(matches_data, enhanced_data):
    """Onglet analyse des matchs."""
    st.subheader("🎮 Analyse des Matchs")
    
    if matches_data['exists'] and matches_data['df'] is not None:
        df = matches_data['df']
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Statistiques des matchs")
            
            # Afficher les colonnes disponibles
            st.write("**Colonnes disponibles:**")
            st.write(list(df.columns))
            
            # Premières lignes du dataset
            st.write("**Aperçu des données:**")
            st.dataframe(df.head(), use_container_width=True)
        
        with col2:
            st.subheader("📈 Métriques")
            
            # Informations générales
            st.metric("Nombre total de matchs", len(df))
            
            if 'date' in df.columns or 'timestamp' in df.columns:
                date_col = 'date' if 'date' in df.columns else 'timestamp'
                try:
                    df[date_col] = pd.to_datetime(df[date_col])
                    latest_match = df[date_col].max()
                    oldest_match = df[date_col].min()
                    
                    st.metric("Match le plus récent", latest_match.strftime("%d/%m/%Y"))
                    st.metric("Match le plus ancien", oldest_match.strftime("%d/%m/%Y"))
                    
                    # Graphique temporel
                    st.subheader("📅 Évolution temporelle")
                    daily_matches = df.groupby(df[date_col].dt.date).size()
                    
                    fig = px.line(
                        x=daily_matches.index,
                        y=daily_matches.values,
                        title="Nombre de matchs par jour"
                    )
                    fig.update_layout(xaxis_title="Date", yaxis_title="Nombre de matchs")
                    st.plotly_chart(fig, use_container_width=True)
                    
                except Exception as e:
                    st.warning(f"Impossible d'analyser les dates: {e}")
    else:
        st.warning("Aucune donnée de match disponible pour l'analyse.")
        st.info("💡 Conseil: Exécutez le script de collecte des matchs pour commencer l'analyse.")

def players_management_tab(db_stats):
    """Onglet gestion des joueurs."""
    st.subheader("👥 Gestion des Joueurs")
    
    if db_stats['exists'] and db_stats['player_count'] > 0:
        try:
            # Charger les données des joueurs depuis la BDD
            db_manager = DatabaseManager()
            
            with sqlite3.connect(PLAYER_DB_PATH) as conn:
                df_players = pd.read_sql_query("SELECT * FROM players", conn)
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.subheader("📋 Liste des joueurs")
                st.dataframe(df_players, use_container_width=True, hide_index=True)
            
            with col2:
                st.subheader("📊 Statistiques")
                st.metric("Total joueurs", len(df_players))
                
                if 'created_at' in df_players.columns:
                    try:
                        df_players['created_at'] = pd.to_datetime(df_players['created_at'])
                        recent_players = len(df_players[df_players['created_at'] > datetime.now() - timedelta(days=7)])
                        st.metric("Nouveaux joueurs (7j)", recent_players)
                    except:
                        pass
                
                # Bouton de rafraîchissement
                if st.button("🔄 Rafraîchir les données"):
                    st.cache_data.clear()
                    st.rerun()
        
        except Exception as e:
            st.error(f"Erreur lors du chargement des joueurs: {e}")
    else:
        st.warning("Aucun joueur dans la base de données.")
        st.info("💡 Conseil: Exécutez le script de collecte des joueurs pour commencer.")

def maintenance_tab(db_stats, matches_data, enhanced_data):
    """Onglet maintenance."""
    st.subheader("🔧 Maintenance et Actions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏃‍♂️ Actions rapides")
        
        # Boutons d'action
        if st.button("🔄 Rafraîchir toutes les données", type="primary"):
            st.cache_data.clear()
            st.success("Cache vidé, données rafraîchies!")
            st.rerun()
        
        if st.button("📊 Vérifier l'intégrité des données"):
            with st.spinner("Vérification en cours..."):
                issues = []
                
                # Vérifications
                if not db_stats['exists']:
                    issues.append("❌ Base de données joueurs inexistante")
                
                if not matches_data['exists']:
                    issues.append("❌ Fichier de matchs inexistant")
                
                if db_stats['player_count'] == 0:
                    issues.append("⚠️ Aucun joueur en base")
                
                if matches_data['count'] == 0:
                    issues.append("⚠️ Aucun match collecté")
                
                if not issues:
                    st.success("✅ Toutes les vérifications sont OK!")
                else:
                    for issue in issues:
                        st.warning(issue)
    
    with col2:
        st.subheader("📋 Commandes utiles")
        
        commands = [
            ("Collecter des joueurs", "cd src && python player_stats_collector.py"),
            ("Collecter des matchs", "cd src && python matchs_collect.py"),
            ("Enrichir les matchs", "cd src && python matchs_enhanced.py"),
            ("Résumé en console", "cd src && python data_summary.py"),
            ("Infos BDD", "cd src && python db_manager.py --info")
        ]
        
        for description, command in commands:
            with st.expander(f"💻 {description}"):
                st.code(command, language="bash")
        
        st.subheader("📁 Chemins des fichiers")
        paths_info = [
            ("Base de données", str(PLAYER_DB_PATH)),
            ("Matchs CSV", str(MATCHS_FILE)),
            ("Matchs enrichis", str(MATCHS_ENHANCED_FILE))
        ]
        
        for name, path in paths_info:
            st.text(f"{name}: {path}")

def main():
    """Fonction principale."""
    load_custom_css()
    
    # Sidebar pour la navigation
    with st.sidebar:
        st.title("🎮 Navigation")
        st.markdown("---")
        
        # Informations de mise à jour
        st.subheader("🔄 Dernière mise à jour")
        st.write(datetime.now().strftime("%H:%M:%S"))
        
        if st.button("Rafraîchir", key="sidebar_refresh"):
            st.cache_data.clear()
            st.rerun()
        
        st.markdown("---")
        
        # Statut rapide
        st.subheader("⚡ Statut rapide")
        db_stats = load_database_stats()
        matches_data = load_matches_data()
        
        status_db = "🟢" if db_stats['player_count'] > 0 else "🔴"
        status_matches = "🟢" if matches_data['count'] > 0 else "🔴"
        
        st.write(f"{status_db} Base de données: {db_stats['player_count']} joueurs")
        st.write(f"{status_matches} Matchs: {matches_data['count']} entrées")
    
    # Contenu principal
    main_dashboard()

if __name__ == "__main__":
    main()
