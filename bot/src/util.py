from datetime import datetime, timedelta
from genshin.types import Game
from genshin.client import Client
from models import (
    DiscordUser,
    HoyolabAccount,
    RedeemedGenshinCode,
    RedeemedStarRailCode,
    DailyCheckInStatus,
    SKPortAccount,
)
from database import db_session
from dotenv import dotenv_values
import requests
import time
import json
import hmac
import hashlib
from urllib.parse import urlparse, parse_qs, urlencode

config = dotenv_values(".env")

def get_skport_common_headers() -> object:
    return {
        "accept": "application/json",
        "accept-language": "en",
        "content-type": "application/json",
        "platform": "3",
        "priority": "u=3, i",
        "sec-ch-ua":
        '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "sk-language": "en",
        "origin": "https://game.skport.com",
        "referer": "https://game.skport.com/",
        "x-language": "en-us",
        "vname": "1.0.0",
        "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 SKPort/0.7.1(701014)",
        "timestamp": str(int(time.time())),
    }

def get_all_discord_ids() -> list[int]:
    return [user.id for user in db_session.query(DiscordUser).all()]


def check_genshin_redeemed_code(code: str) -> bool:
    return (
        db_session.query(RedeemedGenshinCode)
        .filter(RedeemedGenshinCode.code == code)
        .first()
        is not None
    )


def check_starrail_redeemed_code(code: str) -> bool:
    return (
        db_session.query(RedeemedStarRailCode)
        .filter(RedeemedStarRailCode.code == code)
        .first()
        is not None
    )


def add_genshin_code(code: str) -> None:
    db_session.add(RedeemedGenshinCode(code=code))
    db_session.commit()


def add_starrail_code(code: str) -> None:
    db_session.add(RedeemedStarRailCode(code=code))
    db_session.commit()


def get_recent_genshin_codes() -> list[RedeemedGenshinCode]:
    return (
        db_session.query(RedeemedGenshinCode)
        .filter(RedeemedGenshinCode.created_at >= datetime.now() - timedelta(days=1))
        .all()
    )


def get_recent_starrail_codes() -> list[RedeemedStarRailCode]:
    return (
        db_session.query(RedeemedStarRailCode)
        .filter(RedeemedStarRailCode.created_at >= datetime.now() - timedelta(days=1))
        .all()
    )


def get_all_accounts(only_enabled=False) -> list[HoyolabAccount]:
    if only_enabled:
        return (
            db_session.query(HoyolabAccount)
            .filter(HoyolabAccount.is_disabled.is_(False))
            .all()
        )
    return db_session.query(HoyolabAccount).all()


def get_all_genshin_accounts(only_enabled=False) -> list[HoyolabAccount]:
    query = db_session.query(HoyolabAccount).filter(
        HoyolabAccount.genshin_uid.is_not(None)
    )
    if only_enabled:
        return query.filter(HoyolabAccount.is_disabled.is_(False)).all()
    return query.all()


def get_all_starrail_accounts(only_enabled=False) -> list[HoyolabAccount]:
    query = db_session.query(HoyolabAccount).filter(
        HoyolabAccount.starrail_uid.is_not(None)
    )
    if only_enabled:
        return query.filter(HoyolabAccount.is_disabled.is_(False)).all()
    return query.all()


def get_all_zzz_accounts(only_enabled=False) -> list[HoyolabAccount]:
    query = db_session.query(HoyolabAccount).filter(HoyolabAccount.zzz_uid.is_not(None))
    if only_enabled:
        return query.filter(HoyolabAccount.is_disabled.is_(False)).all()
    return query.all()


def get_all_skport_accounts() -> list[SKPortAccount]:
    query = db_session.query(SKPortAccount)
    return query.all()


def get_all_genshin_accounts_with_token() -> list[HoyolabAccount]:
    return (
        db_session.query(HoyolabAccount)
        .filter(
            HoyolabAccount.genshin_uid.is_not(None),
            HoyolabAccount.cookie_token.is_not(None),
        )
        .all()
    )


def get_all_starrail_accounts_with_token() -> list[HoyolabAccount]:
    return (
        db_session.query(HoyolabAccount)
        .filter(
            HoyolabAccount.starrail_uid.is_not(None),
            HoyolabAccount.cookie_token.is_not(None),
        )
        .all()
    )


def get_all_zzz_accounts_with_token() -> list[HoyolabAccount]:
    return (
        db_session.query(HoyolabAccount)
        .filter(
            HoyolabAccount.zzz_uid.is_not(None),
            HoyolabAccount.cookie_token.is_not(None),
        )
        .all()
    )


def get_accounts_by_discord_id(discord_id: int) -> list[HoyolabAccount]:
    return (
        db_session.query(HoyolabAccount)
        .filter(HoyolabAccount.discord_user_id == discord_id)
        .all()
    )


"""Below 2 functions are written on the assumption that every user has only 1 genshin account"""


def get_genshin_acc_by_name(name: str) -> HoyolabAccount:
    return (
        db_session.query(HoyolabAccount)
        .filter(HoyolabAccount.name == name)
        .filter(HoyolabAccount.genshin_uid != None)
        .first()
    )


def get_genshin_acc_by_discord_id(discord_id: int) -> HoyolabAccount:
    return (
        db_session.query(HoyolabAccount)
        .filter(HoyolabAccount.discord_user_id == discord_id)
        .filter(HoyolabAccount.genshin_uid != None)
        .first()
    )


def get_starrail_acc_by_name(name: str) -> HoyolabAccount:
    return (
        db_session.query(HoyolabAccount)
        .filter(HoyolabAccount.name == name)
        .filter(HoyolabAccount.starrail_uid != None)
        .first()
    )


def get_starrail_acc_by_discord_id(discord_id: int) -> HoyolabAccount:
    return (
        db_session.query(HoyolabAccount)
        .filter(HoyolabAccount.discord_user_id == discord_id)
        .filter(HoyolabAccount.starrail_uid != None)
        .first()
    )


def get_zzz_acc_by_name(name: str) -> HoyolabAccount:
    return (
        db_session.query(HoyolabAccount)
        .filter(HoyolabAccount.name == name)
        .filter(HoyolabAccount.zzz_uid != None)
        .first()
    )


def get_zzz_acc_by_discord_id(discord_id: int) -> HoyolabAccount:
    return (
        db_session.query(HoyolabAccount)
        .filter(HoyolabAccount.discord_user_id == discord_id)
        .filter(HoyolabAccount.zzz_uid != None)
        .first()
    )


def get_accounts_by_name(name: str) -> list[HoyolabAccount]:
    return db_session.query(HoyolabAccount).filter(HoyolabAccount.name == name).all()


def get_account_by_name(name: str) -> HoyolabAccount:
    return db_session.query(HoyolabAccount).filter(HoyolabAccount.name == name).first()


def get_account_by_ltuid(ltuid: str) -> HoyolabAccount:
    return (
        db_session.query(HoyolabAccount).filter(HoyolabAccount.ltuid == ltuid).first()
    )


def remove_cookie_token(acc: HoyolabAccount) -> None:
    acc.cookie_token = None
    acc.ltoken_v2 = None
    db_session.commit()


def get_genshin_checkin_status(acc: HoyolabAccount) -> DailyCheckInStatus:
    return (
        db_session.query(DailyCheckInStatus)
        .filter(DailyCheckInStatus.genshin_uid == acc.genshin_uid)
        .filter(DailyCheckInStatus.game_type == Game.GENSHIN)
        .first()
    )


def hoyolab_client_init(acc: HoyolabAccount, game: Game) -> Client:
    client = Client(
        {
            "ltuid_v2": acc.ltuid,
            "ltoken_v2": acc.ltoken_v2,
        },
        game=game,
    )
    return client


def get_skport_cred(acc: SKPortAccount, force: False) -> str:
    if acc.cred is None or force:
        url = 'https://as.gryphline.com/user/oauth2/v2/grant'
        headers = {
            'sec-fetch-site': 'cross-site',
            'referrer': 'https://www.skport.com/',
            'Content-Type': 'application/json',
        }
        payload = {
            'token': acc.account_token,
            'appCode': '6eb76d4e13aa36e6',
            'type': 0,
        }
        response = requests.post(url, json=payload, headers=headers)
        code = response.json()["data"]["code"]

        cred_url = 'https://zonai.skport.com/web/v1/user/auth/generate_cred_by_code'
        cred_headers = {
            'platform': '3',
            'referrer': 'https://www.skport.com/',
            'origin': 'https://www.skport.com',
            'sec-ch-ua': '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
            'priority': 'u=1, i',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'Content-Type': 'application/json',
        }
        cred_payload = {
            'code': code,
            'kind': 1,
        }
        cred_response = requests.post(cred_url, json=cred_payload, headers=cred_headers)
        acc.cred = cred_response.json()["data"]["cred"]
        acc.user_id = cred_response.json()["data"]["userId"]
        db_session.commit()
    return acc.cred

def generate_skport_sign(acc: SKPortAccount, path: str, query: str, timestamp: str) -> str:
    common_headers = get_skport_common_headers()
    salt = acc.account_token
    headers = {
        "platform": common_headers["platform"],
        "timestamp": timestamp,
        "dId": "",
        "vName": common_headers["vname"],
    }
    
    header_json = json.dumps(headers, separators=(',', ':'))
    s = f"{path}{query}{timestamp}{header_json}"
    hmac_hash = hmac.new(salt.encode('utf-8'), s.encode('utf-8'), hashlib.sha256).hexdigest()
    md5_hash = hashlib.md5(hmac_hash.encode('utf-8')).hexdigest()
    
    return md5_hash

def get_query_string(url: str, params: object):
    url_obj = urlparse(url)
    pathname = url_obj.path
    query_params = parse_qs(url_obj.query, keep_blank_values=True)
    flattened_params = {k: v[0] if isinstance(v, list) and len(v) == 1 else v for k, v in query_params.items()}
    
    if params:
        for key, val in params.items():
            if val is not None:
                flattened_params[key] = str(val)
    query_string = urlencode(flattened_params)
    
    return pathname, query_string