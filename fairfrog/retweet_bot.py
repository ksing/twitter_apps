#!/usr/bin/env python

import os
import sys

import arrow

cur_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(cur_dir, "../utils/"))
from twitter_api import setup_api, get_tweets
from set_logger import get_logger

home = os.environ.get("HOME", "/home/fairfrog/")
logger = get_logger(home, "retweeter")

relevant_accounts = [
    "plasticsoupfoun",
    "hetkanWel",
    "DuurzaamBV",
    "DuurzameTweets",
    "DuurzaamNieuws",
    "NLCirculair",
    "Fash_RevNld",
    "loveyourclothes",
    "circulairestad",
    "DuurzaamActueel",
    "FairWork_Nu",
    "EigenwijsBlij",
    "EkoPlaza",
    "CarbonBubble",
    "GoodBiteNL",
    "BuyMeOnce",
    "FairTradeOrigin",
    "FairtradeNL",
    "FairtradeUK",
    "debeterewereld",
    "TrouwGroen",
    "TriodosNL",
    "guardianeco",
    "FossielvrijNL",
    "BionextTweets",
    "Ontdekbio",
    "SlowFoodiesNL",
    "BestEarthPix",
    "Puuruiteten",
    "youngandfair",
    "TheOceanCleanup",
    "JoyfullyECO",
]


if __name__ == "__main__":
    api = setup_api(home)
    now = arrow.now()
    if now.hour > 23 or now.hour < 7:
        logger.info("Time to go to sleep")
        sys.exit(0)
    new_tweets = get_tweets(api, relevant_accounts, logger)
    for tweet in new_tweets:
        try:
            logger.info("Retweeting: " + tweet.text)
            tweet.retweet()
            break
        except:
            continue
    else:
        logger.warning("No relevant tweets to retweet")
        sys.exit(1)
