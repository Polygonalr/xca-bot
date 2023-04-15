import json
import genshin as gs
with open('cookies.json') as f:
    data = json.load(f)
me = data[0]
client = gs.Client({"ltuid": me['ltuid'], 'ltoken': me['ltoken']})
