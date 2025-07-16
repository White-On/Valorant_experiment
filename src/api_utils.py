from dotenv import load_dotenv

import os
import requests
import time
import rich



class APIUtils:
    def __init__(self):
        load_dotenv()
        self.API_KEY = os.getenv("API_KEY")
        self.headers = {"Authorization": self.API_KEY}
        self.timeout = 60  # Default timeout for requests in seconds
    
    def get_matchlist_from_player_name(self, player_name, nb_retry=3, **kwargs):
        url = f"https://api.henrikdev.xyz/valorant/v3/matches/eu/{player_name}/EUW"
        for attempt in range(nb_retry):
            try:
                response = requests.get(url, headers=self.headers, **kwargs)
                response.raise_for_status()  # Raise an error for bad responses
                return response.json()
            except requests.exceptions.RequestException as e:
                if attempt == nb_retry - 1:
                    print(f"Failed to retrieve matchlist for {player_name} after {nb_retry} attempts: {e}")
                    return None
                time.sleep(self.timeout)  # Wait before retrying
            
        

    def get_matchlist_from_puuid(self, puuid, nb_retry=3, **kwargs):
        url = f"https://api.henrikdev.xyz/valorant/v3/by-puuid/matches/eu/{puuid}"
        for attempt in range(nb_retry):
            try:
                response = requests.get(url, headers=self.headers, **kwargs)
                response.raise_for_status()  # Raise an error for bad responses
                return response.json()
            except requests.exceptions.RequestException as e:
                if attempt == nb_retry - 1:
                    print(f"Failed to retrieve matchlist for PUUID {puuid} after {nb_retry} attempts: {e}")
                    return None
                time.sleep(self.timeout)  # Wait before retrying
    
    def get_stored_match_from_puuid(self, puuid, nb_retry=3, **kwargs):
        url = f"https://api.henrikdev.xyz/valorant/v1/by-puuid/stored-matches/eu/{puuid}"
        for attempt in range(nb_retry):
            try:
                response = requests.get(url, headers=self.headers, **kwargs)
                response.raise_for_status()  # Raise an error for bad responses
                return response.json()
            except requests.exceptions.RequestException as e:
                if attempt == nb_retry - 1:
                    print(f"Failed to retrieve stored matches for PUUID {puuid} after {nb_retry} attempts: {e}")
                    return None
                time.sleep(self.timeout)  # Wait before retrying
    
    def retrieve_competitive_stored_matches(self, puuid, nb_retries=3):
        url = f"https://api.henrikdev.xyz/valorant/v1/by-puuid/stored-matches/eu/{puuid}"

        for attempt in range(nb_retries):
            try:
                response = requests.get(url, headers=self.headers, params={"mode":'competitive'})
                response.raise_for_status()  # Raise an error for bad responses
                break  # Exit loop if request is successful
            except requests.exceptions.RequestException as e:
                # print(f"Attempt {attempt + 1} failed for PUUID {puuid}: {e}")
                if attempt == nb_retries - 1:
                    raise
                time.sleep(self.timeout)  # Wait before retrying # Wait before retrying
        data = response.json()
        return data