import os
import sys
from tweepy import Cursor

cur_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(cur_dir, "../utils/"))
from twitter_api import setup_api
from set_logger import get_logger

home = os.environ.get("HOME", "/home/kush/")
desirable_words = [
    "ethical",
    "duurza",
    "organic",
    "biologisch",
    "climate change" "fairtrade",
    "sustainab",
    "fairfashion",
    "recycl",
    "upcycl",
    "plastic",
]

logger = get_logger(home, "follow_unfollow")
api = setup_api(home)
me = api.me()
followers = []

with open(os.path.join(home, "followers_list.txt"), "rU") as f:
    followers_list = set([fol_id.strip() for fol_id in f.readlines()])

logger.info(
    "Name: {0}\nLocation: {1}\nFriends: {2}\nFollowers: {3}\n".format(
        me.name, me.location, me.friends_count, me.followers_count
    )
)

for page in Cursor(api.followers_ids, screen_name=me.screen_name).pages():
    followers.extend([str(fol) for fol in page])

current_followers = set(followers)
with open(os.path.join(home, "followers_list.txt"), "w") as f:
    f.write("\n".join(current_followers))

for unfollower in followers_list - current_followers:
    user = api.get_user(unfollower)
    if user.following:
        user.unfollow()
        logger.info("Unfollowing {}".format(user.name))

for new_follower in current_followers - followers_list:
    user = api.get_user(new_follower)
    if not user.following and any(desirable_words in word for word in user.description().lower()):
        user.follow()
    logger.info("New follower: {}".format(user.name))
