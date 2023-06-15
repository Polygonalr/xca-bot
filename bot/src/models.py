import enum
from genshin import Game
from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, Enum, TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

'''Model which represents a Discord user'''
class DiscordUser(Base):
    __tablename__ = "discord_users"

    '''Discord user ID'''
    id = Column(Integer, primary_key=True, autoincrement=False)
    hoyolab_accounts = relationship("HoyolabAccount", back_populates="discord_user")

    def __init__(self, id: int):
        self.id = id
    
    def __repr__(self):
        return f"<DiscordUser {self.id}>"

'''Model which represents a Hoyolab account'''
class HoyolabAccount(Base):
    __tablename__ = "hoyolab_accounts"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    ltuid = Column(Integer)
    ltoken = Column(String)
    cookie_token = Column(String, nullable=True)
    is_disabled = Column(Boolean)

    starrail_uid = Column(Integer, nullable=True)
    genshin_uid = Column(Integer, nullable=True)

    discord_user_id = Column(Integer, ForeignKey("discord_users.id"))
    discord_user = relationship("DiscordUser", back_populates="hoyolab_accounts")
    daily_checkin_status = relationship("DailyCheckInStatus", back_populates="account")

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
    
class CheckInStatus(enum.Enum):
    success = 1
    failed = 2
    claimed = 3
    unknown = 4

'''For storing daily check-in status of each account'''
class DailyCheckInStatus(Base):
    __tablename__ = "daily_checkin_status"
    account_id = Column(Integer, ForeignKey("hoyolab_accounts.id"), primary_key=True)
    game_type = Column(Enum(Game), primary_key=True)
    status = Column(Enum(CheckInStatus), name="daily_checkin_status_enum", nullable=False)
    last_update = Column(TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp())
    account = relationship("HoyolabAccount", back_populates="daily_checkin_status")

    def __init__(self, account_id: int, game_type: Game, status: CheckInStatus):
        self.account_id = account_id
        self.game_type = game_type
        self.status = status
    
    def __repr__(self):
        return f"<DailyCheckInStatus {self.account_id} {self.game_type} {self.status}>"


'''For tracking genshin codes redeemed through the bot'''
class RedeemedGenshinCode(Base):
    __tablename__ = "redeemed_genshin_codes"
    id = Column(Integer, primary_key=True)
    code = Column(String)
    created_at = Column(TIMESTAMP, server_default=func.now())

    def __init__(self, code: str):
        self.code = code
    
    def __repr__(self):
        return f"<RedeemedGenshinCode {self.id} {self.code}>"

'''For tracking star rail codes redeemed through the bot'''
class RedeemedStarRailCode(Base):
    __tablename__ = "redeemed_starrail_codes"
    id = Column(Integer, primary_key=True)
    code = Column(String)
    created_at = Column(TIMESTAMP, server_default=func.now())

    def __init__(self, code: str):
        self.code = code
    
    def __repr__(self):
        return f"<RedeemedStarRailCode {self.id} {self.code}>"
