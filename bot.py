import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from datetime import datetime
import pytz
import nest_asyncio
import asyncio
from dotenv import load_dotenv

# Allow nested event loops in notebook environments
nest_asyncio.apply()

# Load environment variables from .env file
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")  # Use your token from the .env file

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    await update.message.reply_text("Prompt : \nMarket\nNews\nMarket opened/closed notification\nEntry notification\nExit notification")
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
    elif text == "co-founder" or text =="cofounder":  
        await update.message.reply_text("Prasanna")
    elif text == "market":
        await update.message.reply_text("[under construction]")
    elif text == "news":
        await update.message.reply_text("[under construction]")


    #Automatic message not prompt
    #It should send notifications to targeted users only
    elif text == "market opened/closed notification":
        await update.message.reply_text("[under construction]")
    elif text == "entry notification":
        await update.message.reply_text("[under construction]")
    elif text == "exit notification":
        await update.message.reply_text("[under construction]")
    else :
        await update.message.reply_text("Your prompt is not definded in the code")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("Bot started...")
    app.run_polling()

# Run the bot safely in a notebook
main()