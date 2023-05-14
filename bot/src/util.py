from models import RedeemedGenshinCode, RedeemedStarRailCode

def check_genshin_redeemed_code(code: str) -> bool:
    from database import db_session
    return db_session.query(RedeemedGenshinCode).filter(RedeemedGenshinCode.code == code).first() is not None

def check_star_rail_redeemed_code(code: str) -> bool:
    from database import db_session
    return db_session.query(RedeemedStarRailCode).filter(RedeemedStarRailCode.code == code).first() is not None