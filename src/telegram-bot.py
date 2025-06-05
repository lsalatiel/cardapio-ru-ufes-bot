import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from scraper import get_menu as scrape_menu
import json
import os
from datetime import time

USERS_FILE = "users.json"

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_user(chat_id):
    users = load_users()
    if chat_id not in users:
        users.append(chat_id)
        with open(USERS_FILE, 'w') as f:
            json.dump(users, f)

async def toggle_notifications(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    users = load_users()

    if chat_id in users:
        users.remove(chat_id)
        message = "You have been unsubscribed from daily notifications."
    else:
        users.append(chat_id)
        message = "You have been subscribed to daily notifications."

    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)

    await update.message.reply_text(message)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message = (
        "Welcome to Cardapio RU Ufes Bot!\n\n"
        "Commands:\n"
        "/menu - Get today's menu\n"
        "/almoco - Get today's lunch menu\n"
        "/janta - Get today's dinner menu\n"
        "/notify - Toggle daily notifications\n"
        "/help - Show this help message"
    )
    await update.message.reply_text(welcome_message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "Available commands:\n"
        "/menu - Get today's menu\n"
        "/almoco - Get today's lunch menu\n"
        "/janta - Get today's dinner menu\n"
        "/notify - Toggle daily notifications (ON by default)\n"
        "/help - Show this help message\n\n"
        "You can also just type 'menu' and I'll understand!"
    )
    await update.message.reply_text(help_text)

async def get_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    save_user(update.effective_chat.id)

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    menu = scrape_menu()
    
    await update.message.reply_text(menu)

def __get_lunch():
    menu = scrape_menu()

    if 'Almoço' not in menu:
        return "Lunch menu not available for today yet."
    
    lunch_menu = menu.split('Jantar')[0].strip()
    return lunch_menu

async def get_lunch(update: Update, context: ContextTypes.DEFAULT_TYPE):
    save_user(update.effective_chat.id)

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    lunch_menu = __get_lunch()
    
    await update.message.reply_text(lunch_menu)

def __get_dinner():
    menu = scrape_menu()

    if 'Jantar' not in menu:
        return "Dinner menu not available for today yet."
    
    dinner_menu = menu.split('Jantar')[1].strip()
    return dinner_menu

async def get_dinner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    save_user(update.effective_chat.id)

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    dinner_menu = __get_dinner()
    
    await update.message.reply_text(dinner_menu)

async def send_morning_daily_menu(context: ContextTypes.DEFAULT_TYPE):
    users = load_users()
    lunch_menu = __get_lunch()
    
    message = f"Bom dia estudante! Olha aqui o seu delicioso almosso:\n\n{lunch_menu}"
    
    for chat_id in users:
        try:
            await context.bot.send_message(chat_id=chat_id, text=message)
        except Exception as e:
            print(f"Failed to send to {chat_id}: {e}")

async def send_evening_daily_menu(context: ContextTypes.DEFAULT_TYPE):
    users = load_users()
    lunch_menu = __get_lunch()
    
    message = f"Bom tarde estudante! Da uma olhada na sua jantinha:\n\n{lunch_menu}"
    
    for chat_id in users:
        try:
            await context.bot.send_message(chat_id=chat_id, text=message)
        except Exception as e:
            print(f"Failed to send to {chat_id}: {e}")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    save_user(update.effective_chat.id)

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
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    
    if not BOT_TOKEN:
        print("Error: BOT_TOKEN environment variable not set!")
        return
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("menu", get_menu))
    application.add_handler(CommandHandler("almoco", get_lunch))
    application.add_handler(CommandHandler("janta", get_dinner))
    application.add_handler(CommandHandler("notify", toggle_notifications))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    job_queue = application.job_queue
    job_queue.run_daily(
        send_morning_daily_menu, 
        time=time(13, 30),
        days=(1, 2, 3, 4, 5),
        name="daily_menu"
    )
    job_queue.run_daily(
        send_evening_daily_menu, 
        time=time(19, 0),
        days=(1, 2, 3, 4, 5),
        name="daily_menu"
    )
    
    print("Bot is starting...")
    print("Daily menu will be sent at 10:30 AM and at 16:00 to all users")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    main()
