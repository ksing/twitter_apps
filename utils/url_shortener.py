import json

import requests
from decouple import config

api_key = config("GOOGLE_KEY")
url = "https://www.googleapis.com/urlshortener/v1/url?key={}".format(api_key)


def get_short_url(long_url):
    headers = {"content-type": "application/json"}
    r = requests.post(url, data=json.dumps({"longUrl": long_url}), headers=headers)
    return r.json().get("id", "")


if __name__ == "__main__":
    import sys

    long_url = sys.argv[1]
    print(get_short_url(long_url))
