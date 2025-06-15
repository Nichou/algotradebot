
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from init import *

async def loop(context: ContextTypes.DEFAULT_TYPE) -> None:
    
    job = context.job
    
    btcbot.process()
    btcbot.log.update()
    
    if (btcbot.status.updated()):
        await context.bot.send_message(job.chat_id, text=btcbot.status.message)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    
    chat_id = update.effective_message.chat_id
    
    context.job_queue.run_repeating(loop, 900, chat_id=chat_id,name=str(chat_id),data=900)

    await update.message.reply_text("Initializing algotrade bot")
    
async def log(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    await update.message.reply_text(btcbot.log.readLog())
    
def main():
    application = Application.builder().token(">>> TOKEN <<<").build()

    application.add_handler(CommandHandler("start",start))
    application.add_handler(CommandHandler("log",log))

    application.run_polling(allowed_updates=Update.ALL_TYPES)
    
if __name__ == "__main__":
    main()
    