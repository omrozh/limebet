from selenium import webdriver
from selenium.webdriver.common.by import By

browser = webdriver.Chrome()
browser.get(input("Maçkolik Link: "))
input("proceed")

table_general = browser.find_elements(By.CLASS_NAME, 'Opta-Striped')

# Extend this sprint to enter data automatically.

players_and_points = {}

teams = [input("Team 1: "), input("Team 2: ")]
team_index = -1

for i in table_general:
    formatted_text = i.text.split("\n")
    for c in formatted_text:
        if len(c) > 3:
            try:
                if teams[0] in c or teams[1] in c:
                    team_index += 1
                    continue
                if not int(c.split(" ")[5]) == int(c.split(" ")[-1]):
                    raise ValueError
                players_and_points[teams[team_index] + "&" + c.split(" ")[3]] = int(c.split(" ")[5])
            except Exception as e:
                try:
                    players_and_points[teams[team_index] + "&" + c.split(" ")[2]] = int(c.split(" ")[4])
                except:
                    players_and_points[teams[team_index] + "&" + c.split(" ")[4]] = int(c.split(" ")[6])

browser.find_element(By.XPATH, '//*[@id="widget-opta-match-stats-1"]/div/div/div/div/ul/li[2]').click()

table_general = browser.find_elements(By.CLASS_NAME, 'Opta-Striped')
team_index = -1

for i in table_general:
    formatted_text = i.text.split("\n")
    for c in formatted_text:
        if len(c) > 3:
            try:
                if teams[0] in c or teams[1] in c:
                    team_index += 1
                    continue
                if int(c.split(" ")[6]) < 0:
                    continue
                players_and_points[teams[team_index] + "&" + c.split(" ")[3]] += int(c.split(" ")[6])*15
            except Exception as e:
                try:
                    players_and_points[teams[team_index] + "&" + c.split(" ")[2]] += int(c.split(" ")[5])*15
                except:
                    players_and_points[teams[team_index] + "&" + c.split(" ")[4]] += int(c.split(" ")[7]) * 15

browser.find_element(By.XPATH, '//*[@id="widget-opta-match-stats-1"]/div/div/div/div/ul/li[3]').click()
team_index = -1
table_general = browser.find_elements(By.CLASS_NAME, 'Opta-Striped')

for i in table_general:
    formatted_text = i.text.split("\n")
    for c in formatted_text:
        if len(c) > 3:
            try:
                if teams[0] in c or teams[1] in c:
                    team_index += 1
                    continue
                if int(c.split(" ")[6]) < 0:
                    continue
                players_and_points[teams[team_index] + "&" + c.split(" ")[3]] += int(c.split(" ")[6])*30
                if int(c.split(" ")[4]) < 0:
                    continue
                players_and_points[teams[team_index] + "&" + c.split(" ")[3]] += int(c.split(" ")[4]) * 100
            except Exception as e:
                try:
                    players_and_points[teams[team_index] + "&" + c.split(" ")[2]] += int(c.split(" ")[5]) * 30
                    players_and_points[teams[team_index] + "&" + c.split(" ")[2]] += int(c.split(" ")[3]) * 100
                except:
                    players_and_points[teams[team_index] + "&" + c.split(" ")[4]] += int(c.split(" ")[7]) * 30
                    players_and_points[teams[team_index] + "&" + c.split(" ")[4]] += int(c.split(" ")[5]) * 100

browser.find_element(By.XPATH, '//*[@id="widget-opta-match-stats-1"]/div/div/div/div/ul/li[4]').click()
team_index = -1
table_general = browser.find_elements(By.CLASS_NAME, 'Opta-Striped')

new_table = ""

for i in table_general:
    formatted_text = i.text.split("\n")
    if len(formatted_text) < 3:
        continue
    for c in formatted_text:
        if formatted_text.index(c) % 2 == 0:
            new_table += c + " " + formatted_text[formatted_text.index(c)+1] + "\n"


for c in new_table.split("\n"):
    if len(c) > 3:
        try:
            if teams[0] in c or teams[1] in c:
                team_index += 1
                continue
            if int(c.split(" ")[5]) < 0:
                continue
            players_and_points[teams[team_index] + "&" + c.split(" ")[3]] += int(c.split(" ")[5]) * 20
            if int(c.split(" ")[7]) < 0:
                continue
            players_and_points[teams[team_index] + "&" + c.split(" ")[3]] += int(c.split(" ")[7]) * 20
            if int(c.split(" ")[8]) < 0:
                continue
            players_and_points[teams[team_index] + "&" + c.split(" ")[3]] += int(c.split(" ")[8]) * 15
        except Exception as e:
            try:
                players_and_points[teams[team_index] + "&" + c.split(" ")[2]] += int(c.split(" ")[4]) * 20
                players_and_points[teams[team_index] + "&" + c.split(" ")[2]] += int(c.split(" ")[6]) * 20
                players_and_points[teams[team_index] + "&" + c.split(" ")[2]] += int(c.split(" ")[7]) * 15
            except:
                players_and_points[teams[team_index] + "&" + c.split(" ")[4]] += int(c.split(" ")[6]) * 20
                players_and_points[teams[team_index] + "&" + c.split(" ")[4]] += int(c.split(" ")[8]) * 20
                players_and_points[teams[team_index] + "&" + c.split(" ")[4]] += int(c.split(" ")[9]) * 15

browser.find_element(By.XPATH, '//*[@id="widget-opta-match-stats-1"]/div/div/div/div/ul/li[6]').click()
team_index = -1
table_general = browser.find_elements(By.CLASS_NAME, 'Opta-Striped')

for i in table_general:
    formatted_text = i.text.split("\n")
    for c in formatted_text:
        if len(c) > 3:
            try:
                if teams[0] in c or teams[1] in c:
                    team_index += 1
                    continue
                if int(c.split(" ")[5]) < 0:
                    continue
                players_and_points[teams[team_index] + "&" + c.split(" ")[3]] += int(c.split(" ")[5])*40
                if int(c.split(" ")[6]) < 0:
                    continue
                players_and_points[teams[team_index] + "&" + c.split(" ")[3]] += int(c.split(" ")[6]) * 50
            except Exception as e:
                try:
                    players_and_points[teams[team_index] + "&" + c.split(" ")[2]] += int(c.split(" ")[4]) * 40
                    players_and_points[teams[team_index] + "&" + c.split(" ")[2]] += int(c.split(" ")[5]) * 50
                except:
                    players_and_points[teams[team_index] + "&" + c.split(" ")[4]] += int(c.split(" ")[6]) * 40
                    players_and_points[teams[team_index] + "&" + c.split(" ")[4]] += int(c.split(" ")[7]) * 50

print(players_and_points)
