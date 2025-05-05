import requests
from datetime import datetime
from bs4 import BeautifulSoup

#list of crafting methods with required levels
crafting_methods = [
    {"name": "Spin flax into bowstring", "level": 10},
    {"name": "Cut sapphire", "level": 20},
    {"name": "Make emerald ring", "level": 27},
    {"name": "Blow molten glass into orbs", "level": 46},
    {"name": "Craft fire battlestaff", "level": 63},
    {"name": "Craft air battlestaff", "level": 66},
    {"name": "Craft amulet of glory", "level": 80},
    {"name": "Make black d'hide body", "level": 84},
]

import socket

def notify_success():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(('127.0.0.1', 65432))
            s.sendall(b'Success')
    except Exception as e:
        print(f"Notification failed: {e}")

#fetches item prices based on their ids
def get_item_price(item_id):
    url = f"https://prices.runescape.wiki/api/v1/osrs/latest?id={item_id}"
    headers = {'User-Agent': 'osrs-price-checker-lil-bro/1.0'}

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch price data: {response.status_code}")

    data = response.json()
    return data['data'][str(item_id)]

#finds the difference in price between two items
def compare_item_prices(item1_id, item2_id, item1_name="Item 1", item2_name="Item 2"):
    item1 = get_item_price(item1_id)
    item2 = get_item_price(item2_id)

    item1_price = item1.get('high', 0)
    item2_price = item2.get('high', 0)

    difference = item1_price - item2_price

    print(f"🪙 {item1_name}: {item1_price} gp")
    print(f"🪙 {item2_name}: {item2_price} gp")
    print(f"Price Difference: {abs(difference)} gp ({'Item 1 is more' if difference > 0 else 'Item 2 is more'})")

    return difference

#fetches the users crafting level
def get_crafting_level(username):
    sanitized_username = username.replace(" ", "_")
    url = f"https://secure.runescape.com/m=hiscore_oldschool/index_lite.ws?player={sanitized_username}"
    
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Could not fetch hiscores for '{username}'")
        return None

    lines = response.text.strip().split("\n")

    try:
        crafting_line = lines[13]  # Crafting is the 14th skill (0-based index)
        rank, level, xp = crafting_line.split(",")
        print(f"\n {username.title()}'s Crafting Level: {level}")
        print(f" XP: {int(xp):,}")
        print(f" Rank: {int(rank):,}")
        return int(level)
    except (IndexError, ValueError):
        print("Could not extract crafting data.")
        return None

def get_unlocked_methods(crafting_level):#returns unlocked crafting methods
    return [m["name"] for m in crafting_methods if crafting_level >= m["level"]]

def log_data(username, level, unlocked_methods): #logs data
    with open("crafting_log.txt", "a") as log_file:
        log_file.write(f"\n[{datetime.now()}] Username: {username}, Crafting Level: {level}\n")
        for method in unlocked_methods:
            log_file.write(f" - {method}\n")

def get_all_crafting_methods(user_level): #returns all unlocked crafting methods by scraping the wiki webpage
    url = "https://oldschool.runescape.wiki/w/Crafting"
    headers = {
        "User-Agent": "osrs-crafting-calc/1.0"
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print("Failed to fetch crafting methods.")
        return []

    soup = BeautifulSoup(response.content, "html.parser")
    tables = soup.find_all("table", class_="wikitable")
    methods = []

    for table in tables:
        rows = table.find_all("tr")[1:]  # Skip header row
        for row in rows:
            cols = row.find_all("td")
            if len(cols) >= 3:  # Make sure we have enough columns (level, image, name)
                try:
                    level_required = int(cols[0].text.strip())

                    # Correctly parse item name from the 3rd column
                    link = cols[2].find("a")
                    item_name = link.text.strip() if link else cols[2].text.strip()


                    if level_required <= user_level and item_name:
                        methods.append({
                            "name": item_name,
                            "level": level_required
                        })
                except:

                    continue#silently skip invalid rows

    return methods

def build_item_name_to_id(): #creates a map that associates the item_name with the item_id
    url = "https://prices.runescape.wiki/api/v1/osrs/mapping"
    headers = {"User-Agent": "osrs-crafting-calc/1.0"}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise Exception("Failed to fetch item mapping data.")

    item_map = {}
    for entry in response.json():
        name = entry["name"].lower()
        item_map[name] = entry["id"]

    return item_map

#main of course
def main():
    username = input("Enter RS username: ")
    level = get_crafting_level(username)

    if level is None:
        print(" Could not fetch crafting level.")
        return

    print(f"\n {username.title()}'s Crafting Level: {level}")

    # Get unlocked crafting methods
    unlocked = get_all_crafting_methods(level)

    print(f"\n Crafting Methods Unlocked ({len(unlocked)}):")
    for method in unlocked:
        print(f" - {method['name']} (Level {method['level']})")

    # Log results to file
    log_data(username, level, unlocked)

    # Load item name → ID map
    item_map = build_item_name_to_id()

    # Show GE prices for each unlocked item
    print("\n Current GE Prices for Unlocked Crafting Items:\n")
    for method in unlocked:
        name = method["name"]
        item_id = item_map.get(name.lower())

        if not item_id:
            print(f" No ID found for {name}")
            continue

        try:
            price_data = get_item_price(item_id)
            high_price = price_data.get("high", 0)
            print(f" {name}: {high_price:,} gp")
        except Exception as e:
            print(f" Failed to get price for {name}: {e}")
    notify_success()
if __name__ == "__main__":
    main()