import os
from configparser import ConfigParser

import requests


def get_group_guid(headers):
    r = requests.get('https://api-ssl.bitly.com/v4/groups', headers=headers)
    if r.ok:
        return r.json()['groups'][0]['guid']


def get_short_url(long_url):
    config = ConfigParser()
    config.read(os.path.expanduser('~/.key_data'))
    access_token = config['BitLy'].get("ACCESS_TOKEN")
    url = "https://api-ssl.bitly.com/v4/shorten"
    headers = {
        "content-type": "application/json",
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }
    group_guid = get_group_guid(headers)
    r = requests.post(url, json={"long_url": long_url, "group_guid": group_guid}, headers=headers)
    return r.json().get("link")


if __name__ == "__main__":
    import sys

    long_url = sys.argv[1]
    print(get_short_url(long_url))
