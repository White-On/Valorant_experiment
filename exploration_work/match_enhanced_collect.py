from pathlib import Path
from dotenv import load_dotenv
from tqdm import tqdm

import os
import json
import time
import numpy as np
import requests
import pandas as pd
import rich
import questionary

load_dotenv()

API_KEY = os.getenv("API_KEY")
headers = {"Authorization": API_KEY}

def main():
    pass

if __name__ == "__main__":
    main()