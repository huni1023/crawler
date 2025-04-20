from TikTokApi import TikTokApi
api = TikTokApi.get_instance()
print(api.by_trending(count=1))