from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv


load_dotenv()


app = Flask(__name__)


@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Flask Zoho POC is running"})


if __name__ == "__main__":
    app.run(debug=True)
    