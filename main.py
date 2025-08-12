import os
import logging
import asyncio
import datetime
from zoneinfo import ZoneInfo

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = '8235876145:AAH9xfHaogajtOwzuV02iyfMNoRG2l2E4do'
ADMIN_IDS = [1840751528, 1280460690]
SUBSCRIBER_FILE = "subscribers.txt"
LOG_DIR = "logs"
DELAY = 1.1

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger("nanas44-bot")

def save_log(filename: str, data: str):
    os.makedirs(LOG_DIR, exist_ok=True)
    with open(os.path.join(LOG_DIR, filename), "a", encoding="utf-8") as f:
        f.write(data + "\n")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    first_name = update.effective_user.first_name or "there"

    if not os.path.exists(SUBSCRIBER_FILE):
        open(SUBSCRIBER_FILE, "w").close()
    with open(SUBSCRIBER_FILE, "r+", encoding="utf-8") as f:
        lines = f.read().splitlines()
        if user_id not in lines:
            f.write(f"{user_id}\n")
            save_log("new_users.txt", f"{datetime.datetime.now()} - {user_id}")

    welcome_text = (
        f"👋 HI {first_name}！\n\n"
        "🪜 Step 1:\nJoin Nanas44 Official Channel Claim Free 🎁\n\n"
        "🪜 Step 2:\nJoin Grouplink IOI Partnership Ambil E-wallet Angpaw 💸"
    )
    keyboard = [
        [InlineKeyboardButton("NANAS44 OFFICIAL CHANNEL", url="https://t.me/nanas44")],
        [InlineKeyboardButton("E-WALLET ANGPAO GROUP", url="https://t.me/addlist/XsWuNiUNHG05ZDg1")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    try:
        with open("banner-01.png", "rb") as img:
            await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=img,
                caption=welcome_text,
                reply_markup=reply_markup,
            )
    except FileNotFoundError:
        await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return
    message = " ".join(context.args)
    if not message:
        await update.message.reply_text("Please provide a message. Usage: /broadcast your message here")
        return
    if not os.path.exists(SUBSCRIBER_FILE):
        await update.message.reply_text("No subscribers yet.")
        return

    with open(SUBSCRIBER_FILE, "r", encoding="utf-8") as f:
        ids = list(set(f.read().splitlines()))

    success = 0
    for uid in ids:
        try:
            await context.bot.send_message(chat_id=int(uid), text=message)
            success += 1
            await asyncio.sleep(DELAY)
        except Exception as e:
            logger.warning(f"Broadcast to {uid} failed: {e}")

    await update.message.reply_text(f"Broadcast sent to {success} users.")

async def broadcast_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS or not update.message or not update.message.photo:
        return

    caption = update.message.caption or ""
    if not os.path.exists(SUBSCRIBER_FILE):
        await update.message.reply_text("No subscribers yet.")
        return

    with open(SUBSCRIBER_FILE, "r", encoding="utf-8") as f:
        ids = list(set(f.read().splitlines()))

    success = 0
    file_id = update.message.photo[-1].file_id
    for uid in ids:
        try:
            await context.bot.send_photo(chat_id=int(uid), photo=file_id, caption=caption)
            success += 1
            await asyncio.sleep(DELAY)
        except Exception as e:
            logger.warning(f"Photo broadcast to {uid} failed: {e}")

    await update.message.reply_text(f"Photo broadcast sent to {success} users.")

async def forward_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return
    if not update.message:
        return
    if not os.path.exists(SUBSCRIBER_FILE):
        await update.message.reply_text("No subscribers yet.")
        return

    with open(SUBSCRIBER_FILE, "r", encoding="utf-8") as f:
        ids = list(set(f.read().splitlines()))

    if update.message.forward_from_chat:
        from_chat_id = update.message.forward_from_chat.id
        forward_message_id = update.message.forward_from_message_id
        success = 0
        for uid in ids:
            try:
                await context.bot.forward_message(
                    chat_id=int(uid),
                    from_chat_id=from_chat_id,
                    message_id=forward_message_id,
                )
                success += 1
                await asyncio.sleep(DELAY)
            except Exception as e:
                logger.warning(f"Forward to {uid} failed: {e}")
        await update.message.reply_text(f"✅ Forwarded with channel source to {success} users.")
    else:
        for uid in ids:
            try:
                await context.bot.send_message(chat_id=int(uid), text=update.message.text or "")
                await asyncio.sleep(DELAY)
            except Exception as e:
                logger.warning(f"Text relay to {uid} failed: {e}")

async def subcount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return
    if not os.path.exists(SUBSCRIBER_FILE):
        await update.message.reply_text("👥 Total subscribers: 0")
        return
    with open(SUBSCRIBER_FILE, "r", encoding="utf-8") as f:
        total = len(set(f.read().splitlines()))
    await update.message.reply_text(f"👥 Total subscribers: {total}")

async def export(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return
    if not os.path.exists(SUBSCRIBER_FILE):
        await update.message.reply_text("No subscribers file yet.")
        return
    with open(SUBSCRIBER_FILE, "rb") as f:
        await context.bot.send_document(chat_id=update.effective_chat.id, document=f)

async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id in ADMIN_IDS:
        await update.message.reply_text("Bot restarting...")
        os._exit(1)

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return
    text = (
        "🧠 Bot Commands:\n"
        "/start - Welcome page\n"
        "/broadcast <text> - Send message to all\n"
        "Send a photo with caption - Broadcast image\n"
        "Forward a channel post here - Forward to all (shows source)\n"
        "/subcount - Subscriber count\n"
        "/export - Download subscribers list\n"
        "/restart - Restart bot"
    )
    await update.message.reply_text(text)

async def send_backup(context: ContextTypes.DEFAULT_TYPE):
    try:
        if not os.path.exists(SUBSCRIBER_FILE):
            return
        with open(SUBSCRIBER_FILE, "rb") as f:
            for admin_id in ADMIN_IDS:
                await context.bot.send_document(chat_id=admin_id, document=f)
                f.seek(0)
    except Exception as e:
        logger.error(f"Backup error: {e}")

if __name__ == "__main__":
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("broadcast", broadcast))
    application.add_handler(CommandHandler("subcount", subcount))
    application.add_handler(CommandHandler("export", export))
    application.add_handler(CommandHandler("restart", restart))
    application.add_handler(CommandHandler("help", help_cmd))
    application.add_handler(MessageHandler(filters.PHOTO & filters.User(ADMIN_IDS), broadcast_photo))
    application.add_handler(MessageHandler(filters.FORWARDED & filters.User(ADMIN_IDS), forward_broadcast))

    application.job_queue.run_daily(
        send_backup,
        time=datetime.time(hour=0, minute=0, tzinfo=ZoneInfo("Asia/Kuala_Lumpur")),
        name="daily_backup",
    )

    BASE_URL = os.environ.get("RENDER_EXTERNAL_URL", "https://www.nanas44.com")
    URL_PATH = f"/webhook/{TOKEN.split(':')[0]}"

    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 8443)),
        url_path=URL_PATH.lstrip("/"),
        webhook_url=BASE_URL + URL_PATH,
        drop_pending_updates=True,
    )
