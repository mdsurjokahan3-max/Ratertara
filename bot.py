import logging
import json
import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# =================  (  ) =================
TOKEN = '8279372040:AAGKfFsmnkI5ihQE-T2v6hU47dEoZ892_nA'     # BotFather   
ADMIN_ID = 8415837999             #    ID (userinfobot  )
CHANNEL_USERNAME = "@ratertarachannel" #    (Force Join  )

#   
REFERRAL_BONUS = 5.0
DAILY_BONUS = 2.0
MIN_WITHDRAW = 50.0

DATA_FILE = "business_bot_data.json"

# =================  =================
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# =================   =================
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

# =================   =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    uid = str(user.id)
    data = load_data()

    # .   
    if uid not in data["users"]:
        data["users"][uid] = {
            "name": user.first_name,
            "balance": 0.0,
            "ref_count": 0,
            "bonus_taken": False
        }
        
        #  
        args = context.args
        if args and args[0] != uid:
            referrer = args[0]
            if referrer in data["users"]:
                data["users"][referrer]["balance"] += REFERRAL_BONUS
                data["users"][referrer]["ref_count"] += 1
                try:
                    await context.bot.send_message(referrer, f"     ! +{REFERRAL_BONUS} ")
                except:
                    pass
        save_data(data)

    # .    
    await main_menu(update, context)

async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #          
    user_id = str(update.effective_user.id)
    data = load_data()
    balance = data["users"][user_id]["balance"]

    text = (
        f" **Business Bot Control Panel**\n\n"
        f" : {update.effective_user.first_name}\n"
        f" : {balance} \n"
        f" : {CHANNEL_USERNAME}\n\n"
        "   :"
    )

    buttons = [
        [InlineKeyboardButton("  ", callback_data='daily_bonus'), InlineKeyboardButton("  ", callback_data='refer')],
        [InlineKeyboardButton("   (Withdraw)", callback_data='withdraw')],
        [InlineKeyboardButton(" ", callback_data='stats'), InlineKeyboardButton(" ", callback_data='support')],
    ]
    
    #     
    if update.effective_user.id == ADMIN_ID:
        buttons.append([InlineKeyboardButton("  ", callback_data='admin_panel')])

    if update.callback_query:
        await update.callback_query.message.edit_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(buttons))
    else:
        await update.message.reply_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(buttons))

# =================   =================

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    uid = str(query.from_user.id)
    data = load_data()
    await query.answer()

    # ---   ---
    if query.data == 'daily_bonus':
        #       ,    
        if not data["users"][uid].get("bonus_taken", False):
            data["users"][uid]["balance"] += DAILY_BONUS
            data["users"][uid]["bonus_taken"] = True  #    
            save_data(data)
            await query.message.reply_text(f"  {DAILY_BONUS}   !")
        else:
            await query.message.reply_text("     !")

    # ---   ---
    elif query.data == 'refer':
        link = f"https://t.me/{context.bot.username}?start={uid}"
        await query.message.reply_text(f" **  :**\n{link}\n\n  {REFERRAL_BONUS}  !")

    # ---   ---
    elif query.data == 'withdraw':
        bal = data["users"][uid]["balance"]
        if bal >= MIN_WITHDRAW:
            #      
            data["users"][uid]["balance"] -= bal
            save_data(data)
            
            #   
            admin_msg = (
                f" **  !**\n"
                f" : {query.from_user.first_name} (ID: {uid})\n"
                f"  : {bal}\n"
                f"   "
            )
            try:
                await context.bot.send_message(chat_id=ADMIN_ID, text=admin_msg)
            except:
                pass
            
            await query.message.edit_text(f"  {bal}         !")
        else:
            await query.answer(f"   {MIN_WITHDRAW} !", show_alert=True)

    # ---  ---
    elif query.data == 'stats':
        await query.answer(f"  : {data['users'][uid]['ref_count']} ", show_alert=True)
    
    # ---   ---
    elif query.data == 'admin_panel':
        if int(uid) != ADMIN_ID:
            await query.answer("  !", show_alert=True)
            return
            
        text = (
            f" ** **\n"
            f"  : {len(data['users'])}\n"
            f" : `/broadcast  `   "
        )
        await query.message.edit_text(text, parse_mode='Markdown')

    # ---   ---
    elif query.data == 'back':
        await main_menu(update, context)

# =================    =================

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #        
    if update.effective_user.id != ADMIN_ID:
        return

    #  
    msg = update.message.text.replace('/broadcast ', '')
    if len(msg) < 5:
        await update.message.reply_text("     : `/broadcast    `")
        return

    data = load_data()
    users = data["users"]
    count = 0

    await update.message.reply_text(f"    {len(users)}   ...")

    for user_id in users:
        try:
            await context.bot.send_message(chat_id=user_id, text=f" **:**\n\n{msg}", parse_mode='Markdown')
            count += 1
            await asyncio.sleep(0.1) #      
        except:
            #      
            pass

    await update.message.reply_text(f"  !  {count}   ")

# =================   =================
def main():
    print(" Business Bot Started...")
    app = Application.builder().token(TOKEN).build()

    #  
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("broadcast", broadcast)) #  
    app.add_handler(CallbackQueryHandler(callback_handler))

    #  
    app.run_polling()

if __name__ == '__main__':
    main()