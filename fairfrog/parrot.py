import math
import datetime as dt
import os
import re
import sys
from dataclasses import dataclass
from itertools import zip_longest
from typing import List, Set
from time import sleep

import numpy as np
import requests
from loguru import logger
from lxml import etree as ET

from ..utils.twitter_api import setup_api
from ..utils.url_shortener import get_short_url


BLOG_RSS_URL = 'https://fairfrog.nl/?feed=fairss'
PRODUCT_API_URL = 'https://fairapp.pythonanywhere.com/get_products'
PARSER = ET.XMLParser(
    ns_clean=True, remove_blank_text=True, remove_comments=True, strip_cdata=True, encoding='utf-8'
)
TODAY = dt.date.today()
MAX_NUM_BLOGS = 3
TOTAL_NUM_TWEETS = 5
NUM_HOURS = 22 - 8
HOME = os.getenv('HOME', '/home/fairfrog')


@dataclass
class Blog:
    title: str
    url: str
    publish_date: dt.date
    description: str
    image_url: str
    tags: Set[str]
    author: str

    @property
    def is_relevant(self):
        return is_fibonacci_num((TODAY - self.publish_date).days)

    def tweet(self, twitter) -> None:
        logger.info('Tweeting blog: {}, originally published on {}',
                    self.title, self.publish_date.strftime('%Y-%m-%d'))
        return


@dataclass
class Product:
    name: str
    url: str
    description: str
    image_url: str

    def tweet(self, twitter) -> None:
        logger.info('Tweeting about the product')
        return


def _is_perfect_square(x: int) -> bool:
    sqrt = int(math.sqrt(x))
    return sqrt ** 2 == x


def is_fibonacci_num(x: int) -> bool:
    return _is_perfect_square(5 * x * x + 4) or _is_perfect_square(5 * x * x - 4)


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


def get_site_products(product_sitemap: str) -> List['Product']:
    return []


def get_random_intervals(num_intervals):
    np.random.seed(TODAY)
    for i in np.random.dirichlet(np.ones(num_intervals), 1):
        yield i


def main():
    all_blogs = get_blogs(rss_feed_url=BLOG_RSS_URL)
    # update_blogs_database(all_blogs)
    blogs_to_tweet = get_relevant_blogs(all_blogs)
    products_to_tweet = get_site_products(
        product_url=PRODUCT_API_URL, num_products=TOTAL_NUM_TWEETS - len(blogs_to_tweet)
    )
    twitter_api = setup_api(HOME)
    twitter_me = twitter_api.me()
    logger.info(
        "Name: {}\nLocation: {}\nFriends: {}\nFollowers: {}\n",
        twitter_me.name, twitter_me.location, twitter_me.friends_count, twitter_me.followers_count
    )
    for post in np.random.choice(blogs_to_tweet + products_to_tweet):
        interval = next(get_random_intervals(TOTAL_NUM_TWEETS))
        sleep(interval * NUM_HOURS * 3600)
        post.tweet(twitter_api)
