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


def get_game_iframe(game_id):
    r = requests.get(f"{BASE_URL}/start?demo=true&gameId={game_id}")
    with open("data.html", "w+") as f:
        f.write(r.text)
    return r.content


print(get_games("1"))
