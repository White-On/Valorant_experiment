from config import HARD_ITERATION_LIMIT
from api_utils import APIUtils
from database_utils import DatabaseManager, get_random_players_with_fallback

import chime
import pandas as pd
import time
from tqdm import tqdm
from rich.console import Console

console = Console()

def get_player_dict_in_match(*matchs):
    players = []
    for match in matchs:
        if "players" not in match:
            continue
        for player in match["players"]["all_players"]:
            players.append({"name": player["name"], "puuid": player["puuid"]})
    return players


def main():
    api_utils = APIUtils()
    db_manager = DatabaseManager()

    # Créer la table des joueurs si elle n'existe pas
    db_manager.create_players_table()

    # Obtenir le nombre de joueurs avant la collecte
    nb_players_before = db_manager.get_player_count()
    console.print(f'[blue]Nombre de joueurs avant la collecte : {nb_players_before}[/blue]')

    # Sélectionner des joueurs aléatoires depuis la base de données (avec fallback CSV si nécessaire)
    console.print(f'[blue]Sélection de {HARD_ITERATION_LIMIT} joueurs aléatoires...[/blue]')
    random_players_name = get_random_players_with_fallback(HARD_ITERATION_LIMIT)
    
    if random_players_name.empty:
        console.print('[red]Aucun joueur trouvé pour la collecte. Arrêt du programme.[/red]')
        return

    console.print(f'[green]Collecte de nouveaux joueurs depuis {len(random_players_name)} joueurs de base...[/green]')

    # Collecter les nouveaux joueurs
    new_players_added = 0
    
    # Itérer sur les joueurs aléatoires et obtenir leur historique de matchs
    for _, player_data in tqdm(random_players_name.iterrows(), total=random_players_name.shape[0], 
                              desc="Collecte des nouveaux joueurs", unit="joueur", ncols=100):
        request_match = api_utils.get_matchlist_from_puuid(player_data["puuid"])
        
        # Si la requête a échoué, le joueur n'est plus dans le jeu
        if request_match is None:
            tqdm.write(f"[yellow]Aucun match trouvé pour {player_data['name']} ({player_data['puuid']})[/yellow]")
            continue

        if "errors" in request_match.keys():
            if request_match["errors"][0]["code"] == 0:
                tqdm.write(f"[red]Limite d'appels API atteinte, attente de 60s...[/red]")
                time.sleep(60)
            else:
                tqdm.write(f"[red]Erreur: {request_match['errors'][0]['message']}[/red]")
            continue
        
        request_match_status = request_match.get("status", None)
        if request_match_status != 200:
            tqdm.write(f"[red]Code d'erreur: {request_match['status']}[/red]")
            continue
            
        matchs_list = request_match["data"]
        
        # Obtenir les noms des joueurs dans les matchs 
        players_name_in_match = get_player_dict_in_match(*matchs_list)
        
        # Ajouter les nouveaux joueurs à la base de données
        for player_info in players_name_in_match:
            if db_manager.add_player(player_info["name"], player_info["puuid"]):
                new_players_added += 1
        
    # Afficher les statistiques
    nb_players_after = db_manager.get_player_count()
    console.print(f'[green]Nombre de nouveaux joueurs ajoutés : {new_players_added}[/green]')
    console.print(f'[blue]Total de joueurs dans la base : {nb_players_after}[/blue]')
    console.print(f'[cyan]Croissance : {nb_players_before} → {nb_players_after}[/cyan]')
    
    chime.success()


if __name__ == "__main__":
    main()
