import os
from configparser import ConfigParser

from tweepy import OAuthHandler, API
from random import seed, shuffle
import arrow


def setup_api(home=None):
    config = ConfigParser()
    config.read(os.path.expanduser('~/.key_data'))
    ckey = config['Twitter'].get("CKEY", "")
    csecret = config['Twitter'].get("CSECRET", "")
    atoken = config['Twitter'].get("ATOKEN", "")
    asecret = config['Twitter'].get("ASECRET", "")
    auth = OAuthHandler(ckey, csecret)
    auth.set_access_token(atoken, asecret)
    return API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True, compression=True)


important_hashtags = [
    "ethical",
    "duurza",
    "organic",
    "recycl",
    "upcycl",
    "plastic",
    "biologisch",
    "climate change" "fairtrade",
    "sustainab",
    "fairfashion",
]


def maximize_hashtag(status):
    hashtags = [
        hashtag.get(u"text").lower()
        for hashtag in status.entities.get(u"hashtags")
        if hashtag in important_hashtags
    ]
    return len(hashtags)


def get_tweets(api, relevant_accounts, logger, now=arrow.now()):
    tweets = []
    seed(now.naive)
    shuffle(relevant_accounts)
    for account in relevant_accounts:
        try:
            user = api.get_user(account)
            status = user.status
        except:
            logger.error(account + " does not exist")
            continue
        if (
            not status.retweeted
            and not status.in_reply_to_user_id
            and (now - arrow.get(status.created_at)).seconds < 3600 * 12
            and not hasattr(status, "retweeted_status")
        ):
            tweets.append(status)
    if tweets:
        logger.debug("Sending Tweets...")
        return tweets
    logger.debug("No new tweets..")
    return None
