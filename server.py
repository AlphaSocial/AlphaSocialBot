from flask import Flask, request, jsonify
from flask_cors import CORS
from telethon import TelegramClient
from telethon.tl.functions.channels import GetFullChannelRequest
import asyncio
import os
import sys
from datetime import datetime

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# API Credentials
api_id = 29114639
api_hash = '40fa4fdc6cbf04f01f56da6f7b96aad4'

# Initialize Telegram client at the module level
client = None

@app.route('/')
def home():
    return jsonify({"status": "Server is running", "endpoints": ["/scrape"]}), 200

@app.route('/scrape', methods=['POST', 'OPTIONS'])
async def scrape_channel():
    if request.method == 'OPTIONS':
        response = app.make_default_options_response()
        response.headers['Access-Control-Allow-Methods'] = 'POST'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response

    try:
        print("Received scrape request")
        channel_url = request.json.get('channel_url')
        print(f"Channel URL: {channel_url}")

        if not channel_url:
            return jsonify({'error': 'No channel URL provided'}), 400

        global client
        try:
            print("Initializing Telegram client")
            if client is None:
                client = TelegramClient('anon', api_id, api_hash)
            
            print("Starting client")
            await client.start()
            
            print("Getting channel entity")
            channel = await client.get_entity(channel_url)
            print(f"Channel found: {channel.title}")

            # Initialize dictionary for channel info
            channel_data = {
                "name": channel.title,
                "telegram_link": channel_url,
                "twitter_link": "",
                "website_link": "",
                "scrape_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            print("Searching messages")
            messages = await client.get_messages(channel, limit=100)
            
            for message in messages:
                if message.text:
                    text = message.text.lower()
                    if "twitter.com" in text or "x.com" in text:
                        for word in text.split():
                            if "twitter.com" in word or "x.com" in word:
                                channel_data["twitter_link"] = word
                                break
                    
                    if "http://" in text or "https://" in text:
                        words = text.split()
                        for word in words:
                            if word.startswith(("http://", "https://")) and \
                               not ("twitter.com" in word or "x.com" in word or "t.me" in word):
                                channel_data["website_link"] = word
                                break

            print("Scraping completed successfully")
            return jsonify(channel_data)

        except Exception as e:
            print(f"Error in Telegram operations: {str(e)}", file=sys.stderr)
            print(f"Error type: {type(e)}", file=sys.stderr)
            print(f"Error details: {repr(e)}", file=sys.stderr)
            return jsonify({'error': f'Telegram error: {str(e)}'}), 500

    except Exception as e:
        print(f"Server error: {str(e)}", file=sys.stderr)
        return jsonify({'error': f'Server error: {str(e)}'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    print(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port)