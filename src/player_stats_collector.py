"""
Script de collecte des statistiques des joueurs Valorant.
Ce script utilise la base de données SQLite pour stocker et récupérer les joueurs,
puis collecte leurs statistiques détaillées.
"""

from config import MATCHS_FILE
from api_utils import APIUtils
from database_utils import DatabaseManager

import chime
import pandas as pd
import time
from tqdm import tqdm
from rich.console import Console

console = Console()
chime.theme('pokemon')

def collect_player_stats(api_utils: APIUtils, player_data: dict) -> dict:
    """
    Collecte les statistiques détaillées d'un joueur.
    
    Args:
        api_utils (APIUtils): Instance de l'utilitaire API
        player_data (dict): Données du joueur avec 'name' et 'puuid'
        
    Returns:
        dict: Statistiques du joueur ou None si erreur
    """
    def extract(match):
        stats = match.get('stats')
        if not stats:
            tqdm.write(f"No stats found for match with PUUID {match.get('puuid', 'UNKNOWN')}")
            return None

        shots = stats.get('shots', {})
        damage = stats.get('damage', {})

        return {
            'level': stats.get('level'),
            'tier': stats.get('tier'),
            'score': stats.get('score'),
            'kills': stats.get('kills'),
            'deaths': stats.get('deaths'),
            'assists': stats.get('assists'),
            'headshots': shots.get('head'),
            'bodyshots': shots.get('body'),
            'legshots': shots.get('leg'),
            'damage_made': damage.get('made'),
            'damage_received': damage.get('received'),
        }
    try:
        # Ici vous pouvez ajouter d'autres appels API pour récupérer des stats spécifiques
        # Par exemple: MMR, statistiques détaillées, historique, etc.
        
        # Pour l'instant, on récupère l'historique des matchs
        request_match = api_utils.retrieve_competitive_stored_matches(player_data["puuid"])
        
        if request_match is None:
            return None
            
        if "errors" in request_match.keys():
            return None
            
        if request_match.get("status", None) != 200:
            return None
            
        matchs_list = request_match["data"]

        extracted = filter(None, (extract(match) for match in matchs_list))
        stats_df = pd.DataFrame(extracted)

        mean_stats = stats_df.drop(columns='level', errors='ignore').mean(numeric_only=True).to_dict()
        mean_stats['level'] = int(stats_df['level'].max()) if 'level' in stats_df else None
        mean_stats['puuid'] = matchs_list[0].get('stats',{}).get('puuid', 'UNKNOWN')
        mean_stats['match_count'] = len(matchs_list)
        mean_stats['name'] = player_data.get('name', 'Unknown Player')
        return mean_stats
        
    except Exception as e:
        console.print(f"[red]Erreur lors de la collecte des stats pour {player_data['name']}: {e}[/red]")
        return None


def main():
    """
    Fonction principale pour la collecte des statistiques des joueurs.
    """
    console.print("[bold blue]=== Collecte des statistiques des joueurs Valorant ===[/bold blue]")
    
    api_utils = APIUtils()
    db_manager = DatabaseManager()

    # Obtenir le nombre de joueurs dans la base
    nb_players_total = db_manager.get_player_count()
    console.print(f'[blue]Nombre total de joueurs dans la base : {nb_players_total}[/blue]')

    # Sélectionner de matches aléatoires pour collecter leurs stats
    list_matchs = pd.read_csv(MATCHS_FILE, parse_dates=['start_datetime']) if MATCHS_FILE.exists() else pd.DataFrame()
    if list_matchs.empty:
        console.print("[red]Aucun match trouvé dans le fichier CSV[/red]")
        return

    players_list = pd.DataFrame({
        "name": list_matchs['blue_0_name'].tolist() + list_matchs['red_0_name'].tolist(),
        "puuid": list_matchs['blue_0_puuid'].tolist() + list_matchs['red_0_puuid'].tolist()
    }).drop_duplicates()

    console.print(f'[green]Collecte des statistiques pour {len(players_list)} joueurs...[/green]')

    # Collecter les statistiques
    successful_collections = 0
    
    for _, player_data in tqdm(players_list.iterrows(), total=len(players_list), 
                              desc="Collecte des statistiques", unit="joueur", ncols=100):
        # if the player is already in the database, skip
        if db_manager.player_exists(player_data["puuid"]):
            tqdm.write(f"Joueur {player_data['name']} ({player_data['puuid']}) déjà dans la base, saut de la collecte")
            continue

        # Collecter les statistiques du joueur
        tqdm.write(f"Collecte des stats pour {player_data['name']} ({player_data['puuid']})...")
        stats = collect_player_stats(api_utils, player_data.to_dict())

        # Sauvegarder les statistiques collectées dans la base de données
        if stats:
            successful_collections += 1
            db_manager.add_player(stats)
        else:
            tqdm.write(f"Échec de la collecte des stats pour {player_data['name']}")
        # Petite pause pour éviter de surcharger l'API
        time.sleep(0.5)
            
    console.print(f"[bold green]Collecte terminée : {successful_collections} joueurs traités avec succès[/bold green]")
    chime.success()

if __name__ == "__main__":
    main()
