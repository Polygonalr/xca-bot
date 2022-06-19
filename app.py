import os
import asyncio
import time
import datetime
import json
import genshin as gs

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

with open(os.path.join(__location__, 'cookies.json')) as f:
    data = json.load(f)


async def check_everyone_in():
    logs = open("checkin-log.txt", "w")
    logs.write("Checking in! " + datetime.datetime.now().isoformat() + "\n")
    for i, acc in enumerate(data):
        client = gs.Client({"ltuid": acc['ltuid'], "ltoken": acc['ltoken']}, game=gs.Game.GENSHIN)
        try:
            await client.claim_daily_reward(reward=False)
            logs.write("Successfully signed in for {}".format(acc["name"]) + "\n")
        except gs.AlreadyClaimed:
            logs.write("{} has already claimed the reward!".format(acc["name"]) + "\n")
        if not i == len(data) - 1:
            logs.write("Waiting for 10 seconds before next sign-in" + "\n")
            time.sleep(10)
    logs.close()


if __name__ == "__main__":
    asyncio.run(check_everyone_in())

