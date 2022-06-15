# Copyright (c) 2021 Alberto Rota
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import datetime
import telegram
from telegram.ext import (Updater, 
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    CallbackContext,
    )
from telegram import ReplyKeyboardMarkup
import create
import pandas as pd

MENU=0
ASK_ASSET = 1
ASK_ATYPICAL_ASSET = 1.5
ASK_TIMELINE = 2
ASK_TO_SET_WALLET = 3
ASK_WALLET_HOW = 4
ASK_NOTIFICATIONS_WHICH = 5

def askwallethow(update,context):
    client=context.dispatcher.user_data['client']
    user_id = update.message.from_user['id']
    # chat_id = update.message.chat_id

    wallet_options = [
        ['📈1 Hour Graphs','📈4 Hours Graphs',],
        ['📈Daily Graphs','📈Weekly Graphs'],
        ['📈Monthly Graphs','📈Yearly Graphs'],
        ['💵Show Report'],
        ['🏡Home'],
    ]
    ##############################################################
    profit_msg = create.profits(client,user_id)
    ##############################################################
    update.message.reply_text(
        text=profit_msg,
        # chat_id=update.effective_chat.id,
        parse_mode=telegram.ParseMode.HTML,
        reply_markup=ReplyKeyboardMarkup(
            wallet_options, 
            one_time_keyboard=True,
            resize_keyboard=True,
            )
    )
    return ASK_WALLET_HOW

def showwalletreport(update,context):
    client=context.dispatcher.user_data['client']
    user_id = update.message.from_user['id']
    print(">> "+datetime.datetime.now().strftime(f"[%d/%m/%Y-%H:%M:%S]-{user_id}: ")+
        " SHOWWALLET request --> Report")
    user_id = update.message.from_user['id']
    #############################################################################
    try:
        profit_msg = create.profits(client,user_id)
    except:
        context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text="""It seems like you didn't register a wallet yet 😕\n 
Make sure you do it from the <u>💰Set Wallet</u> button on the main menu""",
            parse_mode=telegram.ParseMode.HTML,
        )
        return MENU
    #############################################################################
    context.bot.send_message(
                    chat_id=update.effective_chat.id, 
                    text=profit_msg,
                    parse_mode=telegram.ParseMode.HTML,
                )
    return ASK_WALLET_HOW

def showwalletgraphs(update,context):
    button2range = {
        '📈1 Hour Graphs':'1hour',
        '📈4 Hours Graphs':'4hour',
        '📈Daily Graphs':'1day',
        '📈Weekly Graphs':'1week',
        '📈Monthly Graphs':'1month',
        '📈Yearly Graphs':'1year',
    }
    timerange = update.effective_message.text
    client=context.dispatcher.user_data['client']
    user_id = update.message.from_user['id']
    print(">> "+datetime.datetime.now().strftime(f"[%d/%m/%Y-%H:%M:%S]-{user_id}: ")+
        " SHOWWALLET request --> Graphs: "+button2range[timerange])
    user_id = update.message.from_user['id']
    
    wallet = f"data/wallets/{user_id}.csv"
    try:
        df = pd.read_csv(wallet)
    except:    
        context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text=
"""It seems like you didn't register a wallet yet 😕\n 
Make sure you do it from the <u>💰Set Wallet</u> button on the main menu""",
            parse_mode=telegram.ParseMode.HTML,
        )
        return MENU


    for a in df['asset']:
        #############################################################################
        figpath,cptn = create.chart(client, a,button2range[timerange])
        # reportmsg = create.report(client, a)
        #############################################################################
        context.bot.send_photo(
            chat_id=update.effective_chat.id, 
            photo=open(figpath,'rb'),
            caption=cptn,
            parse_mode=telegram.ParseMode.HTML,
            )
    return ASK_WALLET_HOW

def requestwallet(update, context):
    user_id = update.message.from_user['id']
    print(">> "+datetime.datetime.now().strftime(f"[%d/%m/%Y-%H:%M:%S]-{user_id}: ")+
        " SETWALLET request ")
    context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text=
"""Type the asssets in your wallet with the following format:
<b>asset quantity buy_price 
asset quantity buy_price 
...</b>
Example:<i>
eth 0.128432 3294.52
btc 0.0045654433 64424.20
dot 5.87874 45.34
bnb 0.12342 495.65
</i>
""",
        parse_mode=telegram.ParseMode.HTML
    )
    return ASK_TO_SET_WALLET

def setwallet(update, context):
    user_id = update.message.from_user['id']
    print(">> "+datetime.datetime.now().strftime(f"[%d/%m/%Y-%H:%M:%S]-{user_id}: ")+
        " New wallet created/updated ")

    user_id = update.message.from_user['id']
    msg = update.message.text.split("\n")
    
    for i,asset in enumerate(msg):
        msg[i]=asset.split(" ")
    
    walletpath = f"data/wallets/{user_id}.csv"
    with open(walletpath, 'w+') as f:
        f.write("asset,quantity,buy_price\n")
        for asset in msg:
            f.write(f"{asset[0].upper()},{asset[1]},{asset[2]}\n")

    with open(walletpath, 'r') as f:
        context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text="<b>Please check the syntax of your wallet:</b>\n"+f.read(),
            parse_mode=telegram.ParseMode.HTML
        )
    return MENU