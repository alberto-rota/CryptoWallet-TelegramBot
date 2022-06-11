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

MENU=0
ASK_ASSET = 1
ASK_ATYPICAL_ASSET = 1.5
ASK_TIMELINE = 2
ASK_TO_SET_WALLET = 3
ASK_WALLET_HOW = 4
ASK_NOTIFICATIONS_WHICH = 5

def home(update, context):
    user_id = update.message.from_user['id']
    print(">> "+datetime.datetime.now().strftime(f"[%d/%m/%Y-%H:%M:%S]-{user_id}: ")+
        " MENU request ")
    menu_options = [
        ['💵My Wallet💵'],
        ['💹Check Asset💹'], 
        ['💰Set Wallet','🔔Notifications'],
        ['📢Report an Issue','🚑Check Status','🚁Help'],
    ]

    update.message.reply_text(
        "Select from the menu:  ",
        reply_markup=ReplyKeyboardMarkup(
            menu_options, 
            one_time_keyboard=True,
            resize_keyboard=True,
        ),
    )
    return MENU

# CHECKS BOT STATUS
def status(update, context):
    user_id = update.message.from_user['id']
    print(">> "+datetime.datetime.now().strftime(f"[%d/%m/%Y-%H:%M:%S]-{user_id}: ")+
        " STATUS request ")

    context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text="The Bot is Active!"
    )

# PRINTS HELP MESSAGE
def help(update, context):
    user_id = update.message.from_user['id']
    print(">> "+datetime.datetime.now().strftime(f"[%d/%m/%Y-%H:%M:%S]-{user_id}: ")+
        " HELP requested ")
    context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text=
"""
To show the main menu, type /home or click it from here

You can set your wallet from <u>💰Set Wallet</u>, with the followwing syntax:
<b>asset quantity buy_price</b>, as in the example:<i>
eth 0.128432 3294.52
btc 0.0045654433 64424.20
dot 5.87874 45.34
bnb 0.12342 495.65</i>

After that, you can see your profits and charts from <u>💵My Wallet💵</u> and you can
recieve volatiliy notifications as well as daily reports. Check out the <u>🔔Notifications</u> function.

If you don't want to set up your wallet, at <u>💹Check Asset💹</u> you can still plot the chart of any cryptocurrency with any of the
timescales supported by the <i>Binance API</i>, on which this bot depends on. The most useful timescales are
provided to you as buttons. 

For any issue, use /report and you'll be redirected to the official Github repository of this project
""",
        parse_mode=telegram.ParseMode.HTML
    )

# PROVIDES THE LINK TO THE ISSUE PANEL ON THE GITHUB PAGE
def link_to_issues(update,context):
    user_id = update.message.from_user['id']
    print(">> "+datetime.datetime.now().strftime(f"[%d/%m/%Y-%H:%M:%S]-{user_id}: ")+
        " REPORT ISSUE request ")
    context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text=
"""If you encounter a bug, problem or if you wanna suggest an improvement,
please report an issue on the official GitHub page of the project following
this link: \nhttps://github.com/alberto-rota/CryptoWallet-TelegramBot/issues
""",
        parse_mode=telegram.ParseMode.HTML
    )

# PROVIDES THE LINK TO THE ISSUE PANEL ON THE GITHUB PAGE [direct command, non-button]
def report(update,context):
    user_id = update.message.from_user['id']
    print(">> "+datetime.datetime.now().strftime(f"[%d/%m/%Y-%H:%M:%S]-{user_id}: ")+
        " REPORT ISSUE request ")
    context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text=
"""If you encounter a bug, problem or if you wanna suggest an improvement,
please report an issue on the official GitHub page of the project following
this link: \nhttps://github.com/alberto-rota/CryptoWallet-Tracket-TelegramBot/issues
""",
        parse_mode=telegram.ParseMode.HTML
    )
