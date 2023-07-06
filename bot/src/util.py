from datetime import datetime, timedelta
from genshin.types import Game
from models import DiscordUser, \
    HoyolabAccount, \
    RedeemedGenshinCode, \
    RedeemedStarRailCode, \
    DailyCheckInStatus
from database import db_session
from dotenv import dotenv_values

config = dotenv_values(".env")

def get_all_discord_ids() -> list[int]:
    return [user.id for user in db_session.query(DiscordUser).all()]

def check_genshin_redeemed_code(code: str) -> bool:
    return db_session.query(RedeemedGenshinCode) \
        .filter(RedeemedGenshinCode.code == code).first() is not None

def check_starrail_redeemed_code(code: str) -> bool:
    return db_session.query(RedeemedStarRailCode) \
        .filter(RedeemedStarRailCode.code == code).first() is not None

def add_genshin_code(code: str) -> None:
    db_session.add(RedeemedGenshinCode(code=code))
    db_session.commit()

def add_starrail_code(code: str) -> None:
    db_session.add(RedeemedStarRailCode(code=code))
    db_session.commit()

def get_recent_genshin_codes() -> list[RedeemedGenshinCode]:
    return db_session.query(RedeemedGenshinCode) \
        .filter(RedeemedGenshinCode.created_at >= datetime.now() - timedelta(days=1)).all()

def get_recent_starrail_codes() -> list[RedeemedStarRailCode]:
    return db_session.query(RedeemedStarRailCode) \
        .filter(RedeemedStarRailCode.created_at >= datetime.now() - timedelta(days=1)).all()

def get_all_genshin_accounts(only_enabled=False) -> list[HoyolabAccount]:
    query = db_session.query(HoyolabAccount) \
        .filter(HoyolabAccount.genshin_uid.is_not(None))
    if only_enabled:
        return query.filter(HoyolabAccount.is_disabled.is_(False)).all()
    return query.all()

def get_all_starrail_accounts(only_enabled=False) -> list[HoyolabAccount]:
    query = db_session.query(HoyolabAccount) \
        .filter(HoyolabAccount.starrail_uid.is_not(None))
    if only_enabled:
        return query.filter(HoyolabAccount.is_disabled.is_(False)).all()
    return query.all()

def get_all_genshin_accounts_with_token() -> list[HoyolabAccount]:
    return db_session.query(HoyolabAccount) \
        .filter(HoyolabAccount.genshin_uid.is_not(None),
                HoyolabAccount.cookie_token.is_not(None)).all()

def get_all_starrail_accounts_with_token() -> list[HoyolabAccount]:
    return db_session.query(HoyolabAccount) \
        .filter(HoyolabAccount.starrail_uid.is_not(None),
                HoyolabAccount.cookie_token.is_not(None)).all()

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

def get_starrail_acc_by_name(name: str) -> HoyolabAccount:
    return db_session.query(HoyolabAccount) \
        .filter(HoyolabAccount.name == name) \
        .filter(HoyolabAccount.starrail_uid != None).first()

def get_starrail_acc_by_discord_id(discord_id: int) -> HoyolabAccount:
    return db_session.query(HoyolabAccount) \
        .filter(HoyolabAccount.discord_user_id == discord_id) \
        .filter(HoyolabAccount.starrail_uid != None).first()

def get_accounts_by_name(name: str) -> list[HoyolabAccount]:
    return db_session.query(HoyolabAccount) \
        .filter(HoyolabAccount.name == name).all()

def get_account_by_name(name: str) -> HoyolabAccount:
    return db_session.query(HoyolabAccount) \
        .filter(HoyolabAccount.name == name).first()

def get_account_by_ltuid(ltuid: str) -> HoyolabAccount:
    return db_session.query(HoyolabAccount) \
        .filter(HoyolabAccount.ltuid == ltuid).first()

def remove_cookie_token(acc: HoyolabAccount) -> None:
    acc.cookie_token = None
    db_session.commit()

def get_genshin_checkin_status(acc: HoyolabAccount) -> DailyCheckInStatus:
    return db_session.query(DailyCheckInStatus) \
        .filter(DailyCheckInStatus.genshin_uid == acc.genshin_uid) \
        .filter(DailyCheckInStatus.game_type == Game.GENSHIN) \
        .first()
