import os
import sys
from tweepy import Cursor
from time import sleep

cur_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(cur_dir, "../utils"))
from twitter_api import setup_api
from set_logger import get_logger
from csv import DictReader


home = os.environ.get("HOME", "/home/fairfrog/")
logger = get_logger(home, "follow_unfollow")


def get_followers(api):
    me = api.me()
    followers = set()
    for page in Cursor(api.followers_ids, screen_name=me.screen_name).pages():
        followers.update([str(fol) for fol in page])
    return followers


def follow_desired_divas(api):
    me = api.me()
    cntr = 0
    with open(os.path.join(cur_dir, "diva_list.csv"), "rb") as f:
        csvreader = DictReader(f)
        new_friends = {row["Id"]: row["Screen_Name"] for row in csvreader}

    for item in Cursor(api.friends_ids, screen_name=me.screen_name).items():
        if item not in followers and item not in new_friends.keys():
            api.destroy_friendship(item)
            cntr += 1
            logger.info("Unfollowing {}".format(item))
            if cntr == 15:
                cntr = 0
                sleep(1800)

    for Id, screen_name in new_friends.items():
        api.create_friendship(screen_name=screen_name)
        cntr += 1
        logger.info("Following {}".format(screen_name))
        if cntr == 10:
            cntr = 0
            sleep(1800)


def remove_unfollowers(api, current_followers):
    with open(os.path.join(home, "followers_list.txt"), "rU") as f:
        followers_list = set([fol_id.strip() for fol_id in f.readlines()])
    for unfollower in followers_list - current_followers:
        try:
            user = api.get_user(unfollower)
            logger.info("{} unfollowed us.".format(user.screen_name))
            if user.following:
                user.unfollow()
                logger.info("Unfollowing {}".format(user.screen_name))
        except Exception as e:
            logger.error("Error: {}".format(e))


if __name__ == "__main__":
    api = setup_api(home)
    me = api.me()
    logger.info(
        "Name: {0}\nLocation: {1}\nFriends: {2}\nFollowers: {3}\n".format(
            me.name, me.location, me.friends_count, me.followers_count
        )
    )
    followers = get_followers(api)
    remove_unfollowers(api, followers)
    with open(os.path.join(home, "followers_list.txt"), "w") as f:
        f.write("\n".join(followers))
    # follow_desired_divas(api)
