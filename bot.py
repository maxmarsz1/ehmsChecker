API = 'API_KEY'
JOB_FILENAME = 'jobs'

from check import checkIfNewAnn

import logging
import pickle
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


def initJobs(job_queue):
    try:
        chat_ids = pickle.load(open(JOB_FILENAME, 'rb'))
        print(chat_ids)
        for chat_id in chat_ids:
            job_queue.run_repeating(check, 1800, chat_id=chat_id, name=str(chat_id))
    except FileNotFoundError as e:
        print("No jobs saved")


def saveJobs(job_queue):
    chat_ids = [job.chat_id for job in job_queue.jobs()]
    pickle.dump(chat_ids, open(JOB_FILENAME, 'wb'))


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Type /subscribe to get notified when new announcements are available")


async def check(context: ContextTypes.DEFAULT_TYPE) -> None:
    job = context.job
    new_ann = checkIfNewAnn()

    if new_ann:
        text = f"Nowe ogłoszenie: {new_ann}"
        await context.bot.send_message(chat_id=job.chat_id, text=text)


def remove_job_if_exists(name: str, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Remove job with given name. Returns whether job was removed."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Add a job to the queue."""
    chat_id = update.effective_message.chat_id

    job_removed = remove_job_if_exists(str(chat_id), context)
    context.job_queue.run_repeating(check, 1800, chat_id=chat_id, name=str(chat_id))

    if job_removed:
        text = "Already subscribed"
    else: 
        text = "Subscribed"
        saveJobs(context.job_queue)


    await update.effective_message.reply_text(text)


async def unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Remove the job if the user changed their mind."""
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    saveJobs(context.job_queue)
    text = "Unsubscribed!" if job_removed else "You have no active subscription."
    await update.message.reply_text(text)


if __name__ == '__main__':
    application = ApplicationBuilder().token(API).build()
    job_queue = application.job_queue

    initJobs(job_queue)
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler("subscribe", subscribe))
    application.add_handler(CommandHandler("unsubscribe", unsubscribe))
    
    application.run_polling()