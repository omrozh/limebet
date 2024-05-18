import datetime
import time

import requests

BASE_URL = "https://fungamess.games/api/v2/kadromilyon"
API_KEY = "e42792aced9806cf74e03a4523949e0f"


def get_providers():
    r = requests.get(f"{BASE_URL}/providersList")
    return r.json()


def get_games(provider_id=None, game_type=None):
    if provider_id:
        r = requests.get(f"{BASE_URL}/gameList?provider={provider_id}")
    elif game_type:
        r = requests.get(f"{BASE_URL}/gameList?type={game_type}")
    else:
        r = requests.get(f"{BASE_URL}/gameList")
    return r.json()


def get_game_iframe(game_id, user_id, user_uuid, demo="true", bonus=None):
    if bonus:
        return f"{BASE_URL}/start?demo={demo}&gameId={game_id}&country=TR&userId={user_id}&token={user_uuid}&lang=tr&bonusName={bonus.bonus.bonus_name}&bonusRounds={bonus.bonus_amount}&bonusBet={bonus.bonus.round_value}&bonusExpired={int(time.time())+3600}"
    else:
        return f"{BASE_URL}/start?demo={demo}&gameId={ game_id }&country=TR&userId={user_id}&token={ user_uuid }&lang=tr"

