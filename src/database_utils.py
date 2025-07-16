"""
Utilitaires pour les opérations de base de données SQLite.
Ce module centralise toutes les opérations liées à la base de données des joueurs.
"""

import pandas as pd
import sqlite3
from pathlib import Path
from rich.console import Console
from config import PLAYER_DB_PATH

console = Console()

class DatabaseManager:
    """
    Gestionnaire pour les opérations de base de données SQLite.
    """
    
    def __init__(self, db_path: Path = PLAYER_DB_PATH):
        """
        Initialise le gestionnaire de base de données.
        
        Args:
            db_path (Path): Chemin vers la base de données SQLite
        """
        self.db_path = db_path
        self.ensure_database_directory()
        if not self.create_players_table():
            console.print(f"[red]Erreur lors de la création de la table dans {self.db_path}[/red]")
    
    def ensure_database_directory(self):
        """Créer le répertoire de la base de données si nécessaire."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
    
    def create_players_table(self) -> bool:
        """
        Crée la table des joueurs si elle n'existe pas déjà.
        
        Returns:
            bool: True si la création est réussie, False sinon
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS players (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        puuid TEXT UNIQUE NOT NULL,
                        level INTEGER NOT NULL,
                        tier TEXT NOT NULL,
                        score FLOAT NOT NULL,
                        kills FLOAT NOT NULL,
                        deaths FLOAT NOT NULL,
                        assists FLOAT NOT NULL,
                        headshots FLOAT NOT NULL,
                        bodyshots FLOAT NOT NULL,
                        legshots FLOAT NOT NULL,
                        damage_made FLOAT NOT NULL,
                        damage_received FLOAT NOT NULL,
                        match_count INTEGER NOT NULL,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                conn.commit()
                return True
                
        except sqlite3.Error as e:
            console.print(f"[red]Erreur lors de la création de la table: {e}[/red]")
            return False
    
    def get_random_players(self, limit: int) -> pd.DataFrame:
        """
        Sélectionne des joueurs aléatoires depuis la base de données.
        
        Args:
            limit (int): Nombre de joueurs à sélectionner
            
        Returns:
            pd.DataFrame: DataFrame contenant les joueurs sélectionnés
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = """
                SELECT name, puuid 
                FROM players 
                ORDER BY RANDOM() 
                LIMIT ?
                """
                
                random_players = pd.read_sql_query(query, conn, params=(limit,))
                
                return random_players
                
        except sqlite3.Error as e:
            console.print(f"[red]Erreur lors de l'accès à la base de données: {e}[/red]")
            return pd.DataFrame()
        except Exception as e:
            console.print(f"[red]Erreur inattendue: {e}[/red]")
            return pd.DataFrame()
    
    def add_player(self, player_data: dict) -> bool:
        """
        Ajoute un joueur à la base de données à partir d'un dictionnaire.

        Args:
            player_data (dict): Dictionnaire contenant les informations du joueur.
                Clés nécessaires:
                - name, puuid, level, tier, score, kills, deaths, assists,
                  headshots, bodyshots, legshots, damage_made, damage_received, match_count

        Returns:
            bool: True si l'ajout est réussi, False sinon
        """
        required_keys = [
            'name', 'puuid', 'level', 'tier', 'score', 'kills', 'deaths', 'assists',
            'headshots', 'bodyshots', 'legshots', 'damage_made', 'damage_received', 'match_count'
        ]
        if not all(key in player_data for key in required_keys):
            console.print("[red]Le dictionnaire ne contient pas toutes les clés requises.[/red]")
            return False

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1 FROM players WHERE puuid = ?", (player_data['puuid'],))
                exists = cursor.fetchone()
                if exists:
                    return False

                cursor.execute("""
                    INSERT INTO players (
                        name, puuid, level, tier, score, kills, deaths, assists,
                        headshots, bodyshots, legshots, damage_made, damage_received, match_count
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    player_data['name'], player_data['puuid'], player_data['level'], player_data['tier'],
                    player_data['score'], player_data['kills'], player_data['deaths'], player_data['assists'],
                    player_data['headshots'], player_data['bodyshots'], player_data['legshots'],
                    player_data['damage_made'], player_data['damage_received'], player_data['match_count']
                ))
                conn.commit()
                return True
        except sqlite3.Error as e:
            console.print(f"[red]Erreur lors de l'ajout du joueur {player_data.get('name')}: {e}[/red]")
            return False

    
    def get_player_count(self) -> int:
        """
        Retourne le nombre total de joueurs dans la base de données.
        
        Returns:
            int: Nombre de joueurs
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM players")
                return cursor.fetchone()[0]
                
        except sqlite3.Error as e:
            console.print(f"[red]Erreur lors du comptage: {e}[/red]")
            return 0
    
    def get_sample_players(self, limit: int = 5) -> pd.DataFrame:
        """
        Retourne un échantillon de joueurs pour affichage.
        
        Args:
            limit (int): Nombre de joueurs à retourner
            
        Returns:
            pd.DataFrame: Échantillon de joueurs
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = "SELECT name, puuid FROM players LIMIT ?"
                return pd.read_sql_query(query, conn, params=(limit,))
                
        except sqlite3.Error as e:
            console.print(f"[red]Erreur lors de la récupération de l'échantillon: {e}[/red]")
            return pd.DataFrame()
    
    def database_exists(self) -> bool:
        """
        Vérifie si la base de données existe et contient des joueurs.
        
        Returns:
            bool: True si la base existe et contient des données
        """
        if not self.db_path.exists():
            return False
        
        return self.get_player_count() > 0
    
    
    def display_database_info(self):
        """
        Affiche des informations sur le contenu de la base de données.
        """
        if not self.db_path.exists():
            console.print(f"[red]La base de données {self.db_path} n'existe pas[/red]")
        
        try:
            total_players = self.get_player_count()
            sample_players = self.get_sample_players()
            
            console.print(f"[blue]Contenu de la base de données:[/blue]")
            console.print(f"[green]- Nombre total de joueurs: {total_players}[/green]")
            
            if not sample_players.empty:
                console.print(f"[blue]- Exemples de joueurs:[/blue]")
                for _, row in sample_players.iterrows():
                    console.print(f"  • {row['name']} ({row['puuid'][:8]}...)")
            else:
                console.print("[yellow]- Aucun joueur dans la base[/yellow]")
                
        except Exception as e:
            console.print(f"[red]Erreur lors de l'affichage: {e}[/red]")
    
    def player_exists(self, puuid: str) -> bool:
        """
        Vérifie si un joueur existe dans la base de données par son PUUID.
        
        Args:
            puuid (str): PUUID du joueur
            
        Returns:
            bool: True si le joueur existe, False sinon
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1 FROM players WHERE puuid = ?", (puuid,))
                return cursor.fetchone() is not None
                
        except sqlite3.Error as e:
            console.print(f"[red]Erreur lors de la vérification de l'existence du joueur: {e}[/red]")
            return False


if __name__ == "__main__":
    # Test rapide du module
    db_manager = DatabaseManager()
    db_manager.display_database_info()
