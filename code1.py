import random
import requests
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Slack Bot Token
slack_token = "YOUR_SLACK_BOT_TOKEN"
client = WebClient(token=slack_token)

# Google Maps API Key
google_maps_api_key = "YOUR_GOOGLE_MAPS_API_KEY"

def get_matcha_cafes(location):
    # Use Google Places API to search for matcha cafes
    search_url = f"https://maps.googleapis.com/maps/api/place/textsearch/json"
    search_query = f"matcha cafes in {location}"
    response = requests.get(search_url, params={
        "query": search_query,
        "key": google_maps_api_key
    })
    
    results = response.json().get("results", [])
    
    # If no results are found, return a message
    if not results:
        return "Sorry, no matcha cafes found in that area."
    
    # Randomly select a cafe
    selected_cafe = random.choice(results)
    name = selected_cafe["name"]
    address = selected_cafe["formatted_address"]
    link = f"https://www.google.com/maps/search/?q={name.replace(' ', '+')}"
    
    return f"Here's a matcha cafe for you!\n*Name*: {name}\n*Address*: {address}\n*Link*: {link}"

def post_to_slack(message, channel="#general"):
    try:
        # Send a message to Slack
        response = client.chat_postMessage(channel=channel, text=message)
    except SlackApiError as e:
        print(f"Error sending message: {e.response['error']}")

def handle_slack_event(event):
    # Check if the message is a command (like !matcha)
    if event.get("text", "").startswith("!matcha"):
        location = event.get("text", "").replace("!matcha", "").strip() or "New York"  # Default location: New York
        cafes_message = get_matcha_cafes(location)
        post_to_slack(cafes_message, event['channel'])

# Example: Handling Slack Events
# This part assumes you are listening to events using the Slack Events API.
# You'll need to set up a server to receive events or use Slack's RTM API for real-time events.
