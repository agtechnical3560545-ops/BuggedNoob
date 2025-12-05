# app.py
from flask import Flask, render_template, request, jsonify
import main  # Bot code

import os

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/trigger_emote", methods=["POST"])
def trigger_emote():
    data = request.form
    tc = data.get("tc")
    uids = [
        data.get("uid1"),
        data.get("uid2"),
        data.get("uid3"),
        data.get("uid4"),
        data.get("uid5"),
        data.get("uid6")
    ]
    emote_id = data.get("emote_id")

    try:
        response = main.trigger_emote(tc, uids, emote_id)
        return jsonify({"status": "success", "response": response})
    except Exception as e:
        return jsonify({"status": "error", "response": str(e)})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
