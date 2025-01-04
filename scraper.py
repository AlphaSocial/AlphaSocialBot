from telethon import TelegramClient, events, sync
from telethon.tl.functions.channels import GetFullChannelRequest
import os
import json
from datetime import datetime

# API Credentials
api_id = 29114639
api_hash = '40fa4fdc6cbf04f01f56da6f7b96aad4'

class TelegramScraper:
    def __init__(self):
        self.client = TelegramClient('scraper_session', api_id, api_hash)
    
    async def connect(self):
        print("Starting Telegram client...")
        await self.client.start()
        
    async def get_channel_info(self, channel_url):
        try:
            # Connect to the channel
            channel = await self.client.get_entity(channel_url)
            
            # Get full channel info
            full_channel = await self.client(GetFullChannelRequest(channel=channel))
            
            # Initialize dictionary for channel info
            channel_data = {
                "name": channel.title,
                "profile_image": "",
                "telegram_link": channel_url,
                "twitter_link": "",
                "website_link": "",
                "scrape_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Get channel profile photo if it exists
            if channel.photo:
                profile_photo = await self.client.download_profile_photo(channel, file="channel_photo.jpg")
                channel_data["profile_image"] = "channel_photo.jpg" if profile_photo else ""
            
            # Search through recent messages for links
            async for message in self.client.iter_messages(channel, limit=100):
                if message.text:
                    text = message.text.lower()
                    
                    # Look for Twitter/X links
                    if "twitter.com" in text or "x.com" in text:
                        for word in text.split():
                            if "twitter.com" in word or "x.com" in word:
                                channel_data["twitter_link"] = word
                                break
                    
                    # Look for website links
                    if "http://" in text or "https://" in text:
                        words = text.split()
                        for word in words:
                            if word.startswith(("http://", "https://")) and \
                               not ("twitter.com" in word or "x.com" in word or "t.me" in word):
                                channel_data["website_link"] = word
                                break
            
            return channel_data
            
        except Exception as e:
            print(f"\nError occurred while scraping: {str(e)}")
            return None

async def main():
    scraper = TelegramScraper()
    await scraper.connect()
    
    # Input the channel URL to scrape
    channel_url = input("\nEnter the Telegram channel URL (e.g., https://t.me/channelname): ")
    
    # Run the scraper
    channel_data = await scraper.get_channel_info(channel_url)
    
    if channel_data:
        print("\nChannel Information:")
        print(f"Name: {channel_data['name']}")
        print(f"Profile Image: {channel_data['profile_image']}")
        print(f"Telegram Link: {channel_data['telegram_link']}")
        print(f"Twitter Link: {channel_data['twitter_link']}")
        print(f"Website Link: {channel_data['website_link']}")
    
    await scraper.client.disconnect()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())