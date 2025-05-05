import requests
from datetime import datetime

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

def log_data(username, level, unlocked_methods):
    with open("crafting_log.txt", "a") as log_file:
        log_file.write(f"\n[{datetime.now()}] Username: {username}, Crafting Level: {level}\n")
        for method in unlocked_methods:
            log_file.write(f" - {method}\n")

#main of course
def main():
    username = input("Enter RS username: ")
    level = get_crafting_level(username)

    if level is not None:
        print(f"\n {username.title()}'s Crafting Level: {level}")
        unlocked = get_unlocked_methods(level)
        print("\n Crafting Methods Unlocked:")
        for method in unlocked:
            print(f" {method}")
        
        # logging
        log_data(username, level, unlocked)
    else:
        print(" Could not get crafting level.")

if __name__ == "__main__":
    main()

    #So far, I have a function that looks up an items price based off of the osrs API, and '
    # compareS it's price to another item
    #This will be used to determine the profit of a crafted item in the future
    #I also have a function that determines a users crafting level'
    #and a function that determines which crafts the user can create at their level
    #I found that it was too difficult to use the wiki's API for now (NOT THE OSRS API)
    #I essentially would have had to scrape a web page using a regex command to find the xp for each item
    #for now I hard coded the xp values for the items
    #I'm going to change this in the future
    #I'd also like to save some of this data to a local drive, allowing the user to have saved profiles
    #for different users

    