from flask import Flask, jsonify, render_template
import os

app = Flask(__name__)

MESSAGE_FILE = "message.txt"

@app.route("/")
def index():
    return render_template("mascot.html")

@app.route("/message")
def get_message():
    if os.path.exists(MESSAGE_FILE):
        with open(MESSAGE_FILE, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
        return jsonify({"messages": lines})
    return jsonify({"messages": []})

if __name__ == "__main__":
    app.run(port=5000)