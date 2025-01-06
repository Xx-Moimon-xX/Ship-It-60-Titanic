import os
import random
import requests
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from flask import Flask, request, jsonify

# Slack token (use your own Slack bot token)
SLACK_BOT_TOKEN = 'xoxb-522979612549-8255454727794-7sb4kKDARJgpwaH6p7tURJTF'
client = WebClient(token=SLACK_BOT_TOKEN)

# Google Maps API key (use your own API key)
GOOGLE_MAPS_API_KEY = 'AIzaSyBue233NkLcfkFxjrde3o339iZh7p164uc'
# PLACES_API_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"
PLACES_API_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"

# Flask app to handle Slack events
app = Flask(__name__)

def get_matcha_cafes(location = None):
    # Send a request to Google Maps API to get Matcha cafe results
    search_query = "cafes that sell matcha"
    response = requests.get(PLACES_API_URL, param={
        'key' = "AIzaSyBue233NkLcfkFxjrde3o339iZh7p164uc",
        'location' = "-33.8736507, 151.207075",
        'radius' = "1000",
        'query' = search_query
    })

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        results = data.get('results', [])
        
        if not results:
            return "Sorry, no matcha cafes found."

        # Randomly select a cafe
        cafe = random.choice(results)

        # Extract necessary details
        name = cafe.get('name')
        address = cafe.get('formatted_address')
        place_id = cafe.get('place_id')
        rating = cafe.get('rating', 'No rating available')

        # Prepare the message
        message = f"*{name}*\nAddress: {address}\nRating: {rating}/5\nhttps://www.google.com/maps/place/?q=place_id:{place_id}"
        return message
    else:
        return "Failed to fetch cafes from Google Maps API."

def send_slack_message(channel, message):
    try:
        response = client.chat_postMessage(
            channel=channel,
            text=message
        )
        print(response)
        return response
    except SlackApiError as e:
        return f"Error sending message: {e.response['error']}"

@app.route('/slack/events', methods=['POST'])
def slack_events():
    # Get the incoming payload from Slack
    data = request.json
    event = data.get('event', {})

    # Check if it's a message event
    if event.get('type') == 'message' and 'subtype' not in event:
        text = event.get('text', '').lower()
        channel = event.get('channel')

        # If the message contains "matcha", send a recommendation
        if 'matcha' in text:
            # Optional: Extract a location if provided in the message
            location = "San Francisco"  # Default location
            if 'in' in text:
                location = text.split('in')[-1].strip()

            # Get the matcha cafe recommendation
            recommendation = get_matcha_cafes(location)

            # Send the recommendation to Slack
            send_slack_message(channel, recommendation)

    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(port=3000)
