import sqlite3
import json
import logging
from telegram import Update, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

# ЁЯСЗ ржЖржкржирж╛рж░ рждржерзНржп ржжрж┐ржи
BOT_TOKEN = "8279372040:AAGKfFsmnkI5ihQE-T2v6hU47dEoZ892_nA"
WEB_APP_URL = "https://ratertara.vercel.app/" # GitHub рж▓рж┐ржВржХ (s рж╕рж╣)
CHANNEL_LINK = "https://t.me/+g7XFPRuwH85iZTI9" # ржЬрзЯрзЗржи ржХрж░рж╛рж░ ржЬржирзНржп
ADMIN_ID = 8415837999 # ржЖржкржирж╛рж░ ржЯрзЗрж▓рж┐ржЧрзНрж░рж╛ржо ID (BotFather ржХрзЗ /myid ржмрж▓рж▓рзЗ ржкрж╛ржмрзЗржи ржирж╛, userinfobot ржП ржкрж╛ржмрзЗржи)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- ржбрж╛ржЯрж╛ржмрзЗрж╕ рж╕рзЗржЯржЖржк ---
def init_db():
    conn = sqlite3.connect('pro_users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (user_id INTEGER PRIMARY KEY, balance REAL, referrals INTEGER, referrer_id INTEGER)''')
    conn.commit()
    conn.close()

def get_user_data(user_id):
    conn = sqlite3.connect('pro_users.db')
    c = conn.cursor()
    c.execute("SELECT balance, referrals FROM users WHERE user_id=?", (user_id,))
    result = c.fetchone()
    conn.close()
    return result if result else (0.0, 0)

def register_user(user_id, referrer_id=None):
    conn = sqlite3.connect('pro_users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    if not c.fetchone():
        # ржирждрзБржи ржЗржЙржЬрж╛рж░
        c.execute("INSERT INTO users (user_id, balance, referrals, referrer_id) VALUES (?, ?, ?, ?)", (user_id, 0.0, 0, referrer_id))
        
        # рж░рзЗржлрж╛рж░рж╛рж░ржХрзЗ ржмрзЛржирж╛рж╕ ржжрзЗржУрзЯрж╛ (ржпржжрж┐ ржерж╛ржХрзЗ)
        if referrer_id:
            c.execute("UPDATE users SET balance = balance + 0.10, referrals = referrals + 1 WHERE user_id=?", (referrer_id,))
            conn.commit()
            return True # ржмрзЛржирж╛рж╕ ржжрзЗржУрзЯрж╛ рж╣рзЯрзЗржЫрзЗ
    conn.commit()
    conn.close()
    return False

def update_balance(user_id, amount):
    conn = sqlite3.connect('pro_users.db')
    c = conn.cursor()
    c.execute("UPDATE users SET balance = balance + ? WHERE user_id=?", (amount, user_id))
    conn.commit()
    conn.close()

# --- ржмржЯ ржХржорж╛ржирзНржбрж╕ ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    args = context.args # рж░рзЗржлрж╛рж░ рж▓рж┐ржВржХ ржЪрзЗржХ (ex: /start 12345)
    referrer_id = None
    
    if args and args[0].isdigit():
        possible_referrer = int(args[0])
        if possible_referrer != user.id:
            referrer_id = possible_referrer

    # рж░рзЗржЬрж┐рж╕рзНржЯрж╛рж░ ржХрж░рж╛
    is_referred = register_user(user.id, referrer_id)
    
    # рж░рзЗржлрж╛рж░рж╛рж░ржХрзЗ ржирзЛржЯрж┐ржлрж┐ржХрзЗрж╢ржи ржкрж╛ржарж╛ржирзЛ
    if is_referred and referrer_id:
        try:
            await context.bot.send_message(chat_id=referrer_id, text=f"ЁЯОЙ New Referral! {user.first_name} joined. You earned $0.10")
        except:
            pass

    # ржЕрзНржпрж╛ржк ржУржкрзЗржи ржХрж░рж╛рж░ рж╕ржорзЯ ржбрж╛ржЯрж╛ ржкрж╛ржарж╛ржирзЛ
    bal, refs = get_user_data(user.id)
    # URL ржПрж░ рж╕рж╛ржерзЗ ржбрж╛ржЯрж╛ ржпрзЛржЧ ржХрж░рзЗ ржжрж┐ржЪрзНржЫрж┐ ржпрж╛рждрзЗ HTML ржП рж╢рзЛ ржХрж░рзЗ
    final_url = f"{WEB_APP_URL}?bal={bal:.2f}&refs={refs}"

    keyboard = [
        [InlineKeyboardButton("ЁЯЪА Open Dashboard", web_app=WebAppInfo(url=final_url))],
        [InlineKeyboardButton("ЁЯУв Join Channel", url=CHANNEL_LINK)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"ЁЯСЛ Welcome {user.first_name} to Pro Earn Bot!\n\n"
        f"ЁЯТ░ Your Balance: ${bal:.2f}\n"
        f"ЁЯСе Referrals: {refs}\n\n"
        "Click below to start earning real money! ЁЯСЗ",
        reply_markup=reply_markup
    )

async def web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = json.loads(update.effective_message.web_app_data.data)
    user = update.effective_user
    
    if data['type'] == 'ad_watched':
        update_balance(user.id, 0.05) # ржЕрзНржпрж╛ржб ржжрзЗржЦрж▓рзЗ $0.05
        bal, _ = get_user_data(user.id)
        await update.message.reply_text(f"тЬЕ Ad Watched! +$0.05 Added.\nЁЯТ░ Current Balance: ${bal:.2f}")
    
    elif data['type'] == 'withdraw':
        amount = float(data['amount'])
        number = data['number']
        bal, _ = get_user_data(user.id)
        
        if bal >= amount:
            update_balance(user.id, -amount) # ржмрзНржпрж╛рж▓рзЗржирзНрж╕ ржХрзЗржЯрзЗ ржирзЗржУрзЯрж╛
            await update.message.reply_text(f"тЬЕ Withdrawal Request Submitted!\nAmount: ${amount}\nNumber: {number}\n\nAdmin will pay you soon.")
            
            # ржПржбржорж┐ржиржХрзЗ ржЬрж╛ржирж╛ржирзЛ
            if ADMIN_ID:
                await context.bot.send_message(chat_id=ADMIN_ID, text=f"ЁЯФФ NEW WITHDRAWAL!\nUser: {user.first_name} (ID: {user.id})\nAmount: ${amount}\nNumber: {number}")
        else:
            await update.message.reply_text("тЭМ Insufficient Balance!")

if __name__ == '__main__':
    init_db()
    print("Connecting...")
    app = ApplicationBuilder().token(BOT_TOKEN).read_timeout(60).write_timeout(60).connect_timeout(60).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, web_app_data))
    
    print("Pro Bot Running...")
    app.run_polling()
