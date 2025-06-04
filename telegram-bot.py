import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from scraper import get_menu as scrape_menu

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message = (
        "Welcome to Cardapio RU Ufes Bot!\n\n"
        "Commands:\n"
        "/menu - Get today's menu\n"
        "/almoco - Get today's lunch menu\n"
        "/janta - Get today's dinner menu\n"
        "/help - Show this help message"
    )
    await update.message.reply_text(welcome_message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "Available commands:\n"
        "/menu - Get today's menu\n"
        "/almoco - Get today's lunch menu\n"
        "/janta - Get today's dinner menu\n"
        "/help - Show this help message\n\n"
        "You can also just type 'menu' and I'll understand!"
    )
    await update.message.reply_text(help_text)

async def get_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    menu = scrape_menu()
    
    await update.message.reply_text(menu)

async def get_lunch(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    menu = scrape_menu()

    if 'Almoço' not in menu:
        await update.message.reply_text("Lunch menu not available for today yet.")
        return
    
    lunch_menu = menu.split('Jantar')[0].strip()
    
    await update.message.reply_text(lunch_menu)

async def get_dinner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    menu = scrape_menu()

    if 'Jantar' not in menu:
        await update.message.reply_text("Dinner menu not available for today yet.")
        return
    
    dinner_menu = menu.split('Jantar')[1].strip()
    
    await update.message.reply_text(dinner_menu)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    
    if any(word in text for word in ['menu', 'cardapio', 'cardápio']):
        await get_menu(update, context)
    if any(word in text for word in ['almoco', 'almosso', 'almoço']):
        await get_lunch(update, context)
    if any(word in text for word in ['janta', 'jantar', 'jantinha']):
        await get_dinner(update, context)
    else:
        await update.message.reply_text(
            "Hi! I can help you get the Ufes menu for today. Type /menu or just say 'menu'!"
        )

def main():
    BOT_TOKEN = "7420733797:AAFXivNHGI7IegCE_bbMwHmEqTXNJQaIzDM"
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("menu", get_menu))
    application.add_handler(CommandHandler("almoco", get_lunch))
    application.add_handler(CommandHandler("janta", get_dinner))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    print("Bot is starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    main()
