from flask import Flask, render_template, jsonify, request
from flask_pymongo import PyMongo
import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve API key from environment variables
api_key = os.getenv("API_KEY")
if not api_key:
    raise ValueError("API_KEY environment variable not set")

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb+srv://openai:openai07@cluster1.hov3w36.mongodb.net/chatgpt"
mongo = PyMongo(app)

def generate_text(prompt):
    url = "https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent"
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key
    }
    data = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()  # Raise an exception for HTTP errors
    return response.json()

@app.route("/")
def home():
    try:
        chats = mongo.db.chats.find({})
        myChats = [chat for chat in chats]
        print(myChats)
        return render_template("index.html", myChats=myChats)
    except Exception as e:
        print(f"Error in home route: {e}")
        return "An error occurred", 500

@app.route("/api", methods=["GET", "POST"])
def qa():
    try:
        if request.method == "POST":
            print(request.json)
            question = request.json.get("question")
            chat = mongo.db.chats.find_one({"question": question})
            print(chat)
            if chat:
                data = {"question": question, "answer": f"{chat['answer']}"}
                return jsonify(data)
            else:
                # Call the API to generate a response
                response = generate_text(question)
                print(response)
                # Extract answer from response
                answer = response['candidates'][0]['content']['parts'][0]['text']
                data = {"question": question, "answer": answer}
                mongo.db.chats.insert_one({"question": question, "answer": answer})
                return jsonify(data)

        data = {"result": "Thank you! I'm just a machine learning model designed to respond to questions and generate text based on my training data. Is there anything specific you'd like to ask or discuss?"}
        return jsonify(data)
    except Exception as e:
        print(f"Error in API route: {e}")
        return jsonify({"error": "An internal error occurred"}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5001)
