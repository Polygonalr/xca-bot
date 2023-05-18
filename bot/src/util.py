from models import HoyolabAccount, RedeemedGenshinCode, RedeemedStarRailCode
from database import db_session
from dotenv import dotenv_values

config = dotenv_values(".env")

def check_genshin_redeemed_code(code: str) -> bool:
    return db_session.query(RedeemedGenshinCode) \
        .filter(RedeemedGenshinCode.code == code).first() is not None

def check_star_rail_redeemed_code(code: str) -> bool:
    return db_session.query(RedeemedStarRailCode) \
        .filter(RedeemedStarRailCode.code == code).first() is not None

def get_all_genshin_accounts() -> list[HoyolabAccount]:
    return db_session.query(HoyolabAccount) \
        .filter(HoyolabAccount.is_genshin == True).all()

def get_all_star_rail_accounts() -> list[HoyolabAccount]:
    return db_session.query(HoyolabAccount) \
        .filter(HoyolabAccount.is_starrail == True).all()

def get_accounts_by_discord_id(discord_id: int) -> list[HoyolabAccount]:
    return db_session.query(HoyolabAccount) \
        .filter(HoyolabAccount.discord_user_id == discord_id).all()

'''Below 2 functions are written on the assumption that every user has only 1 genshin account'''
def get_genshin_acc_by_name(name: str) -> HoyolabAccount:
    return db_session.query(HoyolabAccount) \
        .filter(HoyolabAccount.name == name) \
        .filter(HoyolabAccount.genshin_uid != None).first()

def get_genshin_acc_by_discord_id(discord_id: int) -> HoyolabAccount:
    return db_session.query(HoyolabAccount) \
        .filter(HoyolabAccount.discord_user_id == discord_id) \
        .filter(HoyolabAccount.genshin_uid != None).first()

def get_accounts_by_name(name: str) -> list[HoyolabAccount]:
    return db_session.query(HoyolabAccount) \
        .filter(HoyolabAccount.name == name).all()

def get_account_by_name(name: str) -> HoyolabAccount:
    return db_session.query(HoyolabAccount) \
        .filter(HoyolabAccount.name == name).first()