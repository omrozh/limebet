import requests

BASE_URL = "https://fungamess.games/api/v2/kadromilyon"
API_KEY = "e42792aced9806cf74e03a4523949e0f"


def get_providers():
    r = requests.get(f"{BASE_URL}/providersList")
    return r.json()


def get_games():
    r = requests.get(f"{BASE_URL}/gameList?provider=2")
    return r.json()


def get_game_iframe(game_id):
    r = requests.get(f"{BASE_URL}/start?demo=True&gameId={game_id}")
    with open("data.html", "w+") as f:
        f.write(r.text)
    return r.content


print(get_game_iframe(1000891))
