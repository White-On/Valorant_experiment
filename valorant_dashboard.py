"""
Dashboard Streamlit pour le suivi des données Valorant
Application web interactive pour visualiser et suivre l'état des données collectées.
Version améliorée sans CSS personnalisé avec de meilleures visualisations.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sqlite3
from pathlib import Path

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
from config import MATCHS_FILE, PLAYER_DB_PATH

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

def main_dashboard():
    """Page principale du dashboard avec interface améliorée."""
    st.title("🎮 Dashboard Valorant - Analyse des Données")
    st.markdown("*Tableau de bord interactif pour analyser vos données de jeu Valorant*")
    st.markdown("---")
    
    # Charger les données
    db_stats = load_database_stats()
    matches_data = load_matches_data()
    
    # Indicateurs de statut rapide
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_color = "🟢" if db_stats['player_count'] > 0 else "🔴"
        st.metric(
            label=f"{status_color} Joueurs en BDD",
            value=f"{db_stats['player_count']:,}",
            help="Nombre total de joueurs dans la base de données"
        )
    
    with col2:
        status_color = "🟢" if matches_data['count'] > 0 else "🟠"
        st.metric(
            label=f"{status_color} Matchs Collectés",
            value=f"{matches_data['count']:,}",
            help="Nombre total de matchs dans le fichier CSV"
        )
    
    with col3:
        avg_matches = matches_data['count'] / db_stats['player_count'] if db_stats['player_count'] > 0 else 0
        status_color = "🟢" if avg_matches > 5 else "🟠" if avg_matches > 1 else "🔴"
        st.metric(
            label=f"{status_color} Ratio Matchs/Joueur",
            value=f"{avg_matches:.1f}",
            help="Nombre moyen de matchs par joueur"
        )
    
    # Messages d'état et conseils
    if db_stats['player_count'] == 0 and matches_data['count'] == 0:
        st.error("🚨 **Aucune donnée disponible!** Commencez par collecter des données de joueurs et de matchs.")
    elif db_stats['player_count'] == 0:
        st.warning("⚠️ **Aucun joueur trouvé.** Exécutez le script de collecte des joueurs.")
    elif matches_data['count'] == 0:
        st.warning("⚠️ **Aucun match trouvé.** Collectez des données de matchs pour enrichir l'analyse.")
    elif avg_matches < 2:
        st.info(f"ℹ️ **Données limitées.** Vous avez {avg_matches:.1f} matchs par joueur. Plus de données amélioreront les analyses.")
    else:
        st.success("✅ **Données suffisantes pour l'analyse!** Explorez les onglets ci-dessous.")
    
    st.markdown("---")
    
    # Onglets pour différentes vues
    tabs = st.tabs(["📊 Vue d'ensemble", "👥 Gestion des joueurs", "📈 Analyse des données", "⚙️ Paramètres"])

    with tabs[0]:
        overview_tab(db_stats, matches_data)
    with tabs[1]:
        players_management_tab(db_stats)
    with tabs[2]:
        players_data_tab(db_stats)
    with tabs[3]:
        settings_tab(db_stats, matches_data)

def overview_tab(db_stats, matches_data):
    """Onglet vue d'ensemble avec visualisations améliorées."""
    st.subheader("📊 Vue d'ensemble des données")
    
    # Métriques principales avec delta
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="👥 Joueurs Actifs",
            value=db_stats['player_count'],
            help="Nombre total de joueurs dans la base de données"
        )
    
    with col2:
        st.metric(
            label="🎮 Matchs Collectés", 
            value=f"{matches_data['count']:,}",
            help="Nombre total de matchs dans le fichier CSV"
        )
    
    with col3:
        avg_matches_per_player = matches_data['count'] / db_stats['player_count'] if db_stats['player_count'] > 0 else 0
        st.metric(
            label="📈 Matchs/Joueur",
            value=f"{avg_matches_per_player:.1f}",
            help="Moyenne de matchs par joueur"
        )
    
    st.markdown("---")
    
    # Graphiques de vue d'ensemble
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 État de la Collection de Données")
        
        # Graphique en barres comparant les différents types de données
        data_types = ['Joueurs BDD', 'Matchs CSV']
        data_counts = [db_stats['player_count'], matches_data['count']]
        colors = ['#FF6B6B', '#4ECDC4']
        
        fig_data = px.bar(
            x=data_types,
            y=data_counts,
            title="Volume de données collectées",
            color=data_types,
            color_discrete_sequence=colors
        )
        fig_data.update_layout(
            yaxis_title="Nombre d'entrées",
            xaxis_title="Type de données",
            showlegend=False
        )
        st.plotly_chart(fig_data, use_container_width=True)
    
    with col2:
        st.subheader("🕒 État des Fichiers")
        
        # Indicateurs visuels pour l'état des fichiers
        file_status_data = []
        
        files_info = [
            ("Base de données joueurs", PLAYER_DB_PATH, db_stats['last_updated'], db_stats['exists']),
            ("Fichier matchs", MATCHS_FILE, matches_data['last_updated'], matches_data['exists']),
        ]
        
        for name, file_path, last_update, exists in files_info:
            if exists and last_update:
                time_diff = datetime.now() - last_update
                if time_diff.days == 0:
                    status_text = f"✅ Actif (il y a {time_diff.seconds // 3600}h)"
                    status_score = 100
                elif time_diff.days < 7:
                    status_text = f"⚠️ Ancien (il y a {time_diff.days}j)"
                    status_score = 70
                else:
                    status_text = f"🔴 Très ancien (il y a {time_diff.days}j)"
                    status_score = 30
            else:
                status_text = "❌ Inexistant"
                status_score = 0
            
            file_status_data.append({
                "Fichier": name,
                "État": status_text,
                "Score": status_score
            })
        
        df_status = pd.DataFrame(file_status_data)
        
        # Graphique en barres horizontales pour l'état des fichiers
        fig_status = px.bar(
            df_status,
            x='Score',
            y='Fichier',
            orientation='h',
            title="État de fraîcheur des données",
            color='Score',
            color_continuous_scale='RdYlGn',
            text='État'
        )
        fig_status.update_layout(
            xaxis_title="Score de fraîcheur",
            yaxis_title="",
            showlegend=False
        )
        fig_status.update_traces(textposition='outside')
        st.plotly_chart(fig_status, use_container_width=True)
    
    # Section d'information système
    st.markdown("---")
    st.subheader("ℹ️ Informations Système")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if matches_data['exists']:
            st.info(f"**Taille fichier matchs:** {matches_data['size_mb']:.2f} MB")
        else:
            st.warning("Fichier matchs introuvable")
    
    with col2:
        if db_stats['exists']:
            db_size = PLAYER_DB_PATH.stat().st_size / (1024 * 1024) if PLAYER_DB_PATH.exists() else 0
            st.info(f"**Taille BDD joueurs:** {db_size:.2f} MB")
        else:
            st.warning("Base de données introuvable")
    
    with col3:
        if db_stats['last_updated']:
            st.info(f"**Dernière mise à jour:** {db_stats['last_updated'].strftime('%d/%m/%Y %H:%M')}")
        else:
            st.warning("Pas de données de mise à jour")
    
    # Suggestions d'amélioration
    if db_stats['player_count'] == 0:
        st.warning("💡 **Suggestion:** Commencez par collecter des données de joueurs avec le script de collecte.")
    elif matches_data['count'] == 0:
        st.warning("💡 **Suggestion:** Collectez des données de matchs pour enrichir l'analyse.")
    elif avg_matches_per_player < 5:
        st.info(f"💡 **Suggestion:** Vous avez {avg_matches_per_player:.1f} matchs par joueur en moyenne. Considérez collecter plus de matchs pour des analyses plus riches.")

def players_management_tab(db_stats):
    """Onglet gestion des joueurs avec fonctionnalités améliorées."""
    st.subheader("👥 Gestion des Joueurs")
    
    if not db_stats['exists'] or db_stats['player_count'] == 0:
        st.warning("Aucun joueur dans la base de données.")
        st.info("💡 Conseil: Exécutez le script de collecte des joueurs pour commencer.")
        return
    
    try:
        # Charger les données des joueurs depuis la BDD
        with sqlite3.connect(PLAYER_DB_PATH) as conn:
            df_players = pd.read_sql_query("SELECT * FROM players", conn)
        
        # Statistiques générales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Joueurs", len(df_players))
        
        with col2:
            if 'updated_at' in df_players.columns:
                try:
                    df_players['updated_at'] = pd.to_datetime(df_players['updated_at'])
                    recent_players = len(df_players[df_players['updated_at'] > datetime.now() - timedelta(days=7)])
                    st.metric("Nouveaux (7j)", recent_players)
                except:
                    st.metric("Nouveaux (7j)", "N/A")
            else:
                st.metric("Nouveaux (7j)", "N/A")
        
        with col3:
            active_players = len(df_players[df_players['match_count'] > 10])
            st.metric("Joueurs Actifs", active_players, help="Plus de 10 matchs")
        
        with col4:
            avg_level = df_players['level'].mean()
            st.metric("Niveau Moyen", f"{avg_level:.1f}")
        
        st.markdown("---")
        
        # Filtres et recherche
        st.subheader("🔍 Filtres et Recherche")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Filtre par nom
            search_name = st.text_input("Rechercher par nom", placeholder="Nom du joueur...")
        
        with col2:
            # Filtre par tier
            available_tiers = ['Tous'] + sorted(df_players['tier'].unique().tolist())
            selected_tier = st.selectbox("Filtrer par rank", available_tiers)
        
        with col3:
            # Filtre par niveau
            level_range = st.slider(
                "Filtre niveau",
                min_value=int(df_players['level'].min()),
                max_value=int(df_players['level'].max()),
                value=(int(df_players['level'].min()), int(df_players['level'].max()))
            )
        
        # Appliquer les filtres
        df_filtered = df_players.copy()
        
        if search_name:
            df_filtered = df_filtered[df_filtered['name'].str.contains(search_name, case=False, na=False)]
        
        if selected_tier != 'Tous':
            df_filtered = df_filtered[df_filtered['tier'] == selected_tier]
        
        df_filtered = df_filtered[
            (df_filtered['level'] >= level_range[0]) & 
            (df_filtered['level'] <= level_range[1])
        ]
        
        st.markdown("---")
        
        # Résultats
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.subheader(f"📋 Liste des joueurs ({len(df_filtered)} résultats)")
            
            if len(df_filtered) > 0:
                # Sélectionner les colonnes importantes
                display_columns = ['name', 'level', 'tier', 'score', 'match_count', 'kills', 'deaths', 'assists']
                available_columns = [col for col in display_columns if col in df_filtered.columns]
                
                # Calcul du ratio K/D pour l'affichage
                df_display = df_filtered[available_columns].copy()
                if 'kills' in df_display.columns and 'deaths' in df_display.columns:
                    df_display['K/D'] = (df_display['kills'] / df_display['deaths'].replace(0, 1)).round(2)
                
                # Renommer les colonnes pour l'affichage
                column_names = {
                    'name': 'Nom',
                    'level': 'Niveau',
                    'tier': 'Rank',
                    'score': 'Score',
                    'match_count': 'Matchs',
                    'kills': 'Kills',
                    'deaths': 'Deaths',
                    'assists': 'Assists'
                }
                
                df_display = df_display.rename(columns=column_names)
                
                # Options de tri
                sort_options = list(df_display.columns)
                sort_by = st.selectbox("Trier par", sort_options, index=sort_options.index('Score') if 'Score' in sort_options else 0)
                sort_ascending = st.checkbox("Tri croissant", value=False)
                
                df_display = df_display.sort_values(sort_by, ascending=sort_ascending)
                
                st.dataframe(df_display, use_container_width=True, hide_index=True)
            else:
                st.warning("Aucun joueur ne correspond aux critères de filtrage.")
        
        with col2:
            st.subheader("📊 Statistiques")
            
            if len(df_filtered) > 0:
                st.metric("Joueurs filtrés", len(df_filtered))
                st.metric("Score max", f"{df_filtered['score'].max():.1f}")
                st.metric("Score min", f"{df_filtered['score'].min():.1f}")
                
                # Distribution des tiers dans le filtre
                if len(df_filtered) > 1:
                    tier_dist = df_filtered['tier'].value_counts()
                    st.write("**Ranks représentés:**")
                    for tier, count in tier_dist.items():
                        percentage = (count / len(df_filtered)) * 100
                        st.write(f"• {tier}: {count} ({percentage:.1f}%)")
            
            # Boutons d'action
            st.markdown("---")
            st.subheader("🔄 Actions")
            
            if st.button("🔄 Rafraîchir les données", key="refresh_players"):
                st.cache_data.clear()
                st.rerun()
            
            if st.button("💾 Exporter CSV", key="export_csv"):
                csv = df_filtered.to_csv(index=False)
                st.download_button(
                    label="📥 Télécharger CSV",
                    data=csv,
                    file_name=f"players_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
    
    except Exception as e:
        st.error(f"Erreur lors du chargement des joueurs: {e}")
        st.error("Vérifiez que la base de données existe et est accessible.")

def players_data_tab(db_stats):
    """Onglet données des joueurs avec visualisations améliorées."""
    
    if not db_stats['exists'] or db_stats['player_count'] == 0:
        st.warning("Aucune donnée de joueur disponible.")
        st.info("💡 Conseil: Exécutez le script de collecte des joueurs pour commencer.")
        return
    
    try:
        with sqlite3.connect(PLAYER_DB_PATH) as conn:
            df_players = pd.read_sql_query("SELECT * FROM players", conn)
        
        if df_players.empty:
            st.warning("Aucun joueur trouvé dans la base de données.")
            return
        
        st.header("📊 Analyse des Données des Joueurs")
        
        # Métriques de résumé
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Joueurs", len(df_players))
        with col2:
            st.metric("Niveau Moyen", f"{df_players['level'].mean():.1f}")
        with col3:
            st.metric("Score Moyen", f"{df_players['score'].mean():.1f}")
        with col4:
            st.metric("Matchs Moyens", f"{df_players['match_count'].mean():.1f}")
        
        st.markdown("---")
        
        # Première ligne de graphiques
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🎯 Distribution des Niveaux")
            fig_level = px.histogram(
                df_players, 
                x='level', 
                nbins=30,
                title="Répartition des niveaux des joueurs",
                color_discrete_sequence=['#FF6B6B']
            )
            fig_level.update_layout(
                xaxis_title="Niveau",
                yaxis_title="Nombre de joueurs",
                showlegend=False
            )
            st.plotly_chart(fig_level, use_container_width=True)
        
        with col2:
            st.subheader("🏆 Répartition des Ranks")
            fig_tier = px.histogram(
                df_players, 
                x='tier',
                title="Répartition des ranks des joueurs",
                color_discrete_sequence=['#4ECDC4']
            )
            fig_tier.update_layout(
                xaxis_title="Rank",
                yaxis_title="Nombre de joueurs",
                showlegend=False
            )
            st.plotly_chart(fig_tier, use_container_width=True)

        # Deuxième ligne de graphiques
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Matchs par Joueur")
            # Filtrer les outliers pour une meilleure visualisation
            q95 = df_players['match_count'].quantile(0.95)
            df_filtered = df_players[df_players['match_count'] <= q95]
            
            fig_matches = px.histogram(
                df_filtered,
                x='match_count',
                nbins=25,
                title=f"Distribution des matchs (95% des joueurs, max: {int(q95)})",
                color_discrete_sequence=['#4ECDC4']
            )
            fig_matches.update_layout(
                xaxis_title="Nombre de matchs",
                yaxis_title="Nombre de joueurs",
                showlegend=False
            )
            st.plotly_chart(fig_matches, use_container_width=True)
        
        with col2:
            st.subheader("💯 Scores des Joueurs")
            fig_score = px.box(
                df_players,
                y='score',
                title="Distribution des scores",
                color_discrete_sequence=['#95E1D3']
            )
            fig_score.update_layout(
                yaxis_title="Score",
                showlegend=False
            )
            st.plotly_chart(fig_score, use_container_width=True)
        
        st.markdown("---")
        
        # Troisième ligne - Statistiques de combat
        st.subheader("⚔️ Statistiques de Combat")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Ratio K/D
            df_players['kd_ratio'] = df_players['kills'] / df_players['deaths'].replace(0, 1)
            fig_kd = px.histogram(
                df_players,
                x='kd_ratio',
                nbins=30,
                title="Distribution du ratio K/D",
                color_discrete_sequence=['#F38BA8']
            )
            fig_kd.update_layout(
                xaxis_title="Ratio Kills/Deaths",
                yaxis_title="Nombre de joueurs",
                showlegend=False
            )
            st.plotly_chart(fig_kd, use_container_width=True)
        
        with col2:
            # Précision des tirs (headshots vs total shots)
            df_players['total_shots'] = df_players['headshots'] + df_players['bodyshots'] + df_players['legshots']
            df_players['headshot_percentage'] = (df_players['headshots'] / df_players['total_shots'].replace(0, 1)) * 100
            
            fig_headshot = px.scatter(
                df_players,
                x='total_shots',
                y='headshot_percentage',
                title="Précision des headshots vs Volume de tir",
                color='level',
                size='match_count',
                hover_data=['name', 'tier']
            )
            fig_headshot.update_layout(
                xaxis_title="Total de tirs",
                yaxis_title="% de headshots",
                coloraxis_colorbar_title="Niveau"
            )
            st.plotly_chart(fig_headshot, use_container_width=True)
        
        # Quatrième ligne - Analyse avancée
        st.markdown("---")
        st.subheader("📈 Analyse Avancée")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Corrélation niveau vs performance
            fig_corr = px.scatter(
                df_players,
                x='level',
                y='score',
                title="Corrélation Niveau vs Score",
                color='tier',
                size='match_count',
                hover_data=['name']
            )
            fig_corr.update_layout(
                xaxis_title="Niveau",
                yaxis_title="Score moyen"
            )
            st.plotly_chart(fig_corr, use_container_width=True)
        
        with col2:
            # Top 10 des joueurs
            st.subheader("🏅 Top 10 Joueurs (Score)")
            top_players = df_players.nlargest(10, 'score')[['name', 'score', 'level', 'tier', 'match_count']]
            top_players['score'] = top_players['score'].round(2)
            st.dataframe(top_players, use_container_width=True, hide_index=True)
    
    except Exception as e:
        st.error(f"Erreur lors du chargement des données des joueurs: {e}")
        st.error("Vérifiez que la base de données existe et contient des données valides.")

def settings_tab(db_stats, matches_data):
    """Onglet paramètres et configuration."""
    st.subheader("⚙️ Paramètres et Configuration")
    
    # Informations sur les fichiers
    st.subheader("📁 Informations sur les Fichiers")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Base de données des joueurs:**")
        st.code(str(PLAYER_DB_PATH))
        if db_stats['exists']:
            file_size = PLAYER_DB_PATH.stat().st_size / (1024 * 1024)
            st.success(f"✅ Existe ({file_size:.2f} MB)")
        else:
            st.error("❌ N'existe pas")
    
    with col2:
        st.write("**Fichier des matchs:**")
        st.code(str(MATCHS_FILE))
        if matches_data['exists']:
            st.success(f"✅ Existe ({matches_data['size_mb']:.2f} MB)")
        else:
            st.error("❌ N'existe pas")
    
    st.markdown("---")
    
    # Actions de maintenance
    st.subheader("🔧 Actions de Maintenance")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🧹 Nettoyer le cache"):
            st.cache_data.clear()
            st.success("Cache nettoyé!")
    
    with col2:
        if st.button("🔄 Recharger la page"):
            st.rerun()
    
    with col3:
        if st.button("📊 Afficher infos système"):
            st.info("Dashboard Valorant v2.0 - Version améliorée")
            st.info(f"Dernière mise à jour: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    st.markdown("---")
    
    # Statistiques avancées
    st.subheader("📈 Statistiques Avancées")
    
    if db_stats['exists'] and db_stats['player_count'] > 0:
        try:
            with sqlite3.connect(PLAYER_DB_PATH) as conn:
                # Statistiques de la base de données
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM players")
                total_players = cursor.fetchone()[0]
                
                cursor.execute("SELECT AVG(score) FROM players")
                avg_score = cursor.fetchone()[0]
                
                cursor.execute("SELECT SUM(match_count) FROM players")
                total_matches_db = cursor.fetchone()[0]
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Joueurs dans BDD", total_players)
                with col2:
                    st.metric("Score moyen global", f"{avg_score:.2f}" if avg_score else "N/A")
                with col3:
                    st.metric("Total matchs (BDD)", total_matches_db or 0)
        
        except Exception as e:
            st.error(f"Erreur lors du calcul des statistiques: {e}")
    
    else:
        st.warning("Aucune donnée disponible pour les statistiques avancées.")

def main():
    """Fonction principale."""
    
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
        
        st.markdown("---")
        st.markdown("**Version:** 2.0 - Améliorée")
        st.markdown("**Dernière modification:** Août 2025")
    
    # Contenu principal
    main_dashboard()

if __name__ == "__main__":
    main()
