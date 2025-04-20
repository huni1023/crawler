import json

def get_cookies_from_file():
    with open('/Users/davidperlusz/code/tiktok-scraper/cookies.json') as f:
        cookies = json.load(f)

    cookies_kv = {}
    for cookie in cookies:
        cookies_kv[cookie['Name raw']] = cookie['Content raw"']

    return cookies_kv


cookies = get_cookies_from_file()


def get_cookies(**kwargs):
    return cookies

from TikTokApi import TikTokApi

api = TikTokApi()

api._get_cookies = get_cookies  # This fixes issues the api was having

for trending_video in api.trending.videos(count=50):
    print(trending_video.author.username)