from TikTokApi import TikTokApi
import asyncio
import os

ms_token = os.environ.get("ms_token", None) # get your own ms_token from your cookies on tiktok.com

async def trending_videos():
    async with TikTokApi() as api:
        await api.create_sessions(
            ms_tokens=[ms_token],
            num_sessions=1, sleep_after=3, browser=os.getenv("TIKTOK_BROWSER", "chromium"))
        print(1)
        async for video in api.trending.videos(count=30):
            print(video)
            print(video.as_dict)
        print(2)

if __name__ == "__main__":
    asyncio.run(trending_videos())