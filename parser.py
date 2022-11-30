import cloudscraper
import re
from dataclasses import dataclass
from bs4 import BeautifulSoup
import datetime
import hashlib
import config
import time




@dataclass
class Match:
    hash_game: str
    championship: str
    time_start_game: str
    day_ago_game: int
    name_at: str
    name_ht: str
    total_score: str
    score: list
    total: str
    url: str



class Parser:
    _scraper = cloudscraper.create_scraper()


    def _get_data(self, url):
        try:
            print(url)
            data = self._scraper.get(url)
            print(data.status_code)
            time.sleep(1)
            return data
        except Exception as err:
            print(err)


    def get_championship(self, path, key) -> str:
        try:
            return path.get(f"{key}").get("name_ch")
        except Exception as err:
            print(err)


    def get_time_start_game(self, path, key, id) -> str:
        try:
            return path.get(f"{key}").get("evts").get(id).get("date_ev_str")
        except Exception as err:
            print(err)


    def get_players(self, path, key, id) -> tuple:
        try:
            name_ht = path.get(f"{key}").get("evts").get(id).get("name_ht")
            name_at = path.get(f"{key}").get("evts").get(id).get("name_at")
            return name_ht, name_at
        except Exception as err:
            print(err)


    def _get_url(self, path, key, id) -> str:
        try:
            link = path.get(f"{key}").get("evts").get(id).get("stat_link")
            if link:
                return f"https://betcity.ru/ru/mstat/{link}"
        except Exception as err:
            print(err)


    def get_score(self, table):
        try:
            if table:
                all_score = table[-1].find("td", class_="score").text.replace(",", "").replace("(", "").replace(")", "").split()
                score = [list(map(int, num.split(":"))) for num in all_score[1:]]
                total_score = str(all_score[0])
                return total_score, score
            else:
                return None, None 
        except Exception as err:
            print(err)


    def _table(self, stats_url):
        try:
            if stats_url:
                stats = self._get_data(stats_url).text
                soup = BeautifulSoup(stats, "html5lib")
                table = soup.find_all("table")
                if table and len(table) >= 5:
                    return table
        except Exception as err:
            print(err)

            
    def get_day_ago_game(self, table) -> int:
        try:
            if table:
                date_last_game = table[-1].find("td", class_="date")
                if date_last_game:
                    date_now = datetime.datetime.today().date()
                    date_last_game = list(map(int, date_last_game.text.split(".")))
                    date_last_game = datetime.datetime(date_last_game[2]+2000, date_last_game[1], date_last_game[0]).date()
                    day_ago_game = (date_now-date_last_game).days
                    return day_ago_game
        except Exception as err:
            print(err)     
        

    def get_total(self, total_score:str, score:list) -> str:
        try:
            if total_score in config.TOTAL_SCORE:
                counttm = 0
                counttb = 0  
                for num in score:
                    if sum(num) >= config.SUM_SCORE_OF_GAME: 
                        counttb += 1
                    else: counttm += 1
                if counttb >= 3 or counttm >= 3:
                    total = "Тм" if counttb >= 3 else "Тб"
                    return total
        except Exception as err:
            print(err)
    
            
    def filter_championship(self, championship_name:str) -> bool:
        try:
            for keyword in config.IN_NAME_CHAMPIONSHIP:
                if re.search(keyword, championship_name) == None:
                    for notkeyword in config.NOT_IN_NAME_CHAMPIONSHIP:
                        if re.search(notkeyword, championship_name) != None:
                            return False
            return True
        except Exception as err:
            print(err)


    def start_parsing(self) -> Match:
        try:   
            main_path = self._get_data("https://ad.betcity.ru/d/on_air/soon").json().get("reply").get("sports").get("46").get("chmps")
            for key in main_path.keys():
                championship = self.get_championship(main_path, key)
                
                if self.filter_championship(championship_name=championship):
                    for id_ in main_path.get(f"{key}").get("evts"):
                        url = self._get_url(main_path, key, id_)
                        table = self._table(url)
                        
                        time_start_game = self.get_time_start_game(main_path, key, id_)
                        day_ago_game = self.get_day_ago_game(table)
                        name_at, name_ht = self.get_players(main_path, key, id_)
                        total_score, score = self.get_score(table)
                        
                        if None not in (championship, url, time_start_game, day_ago_game, name_at, name_ht, score, total_score):
                            text_for_get_hash = f"{championship}{time_start_game}{day_ago_game}{name_at}{name_ht}{total_score}{score}{url}"
                            hash_game = hashlib.md5(text_for_get_hash.encode('utf-8')).hexdigest()
                            total = self.get_total(total_score, score)
                            if total:
                                yield Match(
                                    hash_game,
                                    championship,
                                    time_start_game,
                                    day_ago_game,
                                    name_at,
                                    name_ht,
                                    total_score,
                                    score,
                                    total,
                                    url
                                )
        except Exception as err:
            print(err)

    
    

if __name__ == "__main__":
    for i in Parser().start_parsing():
        print(i)
        
                    
                
                