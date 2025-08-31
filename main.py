
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from init import *

async def loop(context: ContextTypes.DEFAULT_TYPE) -> None:
    
    job = context.job
    
    end_sells = False
    
    for bt in bot_handler:
        bt.process()
        bt.log.update()       
        
        if (bt.status.updated()):
            await context.bot.send_message(job.chat_id, text=bt.status.message)
    else:
        bt.resetGlobals()
    
    pm = loadProgramMeta() 

    if pm["post_sell"]:
        if (pm["lock_buy"] == False):
            end_sells = True  
        pm["lock_buy"] = False        
    
    if end_sells:
        pm["post_sell"] = False
    
    saveProgramMeta(pm)
    

        

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    
    bot_handler.sort(reverse=True,key=getPriority)
    
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
    