import datetime

import requests
from app import app, db, OpenBet, BetOdd, BetOption, BetCoupon
import sys

from cloudbet import get_odds_cloudbet

#api_key = "zHMFjNS3bRu7vNgUrtr6JPMwOD5Jcuer7O9yw9pwNZMX4XBFwe2tazdyQLsq"
api_key = "na"


def get_bettable_matches(date):
    r = requests.get(f"https://www.nosyapi.com/apiv2/service/bettable-matches?apiKey={api_key}&date={date}")
    return r.json()


def get_odds(match_id):
    r = requests.get(
        f'https://www.nosyapi.com/apiv2/service/bettable-matches/details?matchID={match_id}&apiKey={api_key}')
    return r.json()


def get_bets():
    bet_info = []
    return get_odds_cloudbet()
    for c in range(1):
        for i in get_bettable_matches((datetime.datetime.today().date() + datetime.timedelta(days=c)).strftime("%Y-%m-%d")).get("data"):
            bet_odds = get_odds(i.get("MatchID")).get("data")[0]
            bets = bet_odds.get("Bets")
            bet_info.append({
                "MatchID": bet_odds.get("MatchID"),
                "DateTime": bet_odds.get("DateTime"),
                "League": bet_odds.get("League"),
                "LeagueFlag": bet_odds.get("LeagueFlag"),
                "Team1": bet_odds.get("Team1"),
                "Team2": bet_odds.get("Team2"),
                "Bets": [{
                        "gameName": i.get("gameName"),
                        "gameDetails": i.get("gameDetails"),
                        "odds": i.get("odds")
                    } for i in bets]
            })
    return bet_info


def register_open_bet():
    for i in get_bets():
        with app.app_context():
            new_open_bet = OpenBet(
                api_match_id=i.get("MatchID"),
                bet_ending_datetime=i.get("DateTime"),
                match_league=i.get("League"),
                league_icon_url=i.get("LeagueFlag"),
                team_1=i.get("Team1"),
                team_2=i.get("Team2"),
                has_odds=False
            )
            db.session.add(new_open_bet)
            db.session.commit()
            for bet_option in i.get("Bets"):
                new_bet_option = BetOption(
                    game_name=bet_option.get("gameName"),
                    game_details=bet_option.get("gameDetails"),
                    open_bet_fk=new_open_bet.id
                )
                db.session.add(new_bet_option)
                db.session.commit()
                for bet_odd in bet_option.get("odds"):
                    new_bet_odd = BetOdd(
                        game_id=bet_odd.get("gameID"),
                        odd=bet_odd.get("odd"),
                        value=bet_odd.get("value"),
                        bet_option_fk=new_bet_option.id
                    )
                    db.session.add(new_bet_odd)
                    db.session.commit()


def get_results(match_id):
    r = requests.get(f'https://www.nosyapi.com/apiv2/service/bettable-result?matchID={match_id}&apiKey={api_key}')
    print(r.json())
    for i in r.json().get("data")[0].get("bettableResult", []):
        game_id = i.get("gameID")

        for c in BetOdd.query.filter_by(game_id=game_id).all():
            c.status = "Başarısız"

        value = i.get("value")
        BetOdd.query.filter_by(game_id=game_id).filter_by(value=value).first().status = "Başarılı"
        db.session.commit()


if sys.argv[1] == "add-matches":
    register_open_bet()


def distribute_rewards():
    with app.app_context():
        for i in OpenBet.query.filter(OpenBet.bet_ending_datetime < datetime.datetime.now() + datetime.timedelta(hours=3)).all():
            try:
                i.update_results()
                db.session.delete(i)
                db.session.commit()
            except Exception as e:
                pass

        for i in BetCoupon.query.filter_by(status="Oluşturuldu"):
            try:
                i.give_reward()
                i.status = "Tamamlandı"
                db.session.commit()
            except Exception as e:
                pass
