import datetime
import time

import requests
import sys

from sqlalchemy import text
# api_key = "zHMFjNS3bRu7vNgUrtr6JPMwOD5Jcuer7O9yw9pwNZMX4XBFwe2tazdyQLsq"
api_key = "na"


def get_bettable_matches(date):
    r = requests.get(f"https://www.nosyapi.com/apiv2/service/bettable-matches?apiKey={api_key}&date={date}")
    return r.json()


def get_odds(match_id):
    r = requests.get(
        f'https://www.nosyapi.com/apiv2/service/bettable-matches/details?matchID={match_id}&apiKey={api_key}')
    return r.json()


def get_bets(is_live=False, sport_name="soccer"):
    from cloudbet import get_odds_cloudbet
    return get_odds_cloudbet(is_live=is_live, sport_name=sport_name)


def instant_odds_update(specific_match=None):
    from app import app, db, OpenBet, BetOdd, BetOption, BetCoupon
    with app.app_context():
        from cloudbet import cloudbet_instant_odd_update
        if not specific_match:
            print("Updating odds")
            open_bets = OpenBet.query.filter(OpenBet.bet_ending_datetime < datetime.datetime.now()).all()
            for open_bet in open_bets:
                for option in open_bet.bet_options:
                    for odd in option.bet_odds:
                        cloudbet_instant_odd_update(odd)
            print("Updated odds")
        else:
            open_bet = OpenBet.query.get(specific_match)
            for option in open_bet.bet_options:
                for odd in option.bet_odds:
                    if odd.bettable:
                        cloudbet_instant_odd_update(odd)


def register_open_bet():
    from app import app, db, OpenBet, BetOdd, BetOption, BetCoupon
    sports = ["soccer", "volleyball", "basketball", "tennis", "cricket", "american_football"]
    with app.app_context():
        for sport in sports:
            for i in get_bets(sport_name=sport):
                with app.app_context():
                    if len(OpenBet.query.filter_by(api_match_id=i.get("MatchID")).all()) > 0:
                        continue
                    new_open_bet = OpenBet(
                        api_match_id=i.get("MatchID"),
                        bet_ending_datetime=i.get("DateTime"),
                        match_league=i.get("League"),
                        league_icon_url=i.get("LeagueFlag"),
                        team_1=i.get("Team1"),
                        team_2=i.get("Team2"),
                        has_odds=False,
                        live_betting_expired=False,
                        sport=sport
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
                                value=bet_odd.get("value").replace("Home", new_open_bet.team_1).replace(
                                    "home", new_open_bet.team_1).replace("away", new_open_bet.team_2).replace(
                                    "Away", new_open_bet.team_2).replace("Draw", "Berabere").replace("draw", "berabere"),
                                bet_option_fk=new_bet_option.id,
                                bettable=True,
                                market_url=bet_odd.get("market_url")
                            )
                            db.session.add(new_bet_odd)
                            new_open_bet.has_odds = True
                            db.session.commit()


def get_results(match_id):
    from app import app, db, OpenBet, BetOdd, BetOption, BetCoupon
    with app.app_context():
        r = requests.get(f'https://www.nosyapi.com/apiv2/service/bettable-result?matchID={match_id}&apiKey={api_key}')
        for i in r.json().get("data")[0].get("bettableResult", []):
            game_id = i.get("gameID")

            for c in BetOdd.query.filter_by(game_id=game_id).all():
                c.status = "Başarısız"

            value = i.get("value")
            BetOdd.query.filter_by(game_id=game_id).filter_by(value=value).first().status = "Başarılı"
            db.session.commit()


def live_betting():
    print("Live bet update options")
    from app import app, db, OpenBet, BetOdd, BetOption, BetCoupon
    import datetime

    sports = ["soccer", "volleyball", "basketball", "tennis", "cricket", "american_football"]

    with app.app_context():
        try:
            with db.session.no_autoflush:
                current_time = datetime.datetime.now()

                # Expire open bets and bet odds
                db.session.execute(
                    text("""
                    UPDATE open_bet
                    SET live_betting_expired = TRUE
                    WHERE bet_ending_datetime < :current_time AND live_betting_expired = FALSE
                    """),
                    {"current_time": current_time}
                )
                print("1")

                db.session.execute(
                    text("""
                    UPDATE bet_odd
                    SET bettable = FALSE, bet_option_fk = 0
                    WHERE bet_option_fk IN (
                        SELECT id FROM bet_option WHERE open_bet_fk IN (
                            SELECT id FROM open_bet WHERE live_betting_expired = TRUE
                        )
                    )
                    """)
                )

                print("2")

                db.session.execute(
                    text("""
                    DELETE FROM bet_option
                    WHERE open_bet_fk IN (
                        SELECT id FROM open_bet WHERE live_betting_expired = TRUE
                    )
                    """)
                )

                print("3")

                db.session.commit()

                for sport in sports:
                    for bet in get_bets(is_live=True, sport_name=sport):
                        new_open_bet = OpenBet.query.filter_by(api_match_id=bet.get("MatchID")).first()
                        if not new_open_bet:
                            continue

                        new_bet_options = []
                        new_bet_odds = []

                        for bet_option in bet.get("Bets"):
                            new_bet_option = BetOption(
                                game_name=bet_option.get("gameName"),
                                game_details=bet_option.get("gameDetails"),
                                open_bet_fk=new_open_bet.id
                            )
                            new_bet_options.append(new_bet_option)

                            for bet_odd in bet_option.get("odds"):
                                new_bet_odd = BetOdd.query.filter_by(game_id=bet_odd.get("gameID")).first()
                                if new_bet_odd:
                                    new_bet_odd.odd = bet_odd.get("odd")
                                    new_bet_odd.bettable = True
                                    new_bet_odd.market_url = bet_odd.get("market_url")
                                    new_bet_odd.bet_option_fk = new_bet_option.id
                                else:
                                    new_bet_odd = BetOdd(
                                        game_id=bet_odd.get("gameID"),
                                        odd=bet_odd.get("odd"),
                                        value=bet_odd.get("value").replace("Home", new_open_bet.team_1)
                                        .replace("home", new_open_bet.team_1).replace("away", new_open_bet.team_2)
                                        .replace("Away", new_open_bet.team_2).replace("Draw", "Berabere")
                                        .replace("draw", "berabere"),
                                        bet_option_fk=new_bet_option.id,
                                        bettable=True,
                                        market_url=bet_odd.get("market_url")
                                    )
                                new_bet_odds.append(new_bet_odd)
                        print("Bulk save")
                        db.session.bulk_save_objects(new_bet_options)
                        db.session.bulk_save_objects(new_bet_odds)
                        new_open_bet.live_betting_expired = False
                        print("bulk save end")

                db.session.commit()
        except Exception as e:
            print(f"Error occurred: {e}")

    print("Live bet updated options")


# Integrate distribute_rewards for cloudbet and make it so people should click on the coupon to claim rewards.


def distribute_rewards():
    from app import app, db, OpenBet, BetOdd, BetOption, BetCoupon
    with app.app_context():
        for i in OpenBet.query.filter(
                OpenBet.bet_ending_datetime < datetime.datetime.now() + datetime.timedelta(hours=3)).all():
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


def open_bet_garbage_collector():
    from app import app, db, OpenBet, BetOption
    with app.app_context():
        for i in OpenBet.query.filter(
                OpenBet.bet_ending_datetime < datetime.datetime.now() + datetime.timedelta(hours=12)).all():
            for c in i.bet_options:
                for j in c.bet_odds:
                    db.session.delete(j)
                db.session.delete(c)
            db.session.delete(i)

