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
import pandas as pd
import create
import os

MENU=0
ASK_ASSET = 1
ASK_ATYPICAL_ASSET = 1.5
ASK_TIMELINE = 2
ASK_TO_SET_WALLET = 3
ASK_WALLET_HOW = 4
ASK_NOTIFICATIONS_WHICH = 5

# DISPLAYS NOTIFICATIONS OPTIONS
def notifications(update, context):
    keyboard_assets = [
        ['🔔A daily wallet report','🔔🔔Two daily wallet reports'],
        ['📈When my assets increase/decrease rapidely'],
        ['🏡Home']
    ]

    update.message.reply_text(
        "When do you wanna recieve a message? [TOGGLE] ",
        reply_markup=ReplyKeyboardMarkup(
            keyboard_assets, 
            one_time_keyboard=True,
            resize_keyboard=True,
        ),
    )
    return ASK_NOTIFICATIONS_WHICH

def toggle_walletreport1(update,context):
    user_id = update.message.from_user['id']
    print(">> "+datetime.datetime.now().strftime(f"[%d/%m/%Y-%H:%M:%S]-{user_id}: ")+
        " Toggled Daily Wallet Notifications [once a day]")
    s = f"data/notify_settings.csv"
    s = pd.read_csv(s)
    user_id = update.message.from_user['id']
    # chat_id = update.message.chat_id

    settings = f"data/notify_settings.csv"
    s = pd.read_csv(settings).set_index('ID')

    if user_id in s.index:
        s.loc[user_id].DailyReportOnce = not s.loc[user_id].DailyReportOnce
        if s.loc[user_id].DailyReportOnce == True and s.loc[user_id].DailyReportTwice == True:
            s.loc[user_id].DailyReportTwice = False
        s.to_csv(settings)
    else:
        with open(settings, 'a+') as f:
            f.write(f"{user_id},True,False,False\n")
            f.close()

    s = pd.read_csv(settings).set_index('ID')
    context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text=f"<b>Please check that the settings are correct:</b>\n{ s.loc[user_id]}",
        parse_mode=telegram.ParseMode.HTML
    )
    return ASK_NOTIFICATIONS_WHICH

def toggle_walletreport2(update,context):
    user_id = update.message.from_user['id']
    print(">> "+datetime.datetime.now().strftime(f"[%d/%m/%Y-%H:%M:%S]-{user_id}: ")+
        " Toggled Daily Wallet Notifications [twice a day]")
    s = f"data/notify_settings.csv"
    s = pd.read_csv(s)
    user_id = update.message.from_user['id']
    chat_id = update.message.chat_id

    settings = f"data/notify_settings.csv"
    s = pd.read_csv(settings).set_index('ID')

    if user_id in s.index:
        s.loc[user_id].DailyReportTwice = not s.loc[user_id].DailyReportTwice
        if s.loc[user_id].DailyReportOnce == True and s.loc[user_id].DailyReportTwice == True:
            s.loc[user_id].DailyReportOnce = False
        s.to_csv(settings)
    else:
        with open(settings, 'a+') as f:
            f.write(f"{user_id},False,True,False\n")
            f.close()

    s = pd.read_csv(settings).set_index('ID')
    context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text=f"<b>Please check that the settings are correct:</b>\n{ s.loc[user_id]}",
        parse_mode=telegram.ParseMode.HTML
    )
    return ASK_NOTIFICATIONS_WHICH

def toggle_rapidincrease(update,context):
    user_id = update.message.from_user['id']
    print(">> "+datetime.datetime.now().strftime(f"[%d/%m/%Y-%H:%M:%S]-{user_id}: ")+
        " Toggled Rapid Changes Notifications")
    s = f"data/notify_settings.csv"
    s = pd.read_csv(s)
    user_id = update.message.from_user['id']
    chat_id = update.message.chat_id

    settings = f"data/notify_settings.csv"
    s = pd.read_csv(settings).set_index('ID')

    if user_id in s.index:
        s.loc[user_id].SuddenChanges = not s.loc[user_id].SuddenChanges
        s.to_csv(settings)
    else:
        with open(settings, 'a+') as f:
            f.write(f"{user_id},False,False,True\n")
            f.close()

    s = pd.read_csv(settings).set_index('ID')
    context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text=f"<b>Please check that the settings are correct:</b>\n{ s.loc[user_id]}",
        parse_mode=telegram.ParseMode.HTML
    )
    return ASK_NOTIFICATIONS_WHICH

def check_todo(context):
    s = f"data/notify_settings.csv"
    s = pd.read_csv(s)

    sendtime1 =             {'h':21,'m':0}
    sendtime2 =             {'h':12,'m':0}
    emptybufferfoldertime = {'h':0, 'm':0}

    volatilitycheck = {'1h':5,'4h':7.5,'12h':10,'24h':12}

    # Saves current timestamp
    time =datetime.datetime.now()
    for _,user in s.iterrows():
        # Sends wallet report if time is 21.00 (t)
        if user['DailyReportOnce']==True:
            if time.hour==sendtime1['h'] and time.minute ==sendtime1['m']:
                print(">> "+datetime.datetime.now().strftime(f"[%d/%m/%Y-%H:%M:%S]-BOT: ")+
                    f" Sending evening daily report to {user['ID']}")
                context.bot.send_message(
                    chat_id=user['ID'], 
                    text=create.profits(context.dispatcher.user_data['client'],user['ID']),
                    parse_mode=telegram.ParseMode.HTML,
                )
                wallet = f"data/wallets/{user['ID']}.csv"
                df = pd.read_csv(wallet)
                for a in df['asset']:
                    #############################################################################
                    figpath,cptn = create.chart(client, a,'1day')
                    # reportmsg = create.report(client, a)
                    #############################################################################
                    context.bot.send_photo(
                        chat_id=user['ID'], 
                        photo=open(figpath,'rb'),
                        caption=cptn,
                        parse_mode=telegram.ParseMode.HTML,
                        )
        # Sends wallet report if time is 12.00
        if user['DailyReportTwice']==True:
            if time.hour==sendtime1['h'] and time.minute ==sendtime1['m']:
                print(">> "+datetime.datetime.now().strftime(f"[%d/%m/%Y-%H:%M:%S]-BOT: ")+
                    f" Sending evening daily report to {user['ID']}")
                context.bot.send_message(
                    chat_id=user['ID'], 
                    text=create.profits(context.dispatcher.user_data['client'],user['ID']),
                    parse_mode=telegram.ParseMode.HTML,
                )
                wallet = f"data/wallets/{user['ID']}.csv"
                df = pd.read_csv(wallet)
                for a in df['asset']:
                    #############################################################################
                    figpath,cptn = create.chart(client, a,'12hour')
                    # reportmsg = create.report(client, a)
                    #############################################################################
                    context.bot.send_photo(
                        chat_id=user['ID'], 
                        photo=open(figpath,'rb'),
                        caption=cptn,
                        parse_mode=telegram.ParseMode.HTML,
                        )

            if time.hour==sendtime2['h'] and time.minute ==sendtime2['m']:
                print(">> "+datetime.datetime.now().strftime(f"[%d/%m/%Y-%H:%M:%S]-BOT: ")+
                    f" Sending midday daily report to {user['ID']}")
                context.bot.send_message(
                    chat_id=user['ID'], 
                    text=create.profits(context.dispatcher.user_data['client'],user['ID']),
                    parse_mode=telegram.ParseMode.HTML,
                )
                wallet = f"data/wallets/{user['ID']}.csv"
                df = pd.read_csv(wallet)
                for a in df['asset']:
                    #############################################################################
                    figpath,cptn = create.chart(client, a,'12hour')
                    # reportmsg = create.report(client, a)
                    #############################################################################
                    context.bot.send_photo(
                        chat_id=user['ID'], 
                        photo=open(figpath,'rb'),
                        caption=cptn,
                        parse_mode=telegram.ParseMode.HTML,
                        )

        if user['SuddenChanges']==True:
            client=context.dispatcher.user_data['client']
            wallet = f"data/wallets/{user['ID']}.csv"
            try:
                df = pd.read_csv(wallet)
            except:    
                context.bot.send_message(
                    chat_id=user['ID'],
                    text=
"""It seems like you didn't register a wallet yet 😕\n 
Make sure you do it from the <u>💰Set Wallet</u> button on the main menu"""
                )
                return MENU

            for a in df['asset']:
                #############################################################################
                klines = client.get_historical_klines(
                        symbol=a+"USDT",
                        start_str='1day', 
                        interval='1h'
                )
                #############################################################################
                kl = pd.DataFrame(
                    klines, 
                    columns=['dateTime', 'open', 'high', 'low', 'close','volume',
                        'closeTime', 'quoteAssetVolume', 'numberOfTrades', 'takerBuyBaseVol', 'takerBuyQuoteVol', 'ignore']
                )
                
                for var in ["open","high","low","close"]:
                    kl[var] = pd.to_numeric(kl[var], downcast="float")

                # 24h, 12h, 4h and 1h variations
                h24var=(kl['close'].iloc[-1]-kl['open'].iloc[0])/kl['open'].iloc[0]*100
                h12var=(kl['close'].iloc[-1]-kl['open'].iloc[-13])/kl['open'].iloc[-13]*100
                h4var=(kl['close'].iloc[-1]-kl['open'].iloc[-5])/kl['open'].iloc[-5]*100
                h1var=(kl['close'].iloc[-1]-kl['open'].iloc[-2])/kl['open'].iloc[-2]*100

                # Checks 24h high variation > 10% thrice a day 
                if abs(h24var) > volatilitycheck['24h'] and time.hour%4==0 and time.minute == 0:
                    print(">> "+datetime.datetime.now().strftime("[%d/%m/%Y-%H:%M:%S]-BOT")+
                        f" Signalling a high variation for {a} in the last 24h")
                    if h24var>0:
                        h24var =  "{:.2f}".format(h24var)
                        notification_text = f"🟩{a} is <b>UP {h24var}%</b> since the last 24 hours!"
                    else:
                        h24var =  "{:.2f}".format(h24var)
                        notification_text = f"🟥{a} is <i>DOWN {h24var}%</i> since the last 24 hours!"
                    context.bot.send_message(
                        chat_id=user['ID'], 
                        text=notification_text,
                        parse_mode=telegram.ParseMode.HTML,
                    )
                    break
                # Checks 12h high variation > 7.5% 4 times a day
                if abs(h12var) > volatilitycheck['12h'] and time.hour%3==0 and time.minute == 0:
                    print(">> "+datetime.datetime.now().strftime("[%d/%m/%Y-%H:%M:%S]-BOT")+
                        f" Signalling a high variation for {a} in the last 12h")
                    if h12var>0:
                        h12var =  "{:.2f}".format(h12var)
                        notification_text = f"🟩{a} is <b>UP {h12var}%</b> since the last 12 hours!"
                    else:
                        h12var =  "{:.2f}".format(h12var)
                        notification_text = f"🟥{a} is <i>DOWN {h12var}%</i> since the last 12 hours!"
                    context.bot.send_message(
                        chat_id=user['ID'], 
                        text=notification_text,
                        parse_mode=telegram.ParseMode.HTML,
                    )
                    break
                # Checks 4h high variation > 5% 12 times a day 
                if abs(h4var) > volatilitycheck['4h'] and time.hour&2==0 and time.minute == 0:
                    print(">> "+datetime.datetime.now().strftime("[%d/%m/%Y-%H:%M:%S]-BOT")+
                        f" Signalling a high variation for {a} in the last 4h")
                    if h4var>0:
                        h4var =  "{:.2f}".format(h4var)
                        notification_text = f"🟩{a} is <b>UP {h4var}%</b> since the last 4 hours!"
                    else:
                        h4var =  "{:.2f}".format(h4var)
                        notification_text = f"🟥{a} is <i>DOWN {h4var}%</i> since the last 4 hours!"
                    context.bot.send_message(
                        chat_id=user['ID'], 
                        text=notification_text,
                        parse_mode=telegram.ParseMode.HTML,
                    )
                    break
                
                # Checks 1h high variation > 3% 4 times an hour
                if (abs(h1var) > volatilitycheck['1h']) and time.minute%15==0:
                    print(">> "+datetime.datetime.now().strftime("[%d/%m/%Y-%H:%M:%S]-BOT")+
                        f" Signalling a high variation for {a} in the last 1h")
                    if h1var>0:
                        h1var =  "{:.2f}".format(h1var)
                        notification_text = f"🟩{a} is <b>UP {h1var}%</b> since the last 1 hour!"
                    else:
                        h1var =  "{:.2f}".format(h1var)
                        notification_text = f"🟥{a} is <i>DOWN {h1var}%</i> since the last 1 hour!"
                    context.bot.send_message(
                        chat_id=user['ID'], 
                        text=notification_text,
                        parse_mode=telegram.ParseMode.HTML,
                    )
                    break

    # Deletes all saved graphs in the buffer folder at midnight every day
    if time.hour==emptybufferfoldertime['h'] and time.minute==emptybufferfoldertime['m']:
        for f in os.listdir('savedfigs'):
            os.remove(os.path.join('savedfigs', f))
        print(">> "+datetime.datetime.now().strftime("[%d/%m/%Y-%H:%M:%S]-BOT: ")+
                        f" Deleted all graphs in the buffer folder")
                    