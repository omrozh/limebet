import datetime

import requests


def new_odds():
    req1 = requests.get(
        "http://www.goalserve.com/getfeed/b2e41cf452a94ca26dc108dc57bd5b00/getodds/soccer?cat=soccer_10&json=1&date_start=10.04.2024&date_end=10.04.2024&bm=105")

    data = req1.json()

    matches = []

    for i in data.get("scores").get("categories"):
        for c in i.get("matches"):
            match_dictionary = {"MatchID": c.get("id"), "Team1": c.get("localteam").get("name"), "Team2": c.get("visitorteam").get("name"),
                                "League": i.get("name"), "LeagueFlag": "n/a",
                                "DateTime": datetime.datetime.strptime(c.get("formatted_date") + " " + c.get("time"),
                                                                       '%d.%m.%Y %H:%M')}

            odds = []

            for j in c.get("odds"):
                odds.append({
                    "value": j.get("name"),
                    "gameDetails": "",
                    "odds": [
                        {
                            "gameID": "n/a",
                            "value": a.get("name"),
                            "odd": float(a.get("value"))
                        }
                        for a in j.get("bookmakers")[0].get("odds")
                    ]
                })

            match_dictionary["Bets"] = odds

            print(match_dictionary)

            matches.append(match_dictionary)

    return matches
