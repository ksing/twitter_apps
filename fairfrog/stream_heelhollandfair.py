from tweepy import Stream, StreamListener
from datetime import datetime
from time import sleep
import os
import sys
cur_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(cur_dir, '../utils/'))
from twitter_api import setup_api
from set_logger import get_logger


forbidden_word_list = ['job', 'factuur']
home = os.environ.get('HOME', '/home/fairfrog/')
logger = get_logger(home, 'streaming_heelholland')



class MyStreamListener(StreamListener):

	def on_connect(self):
		logger.info("Connecting the stream...")


	def on_status(self, status):
		tweet = status.text.encode('UTF-8')
		if not any(word in tweet for word in forbidden_word_list):
			try:
				api.retweet(status.id)
				status.favorite()
			except Exception as e:
				print e
			finally:
				logger.info("Retweeted: " + tweet)
		now_hour = datetime.now().hour
		if now_hour > 23 or now_hour < 1:
			return False
		else:
			return True


	def on_error(self, status):
		logger.error(status)
		sleep(5*60)
		return True


	def on_timeout(self):
		logger.warning('Timeout...')
		sleep(2*60)
		return True



if __name__ == '__main __':
	api = setup_api(home)
	user = api.me()
	logger.debug('Name: {0}\nLocation: {1}\nFriends: {2}\nFollowers: {3}\n'.format(user.name, user.location, user.friends_count, user.followers_count))
	myStream = Stream(api.auth, listener=MyStreamListener())
	myStream.filter(track=['#Heelhollandfair'], async=True)
