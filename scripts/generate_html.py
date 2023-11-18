import re
import os
import json
import glob
import bleach


SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))
BASE_PATH = os.path.abspath(os.path.join(SCRIPT_PATH, ".."))
BASE_URL = "https://mklarz.github.io/etjenesten-cybertalent2023-winter-scoreboard/"

DATA_PATH = BASE_PATH + "/data"

TEMPLATES_PATH = BASE_PATH + "/templates"
INDEX_TEMPLATE_PATH = TEMPLATES_PATH + "/index.html"
USER_TEMPLATE_PATH = TEMPLATES_PATH + "/user.html"
HIGHSCORE_TEMPLATE_PATH = TEMPLATES_PATH + "/highscore.html"

HIGHSCORE_JSON_PATH = DATA_PATH + "/highscore.min.json"
HIGHSCORE_HTML_PATH = BASE_PATH + "/index.html"
HIGHSCORE_LIST_ITEM_HTML_FORMAT = '<li class=counter onclick="location=\'./users/{}.html\'"><span class="navn">{}</span><span class="sum">{}</span><span class="stars">{}</span></li>\n'
HIGHSCORE_LIST_ITEM_UNKNOWN_HTML_FORMAT = '<li class=unknown onclick="location=\'./users/{}.html\'"><span class="navn">{}</span><span class="sum">{}</span><span class="stars">{}</span></li>\n'
STAR_IMAGE_HTML = '<img src="./static/bug.gif" height="40px" alt="Stjerne: umulig"/>'
STAR_USER_IMAGE_HTML = '<img src="../static/bug.gif" height="40px" alt="Stjerne: umulig"/>'

USERS_PATH = BASE_PATH + "/users/"
USER_JSON_PATH = USERS_PATH + "{}.json"
USER_HTML_PATH = USERS_PATH + "{}.html"
USER_CATEGORY_HTML_FORMAT = '<li><span class="navn">{}<span class="sum">{}%</span></span></li>\n'

USERS = [user_file.replace(USERS_PATH, "").replace(".json", "") for user_file in glob.glob(USER_JSON_PATH.format("*"))]
print("Found", len(USERS), "users.")


# Templates
with open(INDEX_TEMPLATE_PATH) as fd:
    index_template = fd.read()

with open(USER_TEMPLATE_PATH) as fd:
    user_template = fd.read()

with open(HIGHSCORE_TEMPLATE_PATH) as fd:
    highscore_template = fd.read()

# Parse users
all_users = []
for user_id in USERS:
    print("Parsing user:", user_id)
    with open(USER_JSON_PATH.format(user_id)) as fd:
        user_data = json.load(fd)
        all_users.append(user_data)
    
    position_str = "{}. plass".format(user_data["position"]) if user_data["position"] else "Ukjent plassering"

    user_html = user_template
    user_html = user_html.replace("{USER_NAME}", bleach.clean(user_data["name"]))
    user_html = user_html.replace("{USER_POINTS}", str(user_data["points"]))
    user_html = user_html.replace("{USER_POSITION}", position_str)
    user_html = user_html.replace("{USER_STARS}", user_data["stars"] * STAR_USER_IMAGE_HTML)
    categories_html = ""
    for category_name, percent in user_data["categories"].items():
        categories_html += USER_CATEGORY_HTML_FORMAT.format(category_name, percent)
    user_html = user_html.replace("{USER_CATEGORIES}", categories_html.strip())

    with open(USER_HTML_PATH.format(user_id), "w") as fd:
        fd.write(user_html)


# Generate highscore

print("Saving highscore HTML to {}".format(HIGHSCORE_HTML_PATH))
with open(HIGHSCORE_JSON_PATH) as f:
    highscore_html = highscore_template
    highscore_users_html = ""
    highscore = json.load(f)
    for user in highscore:
        highscore_users_html += HIGHSCORE_LIST_ITEM_HTML_FORMAT.format(
                user["user_id"],
                bleach.clean(user["name"]),
                user["points"],
                user["stars"] * STAR_IMAGE_HTML,
        )
        all_users[:] = [d for d in all_users if d.get("user_id") != user["user_id"]]

    # Add the remaining users with unknown positions
    all_users = sorted(all_users, key=lambda d: d["points"], reverse=True)
    for user in all_users:
        highscore_users_html += HIGHSCORE_LIST_ITEM_UNKNOWN_HTML_FORMAT.format(
                user["user_id"],
                bleach.clean(user["name"]),
                user["points"],
                user["stars"] * STAR_IMAGE_HTML,
        )

    highscore_html = highscore_html.replace("{USERS}", highscore_users_html)

    with open(HIGHSCORE_HTML_PATH, "w") as fd:
        fd.write(highscore_html)
