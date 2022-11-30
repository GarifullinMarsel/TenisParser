import sqlite3 
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from parser import Match





class DataBase:
    def __init__(self, patch_db:str) -> None:
        self.connect = sqlite3.connect(patch_db)
        self.cursor = self.connect.cursor()
    
    def __del__(self):
        self.cursor.close()
        self.connect.close()
        

    def _new_game_recording(self, match:Match) -> None:
        score = ""
        for i in match.score:
            score += f"({i})"

        self.cursor.execute("""
        INSERT INTO games (
            hash,
            championship,
            time_start_game,
            day_ago_game,
            name_at,
            name_ht,
            total_score,
            score,
            total,
            url,
            verification
        ) 
        VALUES(?,?,?,?,?,?,?,?,?,?,?);""",(
        match.hash_game,
        match.championship, 
        match.time_start_game,
        match.day_ago_game,
        match.name_at, 
        match.name_ht, 
        match.total_score, 
        score,
        match.total,
        match.url,
        False
    )
)
        self.connect.commit()
        


    def game_on_table(self, match:Match) -> bool:
        info = self.cursor.execute('SELECT * FROM games WHERE hash = ?', (match.hash_game,))
        if info.fetchone(): 
            self._new_game_recording(match)
            return False
        else:
            return True

    
    def entry_message_id(self, hash_game:str, message_id:int) -> None:
        self.cursor.execute(f"UPDATE games SET message_id = ? WHERE hash = ?", (message_id, hash_game))
        self.connect.commit()

    
    def get_unverified_games(self):
        return self.cursor.execute("SELECT * FROM games WHERE verification = FALSE").fetchall()


    def verification_confirmation(self, hash_game, verification):
        self.cursor.execute(f"UPDATE games SET verification = ? WHERE hash = ?", (verification, hash_game))
        self.connect.commit()
