import os
import sys
from csv import DictReader, DictWriter
from multiprocessing import Pool


reload(sys)
sys.setdefaultencoding('utf8')
# tweets = []

def print_tweet_length(tweet):
    if len(tweet['Text']) > 135:
        print len(tweet['Text']), tweet['Id'], tweet['Text']


with open('fairfrog_tweets.csv', 'rb') as f:
    csvreader = DictReader(f)
    cntr = 0
    links = []
    p = Pool(5)
    tweets = [row for row in csvreader]
    p.map(print_tweet_length, tweets)
