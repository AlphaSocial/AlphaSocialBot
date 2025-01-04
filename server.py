from flask import Flask, request, jsonify
from flask_cors import CORS
from scraper import TelegramScraper
import asyncio

app = Flask(__name__)
CORS(app)  # This allows any website to access your API (for testing)

@app.route('/scrape', methods=['POST'])
def scrape_channel():
    # Get the channel URL from the request
    channel_url = request.json.get('channel_url')
    
    if not channel_url:
        return jsonify({'error': 'No channel URL provided'}), 400
    
    # Create scraper and get data
    async def run_scraper():
        scraper = TelegramScraper()
        await scraper.connect()
        data = await scraper.get_channel_info(channel_url)
        await scraper.client.disconnect()
        return data
    
    # Run the scraper
    data = asyncio.run(run_scraper())
    
    if data:
        return jsonify(data)
    else:
        return jsonify({'error': 'Failed to scrape channel'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)