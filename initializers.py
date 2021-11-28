from binance import Client
from telegram.ext import Updater

def binance_client(api_keys_filepath):
    
    with open(api_keys_filepath) as f:
        tokens = f.readlines()

    api_key = tokens[1].strip("\n")
    api_secret = tokens[2].strip("\n")

    try:
        return Client(api_key, api_secret)
    except:
        return 0


def telegram_bot(api_keys_filepath):
    with open(api_keys_filepath) as f:
        tokens = f.readlines()

    bot_token = tokens[0].strip("\n")
    try:
        updater = Updater(token=bot_token, use_context=True)
        return updater
    except:
        return 0