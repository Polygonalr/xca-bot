import asyncio
import genshin as gs

from models import DailyCheckInStatus, CheckInStatus, HoyolabAccount
from database import init_db, db_session
from util import get_all_genshin_accounts, get_all_starrail_accounts, get_all_zzz_accounts

'''
Claim daily rewards for all Genshin, HSR and ZZZ accounts.
Badly written code without DRY but it works for now.
'''
async def checkin():
    for acc in get_all_genshin_accounts(only_enabled=True):
        client = gs.Client({
            "ltuid": acc.ltuid,
            "ltoken": acc.ltoken,
        }, game=gs.Game.GENSHIN)
        query = db_session.query(DailyCheckInStatus).filter(DailyCheckInStatus.account_id == acc.id, DailyCheckInStatus.game_type == gs.Game.GENSHIN)
        try:
            await client.claim_daily_reward(reward=False)
            new_status = CheckInStatus.success
        except gs.AlreadyClaimed:
            new_status = CheckInStatus.claimed
        except gs.GeetestTriggered:
            new_status = CheckInStatus.failed
            # Not too sure which 2 lines of code below works better, so might as well try both
            db_session.query(HoyolabAccount).filter(HoyolabAccount.id == acc.id).update({'is_disabled': True})
            acc.is_disabled = True
        
        if query.count() == 0:
            status = DailyCheckInStatus(acc.id, gs.Game.GENSHIN, new_status)
            db_session.add(status)
        else:
            query.update({"status": new_status})
        db_session.commit()
        await asyncio.sleep(5)

    for acc in get_all_starrail_accounts(only_enabled=False):
        client = gs.Client({
            "ltuid": acc.ltuid,
            "ltoken": acc.ltoken,
        }, game=gs.Game.STARRAIL)
        query = db_session.query(DailyCheckInStatus).filter(DailyCheckInStatus.account_id == acc.id, DailyCheckInStatus.game_type == gs.Game.STARRAIL)
        try:
            await client.claim_daily_reward(reward=False)
            new_status = CheckInStatus.success
        except gs.AlreadyClaimed:
            new_status = CheckInStatus.claimed
        except gs.GeetestTriggered:
            new_status = CheckInStatus.failed
        
        if query.count() == 0:
            status = DailyCheckInStatus(acc.id, gs.Game.STARRAIL, new_status)
            db_session.add(status)
        else:
            query.update({"status": new_status})
        db_session.commit()
        await asyncio.sleep(5)
            
    for acc in get_all_zzz_accounts(only_enabled=False):
        client = gs.Client({
            "ltuid": acc.ltuid,
            "ltoken": acc.ltoken,
        }, game=gs.Game.ZZZ)
        try:
            await client.claim_daily_reward(reward=False)
        except gs.AlreadyClaimed:
            print("Already claimed")
        except gs.GeetestTriggered:
            print("Damn captcha")

        await asyncio.sleep(5)

if __name__ == "__main__":
    init_db()
    asyncio.run(checkin())
