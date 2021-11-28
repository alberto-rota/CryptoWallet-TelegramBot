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
current_asset=None
MENU=0
ASK_ASSET = 1
ASK_ATYPICAL_ASSET = 1.5
ASK_TIMELINE = 2
ASK_TO_SET_WALLET = 3
ASK_WALLET_HOW = 4
ASK_NOTIFICATIONS_WHICH = 5
LAST = 6


def assets(update, context):
    user_id = update.message.from_user['id']
    print(">> "+datetime.datetime.now().strftime(f"[%d/%m/%Y-%H:%M:%S]-{user_id}: ")+
        " ASSETS request ",end='')
    keyboard_assets = [
        ['ETH','BTC','SOL','DOT'], 
        ['BNB','ADA','LTC','XRP'],
        ['▶️Others','🏡Home']
    ]

    update.message.reply_text(
        "Select an asset:  ",
        reply_markup=ReplyKeyboardMarkup(
            keyboard_assets, 
            one_time_keyboard=True,
            resize_keyboard=True,
            input_field_placeholder='Type it here if not in the list'
        ),
    )
    return ASK_ASSET

def timelines(update, context):
    client=context.dispatcher.user_data['client']
    if update['message']['text']=='Others':
        print("--> Others: ",end='')
        return ASK_ATYPICAL_ASSET
    
    print("--> "+update.message.text)

    if update.message.text not in ['1hour','1day','1week','1month','1year']:
        global current_asset
        current_asset = update['message']['text']
        try:
            #############################################################################
            figpath,cptn = create.chart(client, update.message.text,'4hour')
            #############################################################################
        except:
            user_id = update.message.from_user['id']
            print(">> "+datetime.datetime.now().strftime(f"[%d/%m/%Y-%H:%M:%S]-{user_id}: ")+
                " Invalid ASSET request ")
            context.bot.send_message(
                chat_id=update.effective_chat.id, 
                text="Invalid request",
            )   
            return MENU
    else:
        try:
            #############################################################################
            figpath,cptn = create.chart(client, current_asset,update.message.text)
            #############################################################################
        except:
            user_id = update.message.from_user['id']
            print(">> "+datetime.datetime.now().strftime(f"[%d/%m/%Y-%H:%M:%S]-{user_id}: ")+
                " Invalid ASSET request ")
            context.bot.send_message(
                chat_id=update.effective_chat.id, 
                text="Invalid request",
            )   
            return MENU
    

    context.saved_asset=update.message.text
    user_id = update.message.from_user['id']
    print(">> "+datetime.datetime.now().strftime(f"[%d/%m/%Y-%H:%M:%S]-{user_id}: ")+
        " TIMELINES requested ",end="")

    context.bot.send_photo(
        chat_id=update.effective_chat.id, 
        photo=open(figpath,'rb'),
        caption=cptn,
        parse_mode=telegram.ParseMode.HTML,
        )

    keyboard_timelines = [
        ['1hour','1day','1week','1month','1year'],
        ['🔙Back to Assets','🏡Home']
        ]
    print()
    update.message.reply_text(
        "Select a timeline:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard_timelines, 
            one_time_keyboard=True,
            resize_keyboard=True,
            input_field_placeholder='Type it here if not in the list'
        ),
    )
    return ASK_TIMELINE

def others(update, context):
    user_id = update.message.from_user['id']
    print(">> "+datetime.datetime.now().strftime(f"[%d/%m/%Y-%H:%M:%S]-{user_id}: ")+
    " OTHERS requested ")
    context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text="Write the name of the asset <i>[Example: ADA]</i>\nClick ➡️/home to go back",
        parse_mode=telegram.ParseMode.HTML,
    )
    return ASK_ATYPICAL_ASSET

def exit_conv(update, context):
    client=context.dispatcher.user_data['client']
    #############################################################################
    figpath,cptn = create.chart(client, current_asset, update['message']['text'])
    #############################################################################
    context.bot.send_photo(
        chat_id=update.effective_chat.id, 
        photo=open(figpath,'rb'),
        caption=cptn,
        parse_mode=telegram.ParseMode.HTML,
    )
    
    exit_button = [['🔙Back to Assets','🕜Different Timeline'],['🏡Home']]
    update.message.reply_text(
        "Exit",
        reply_markup=ReplyKeyboardMarkup(
            exit_button, 
            one_time_keyboard=True,
            resize_keyboard=True,
        ),
    )
    
    print(">> "+datetime.datetime.now().strftime("[%d/%m/%Y-%H:%M:%S]")+
        " Conversation tarminated naturally")
    return LAST