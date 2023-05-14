from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

"""Model which represents a Discord user"""
class DiscordUser(Base):
    __tablename__ = "discord_users"

    """Discord user ID"""
    id = Column(Integer, primary_key=True, autoincrement=False)
    hoyolab_accounts = relationship("HoyolabAccount", back_populates="discord_user")

    def __init__(self, id: int):
        self.id = id
    
    def __repr__(self):
        return f"<DiscordUser {self.id}>"

"""Model which represents a Hoyolab account"""
class HoyolabAccount(Base):
    __tablename__ = "hoyolab_accounts"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    ltuid = Column(Integer)
    ltoken = Column(String)
    cookie_token = Column(String, nullable=True)

    starrail_uid = Column(Integer, nullable=True)
    genshin_uid = Column(Integer, nullable=True)

    discord_user_id = Column(Integer, ForeignKey("discord_users.id"))
    discord_user = relationship("DiscordUser", back_populates="hoyolab_accounts")

    def __init__(self, name: str, ltuid: int, ltoken: str, cookie_token: str, discord_user_id: int, starrail_uid: int = None, genshin_uid: int = None):
        self.name = name
        self.ltuid = ltuid
        self.ltoken = ltoken
        self.cookie_token = cookie_token
        self.discord_user_id = discord_user_id
        self.is_disabled = False
        self.starrail_uid = starrail_uid
        self.genshin_uid = genshin_uid


    def __repr__(self):
        return f"<HoyolabAccount {self.id} {self.name}>"


"""For tracking genshin codes redeemed through the bot"""
class RedeemedGenshinCode(Base):
    __tablename__ = "redeemed_genshin_codes"
    id = Column(Integer, primary_key=True)
    code = Column(String)

    def __init__(self, code: str):
        self.code = code
    
    def __repr__(self):
        return f"<RedeemedGenshinCode {self.id} {self.code}>"

"""For tracking star rail codes redeemed through the bot"""
class RedeemedStarRailCode(Base):
    __tablename__ = "redeemed_starrail_codes"
    id = Column(Integer, primary_key=True)
    code = Column(String)

    def __init__(self, code: str):
        self.code = code
    
    def __repr__(self):
        return f"<RedeemedStarRailCode {self.id} {self.code}>"
