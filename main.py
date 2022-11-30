from parser import Parser, Match
import config
from parser import Match
import telebot
from DataBase.db import DataBase
import schedule
import time



BOT = telebot.TeleBot(config.TOKEN)

def edit_message(match:Match, message_id:int, verification:str, new_score:str, db:DataBase):
    try:
        message = f"""
Лига: {match.championship}
{match.name_at} vs {match.name_ht}
Начало игры: {match.time_start_game}
{match.total} {verification}
С 1 по 3 партию
{match.url}
{", ".join([":".join(list(map(str, i))) for i in new_score])}
"""
        BOT.edit_message_text(message, config.PEER_ID, message_id)
        time.sleep(config.DELAY_BETWEEN_API_REQUESTS)
        db.verification_confirmation(match.hash_game, True)
    except Exception as err:
        print(err)
    

        
def check_strategy(db:DataBase):
    try:
        parser = Parser()
        for game in db.get_unverified_games():
            match = Match(
                game[0],
                game[1],
                game[2],
                game[3],
                game[4],
                game[5],
                game[6],
                game[7],
                game[8],
                game[9],
            )

            stat_url = match.url
            table = parser._table(stat_url)
            last_game = parser.get_day_ago_game(table)
            print(last_game)
            
            if isinstance(last_game, int) and last_game <= 0:
                print("edit message!")
                new_score = parser.get_score(table)[1]
                
                for score_of_party in new_score[0:2]:
                    if (sum(score_of_party) <= config.SUM_SCORE_OF_GAME + 0.5 and match.total == "Тм") or (sum(score_of_party) >= config.SUM_SCORE_OF_GAME - 0.5 and match.total == "Тб"):
                        edit_message(match=match, message_id=game[11], verification="✅", new_score=new_score, db=db)
                    else:
                        edit_message(match=match, message_id=game[11], verification="❌", new_score=new_score, db=db)

    except Exception as err:
        print(err)


        
def main():
    try:
        parser = Parser()
        base = DataBase(config.PATCH_DB)
        for stats_match in parser.start_parsing():
            print(stats_match)
            if stats_match.day_ago_game <= config.DAY_AGO and stats_match.total_score in config.TOTAL_SCORE and stats_match.total:
                text = f"""
Лига: {stats_match.championship}
{stats_match.name_at} vs {stats_match.name_ht}
Начало игры: {stats_match.time_start_game}
{stats_match.total}
{stats_match.url}
"""
                if  not base.game_on_table(stats_match):
                    result = BOT.send_message(config.PEER_ID, text=text)
                    print("send message!")
                    time.sleep(config.DELAY_BETWEEN_API_REQUESTS)
                    base.entry_message_id(stats_match.hash_game, result.message_id)
        check_strategy(db=base)
        print("Finished! Waiting for more...")
    except Exception as err:
        print(err)

        

def timer(minutes:int):
    schedule.every().hours.do(main)
    while True:
        schedule.run_pending()
        time.sleep(1)


        


if __name__ == "__main__":
    print("Bot is ranning!")
    main()
    timer(config.DELAY)