import asyncio
import genshin as gs

from models import DailyCheckInStatus, CheckInStatus
from database import init_db, db_session
from util import get_all_genshin_accounts, get_all_starrail_accounts

'''
Claim daily rewards for all Genshin and Star Rail accounts.
Badly written code without DRY but it works for now.
'''
async def checkin():
    print(get_all_genshin_accounts())
    print(get_all_starrail_accounts())
    for acc in get_all_genshin_accounts():
        client = gs.Client({
            "ltuid": acc.ltuid,
            "ltoken": acc.ltoken,
        }, game=gs.Game.GENSHIN)
        try:
            await client.claim_daily_reward(reward=False)
            query = db_session.query(DailyCheckInStatus).filter(DailyCheckInStatus.account_id == acc.id, DailyCheckInStatus.game_type == gs.Game.GENSHIN)
            if query.count() == 0:
                status = DailyCheckInStatus(acc.id, gs.Game.GENSHIN, CheckInStatus.success)
                db_session.add(status)
            else:
                query.update({"status": CheckInStatus.success})
        except gs.AlreadyClaimed:
            query = db_session.query(DailyCheckInStatus).filter(DailyCheckInStatus.account_id == acc.id, DailyCheckInStatus.game_type == gs.Game.GENSHIN)
            if query.count() == 0:
                status = DailyCheckInStatus(acc.id, gs.Game.GENSHIN, CheckInStatus.claimed)
                db_session.add(status)
            else:
                query.update({"status": CheckInStatus.claimed})
        except gs.GeetestTriggered:
            query = db_session.query(DailyCheckInStatus).filter(DailyCheckInStatus.account_id == acc.id, DailyCheckInStatus.game_type == gs.Game.GENSHIN)
            if query.count() == 0:
                status = DailyCheckInStatus(acc.id, gs.Game.GENSHIN, CheckInStatus.failed)
                db_session.add(status)
            else:
                query.update({"status": CheckInStatus.failed})
        db_session.commit()
        await asyncio.sleep(5)

    for acc in get_all_starrail_accounts():
        client = gs.Client({
            "ltuid": acc.ltuid,
            "ltoken": acc.ltoken,
        }, game=gs.Game.STARRAIL)
        try:
            await client.claim_daily_reward(reward=False)
            query = db_session.query(DailyCheckInStatus).filter(DailyCheckInStatus.account_id == acc.id, DailyCheckInStatus.game_type == gs.Game.STARRAIL)
            if query.count() == 0:
                status = DailyCheckInStatus(acc.id, gs.Game.STARRAIL, CheckInStatus.success)
                db_session.add(status)
            else:
                query.update({"status": CheckInStatus.success})
        except gs.AlreadyClaimed:
            query = db_session.query(DailyCheckInStatus).filter(DailyCheckInStatus.account_id == acc.id, DailyCheckInStatus.game_type == gs.Game.STARRAIL)
            if query.count() == 0:
                status = DailyCheckInStatus(acc.id, gs.Game.STARRAIL, CheckInStatus.claimed)
                db_session.add(status)
            else:
                query.update({"status": CheckInStatus.claimed})
        except gs.GeetestTriggered:
            query = db_session.query(DailyCheckInStatus).filter(DailyCheckInStatus.account_id == acc.id, DailyCheckInStatus.game_type == gs.Game.STARRAIL)
            if query.count() == 0:
                status = DailyCheckInStatus(acc.id, gs.Game.STARRAIL, CheckInStatus.failed)
                db_session.add(status)
            else:
                query.update({"status": CheckInStatus.failed})
        db_session.commit()
        await asyncio.sleep(5)
            

if __name__ == "__main__":
    init_db()
    asyncio.run(checkin())
