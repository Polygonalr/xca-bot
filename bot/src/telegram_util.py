from typing import List
from genshin.types import Game
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, ContextTypes
from sqlalchemy.exc import IntegrityError
from dotenv import dotenv_values
import signal

from database import init_db, db_session
from models import TelegramCodeSubscriber

NAME_MAPPING = {
    Game.GENSHIN: "Genshin Impact",
    Game.STARRAIL: "Star Rail"
}

GENSHIN_REDEEM_LINK = "https://genshin.hoyoverse.com/en/gift?code="
STARRAIL_REDEEM_LINK = "https://hsr.hoyoverse.com/gift?code="

config = dotenv_values(".env")
app = Application.builder().token(config["TELEGRAM_TOKEN"]).build()

def launch_telegram():
    init_db()

    def terminate():
        print("Terminating...")
        exit(0)

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("genshin", subscribe_genshin))
    app.add_handler(CommandHandler("starrail", subscribe_starrail))
    app.add_handler(CommandHandler("unsub_genshin", unsubscribe_genshin))
    app.add_handler(CommandHandler("unsub_starrail", unsubscribe_starrail))

    signal.signal(signal.SIGINT, terminate)

    print("Starting telegram bot!")

    app.run_polling()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print(update.effective_message.chat_id)
    await update.message.reply_text("Nyaa~\nUse /genshin to subscribe to notifications for new Genshin Impact codes!\n" + \
                                    "Use /starrail to subscribe to notifications for new Honkai: Star Rail codes!\n" + \
                                    "Use /unsub_genshin or /unsub_starrail to stop receiving notifications.")

async def subscribe_genshin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await subscribe(update, context, Game.GENSHIN)

async def subscribe_starrail(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await subscribe(update, context, Game.STARRAIL)

async def unsubscribe_genshin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await unsubscribe(update, context, Game.GENSHIN)

async def unsubscribe_starrail(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await unsubscribe(update, context, Game.STARRAIL)

async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE, game: Game) -> None:
    chat_id = update.effective_message.chat_id
    print(chat_id)
    db_session.add(TelegramCodeSubscriber(telegram_id=chat_id, game_type=game))
    try:
        db_session.commit()
    except IntegrityError:
        db_session.rollback()
        await update.message.reply_text("You have already subscribed to this game nya~")
        return

    await update.message.reply_text(f"You have subscribed to {NAME_MAPPING[game]} code notifications!")

async def unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE, game: Game) -> None:
    chat_id = update.effective_message.chat_id
    print(chat_id)
    db_session.query(TelegramCodeSubscriber) \
            .filter(TelegramCodeSubscriber.telegram_id == chat_id, TelegramCodeSubscriber.game_type == game) \
            .delete()
    db_session.commit()
    await update.message.reply_text(f"You have unsubscribed from {NAME_MAPPING[game]} code notifications!")
    
async def broadcast_code(codes: List[str], game: Game):
    subscriptions = db_session.query(TelegramCodeSubscriber).filter(TelegramCodeSubscriber.game_type == game).all()
    bot = Bot(token=config["TELEGRAM_TOKEN"])

    if game == Game.GENSHIN:
        link = GENSHIN_REDEEM_LINK
    else:
        link = STARRAIL_REDEEM_LINK

    for sub in subscriptions:
        await bot.send_message(chat_id=sub.telegram_id, text=f"*New {NAME_MAPPING[game]} code\(s\) available\!*\nClick on the links below or copy the codes to redeem them\!", parse_mode="MarkdownV2")
        for code in codes:
            await bot.send_message(chat_id=sub.telegram_id, text=f"[{code}]({link+code})", parse_mode="MarkdownV2", disable_web_page_preview=True)

    return

if __name__ == "__main__":
    launch_telegram()
