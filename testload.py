import genshin as gs
from database import *
from models import *
init_db()
account = db_session.query(HoyolabAccount).first()
client = gs.Client({"ltuid": account.ltuid, "ltoken": account.ltoken})