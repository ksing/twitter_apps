import os
import sys
from tweepy import Stream, StreamListener
from time import sleep
cur_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(cur_dir, '../utils/'))
from twitter_api import setup_api
from set_logger import get_logger

home = os.environ.get('HOME', '/home/kush/')
logger = get_logger(home, 'fairfrog_streamer' )


class MyStreamListener(StreamListener):

    def __init__(self, api):
        self.api = api

    def on_connect(self):
        user = self.api.me()
        logger.debug('Name: {0}\nLocation: {1}\nFriends: {2}\nFollowers: {3}\n'.\
                    format(user.name, user.location, user.friends_count, user.followers_count))
        last_updates = self.api.user_timeline('fairfrogNL', count=10)
        for status in last_updates:
            logger.debug(status.text.encode('UTF-8'))
            if not status.in_reply_to_user_id and not hasattr(status, 'retweeted_status'):
                try:
                    status.retweet()
                    logger.info("Retweeted: {}".format(status.text.encode('UTF-8')))
                    self.api.create_favorite(status.id)
                except Exception as e:
                    logger.error(e)
                    continue
                break
        logger.info("Connected to fairfrogNL stream...")
        return True

    def on_status(self, status):
        logger.info(status.text.encode('UTF-8'))
        if not status.in_reply_to_user_id and not hasattr(status, 'retweeted_status'):
            try:
                status.retweet()
                logger.info("Retweeted: {}".format(status.text.encode('UTF-8')))
                self.api.create_favorite(status.id)
            except Exception as e:
                logger.error(e)
        else:
            logger.warning("Not retweeting this one")
        return True

    def on_error(self, status_code):
        logger.error(status_code)
        if status_code == 420:
            sleep(5*60)
        return True

    def on_timeout(self):
        logger.warning('Timeout...')
        sleep(2*60)
        return True


if __name__ == '__main__':
    logger.debug("Starting the streamer...")
    api = setup_api(home)
    fairfrog_id = '3805728255'
    myStream = Stream(api.auth, listener=MyStreamListener(api))
    myStream.filter(follow=[fairfrog_id], async=True)
