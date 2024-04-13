from selenium import webdriver
from selenium.webdriver.common.by import By
import os

browser = webdriver.Chrome()
file = open("team-import", "r")
data = file.read()

for c in data.split("\n"):
    browser.get(c.split(" ")[0])
    input("Proceed? ")
    team_name = c.split(" ")[1]

    elem = browser.find_elements(By.CLASS_NAME, 'odd')
    elem2 = browser.find_elements(By.CLASS_NAME, 'even')

    elem = zip(elem, elem2)

    elem = [item for pair in elem for item in pair]

    images = browser.find_elements(By.CLASS_NAME, "bilderrahmen-fixed")

    elem.extend(elem2)

    players = []

    for i in range(len(elem)):
        try:
            players.append({
                "name": elem[i].text.split("\n")[1].replace(" ", "-").replace("'", "-"),
                "price": float(elem[i].text.split("\n")[3].split(" ")[4])*100 if "mil" in elem[i].text.split("\n")[3].split(" ")[5] else elem[i].text.split("\n")[3].split(" ")[4],
                "team": team_name,
                "image_url": images[i].get_attribute("src")
            })
        except:
            try:
                players.append({
                    "name": elem[i].text.split("\n")[1].replace(" ", "-").replace("'", "-"),
                    "price": float(elem[i].text.split("\n")[4].split(" ")[0])*100 if "mil" in elem[i].text.split("\n")[4] else float(elem[i].text.split("\n")[4].split(" ")[0])/10,
                    "team": team_name,
                    "image_url": images[i].get_attribute("src")
                })
            except:
                try:
                    players.append({
                        "name": elem[i].text.split("\n")[1].replace(" ", "-").replace("'", "-"),
                        "price": 100,
                        "team": team_name,
                        "image_url": images[i].get_attribute("src")
                    })
                except:
                    break

    print(str(len(players)) + " athletes added")
    for i in players:
        print(f"{i.get('name')}: {i.get('price')}₺")
    input("Confirm: ")

    os.system(f"python util.py add-team {team_name}")

    for i in players:
        os.system(f"python util.py add-athlete {i.get('name')} {int(i.get('price'))} {i.get('team')}")

