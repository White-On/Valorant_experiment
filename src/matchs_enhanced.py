from config import MATCHS_FILE, HARD_ITERATION_LIMIT, PLAYER_DB_PATH
from api_utils import APIUtils

import chime
import pandas as pd
from tqdm import tqdm
from rich.console import Console
import sqlite3

console = Console()

def stats_player(matches_list):
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

    extracted = filter(None, (extract(match) for match in tqdm(matches_list, desc="Processing matches", unit="match")))
    stats_df = pd.DataFrame(extracted)

    mean_stats = stats_df.drop(columns='level', errors='ignore').mean(numeric_only=True).to_dict()
    mean_stats['level'] = int(stats_df['level'].max()) if 'level' in stats_df else None
    mean_stats['puuid'] = matches_list[0].get('stats',{}).get('puuid', 'UNKNOWN')
    mean_stats['match_count'] = len(matches_list)
    return mean_stats

def get_db_connection():
    conn = sqlite3.connect(PLAYER_DB_PATH)
    return conn

def add_player_stats_to_db(stats):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO player_stats (puuid, level, tier, score, kills, deaths, assists, headshots, bodyshots, legshots, damage_made, damage_received, match_count)
        VALUES (:puuid, :level, :tier, :score, :kills, :deaths, :assists, :headshots, :bodyshots, :legshots, :damage_made, :damage_received, :match_count)
    ''', stats)
    # Commit the changes and close the connection
    conn.commit()
    conn.close()

def is_player_stats_in_db(puuid):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) FROM player_stats WHERE puuid = ?', (puuid,))
    count = cursor.fetchone()[0]

    conn.close()
    return count > 0

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS player_stats (
            puuid TEXT,
            level INTEGER,
            tier TEXT,
            score FLOAT,
            kills FLOAT,
            deaths FLOAT,
            assists FLOAT,
            headshots FLOAT,
            bodyshots FLOAT,
            legshots FLOAT,
            damage_made FLOAT,
            damage_received FLOAT,
            match_count INTEGER
        )
        ''')
    
    conn.commit()
    conn.close()

def main():
    api_utils = APIUtils()
    init_db()

    # load the matchs file
    if not MATCHS_FILE.exists():
        assert MATCHS_FILE.is_file(), f"File {MATCHS_FILE} does not exist"
    matchs_dataframe = pd.read_csv(MATCHS_FILE, parse_dates=['start_datetime'])

    choosen_matchs = matchs_dataframe.sample(HARD_ITERATION_LIMIT)
    for index, row in choosen_matchs.iterrows():
        console.print(f"Processing match {index + 1}/{len(choosen_matchs)}: {row['match_id']}")

        # get the players PUUIDs from the match
        players_puuid = row.filter(like='_puuid').values.flatten().tolist()
        console.print(f"Players PUUIDs: {players_puuid}")
        
        # loop through the players PUUIDs and get their stats
        
        for puuid in players_puuid:
            if is_player_stats_in_db(puuid):
                tqdm.write(f"Stats for PUUID {puuid} already in database, skipping...")
                continue
            tqdm.write(f"Processing PUUID: {puuid}")
            stored_matchs = api_utils.get_stored_match_from_puuid(puuid, params={"mode":'competitive'})
            
            if stored_matchs is None:
                tqdm.write(f"No stored matches found for PUUID {puuid}")
                continue
            
            matches_list = stored_matchs.get('data', [])
            if not matches_list:
                tqdm.write(f"No matches found for PUUID {puuid}")
                continue
            
            stats = stats_player(matches_list)
            add_player_stats_to_db(stats)

    chime.success()


if __name__ == "__main__":
    main()