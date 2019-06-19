from csv import DictReader
from multiprocessing import Pool


# importlib.reload(sys)
# sys.setdefaultencoding('utf8')
# tweets = []


def print_tweet_length(tweet):
    if len(tweet["Text"]) > 135:
        print(len(tweet["Text"]), tweet["Id"], tweet["Text"])


with open("fairfrog_tweets.csv", "rb") as f:
    csvreader = DictReader(f)
    with Pool(proceeses=4) as p:
        tweets = [row for row in csvreader]
        p.map(print_tweet_length, tweets)
