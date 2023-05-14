from models import HoyolabAccount, RedeemedGenshinCode, RedeemedStarRailCode
from database import db_session

def check_genshin_redeemed_code(code: str) -> bool:
    return db_session.query(RedeemedGenshinCode) \
        .filter(RedeemedGenshinCode.code == code).first() is not None

def check_star_rail_redeemed_code(code: str) -> bool:
    return db_session.query(RedeemedStarRailCode) \
        .filter(RedeemedStarRailCode.code == code).first() is not None

def get_all_genshin_accounts() -> List[HoyolabAccount]:
    return db_session.query(HoyolabAccount) \
        .filter(HoyolabAccount.is_genshin == True).all()

def get_all_star_rail_accounts() -> List[HoyolabAccount]:
    return db_session.query(HoyolabAccount) \
        .filter(HoyolabAccount.is_starrail == True).all()

def get_accounts_by_discord_id(discord_id: int) -> List[HoyolabAccount]:
    return db_session.query(HoyolabAccount) \
        .filter(HoyolabAccount.discord_user_id == discord_id).all()