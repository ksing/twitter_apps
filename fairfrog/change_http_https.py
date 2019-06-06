import os
import sys
from csv import DictReader, DictWriter
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from time import sleep

cur_dir = os.path.abspath(os.path.dirname(__file__))
from url_shortener import get_short_url
from multiprocessing import Pool


reload(sys)
sys.setdefaultencoding("utf8")
os.environ["MOZ_HEADLESS"] = "1"
# tweets = []
driver = webdriver.Firefox()

fout = open("new_unfiltered_tweets.csv", "w")
writer = DictWriter(
    fout, fieldnames="Id,Date,Retweeted,Liked,Text,hashtags,url,expanded_url".split(",")
)
writer.writeheader()


def get_text_url(link, row):
    driver.get(link)
    while link == driver.current_url:
        sleep(2)
    redirected_url = driver.current_url
    new_url = redirected_url.rpartition("?")[0]
    if "fairfrog.nl/#!/products" in new_url:
        heading = driver.find_element_by_xpath('//div[contains(@class, "product-block")]//h4')
        print(heading.text, end=" ")
        if heading.text.split(">")[0]:
            short_url = get_short_url(new_url)
            row["Text"] = row["Text"].replace(row["url"], short_url)
            print(row["Id"], len(row["Text"]))
            row["url"] = short_url
            row["expanded_url"] = new_url
            # tweets.append(row)
            writer.writerow(row)
        else:
            print(row["Id"], new_url)
    else:
        # tweets.append(row)
        writer.writerow(row)


with open("unfiltered_tweets.csv", "rb") as f:
    csvreader = DictReader(f)
    """
    cntr = 0
    links = []
    p = Pool(5)
    """
    for row in csvreader:
        link = row["url"]
        if link:
            """
            links.append(link)
            cntr+=1
            if cntr == 5:
                p.map(get_text_url, links)
            """
            get_text_url(link, row)
            """
                sleep(3)
                cntr = 0
                links = []
                p = Pool(5)
            """
        else:
            writer.writerow(row)


fout.close()
