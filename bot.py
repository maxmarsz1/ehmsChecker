with open("API_KEY", "r") as f:
    API = f.read().strip()
FILENAME_JOBS = "jobs.txt"
INTERVAL = 1800

from check import Checker

import json
import datetime
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


def initJobs() -> list:
    try:
        with open(FILENAME_JOBS, "r") as f:
            data = f.read()
    except FileNotFoundError:
        data = '[]'

    return json.loads(data)


def saveJobs(jobs) -> None:
    data = json.dumps(jobs)
    with open(FILENAME_JOBS, "w+") as f:
        f.write(data)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Type /subscribe to get notified when new announcements are available",
    )


async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Add a job to the queue."""
    chat_id = update.effective_message.chat_id
    jobs = context.bot_data["jobs"]
    text = "Already subscribed"
    if chat_id not in jobs:
        jobs.append(chat_id)
        text = "Subscribed"

    saveJobs(jobs)
    await update.effective_message.reply_text(text)


async def unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Remove the job if the user changed their mind."""
    chat_id = update.message.chat_id
    jobs = context.bot_data["jobs"]
    try:
        jobs.remove(chat_id)
        text = "Unsubscribed"
    except ValueError:
        text = "You have no active subscription."

    saveJobs(jobs)
    await update.message.reply_text(text)


async def check(context) -> None:
    newAnn = context.bot_data['checker'].checkIfNewAnn()
    if newAnn:
        for chat_id in context.bot_data['jobs']:
            await context.bot.send_message(chat_id, text=context.bot_data['checker'].new_ann)


if __name__ == "__main__":
    application = ApplicationBuilder().token(API).build()
    application.bot_data["jobs"] = initJobs()
    application.job_queue.run_repeating(check, INTERVAL, first=10)

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("subscribe", subscribe))
    application.add_handler(CommandHandler("unsubscribe", unsubscribe))

    application.bot_data['checker'] = Checker()
    if application.bot_data['checker'].is_authorized:
        application.run_polling()

    
