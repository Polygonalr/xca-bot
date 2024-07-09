import sys
import asyncio

from dotenv import dotenv_values
sys.path.append('bot/src')
from database import db_session
from util import get_all_accounts
from keyrings.cryptfile.cryptfile import CryptFileKeyring
import genshin as gs
import time

config = dotenv_values(".env")
DELIMITER = ":::"

async def main():
    kr = CryptFileKeyring()
    try:
        kr.keyring_key = sys.argv[1]
    except ValueError as e:
        print(f"Error: {e}")
        exit(1)

    for account in get_all_accounts(only_enabled=True):
        cred = kr.get_password("xca-bot", account.name)
        if cred == None:
            continue
        un, pw = cred.split(DELIMITER)
        client = gs.Client()
        cookies = await client.login_with_password(un, pw)
        account.cookie_token = cookies.cookie_token_v2
        account.ltoken_v2 = cookies.ltoken_v2
        db_session.commit()
        time.sleep(2.5)

    print("Done!")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 loadcookie <master_password>")
        exit(1)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())