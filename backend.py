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

COOKIE = "_|WARNING:-DO-NOT-SHARE-THIS.--Sharing-this-will-allow-someone-to-log-in-as-you-and-to-steal-your-ROBUX-and-items.|_9E07C6DA964BEA375E2E9352F47594A0438D76828A7743CB89A5D4DB341B57B24FDC0F58D684160EF4BAE5338D2A9EB4AD2F44E11F0F55919CEDDC9CE1B825E2E66381AE7820F9BA71C814BE08E8F6D573DE44BEEE17A4971DA163D4CD530AE7DEB62C97D014802454D4DCDA0D758F1ACDD360ED6D333687B2A285C6E52806FFFD67614058E192AFF5D16B186D2DC4C9E483EE2A9B3AEB4C371FA40F258BE0D146EB1178A6426F4C54AB0C26A44B8214E97ACDA522256AB5E32A1134606A00427645027C58214B0A277364E17872C30D410FFAF162C96F785E0CCE8EF4BB9DD75A2A526F6DBD020BDCA636A09BB2587F646981B3A8866FEB5ED7F92A5F18747977AF0F2308BA30C574C4ABA5E6E1B37FF08513BBD1D906F2D510A0ED7247F76F7CA6E0A517F880BDC2BC68F3AD310AB87630F615EEFCB75E8CE00B9B16295F1C877082BD411FF8A595AE9833A93CEE255615808A02A1F310F812F974AD04ECE3EDAA14F6E33C1AC8B123BD05DF5EEBB1FF3809B4A51EFA73297E6B58C679330368A531C66734903AA34A3E495AE12F90A8475668B7F12F3F920416E121A5F509EA82BAD7A73C60466216DD01A8EF3D2D2C57FED280F6A39366C8849822760BAFC8FCEF63B6175925DE3A4D887D91EE376A2828245448448B6157F4BE0F29F049A379491595006B498D2A684BF5F0D5594170123B43A92D40954BE1EBF782AC719CA66490A2AAAAD69B8B50048BC078D896A415E30FD050FD73183C400A5ADAB6888FC433060E0D3D13DDDBA31522058ECC5139FC8B33702891C91F125B73CFC13330491EC9B40EE64AC2D140771C89AF340AAFE30A8FED6051C6B4739104400ACC67451EE66C452D1B253C2C6AF38D0857E8027BDF372C5FFFB09F13C6609CDBBE4905F0F0B833F525403995881977B652573E0D29DEE4FD7A6F3436264D944BB4A70581BF642CDA54C4F1BCC6D6EE4BFCF55A162120861B2383F2795972C9F74C43F511A6D03093819823DD70098E39A57D38A02BCF81B3E1D507266C08AD722AE85CD60623317C62831037A491988B340B3A30AA2FA3EFD5A0EB3FB9E3ECC8942628972122B73E37A7BBE274403F70CA917BA5"  # Vul hier jouw ROBLOSECURITY cookie in
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
