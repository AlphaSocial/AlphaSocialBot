from flask import Flask, request, jsonify
from flask_cors import CORS
from scraper import TelegramScraper
import asyncio
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Add a basic root route
@app.route('/')
def home():
    return jsonify({"status": "Server is running", "endpoints": ["/scrape"]}), 200

@app.route('/scrape', methods=['POST', 'OPTIONS'])
def scrape_channel():
    print("Received request to /scrape")  # Debug logging
    
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = app.make_default_options_response()
        response.headers['Access-Control-Allow-Methods'] = 'POST'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response

    try:
        print("Request JSON:", request.json)  # Debug logging
        channel_url = request.json.get('channel_url')
        
        if not channel_url:
            return jsonify({'error': 'No channel URL provided'}), 400
        
        print(f"Processing channel URL: {channel_url}")  # Debug logging
        
        async def run_scraper():
            try:
                scraper = TelegramScraper()
                await scraper.connect()
                data = await scraper.get_channel_info(channel_url)
                await scraper.client.disconnect()
                return data
            except Exception as e:
                print(f"Scraper error: {str(e)}")  # Debug logging
                return None
        
        data = asyncio.run(run_scraper())
        
        if data:
            print("Successfully scraped data:", data)  # Debug logging
            return jsonify(data)
        else:
            return jsonify({'error': 'Failed to scrape channel'}), 500
            
    except Exception as e:
        print(f"Server error: {str(e)}")  # Debug logging
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    print(f"Starting server on port {port}")  # Debug logging
    app.run(host='0.0.0.0', port=port)