import sqlite3 as sql
from csv import reader
import os
import sys

reload(sys)
sys.setdefaultencoding('utf8')

cur_dir = os.path.abspath(os.path.dirname(__file__))

conn = sql.connect("fairfrog_tweets.db")
cursor = conn.cursor()
conn.text_factory = str


cursor.execute("""CREATE Table IF NOT EXISTS Appeals
                (Id VARCHAR(30), Tweet_Date VARCHAR(22),Retweeted VARCHAR(3),Liked VARCHAR(3),Text TINYTEXT,
                hashtags TINYTEXT,url TINYTEXT,expanded_url TINYTEXT);"""
            )

cursor.execute("""CREATE Table IF NOT EXISTS Tweets
                (Id VARCHAR(30), Tweet_Date VARCHAR(22),Retweeted VARCHAR(3),Liked VARCHAR(3),Text TINYTEXT,
                hashtags TINYTEXT,url TINYTEXT,expanded_url TINYTEXT);"""
            )


with open(os.path.join(cur_dir, 'fairfrog_tweets.csv'), 'rb') as f:
    fieldnames = f.readline()
    csvreader = reader(f)
    tweets = [tuple(row + [row[1]]) for row in csvreader]


with open(os.path.join(cur_dir, 'appeals.csv'), 'rb') as f:
    fieldnames = f.readline()
    csvreader = reader(f)
    appeals = [tuple(row + [row[1]]) for row in csvreader]

try:
    cursor.executemany("Insert INTO Appeals VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", appeals)
    cursor.executemany("Insert INTO Tweets VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", tweets)
    conn.commit()
except:
    conn.rollback()
    raise
finally:
    conn.close()
