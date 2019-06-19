import os
import sys
import html
from time import sleep

cur_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(cur_dir, "../utils"))
from twitter_api import setup_api
from set_logger import get_logger
from time import sleep
from random import randint, shuffle, random, seed
from logging import DEBUG
import arrow
import sqlite3 as sql


home = os.environ.get("HOME", "/home/fairfrog/")
logger = get_logger(home, "old_tweets")
# logger.setLevel(DEBUG)
now = arrow.now()


def get_conn():
    conn = sql.connect(cur_dir + "/fairfrog_tweets.db")
    conn.row_factory = sql.Row
    conn.text_factory = str
    return conn


def close_conn(conn):
    conn.commit()
    conn.close()


def post_old_tweet(api):
    conn = get_conn()
    cursor = conn.cursor()
    query = conn.execute("SELECT Id, Tweet_Date, Text FROM Tweets ORDER BY Tweet_Date")
    statuses = query.fetchall()
    now = arrow.now()
    shuffle(statuses)
    for status in statuses:
        tweet = html.unescape(status["Text"])
        tweet_id = html.unescape(status["Id"])
        tweet_date = arrow.get(status["Tweet_Date"])
        if len(tweet) <= 180:
            if (now - tweet_date).days > 30:
                break
        else:
            logger.warning("Tweet (ID: {}) longer than 140 characters: {}".format(tweet_id, tweet))
    else:
        logger.error("We're all tweeted out!")
        close_conn(conn)
        return

    logger.info("Posting old tweet ({}): {}".format(tweet_id, tweet))
    try:
        tweeted = api.update_status(tweet)
        logger.debug(tweeted)
        cursor.execute(
            "UPDATE Tweets SET Tweet_Date=? WHERE Id=?", (now.strftime("%Y-%m-%d %H:%M"), tweet_id)
        )
    except Exception as e:
        logger.error("Tweet failed: {}".format(e))
    finally:
        close_conn(conn)


def post_appeal(api):
    conn = get_conn()
    cursor = conn.cursor()
    query = conn.execute("SELECT Id, Tweet_Date, Text FROM Appeals ORDER BY Tweet_Date")
    statuses = query.fetchall()
    now = arrow.now()
    shuffle(statuses)
    for status in statuses:
        tweet = html.unescape(status["Text"])
        tweet_id = html.unescape(status["Id"])
        tweet_date = arrow.get(status["Tweet_Date"])
        if len(tweet) <= 180:
            if (now - tweet_date).days > 10:
                break
        else:
            logger.warning("Appeal (ID: {}) longer than 140 characters: {}".format(tweet_id, tweet))
    else:
        logger.error("We've  been posting too many appeals")
        close_conn(conn)
        return

    try:
        tweeted = api.update_status(tweet)
        logger.debug(tweeted)
        logger.info("Posting an appeal({}): {}".format(tweet_id, tweet))
        cursor.execute(
            "UPDATE Appeals SET Tweet_Date=? WHERE Id=?", (now.strftime("%Y-%m-%d %H:%M"), tweet_id)
        )
    except Exception as e:
        logger.error("Tweet failed: {}".format(e))
    finally:
        close_conn(conn)


if __name__ == "__main__":
    api = setup_api(home)
    me = api.me()
    logger.info(
        "Name: {0}\nLocation: {1}\nFriends: {2}\nFollowers: {3}\n".format(
            me.name, me.location, me.friends_count, me.followers_count
        )
    )
    num_seconds_to_sleep = randint(2, 8) * 3600
    seed(num_seconds_to_sleep)
    logger.debug("Going to sleep for {} minutes".format(num_seconds_to_sleep / (60 * 8)))
    sleep(num_seconds_to_sleep / 8)
    post_old_tweet(api)
    logger.info("Going to sleep for {} hours".format(num_seconds_to_sleep / 3600))
    sleep(num_seconds_to_sleep)
    if random() > 0.70:
        post_appeal(api)
    else:
        logger.debug("Posting another old tweet again")
        post_old_tweet(api)
