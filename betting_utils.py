import datetime

import requests
import sys

#api_key = "zHMFjNS3bRu7vNgUrtr6JPMwOD5Jcuer7O9yw9pwNZMX4XBFwe2tazdyQLsq"
api_key = "na"


def get_bettable_matches(date):
    r = requests.get(f"https://www.nosyapi.com/apiv2/service/bettable-matches?apiKey={api_key}&date={date}")
    return r.json()


def get_odds(match_id):
    r = requests.get(
        f'https://www.nosyapi.com/apiv2/service/bettable-matches/details?matchID={match_id}&apiKey={api_key}')
    return r.json()


def get_bets(is_live=False):
    from cloudbet import get_odds_cloudbet
    return get_odds_cloudbet(is_live=is_live)


def instant_odds_update(specific_match=None):
    from app import app, db, OpenBet, BetOdd, BetOption, BetCoupon
    with app.app_context():
        from cloudbet import cloudbet_instant_odd_update
        if not specific_match:
            open_bets = OpenBet.query.filter(OpenBet.bet_ending_datetime < datetime.datetime.now()).all()
            for open_bet in open_bets:
                for option in open_bet.bet_options:
                    for odd in option.bet_odds:
                        if odd.bettable:
                            cloudbet_instant_odd_update(odd)
        else:
            open_bet = OpenBet.query.get(specific_match)
            for option in open_bet.bet_options:
                for odd in option.bet_odds:
                    if odd.bettable:
                        cloudbet_instant_odd_update(odd)


def register_open_bet():
    from app import app, db, OpenBet, BetOdd, BetOption, BetCoupon
    with app.app_context():
        for i in get_bets():
            with app.app_context():
                new_open_bet = OpenBet(
                    api_match_id=i.get("MatchID"),
                    bet_ending_datetime=i.get("DateTime"),
                    match_league=i.get("League"),
                    league_icon_url=i.get("LeagueFlag"),
                    team_1=i.get("Team1"),
                    team_2=i.get("Team2"),
                    has_odds=False,
                    live_betting_expired=False
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
        print(r.json())
        for i in r.json().get("data")[0].get("bettableResult", []):
            game_id = i.get("gameID")

            for c in BetOdd.query.filter_by(game_id=game_id).all():
                c.status = "Başarısız"

            value = i.get("value")
            BetOdd.query.filter_by(game_id=game_id).filter_by(value=value).first().status = "Başarılı"
            db.session.commit()


def live_betting():
    from app import app, db, OpenBet, BetOdd, BetOption, BetCoupon

    with app.app_context():
        open_bets = OpenBet.query.filter(OpenBet.bet_ending_datetime < datetime.datetime.now()).filter_by(
            live_betting_expired=False).all()
        for i in open_bets:
            i.live_betting_expired = True
            for c in BetOption.query.filter_by(open_bet_fk=i.id):
                for j in BetOdd.query.filter_by(bet_option_fk=c.id):
                    j.bettable = False
                    j.bet_option_fk = 0
                db.session.delete(c)
                db.session.commit()

        for i in get_bets(is_live=True):
            with app.app_context():
                new_open_bet = OpenBet.query.filter_by(api_match_id=i.get("MatchID")).first()
                if not new_open_bet:
                    continue
                for bet_option in i.get("Bets"):
                    new_bet_option = BetOption(
                        game_name=bet_option.get("gameName"),
                        game_details=bet_option.get("gameDetails"),
                        open_bet_fk=new_open_bet.id
                    )
                    db.session.add(new_bet_option)
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
                                value=bet_odd.get("value"),
                                bet_option_fk=new_bet_option.id,
                                bettable=True,
                                market_url=bet_odd.get("market_url")
                            )
                            db.session.add(new_bet_odd)
                        new_open_bet.live_betting_expired = False
                    db.session.commit()

        db.session.commit()


# Integrate distribute_rewards for cloudbet and make it so people should click on the coupon to claim rewards.


def distribute_rewards():
    from app import app, db, OpenBet, BetOdd, BetOption, BetCoupon
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


