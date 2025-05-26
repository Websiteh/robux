from flask import Flask, jsonify, request, Response
from threading import Thread
from time import sleep, time
import requests

app = Flask(__name__)

# Jouw groepen en logo's (gebruik deze om te matchen in frontend)
GROUPS = {
    "35930799": {"name": "Cothing", "logo": "https://i.imgur.com/LMI06BN.png"},
    "36026449": {"name": "Ralph Lauren Babes", "logo": "https://i.imgur.com/GVlEl9q.png"},
    "36026461": {"name": "Polo Princesses", "logo": "https://i.imgur.com/pyyIzTm.png"},
    "36026484": {"name": "Lauren Luxe Club", "logo": "https://i.imgur.com/SJXH62B.png"},
    "36026516": {"name": "Pastel Polo Squad", "logo": "https://i.imgur.com/BZN1xJo.png"}
}

COOKIE = "_|WARNING:-DO-NOT-SHARE-THIS...je cookie hier"  # Vul hier jouw ROBLOSECURITY cookie in
PASSWORD = "Wachtwoord123"  # Toegangs wachtwoord

# Data opslag in geheugen
sales_data = []
past_ids = {gid: set() for gid in GROUPS.keys()}
past_pending = {gid: 0 for gid in GROUPS.keys()}

# Helper om Roblox profiel pic te halen (optioneel)
def get_profile_picture(user_id):
    try:
        r = requests.get(f'https://www.roblox.com/users/{user_id}/profile')
        html = r.text
        return html.split('<meta property="og:image" content="')[1].split('"')[0]
    except:
        return "https://tr.rbxcdn.com/af0be829bc4349c0b116ae36843a0a91/150/150/AvatarHeadshot/Png"

def poll_groups():
    global sales_data, past_ids, past_pending
    while True:
        for gid, info in GROUPS.items():
            try:
                r = requests.get(f'https://economy.roblox.com/v1/groups/{gid}/revenue/summary/day', cookies={'.ROBLOSECURITY': COOKIE})
                now_pending = r.json().get('pendingRobux', 0)

                if now_pending > past_pending[gid]:
                    trans = requests.get(f'https://economy.roblox.com/v2/groups/{gid}/transactions?cursor=&limit=10&transactionType=Sale', cookies={'.ROBLOSECURITY': COOKIE}).json()
                    for purchase in trans.get('data', []):
                        if purchase['idHash'] not in past_ids[gid]:
                            past_ids[gid].add(purchase['idHash'])
                            past_pending[gid] = now_pending

                            sale = {
                                "group_id": gid,
                                "group_name": info['name'],
                                "group_logo": info['logo'],
                                "user": purchase['agent']['name'],
                                "user_id": purchase['agent']['id'],
                                "item": purchase['details']['name'],
                                "item_id": purchase['details']['id'],
                                "robux": purchase['currency']['amount'],
                                "time": int(time()),
                                "profile_pic": get_profile_picture(purchase['agent']['id'])
                            }
                            sales_data.insert(0, sale)
                            if len(sales_data) > 100:
                                sales_data.pop()  # max 100 sales onthouden
            except Exception as e:
                print(f"Error polling group {info['name']}: {e}")
        sleep(10)  # wacht 10 sec voor de volgende poll

@app.route("/api/sales")
def get_sales():
    auth = request.headers.get("Authorization")
    if auth != PASSWORD:
        return Response("Unauthorized", status=401)

    # Formatteer tijd naar leesbare string
    formatted = []
    from datetime import datetime
    for s in sales_data:
        dt = datetime.utcfromtimestamp(s['time']).strftime('%Y-%m-%d %H:%M:%S')
        formatted.append({**s, "time": dt})
    return jsonify({"sales": formatted})

if __name__ == "__main__":
    # Start polling in aparte thread
    poller = Thread(target=poll_groups, daemon=True)
    poller.start()

    app.run(host="0.0.0.0", port=5000)
