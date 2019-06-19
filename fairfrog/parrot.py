#!/usr/bin/env python3
import html
import math
import datetime as dt
import os
import re
import sqlite3 as sql
import sys
from dataclasses import dataclass
from functools import lru_cache
from typing import List, Set
from time import sleep

import numpy as np
import requests
from lxml import etree as ET

CUR_DIR = os.path.dirname(__file__)
sys.path.append(os.path.join(CUR_DIR, '../utils/'))
from set_logger import get_logger
from twitter_api import setup_api
from url_shortener import get_short_url


BLOG_RSS_URL = 'https://fairfrog.nl/?feed=fairss'
FAIRFROG_URL = 'https://fairfrog.nl/#!/products/{webshop}/{title}/{Id}/'
PRODUCT_API_URL = os.getenv('PRODUCT_API_URL')
PARSER = ET.XMLParser(
    ns_clean=True, remove_blank_text=True, remove_comments=True, strip_cdata=True, encoding='utf-8'
)
TODAY = dt.datetime.now()
MAX_NUM_BLOGS = 3
TOTAL_NUM_TWEETS = 6
TWEET_LENGTH = 280
NUM_HOURS = 22 - 8
HOME = os.getenv('HOME', '/home/fairfrog')
INSERT_BLOG_QUERY = """INSERT INTO FairFrog_Blogs
    (Title, Url, Publish_Date, Description, Image, Tags, Author, Last_Update)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
"""
logger = get_logger(HOME, f'parrot_{TODAY.date()}', 'Parrot')


@lru_cache(8)
def get_api_config_settings(api):
    config = api.configuration()
    return config['characters_reserved_per_media'], config['short_url_length_https']


def download_image_to_temp(image_url: str) -> str:
    try:
        response = requests.get(image_url, allow_redirects=True)
    except requests.exceptions.MissingSchema:
        response = requests.get('http:' + image_url, allow_redirects=True)
    temp_filename = '/tmp/' + image_url.rpartition('/')[2].partition('?')[0]
    with open(temp_filename, 'wb') as f:
        f.write(response.content)
    return temp_filename


def upload_media_to_twitter(image_url: str, twitter) -> int:
    file_name = download_image_to_temp(image_url)
    media = twitter.media_upload(file_name)
    os.remove(file_name)
    return media


def _is_perfect_square(x: int) -> bool:
    sqrt = int(math.sqrt(x))
    return sqrt ** 2 == x


def is_fibonacci_num(x: int) -> bool:
    return _is_perfect_square(5 * x * x + 4) or _is_perfect_square(5 * x * x - 4)


def add_hashtags(status, tags, url_length, twitter_api, media=False):
    characters_reserved_per_media, short_url_length = get_api_config_settings(twitter_api)
    for tag in tags:
        if (
            len(status + f'#{tag} ') <
            TWEET_LENGTH - characters_reserved_per_media * media - short_url_length + url_length
        ):
            status += html.unescape(f'#{tag.replace(" ", "")} ')
    return status


def send_tweet(twitter, status, media=None):
    try:
        if media is not None:
            tweet = twitter.update_status(status=status, media_ids=[media.media_id])
        else:
            tweet = twitter.update_status(status=status)
        logger.info('Tweeted with the id %s at %s, with text: %s',
                    tweet._json['id_str'], tweet._json['created_at'], tweet._json['text'])
    except Exception as e:
        logger.warning('Could not tweet %s because: %s', tweet, e)


@dataclass
class Blog:
    title: str
    url: str
    publish_date: dt.datetime
    description: str
    image_url: str
    tags: Set[str]
    author: str

    @property
    def is_relevant(self):
        return is_fibonacci_num(self.days_since_publish)

    @property
    def days_since_publish(self):
        return (TODAY.date() - self.publish_date.date()).days

    def insert_in_database(self, cursor):
        cursor.execute(INSERT_BLOG_QUERY, (
            self.title, self.url, self.publish_date.strftime('%Y-%m-%d'), self.description[:512],
            self.image_url, ','.join(self.tags), self.author,
            TODAY.strftime('%Y-%m-%d')
        ))

    def tweet(self, twitter) -> None:
        short_url = get_short_url(self.url)
        status = (f"{self.description} [Gemist sinds {self.days_since_publish} dagen] \n"
                  f"{short_url}\n")
        status = add_hashtags(status, self.tags, len(short_url), twitter)
        logger.info('Tweeting blog: %s, originally published on %s',
                    self.title, self.publish_date.strftime('%Y-%m-%d'))
        send_tweet(twitter, status)


@dataclass
class Product:
    Id: int
    title: str
    webshop_name: str
    description: str
    image_url: str
    tags: List[str]

    @property
    def url(self):
        return FAIRFROG_URL.format(
            webshop=self._urlify(self.webshop_name), title=self._urlify(self.title), Id=self.Id
        )

    @staticmethod
    def _urlify(text: str) -> str:
        return text.lower().replace(' ', '_')

    def tweet(self, twitter) -> None:
        short_url = get_short_url(self.url)
        media = upload_media_to_twitter(self.image_url, twitter)
        status = (f'Check out dit mooi product uit onze collectie: '
                  f'{self.title} van {self.webshop_name} op {short_url}\n')
        status = add_hashtags(status, self.tags, len(short_url), twitter, media=True)
        logger.info('Tweeting about the product: %s from %s', self.title, self.webshop_name)
        send_tweet(twitter, status, media)


def get_blogs(rss_feed_url: str) -> List['Blog']:
    output_blogs: List['Blog'] = []
    response = requests.get(rss_feed_url)
    response.raise_for_status()
    xml_tree = ET.fromstring(response.text.encode('utf-8'), parser=PARSER)
    for item in xml_tree.xpath('.//item'):
        title = item.findtext('{*}title')
        link = item.findtext('{*}link')
        publish_date = dt.datetime.strptime(
            item.findtext('{*}pubDate'), '%a, %d %b %Y %H:%M:%S +%f'
        )
        desc_html = ET.HTML(item.findtext('{*}description'))
        description = ' '.join(desc_html.xpath('.//p/text()'))
        image_url = desc_html.xpath('.//img/@src')[0]
        tags = {category.strip().lower() for category in item.xpath('./category/text()')}
        author = ' '.join(re.findall(r'>(.+)</a>', item.findtext('{*}creator')))
        output_blogs.append(Blog(
            title=title,
            url=link,
            publish_date=publish_date,
            description=description,
            image_url=image_url,
            tags=tags,
            author=author
        ))
    return output_blogs


def get_relevant_blogs(blogs: List['Blog']) -> List['Blog']:
    return [blog for blog in blogs if blog.is_relevant][:MAX_NUM_BLOGS]


def get_site_products(product_url: str, num_products: int) -> List['Product']:
    np.random.seed(TODAY.toordinal())
    response = requests.get(product_url + f'/get_products/')
    products = response.json()['products_list']
    np.random.shuffle(products)
    return [
        Product(
            Id=product['Id'], title=product['title'], webshop_name=product['webshop_name'],
            description=product['meta_text'], image_url=product['images'][0],
            tags=product['categories']
        ) for product in products[:num_products]
    ]


def get_random_intervals(num_intervals):
    np.random.seed(TODAY.toordinal())
    for i in np.random.dirichlet(np.ones(num_intervals), 1)[0]:
        yield i


def create_blog_table(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS FairFrog_Blogs
        (Id INTEGER PRIMARY KEY AUTOINCREMENT, Title VARCHAR(256), Url VARCHAR(128),
         Publish_Date VARCHAR(16), Description VARCHAR(512), Image VARCHAR(128),
         Tags VARCHAR(128), Author VARCHAR(64), Last_Update VARCHAR(16))
    """)


def update_blogs_database(all_blogs: List['Blog']):
    with sql.connect(os.path.join(CUR_DIR, 'blogs.db')) as conn:
        cursor = conn.cursor()
        create_blog_table(cursor)
        current_blog_urls = [
            url.lower() for id_, url in cursor.execute('SELECT Id, Url from FairFrog_Blogs')
        ]
        for blog in all_blogs:
            if blog.url not in current_blog_urls:
                blog.insert_in_database(cursor)
        conn.commit()
        cursor.close()


def main():
    all_blogs = get_blogs(rss_feed_url=BLOG_RSS_URL)
    update_blogs_database(all_blogs)
    blogs_to_tweet = get_relevant_blogs(all_blogs)
    products_to_tweet = get_site_products(
        product_url=PRODUCT_API_URL, num_products=TOTAL_NUM_TWEETS - len(blogs_to_tweet)
    )
    twitter_api = setup_api()
    twitter_me = twitter_api.me()
    logger.info(
        "Name: %s\nLocation: %s\nFriends: %s\nFollowers: %s\n",
        twitter_me.name, twitter_me.location, twitter_me.friends_count, twitter_me.followers_count
    )
    for post in np.random.permutation(blogs_to_tweet + products_to_tweet):
        interval = next(get_random_intervals(TOTAL_NUM_TWEETS))
        logger.info(f'Sleeping for {interval * NUM_HOURS * 3600: 0.2f} seconds')
        sleep(interval * NUM_HOURS * 3600)
        post.tweet(twitter_api)


if __name__ == '__main__':
    main()
