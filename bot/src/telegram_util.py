from typing import List
from genshin.types import Game
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, ContextTypes
from sqlalchemy.exc import IntegrityError
from dotenv import dotenv_values
import signal

from database import init_db, db_session
from models import TelegramCodeSubscriber

GAME_MAPPING = {
    "genshin": Game.GENSHIN,
    "starrail": Game.STARRAIL
}

NAME_MAPPING = {
    "genshin": "Genshin Impact",
    "starrail": "Star Rail"
}

GENSHIN_REDEEM_LINK = "https://genshin.hoyoverse.com/en/gift?code="
STARRAIL_REDEEM_LINK = "https://hsr.hoyoverse.com/gift"

config = dotenv_values(".env")
app = Application.builder().token(config["TELEGRAM_TOKEN"]).build()

def launch_telegram():
    init_db()

    def terminate():
        print("Terminating...")
        exit(0)

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("subscribe", subscribe))
    app.add_handler(CommandHandler("unsubscribe", unsubscribe))

    signal.signal(signal.SIGINT, terminate)

    print("Starting telegram bot!")

    app.run_polling()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print(update.effective_message.chat_id)
    await update.message.reply_text("Nyaa~\nUse /subscribe <genshin/starrail> to subscribe to notifications of new codes!\nUse /unsubscribe <genshin/starrail> to unsubscribe.")

async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_message.chat_id
    print(chat_id)
    if len(context.args) != 1:
        await update.message.reply_text("You're using the command wrongly!\nUsage: /subscribe <genshin/starrail>")
        return
    game_type_str = context.args[0].lower()
    if game_type_str not in GAME_MAPPING:
        await update.message.reply_text("Invalid game specified nya~")
        return
    game = GAME_MAPPING[game_type_str]
    db_session.add(TelegramCodeSubscriber(telegram_id=chat_id, game_type=game))
    try:
        db_session.commit()
    except IntegrityError:
        db_session.rollback()
        await update.message.reply_text("You have already subscribed to this game nya~")
        return

    await update.message.reply_text(f"You have subscribed to {NAME_MAPPING[game_type_str]} code notifications!")

async def unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_message.chat_id
    print(chat_id)
    if len(context.args) != 1:
        await update.message.reply_text("You're using the command wrongly!\nUsage: /unsubscribe <genshin/starrail>")
        return
    game_type_str = context.args[0].lower()
    if game_type_str not in GAME_MAPPING:
        await update.message.reply_text("Invalid game specified nya~")
        return
    game = GAME_MAPPING[game_type_str]
    db_session.query(TelegramCodeSubscriber) \
            .filter(TelegramCodeSubscriber.telegram_id == chat_id, TelegramCodeSubscriber.game_type == game) \
            .delete()
    db_session.commit()
    await update.message.reply_text(f"You have unsubscribed from {NAME_MAPPING[game_type_str]} code notifications!")
    
async def broadcast_code(codes: List[str], game: Game):
    subscriptions = db_session.query(TelegramCodeSubscriber).filter(TelegramCodeSubscriber.game_type == game).all()
    bot = Bot(token=config["TELEGRAM_TOKEN"])

    if game == Game.GENSHIN:
        for sub in subscriptions:
            await bot.send_message(chat_id=sub.telegram_id, text="*New Genshin Impact code\(s\) available\!*\nClick on the links below or copy the codes to redeem them\!", parse_mode="MarkdownV2")
            for code in codes:
                await bot.send_message(chat_id=sub.telegram_id, text=f"[{code}]({GENSHIN_REDEEM_LINK+code})", parse_mode="MarkdownV2", disable_web_page_preview=True)
    elif game == Game.STARRAIL:
        for sub in subscriptions:
            await bot.send_message(chat_id=sub.telegram_id, text=f"*New Star Rail code\(s\) available\!*\n[Click here for the link to redeem them\!]({STARRAIL_REDEEM_LINK})", parse_mode="MarkdownV2")
            for code in codes:
                await bot.send_message(chat_id=sub.telegram_id, text=code, parse_mode="MarkdownV2")
    return

if __name__ == "__main__":
    launch_telegram()
