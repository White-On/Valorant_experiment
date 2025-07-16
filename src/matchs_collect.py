from config import MATCHS_FILE, HARD_ITERATION_LIMIT, MATCHS_EXPIRATION_LIMIT
from api_utils import APIUtils
from database_utils import DatabaseManager

import pandas as pd
import time
from tqdm import tqdm
from rich.console import Console
from datetime import datetime

console = Console()

def simplify_match_metadata(*matchs:list[dict])-> list[dict]:
    # ['is_available', 'metadata', 'players', 'observers', 'coaches', 'teams', 'rounds', 'kills']
    cleaned_matchs = []
    date_format = '%A, %B %d, %Y %I:%M %p'
    for match in matchs:
        if match["is_available"] == False:
            continue
        match_data = match['metadata']
        winner_team = match['teams']
        team_blue = match['players']['blue']
        team_red = match['players']['red']
        summarized_match = {
            "match_id": match_data.get("matchid"),
            "start_datetime": datetime.strptime(match_data.get("game_start_patched"), date_format),
            "winner_team": 'red' if winner_team and winner_team.get('red', {}).get('has_won') else 'blue',
        }
        for i, player in enumerate(team_blue):
            summarized_match[f'blue_{i}_name'] = player['name']
            summarized_match[f'blue_{i}_puuid'] = player['puuid']

        for i, player in enumerate(team_red):
            summarized_match[f'red_{i}_name'] = player['name']
            summarized_match[f'red_{i}_puuid'] = player['puuid']  

        cleaned_matchs.append(summarized_match)

    return cleaned_matchs


def main():
    api_utils = APIUtils()

    # Charger le DataFrame des matchs existants
    matchs_dataframe = pd.read_csv(MATCHS_FILE, parse_dates=['start_datetime']) if MATCHS_FILE.exists() else pd.DataFrame()

    # Sélectionner des joueurs aléatoires depuis la base de données SQL avec fallback automatique
    console.print(f"[blue]Selecting random players from the database...[/blue]")

    db_manager = DatabaseManager()
    random_players_name = db_manager.get_random_players(HARD_ITERATION_LIMIT)
    
    # Vérifier qu'on a bien des joueurs à traiter
    if random_players_name.empty:
        console.print("[red]No players found in the database! Exiting...[/red]")
        return

    for idx, player_data in tqdm(random_players_name.iterrows(), desc="Collecting matches", unit="match", ncols=100, total=random_players_name.shape[0]):
        request_match = api_utils.get_matchlist_from_puuid(player_data['puuid'], params={"mode":'competitive'})

        # if the request failed, the player is not in the game anymore
        # TODO : add a removal of the player from the dataframe or a retry mechanism
        if request_match is None:
            tqdm.write(f"No match found for player {player_data['name']} ({player_data['puuid']})")
            continue

        if "errors" in request_match.keys():
            if request_match["errors"][0]["code"] == 0:
                tqdm.write(f"API call limit reached, Waiting for 60s before retrying")
                time.sleep(60)
            else:
                tqdm.write(f"Error: {request_match['errors'][0]['message']}")
            continue

        request_match_status = request_match.get('status', None)
        if request_match_status != 200:
            # print(f'Error in iteration {idx}, Error code: {request_match_status} : {request_match.get("status", "Unknown")}')
            tqdm.write(f'Error in iteration {idx}, Error code: {request_match_status} : {request_match.get("status", "Unknown")}')
            continue
        currated_matchs_list = simplify_match_metadata(*request_match['data'])
        # add the matchs to the dataframe
        matchs_dataframe = pd.concat([matchs_dataframe, pd.DataFrame(currated_matchs_list)], ignore_index=True)

    # clean the dataframe of duplicates
    matchs_dataframe = matchs_dataframe.drop_duplicates(subset="match_id")
    # remove matchs that are older than the expiration limit
    matchs_dataframe = matchs_dataframe[matchs_dataframe['start_datetime'] > MATCHS_EXPIRATION_LIMIT]
    # save the matchs dataframe to a csv file
    matchs_dataframe.to_csv(MATCHS_FILE, index=False)
    # display statistics
    nb_matchs_after = len(matchs_dataframe)
    
    console.print(f"[green]Collecting matchs completed![/green] Total matchs collected: {nb_matchs_after}")

    # save the matchs dataframe
    matchs_dataframe.to_csv(MATCHS_FILE, index=False)
        


if __name__ == "__main__":
    main()
