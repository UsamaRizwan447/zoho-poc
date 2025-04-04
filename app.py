import os
import requests
from flask import Flask, redirect, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Load environment variables
CLIENT_ID = os.getenv("ZOHO_CLIENT_ID")
CLIENT_SECRET = os.getenv("ZOHO_CLIENT_SECRET")
REDIRECT_URI = os.getenv("ZOHO_REDIRECT_URI") # Must match in Zoho Developer Console

# Store tokens (You should use a database for real applications)
TOKEN_URL = os.getenv("ZOHO_TOKEN_URL")
AUTH_URL = os.getenv("ZOHO_AUTH_URL")

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")  # Persisted in Render's environment variables
REFRESH_TOKEN = os.getenv("REFRESH_TOKEN")

@app.route("/")
def home():
    return "Zoho OAuth Integration Active!"

# Generate Authorization URL
@app.route("/authorize")
def authorize():
    auth_url = (
        f"{AUTH_URL}?client_id={CLIENT_ID}"
        f"&response_type=code&redirect_uri={REDIRECT_URI}"
        f"&scope=Desk.tickets.ALL,ZohoDesk.contacts.ALL"
        f"&access_type=offline&prompt=consent"
    )
    return redirect(auth_url)

# Handle Callback & Exchange Code for Access Token
@app.route("/oauth/callback")
def callback():
    global ACCESS_TOKEN, REFRESH_TOKEN

    code = request.args.get("code")
    if not code:
        return jsonify({"error": "Authorization code missing"}), 400

    # Exchange authorization code for access token
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI,
        "code": code,
    }

    response = requests.post(TOKEN_URL, data=data)
    token_data = response.json()

    if "access_token" in token_data:
        ACCESS_TOKEN = token_data["access_token"]
        REFRESH_TOKEN = token_data.get("refresh_token")  # Save for future token refresh
        return jsonify({"message": "Authorization successful!", "access_token": ACCESS_TOKEN, "refresh_token": REFRESH_TOKEN})
    
    return jsonify({"error": "Failed to get access token", "response": token_data})

# Refresh Access Token when it expires
@app.route("/refresh_token")
def refresh_token():
    global ACCESS_TOKEN

    if not REFRESH_TOKEN:
        return jsonify({"error": "Refresh token not available"}), 400

    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "refresh_token",
        "refresh_token": REFRESH_TOKEN,
    }

    response = requests.post(TOKEN_URL, data=data)
    token_data = response.json()

    if "access_token" in token_data:
        ACCESS_TOKEN = token_data["access_token"]
        return jsonify({"message": "Token refreshed successfully!", "access_token": ACCESS_TOKEN})
    
    return jsonify({"error": "Failed to refresh token", "response": token_data})

@app.route('/webhook', methods=['GET', 'POST'])
def zoho_webhook():

    if request.method == 'GET':
        return "Zoho Webhook Verification", 200  # Just return a 200 response
    
    data = request.json  # Get JSON payload from Zoho Desk
    print("Received Webhook:", data)  # Debugging

    # Example processing
    if data.get("status") == "Resolved":
        ticket_id = data.get("ticketId")
        subject = data.get("subject")
        print(f"Ticket {ticket_id} resolved: {subject}")

    return jsonify({"message": "Webhook received successfully"}), 200

if __name__ == "__main__":
    app.run(debug=True)
