import os
import sys
cur_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(cur_dir, '../utils/'))
from tweepy import Cursor
from twitter_api import setup_api
from set_logger import get_logger
from csv import writer
from operator import attrgetter


home = os.environ.get('HOME', '/home/kush/')
logger = get_logger(home, 'get_tweets')
api = setup_api(home)
me = api.me()


with open(cur_dir + '/fairfrog_tweets.csv', 'w') as f:
    csvwriter = writer(f)
    for my_tweet in Cursor(api.user_timeline, screen_name=me.screen_name, tweet_mode="extended" ).items():
        if not hasattr(my_tweet, 'retweeted_status'):
            try:
                csvwriter.writerow([my_tweet.id, my_tweet.created_at.strftime('%Y-%m-%d %H:%M'),
                                    my_tweet.retweet_count, my_tweet.favorite_count,
                                    my_tweet.full_text.encode('UTF-8'),
                                    ','.join([tag.get('text').encode('UTF-8') for tag in
                                                my_tweet.entities.get('hashtags')]),
                                    ','.join([url.get('url').encode('UTF-8') for url in
                                                my_tweet.entities.get('urls')]),
                                    ','.join([url.get(u'expanded_url').encode('UTF-8') for url in
                                                my_tweet.entities.get('urls')])])
            except Exception as e:
                print e
                print my_tweet.id_str
                csvwriter.writerow([my_tweet.id, my_tweet.created_at.strftime('%Y-%m-%d %H:%M'),
                                    my_tweet.retweet_count, my_tweet.favorite_count,
                                    ','.join([tag.get('text').encode('UTF-8') for tag in
                                                my_tweet.entities.get('hashtags')]),
                                    ','.join([url.get('url').encode('UTF-8') for url in
                                                my_tweet.entities.get('urls')]),
                                    ','.join([url.get(u'expanded_url').encode('UTF-8') for url in
                                                my_tweet.entities.get('urls')])])
                continue
