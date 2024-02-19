from selenium import webdriver
from selenium.webdriver.common.by import By
import os

browser = webdriver.Chrome()
browser.get(input("Import Team URL: "))
team_name = input("Team name: ")

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
    except IndexError as e:
        try:
            players.append({
                "name": elem[i].text.split("\n")[1].replace(" ", "-").replace("'", "-"),
                "price": float(elem[i].text.split("\n")[4].split(" ")[0])*100 if "mil" in elem[i].text.split("\n")[4] else float(elem[i].text.split("\n")[4].split(" ")[0])/10,
                "team": team_name,
                "image_url": images[i].get_attribute("src")
            })
        except IndexError:
            break

print(str(len(players)) + " athletes added")
for i in players:
    print(f"{i.get('name')}: {i.get('price')}₺")
input("Confirm: ")

os.system(f"python util.py add-team {team_name} {input('Team Image URL: ')}")

for i in players:
    os.system(f"python util.py add-athlete {i.get('name')} {int(i.get('price'))} {i.get('team')}")
    os.system(f"python util.py add-image {i.get('name')} {i.get('image_url')}")
