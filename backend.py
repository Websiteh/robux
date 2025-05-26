from flask import Flask, jsonify, request

app = Flask(__name__)

PASSWORD = "Wachtwoord123"

# Dummy sales data voorbeeld
dummy_sales = [
    {
        "user": "RobloxFan1",
        "item": "Cool Shirt",
        "group_name": "Pastel Polo Squad",
        "group_logo": "https://i.imgur.com/BZN1xJo.png",
        "robux": 100,
        "time": "5 minuten geleden",
        "profile_pic": "https://www.roblox.com/headshot-thumbnail/image?userId=1&width=50&height=50&format=png"
    },
    {
        "user": "RalphLover",
        "item": "Fancy Hat",
        "group_name": "Ralph Lauren Babes",
        "group_logo": "https://i.imgur.com/GVlEl9q.png",
        "robux": 250,
        "time": "10 minuten geleden",
        "profile_pic": "https://www.roblox.com/headshot-thumbnail/image?userId=2&width=50&height=50&format=png"
    }
]

@app.route('/api/sales')
def get_sales():
    auth = request.headers.get('Authorization')
    if auth != PASSWORD:
        return jsonify({"error": "Unauthorized"}), 401

    return jsonify({"sales": dummy_sales})

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
