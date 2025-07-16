from pathlib import Path
import datetime

# data file path
DATA_FILE = Path(__file__).parents[1] / "data"

# Hard limit for iterations to avoid infinite loop
HARD_ITERATION_LIMIT = 10

# Matchs file path
MATCHS_FILE = DATA_FILE / "matchs.csv"

# expiration limit for the matchs in the file (a month)
MATCHS_EXPIRATION_LIMIT = datetime.datetime.now() - datetime.timedelta(days=30)

# Matchs enhanced file path
MATCHS_ENHANCED_FILE = DATA_FILE / "matchs_enhanced.csv"

# Path to the SQLite player database
PLAYER_DB_PATH = DATA_FILE / "player_stats.db"