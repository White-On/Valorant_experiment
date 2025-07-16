from pathlib import Path
from dotenv import load_dotenv

import os
import requests
import json
import pandas as pd
import time

load_dotenv()

API_KEY = os.getenv("API_KEY")
headers = {"Authorization": API_KEY}
players_name_file = Path("players_name.csv")
HARD_INTERACTION_LIMIT = 200


def get_matchlist_from_player_name(player_name, **kwargs):
    url = f"https://api.henrikdev.xyz/valorant/v3/matches/eu/{player_name}/EUW"
    try:
        response = requests.get(url, headers=headers, **kwargs)
        return response.json()
    except Exception as e:
        print(e)
        return None


def get_matchlist_from_puuid(puuid, **kwargs):
    url = f"https://api.henrikdev.xyz/valorant/v3/by-puuid/matches/eu/{puuid}"
    try:
        response = requests.get(url, headers=headers, **kwargs)
        return response.json()
    except Exception as e:
        print(e)
        return None


def get_players_name_in_match(*matchs):
    players = []
    for match in matchs:
        if "players" not in match:
            continue
        for player in match["players"]["all_players"]:
            players.append(player["name"])
    return players


def get_player_dict_in_match(*matchs):
    players = {}
    for match in matchs:
        if "players" not in match:
            continue
        for player in match["players"]["all_players"]:
            players[player["name"]] = player["puuid"]
    return players


def simplify_match_metadata(*matchs):
    cleaned_matchs = []
    # ['is_available', 'metadata', 'players', 'observers', 'coaches', 'teams', 'rounds', 'kills']
    for match in matchs:
        if match["is_available"] == False:
            continue
        cleaned_match = match.copy()

        cleaned_match.pop("is_available", None)
        cleaned_match.pop("observers", None)
        cleaned_match.pop("coaches", None)
        cleaned_match.pop("rounds", None)
        cleaned_match.pop("kills", None)

        cleaned_matchs.append(cleaned_match)
    return cleaned_matchs


def extend_json(json_file, values):
    try:
        with open(json_file, "r") as f:
            existing_data = json.load(f)
    except FileNotFoundError:
        existing_data = []

    existing_data.extend(values)

    with open(json_file, "w") as f:
        json.dump(existing_data, f, indent=4)


def main():
    if not players_name_file.exists():
        print(f"file {players_name_file} not found")
        return
    df = pd.read_csv(players_name_file)
    match_file = 'matchs7.json'
    matchs_list = []

    for idx in range(1, HARD_INTERACTION_LIMIT):
        random_player_puuid = df.sample(1)['puuid'].values[0]
        print(f'iteration {idx}')
        request_match = get_matchlist_from_puuid(random_player_puuid, params={"mode":'competitive'})
        if request_match is None:
            print(f'Error in iteration {idx}')
            break
        if 'errors' in request_match.keys():
            print(f'Error in iteration {idx}, Error : {request_match["errors"]}')
            if request_match["errors"][0]['code'] == 0:
                print(f"API call limit reached, Waiting for 60s before retrying")
                time.sleep(60)
                continue
        request_match_status = request_match.get('status', None)
        if request_match_status != 200:
            print(f'Error in iteration {idx}, Error code: {request_match["status"]}')
            break
        matchs_list.extend(simplify_match_metadata(*request_match['data']))
        
        if idx % 5 == 0:
            extend_json(match_file, matchs_list)
            matchs_list = []
            print(f'Quick break to avoid API call limit')
            time.sleep(60)


    extend_json(match_file, matchs_list)


if __name__ == "__main__":
    main()
