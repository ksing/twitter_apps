import os
import sys
import arrow
from time import sleep

cur_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(cur_dir, "../utils/"))
from twitter_api import setup_api, get_tweets
from set_logger import get_logger

home = os.environ.get("HOME", "/home/kush/")
relevant_accounts = [
    "CECHR_UoD",
    "Ecosia",
    "FairWork_Nu",
    "Meerwind_HLMMR",
    "trustedclothes",
    "Essenza_Bio",
    "CFADC",
    "Groenemusketier",
    "ethicalbrandz",
    "wearetheninety9",
    "FAIRTRADE",
    "hackandcraft",
    "fairtrade_india",
    "ECOCENT_NL",
    "EnergieOverheid",
    "GroeneCourant",
    "TrouwGroen",
    "bnrduurzaam",
    "DuurzaamNieuws",
    "DuurzaamBV",
    "NatGeoPhotos",
    "SpaceX",
    "NatGeo",
    "NASA",
]


if __name__ == "__main__":
    logger = get_logger(home, "retweeter")
    logger.info("Setting up api connection...")
    api = setup_api(home)
    user = api.me()
    logger.info(
        "Name: {0}\nLocation: {1}\nFriends: {2}\nFollowers: {3}\n".format(
            user.name, user.location, user.friends_count, user.followers_count
        )
    )
    while 1:
        now = arrow.now()
        new_tweets = get_tweets(api, relevant_accounts, logger)
        for tweet in new_tweets:
            try:
                logger.info("Retweeting: " + tweet.text)
                tweet_message = tweet.retweet()
                break
            except:
                continue
        else:
            logger.warning("No relevant tweets to retweet")
        if now.time().hour > 23 or now.time().hour < 7:
            logger.warning("Time to go to sleep")
            break
        sleep(14400)
