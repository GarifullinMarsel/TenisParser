import sqlite3 
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from config import PATCH_DB


connect = sqlite3.connect(PATCH_DB)
cursor = connect.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS games(
    hash TEXT PRIMARY KEY,
    championship TEXT,
    time_start_game TEXT,
    day_ago_game INTEGER,
    name_at TEXT,
    name_ht TEXT,
    total_score TEXT,
    score TEXT,
    total TEXT,
    url TEXT,
    verification BOOL,
    message_id INTEGER
    )
    """)

connect.commit()