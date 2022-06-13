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

from telegram.ext import (Updater, 
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    CallbackContext,    
    Filters
)

import datetime
import os

import initializers as init
import commands_wallet, commands_misc, commands_assets, commands_notifications

MENU=0
ASK_ASSET = 1
ASK_ATYPICAL_ASSET = 1.5
ASK_TIMELINE = 2
ASK_TO_SET_WALLET = 3
ASK_WALLET_HOW = 4
ASK_NOTIFICATIONS_WHICH = 5
LAST = 6

def main():

    # Loading the telegram bot updater and the binance client from the APIs
    print(">> "+datetime.datetime.now().strftime("[%d/%m/%Y-%H:%M:%S]-BOT: ")+
        " Loading Telegram bot: ",end="")
    updater = init.telegram_bot(api_keys_filepath="data/api_keys.txt")
    dispatcher = updater.dispatcher
    print("SUCCESS") if updater!=0 else print("FAIL")
    print(">> "+datetime.datetime.now().strftime("[%d/%m/%Y-%H:%M:%S]-BOT: ")+
        " Loading Binance Client: ",end="")
    client = init.binance_client(api_keys_filepath="data/api_keys.txt")
    dispatcher.user_data['client'] = client
    print("SUCCESS") if client!=0 else print("FAIL")
    
    # Conversation handlerµ
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('home', commands_misc.home)],
        states={
            MENU: 
                [
                MessageHandler(Filters.regex('^(💵My Wallet💵)$'), commands_wallet.askwallethow),
                MessageHandler(Filters.regex('^(💹Check Asset💹)$'), commands_assets.assets),
                MessageHandler(Filters.regex('^(💰Set Wallet)$'), commands_wallet.requestwallet),
                MessageHandler(Filters.regex('^(🚑Check Status)$'), commands_misc.status),
                MessageHandler(Filters.regex('^(🔔Notifications)$'), commands_notifications.notifications),
                MessageHandler(Filters.regex('^(📢Report an Issue)$'), commands_misc.link_to_issues),
                MessageHandler(Filters.regex('^(🚁Help)$'), commands_misc.help),
                ],
            ASK_NOTIFICATIONS_WHICH:
                [
                MessageHandler(Filters.regex('^(🔔A daily wallet report)$'), commands_notifications.toggle_walletreport1),
                MessageHandler(Filters.regex('^(🔔🔔Two daily wallet reports)$'), commands_notifications.toggle_walletreport2),
                MessageHandler(Filters.regex('^(📈When my assets increase/decrease rapidely)$'), commands_notifications.toggle_rapidincrease),
                MessageHandler(Filters.regex('^(🏡Home)$'),commands_misc.home),
                ],
            ASK_WALLET_HOW:
                [
                MessageHandler(Filters.regex('^(📈1 Hour Graphs)$'), commands_wallet.showwalletgraphs),
                MessageHandler(Filters.regex('^(📈4 Hours Graphs)$'), commands_wallet.showwalletgraphs),
                MessageHandler(Filters.regex('^(📈Daily Graphs)$'), commands_wallet.showwalletgraphs),
                MessageHandler(Filters.regex('^(📈Weekly Graphs)$'), commands_wallet.showwalletgraphs),
                MessageHandler(Filters.regex('^(📈Monthly Graphs)$'), commands_wallet.showwalletgraphs),
                MessageHandler(Filters.regex('^(📈Yearly Graphs)$'), commands_wallet.showwalletgraphs),
                MessageHandler(Filters.regex('^(💵Show Report)$'), commands_wallet.showwalletreport),
                MessageHandler(Filters.regex('^(🏡Home)$'), commands_misc.home),
                ],
            ASK_TO_SET_WALLET:
                [
                MessageHandler(Filters.text & ~Filters.command, commands_wallet.setwallet),
                ],
            ASK_ASSET: 
                [
                MessageHandler(Filters.regex('^(ETH|BTC|SOL|DOT)$'), commands_assets.timelines),
                MessageHandler(Filters.regex('^(BNB|ADA|LTC|XRP)$'), commands_assets.timelines),
                MessageHandler(Filters.regex('^(BNB|ADA|LTC|XRP)$'), commands_assets.timelines),
                MessageHandler(Filters.regex('^(▶️Others)$'), commands_assets.others),
                MessageHandler(Filters.regex('^(🏡Home)$'), commands_misc.home),
                MessageHandler(Filters.text & ~Filters.command, commands_assets.timelines),
                ],
            ASK_ATYPICAL_ASSET:
                [
                MessageHandler(Filters.text & ~Filters.command, commands_assets.timelines),
                MessageHandler(Filters.regex('^(🔙Back to Assets)$'), commands_assets.assets),
                MessageHandler(Filters.regex('^(🏡Home)$'), commands_misc.home),
                ],
            ASK_TIMELINE:
                [
                MessageHandler(Filters.regex('^(1hour|1day|1week|1month|1year)$'), commands_assets.timelines),
                MessageHandler(Filters.regex('^(🔙Back to Assets)$'), commands_assets.assets),
                MessageHandler(Filters.regex('^(🏡Home)$'), commands_misc.home),
                ],
            LAST:
                [
                MessageHandler(Filters.regex('^(🔙Back to Assets)$'), commands_assets.assets),
                MessageHandler(Filters.regex('^(🕜Different Timeline)$'), commands_assets.timelines),
                MessageHandler(Filters.regex('^(🏡Home)$'), commands_misc.home),
                ],
        }, 
        fallbacks=[CommandHandler('home', commands_misc.home)],
    )
    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(CommandHandler('report', commands_misc.report))
    dispatcher.add_handler(CommandHandler('helpme', commands_misc.help))
    # Task performed continuously (notifications,checks,...)
    jobqueue = updater.job_queue
    jobqueue.run_repeating(
        callback=commands_notifications.check_todo,
        interval=60,
    )

    print(">> "+datetime.datetime.now().strftime("[%d/%m/%Y-%H:%M:%S]-BOT: ")+
        " Callbacks initialized. Polling started")
    if not os.path.isdir("savedfigs"): os.makedirs("savedfigs")
    updater.start_polling()
    updater.idle()
    return

if __name__ == '__main__':
    main()