import re
import os
import time
import json
import glob
import requests
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem
from bs4 import BeautifulSoup

# dirty and quick script for tracking the highscore. buy me a beer :))


SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))
BASE_PATH = os.path.abspath(os.path.join(SCRIPT_PATH, ".."))
HIGHSCORE_URL = "https://ctf.cybertalent.no/highscore"
USER_URL = "https://ctf.cybertalent.no/u/{}"
TEMPLATES_PATH = BASE_PATH + "/templates"
DATA_PATH = BASE_PATH + "/data/"
USERS_PATH = BASE_PATH + "/users/"
USER_JSON_PATH = USERS_PATH + "{}.json"

existing_users = [user_file.replace(USERS_PATH, "").replace(".json", "") for user_file in glob.glob(USER_JSON_PATH.format("*"))]

retries = Retry(
    total=5,
    backoff_factor=0.1,
    status_forcelist=[500, 502, 503, 504]
)
s = requests.Session()
s.mount(HIGHSCORE_URL, HTTPAdapter(max_retries=retries))

software_names = [SoftwareName.CHROME.value]
operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]   
user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=100)

r = s.get(HIGHSCORE_URL, headers={"User-Agent": user_agent_rotator.get_random_user_agent()})

soup = BeautifulSoup(r.content, 'html.parser')

highscore = []
users = {}


def handle_user(user_id, user=None):
    r = s.get(USER_URL.format(user_id))
    soup = BeautifulSoup(r.content, 'html.parser')

    if not user:
        user = {
            "position": None,
            "user_id": user_id,
            "name": soup.find("h1").text.strip(),
            "points": int(soup.find("h2").text.strip().replace(" poeng", "")),
            "stars": 0,
        }

    # Let's add their current solves
    user["categories"] = {}

    # Loop through the categories and map the percentages
    for li in soup.find("ol", class_="liste").find_all("li"):
        percent = li.find("span", class_="sum").text.strip()
        name = li.find("span", class_="navn").text.strip()[:-len(percent)]
        user["categories"][name] = int(percent[:-1]) # Remove the %

    # Save the individual data for each user
    with open(USER_JSON_PATH.format(user_id), "w") as f:
        json.dump(user, f, indent=4)
    print("Done processing: {}".format(user_id))

highscore_users = set()
for position, li in enumerate(soup.find("ol", class_="liste").find_all("li")):
    # Extract all the user information
    user_id = re.search(r"'/u/(.*?)'", li["onclick"]).group(1)
    points = li.find("span", class_="sum").text.strip()
    username = li.find("span", class_="navn").text.strip()
    stars = len(li.find("span", class_="stars").find_all("img", {"alt": "Stjerne: umulig"}))


    # Initialize the user object and add it to the highscore table
    user = {
        "position": position + 1,
        "user_id": user_id,
        "name": username,
        "points": int(points),
        "stars": stars,
    }
    highscore.append(user)
    highscore_users.add(user_id)
    handle_user(user_id, user.copy())

    # Let's be a bit nice and sleep for a bit
    time.sleep(0.2)

for user_id in existing_users:
    if user_id in highscore_users:
        continue
    # We now have an user that is not in the top 100 anymore, let's track them by grabbing them directly
    handle_user(user_id)


with open("{}/highscore.min.json".format(DATA_PATH), "w") as f:
    json.dump(highscore, f)

with open("{}/highscore.json".format(DATA_PATH), "w") as f:
    json.dump(highscore, f, indent=4)

print("Done saving highscore JSON files")
