import time

import requests
import json

import datetime


def get_odds_cloudbet():
    with open("cloudbets_readable_json", "r") as language_data:
        language_dictionary = json.loads(language_data.read())

    event_url = f"https://sports-api.cloudbet.com/pub/v2/odds/events?sport=soccer&live=false&limit=1000&from={int(time.time())}&to={int(time.time()+3600*24)}"
    api_key = "eyJhbGciOiJSUzI1NiIsImtpZCI6IkhKcDkyNnF3ZXBjNnF3LU9rMk4zV05pXzBrRFd6cEdwTzAxNlRJUjdRWDAiLCJ0eXAiOiJKV1QifQ.eyJhY2Nlc3NfdGllciI6InRyYWRpbmciLCJleHAiOjIwMjgwNDU1ODksImlhdCI6MTcxMjY4NTU4OSwianRpIjoiYjIxZGRjZGYtZjZmNy00NTg1LWFlZDItOTVhNTkwMmU2YmUxIiwic3ViIjoiMzEyMTg1NDgtY2U3MS00NWJiLTlmNTctNmE4YmI3NTI5NjY2IiwidGVuYW50IjoiY2xvdWRiZXQiLCJ1dWlkIjoiMzEyMTg1NDgtY2U3MS00NWJiLTlmNTctNmE4YmI3NTI5NjY2In0.1e8o2kkX_UEccVndkKZDUS0IER6pFJPaSpIR3dzb486PyfpbFq82UggU6goIj9g7hns8sB1HNV__9U6XXLStE_x2qWDd2ZoFwMTeZeuGyMBFqdUK3Z-GGAg-_uYr3wqRB9QbhHHrS_BXEyTpRoxuGLncY8Yq87XuyfH0KbTAjexJOqd6RoseKGLnkex2mAaCc53CrLJh2ysq8wvLtRAYDxCQQN7eCbhRm58TDjTFZKU49u3kokNy4JuwLgjubcqC7F1ibYXwLMGPYH6kSN2zkApje_kmw3SSpJ3HqXptfdy1bIsV-GvlSXStpFnz7btp2Jj2Dhv4E4Hqclt8bRQRng"

    event_id = 123456
    headers = {
        "accept": "application/json",
        "X-API-Key": api_key,
        "Content-Type": "application/json"
    }

    bets = []

    try:
        response = requests.get(event_url.format(event_id), headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        event_data = response.json()
        data = (json.dumps(event_data, indent=4))
    except requests.exceptions.RequestException as e:
        print("Error:", e)

    for competition in event_data.get("competitions"):
        for event in competition.get("events"):
            match = {
                "MatchID": event.get("id"),
                "DateTime": datetime.datetime.strptime(event.get("cutoffTime"), "%Y-%m-%dT%H:%M:%SZ") + datetime.timedelta(hours=3),
                "League": competition.get("name"),
                "LeagueFlag": "n/a",
                "Team1": event.get("home").get("name"),
                "Team2": event.get("away").get("name"),
            }
            odds = []
            for market in event.get("markets").keys():
                submarkets = event.get("markets").get(market).get("submarkets")
                selections = []
                for submarket in list(submarkets.keys()):
                    for selection in submarkets.get(submarket).get("selections"):
                        selections.append(selection)
                odds.append(
                    {
                        "gameName": language_dictionary.get(market).get("Name"),
                        "gameDetails": "",
                        "odds": [{
                            "gameID": "tbd",
                            "value": selection.get("outcome").replace("_", "/").replace("=", ": ").capitalize() + str(" | " if len(selection.get("params").replace("=", ": ")) > 3 else "") + selection.get("params").replace("=", ": "),
                            "odd": float(selection.get("price"))
                        } for selection in selections]
                    }
                )

            match["Bets"] = odds
            bets.append(match)

    return bets
# TO DO: Test bets and odds. FYI, change timestamps for end and start tomorrow.
# TO DO: Implement submarkets.
