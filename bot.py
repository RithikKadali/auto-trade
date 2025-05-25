import os
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from datetime import datetime
import pytz
import nest_asyncio
import asyncio
from dotenv import load_dotenv

from market_scrapper import monitor_market

# Allow nested event loops in notebook environments
nest_asyncio.apply()

# Load environment variables from .env file
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
USER_CHAT_ID = os.getenv("TARGET_CHAT_ID")  # Add this to .env file

# Telegram Bot instance for manual message sending
bot = Bot(token=BOT_TOKEN)

# Helper: Send scheduled messages
async def scheduled_notifier():
    ist = pytz.timezone('Asia/Kolkata')
    notified = {
        "09:15": False,
        "10:15": False,
        "14:30": False,
        "15:15": False
    }

    while True:
        now = datetime.now(ist)
        current_time = now.strftime('%H:%M')

        if current_time == "09:15" and not notified["09:15"]:
            await bot.send_message(chat_id=USER_CHAT_ID, text="📈 Indian Market is now OPEN (9:15 AM IST)")
            notified["09:15"] = True

        elif current_time == "10:15" and not notified["10:15"]:
            await bot.send_message(chat_id=USER_CHAT_ID, text="🔍 Best time to peek into the Indian Market (10:15 AM IST)")
            notified["10:15"] = True

        elif current_time == "14:30" and not notified["14:30"]:
            await bot.send_message(chat_id=USER_CHAT_ID, text="⏳ Better to close all the orders now (2:30 PM IST)")
            notified["14:30"] = True

        elif current_time == "15:15" and not notified["15:15"]:
            await bot.send_message(chat_id=USER_CHAT_ID, text="🔒 Indian Market is now CLOSED (3:15 PM IST)")
            notified["15:15"] = True

        # Reset flags at midnight
        if current_time == "00:00":
            for key in notified:
                notified[key] = False

        await asyncio.sleep(60)

# Handles user messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    await update.message.reply_text("Prompt:\n- Market\n- News\nFeatures\n- Market Opened/Closed Notification\n- Entry Notification\n- Exit Notification")
    if text == "hi":
        await update.message.reply_text("HI, Rithik")
    elif text == "time":
        ist = pytz.timezone('Asia/Kolkata')
        now_ist = datetime.now(ist).strftime('%Y-%m-%d %H:%M:%S IST')
        await update.message.reply_text(f"Current IST time: {now_ist}")
    elif text == "rima":
        await update.message.reply_text("Crystal")
    elif text == "akka":
        await update.message.reply_text("Investor - Chanoja")
    elif text == "owner" or text == "ceo":
        await update.message.reply_text("Rithik")
    elif text == "co-founder" or text == "cofounder":  
        await update.message.reply_text("Prasanna")
    elif text == "market":
        try:
            market_data = monitor_market()
            await update.message.reply_text(market_data)
        except Exception as e:
            await update.message.reply_text(f"❌ Error fetching market data: {e}")
    elif text == "news":
        await update.message.reply_text("[under construction]")
    elif text == "market opened/closed notification":
        await update.message.reply_text("Working Fine")
    elif text == "entry notification":
        await update.message.reply_text("[under construction]")
    elif text == "exit notification":
        await update.message.reply_text("[under construction]")
    else:
        await update.message.reply_text("Your prompt is not defined in the code")

# Run bot
def main():
    async def post_init(application):
        application.create_task(scheduled_notifier())

    app = ApplicationBuilder().token(BOT_TOKEN).post_init(post_init).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    print("Bot started...")
    app.run_polling()

main()
