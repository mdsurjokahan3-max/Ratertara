import logging
import json
import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.request import HTTPXRequest # এই লাইনটি নতুন যোগ করা হয়েছে

# ================= কনফিগারেশন =================
TOKEN = '8279372040:AAGKfFsmnkI5ihQE-T2v6hU47dEoZ892_nA'  # <--- আপনার টোকেন বসান
ADMIN_ID = 8415837999          # <--- আপনার আইডি বসান

DATA_FILE = "business_bot_data.json"
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# ================= ডেটাবেস সিস্টেম =================
def load_data():
    if not os.path.exists(DATA_FILE):
        return {"users": {}, "withdrawals": []}
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except:
        return {"users": {}, "withdrawals": []}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# ================= ফাংশনস =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    uid = str(user.id)
    data = load_data()

    if uid not in data["users"]:
        data["users"][uid] = {"name": user.first_name, "balance": 0.0, "bonus": False}
        save_data(data)

    await main_menu(update)

async def main_menu(update: Update):
    uid = str(update.effective_user.id)
    data = load_data()
    bal = data["users"][uid]["balance"]
    
    text = f"Business Bot Panel\nBalance: {bal} Taka"
    buttons = [
        [InlineKeyboardButton("Daily Bonus", callback_data='daily')],
        [InlineKeyboardButton("Withdraw", callback_data='withdraw')]
    ]
    if update.effective_user.id == ADMIN_ID:
         buttons.append([InlineKeyboardButton("Admin Check", callback_data='admin')])

    # মেসেজ বাটন দিয়ে পাঠানো বা এডিট করা
    if update.callback_query:
        await update.callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))
    else:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    uid = str(query.from_user.id)
    data = load_data()
    await query.answer()

    if query.data == 'daily':
        if not data["users"][uid]["bonus"]:
            data["users"][uid]["balance"] += 5.0
            data["users"][uid]["bonus"] = True
            save_data(data)
            await query.message.reply_text("Added 5 Taka Bonus!")
        else:
            await query.message.reply_text("Bonus already taken!")
    
    elif query.data == 'withdraw':
        await query.message.reply_text(f"Your balance {data['users'][uid]['balance']} is too low!")

    await main_menu(update)

# ================= মেইন ফাংশন (যেখানে ফিক্স করা হয়েছে) =================
def main():
    print("🚀 Bot connecting (High Timeout)...")

    # ইন্টারনেটের কানেকশন ধরে রাখার জন্য রিকোয়েস্ট টাইমআউট বাড়ানো হয়েছে
    t_request = HTTPXRequest(connection_pool_size=8, connect_timeout=60, read_timeout=60)

    app = Application.builder().token(TOKEN).request(t_request).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(callback_handler))

    # পোলিং সেটিংস (টাইমআউট সহ)
    app.run_polling(timeout=60, read_timeout=60)

if __name__ == '__main__':
    main()