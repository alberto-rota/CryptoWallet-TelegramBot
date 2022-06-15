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
import pandas as pd
import warnings
import mplfinance as mplf   
detail = {'1year':'1w','1month':'1d','1week':'4h','1day':'15m','4hour':'3m','1hour':'1m'}

def chart(client, asset, begin):
    # Get data from Binance
    exchange = asset.upper()+"USDT"
    #############################################################################
    klines = client.get_historical_klines(
        symbol=exchange,
        start_str=begin, 
        interval=detail[begin]
    )
    #############################################################################
    TIMESHIFT=7.2e6; # 2h ahead of UTC
    df = pd.DataFrame(
        klines, 
        columns=['dateTime', 'open', 'high', 'low', 'close','volume',
        'closeTime', 'quoteAssetVolume', 'numberOfTrades', 
        'takerBuyBaseVol', 'takerBuyQuoteVol', 'ignore']
        )
    # Removes unnecessary columns
    # df.drop(columns=['volume','closeTime', 'quoteAssetVolume', 'numberOfTrades', 
    #     'takerBuyBaseVol', 'takerBuyQuoteVol', 'ignore'],inplace=True)

    df.dateTime = pd.to_datetime(df.dateTime+TIMESHIFT, unit='ms')
    df.closeTime = pd.to_datetime(df.closeTime+TIMESHIFT, unit='ms')
    for var in df.columns[1:]: #["open","high","low","close","volume"]:
        df[var] = pd.to_numeric(df[var], downcast="float")
    df.set_index('dateTime', inplace=True)

    figpath = "savedfigs/"+exchange+"_"+df.index[-1].strftime("%d_%m_%Y__%H_%M.png")

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        mplf.plot(
            df,
            type='candle',
            style='binance',
            title="\n\n"+exchange.replace('USDT','/USDT'),
            savefig=dict(fname=figpath,dpi=100,pad_inches=0),
            )

    variation=(df['close'].iloc[-1]-df['open'].iloc[0])/df['open'].iloc[0]*100
    variation_str = "{:.2f}".format(variation)
    currentprice_str = "{:.2f}".format(df['close'].iloc[-1])
    if variation>=0:
        cptn = f"🟩{exchange.replace('USDT','').upper()}: <b> {currentprice_str}$ | +{variation_str}%</b> 🟩 [since {begin}]"
    else:
        cptn = f"🟥{exchange.replace('USDT','').upper()}: <i> {currentprice_str}$ | {variation_str}%</i> 🟥 [since {begin}]"
    cptn=cptn+"\n-------------------------------------------------------------------\n"+report(client,asset)
    return figpath, cptn

def report(client, asset):
    exchange = asset.upper()+"USDT"
    #############################################################################
    klines = client.get_historical_klines(
        symbol=exchange,
        start_str='1year', 
        interval='1w'
    )
    #############################################################################
    df1y = pd.DataFrame(
        klines,
        columns=['dateTime', 'open', 'high', 'low', 'close','volume',
            'closeTime', 'quoteAssetVolume', 'numberOfTrades', 'takerBuyBaseVol', 'takerBuyQuoteVol', 'ignore'])
    
    klines = client.get_historical_klines(
        symbol=exchange,
        start_str='1week', 
        interval='1h'
    )
    df1w = pd.DataFrame(
        klines, 
        columns=['dateTime', 'open', 'high', 'low', 'close','volume',
            'closeTime', 'quoteAssetVolume', 'numberOfTrades', 'takerBuyBaseVol', 'takerBuyQuoteVol', 'ignore'])
    
    for var in ["open","high","low","close"]:
        df1y[var] = pd.to_numeric(df1y[var], downcast="float")
        df1w[var] = pd.to_numeric(df1w[var], downcast="float")

    variations = {
        "1 year":   (df1y['close'].iloc[-1]-df1y['open'].iloc[0])/df1y['open'].iloc[0]*100,
        "1 month":  (df1y['close'].iloc[-1]-df1y['open'].iloc[-4])/df1y['open'].iloc[-4]*100,
        "1 week":   (df1y['close'].iloc[-1]-df1y['open'].iloc[-2])/df1y['open'].iloc[-2]*100,
        "24 hours": (df1w['close'].iloc[-1]-df1w['open'].iloc[-25])/df1w['open'].iloc[-25]*100,
        "1 hour":   (df1w['close'].iloc[-1]-df1w['open'].iloc[-2])/df1w['open'].iloc[-2]*100,
    }
    prices = {
        "1 year":   df1y['open'].iloc[0],
        "1 month":  df1y['open'].iloc[-4],
        "1 week":   df1y['open'].iloc[-2],
        "24 hours": df1w['open'].iloc[-25],
        "1 hour":   df1w['open'].iloc[-2],
    }
    message = ""
    for k in variations.keys():
        variation_str =  "{:.2f}".format(variations[k])
        price_str =  "{:.2f}".format(prices[k])
        if variations[k]>=0:
            message=message+f"🟩 <b>{k} | +{variation_str}% [was {price_str}$]</b> \n"
        else:
            message=message+ f"🟥 <i>{k} | {variation_str}% [was {price_str}$]</i> \n"
    
    return message

def profits(client,user_id):
    USD2EUR = client.get_avg_price(symbol="EURUSDT")
    wallet = f"data/wallets/{user_id}.csv"
    try:
        df = pd.read_csv(wallet)
    except:
        print(">> "+datetime.datetime.now().strftime(f"[%d/%m/%Y-%H:%M:%S]-{user_id}: ")+
            f" Requested a wallet that doesn't exist")
        return "You have to set up a wallet first! Do it from '💰Set Wallet'"

    message = "<b>Your Wallet:</b>\n"
    message=message+"-------------------------------------------------------------------\n"
    total_profit=0
    invested=0;
    for index, row in df.iterrows():
        #############################################################################
        current_price = client.get_avg_price(symbol=f"{row['asset'].upper()}USDT")
        #############################################################################
        variation = (float(current_price['price'])-row['buy_price'])/row['buy_price']
        profitdollar = row['buy_price']*row['quantity']*variation
        profiteur=profitdollar/float(USD2EUR['price'])
        invested = invested+row['buy_price']*row['quantity']
    
        variation_str =  "{:.2f}".format(variation*100)
        profitdollar_str =  "{:.2f}".format(profitdollar)
        profiteur_str =  "{:.2f}".format(profiteur)
        if variation>=0:
            message=message+f"🟩 {row['asset'].upper()} | <b> +{variation_str}%</b> | <b>+{profitdollar_str}</b>$  | <b>+{profiteur_str}€ </b>\n"
        else:
            message=message+f"🟥 {row['asset'].upper()} | <i> {variation_str}%</i> | <i>{profitdollar_str}</i>$  | <i>{profiteur_str}€ </i>\n"

        total_profit+=profitdollar

    
    investedeur=invested/float(USD2EUR['price'])
    invested_str =  "{:.2f}".format(invested)
    investedeur_str =  "{:.2f}".format(investedeur)
    current=invested+total_profit
    current_str = "{:.2f}".format(current)
    currenteur=current/float(USD2EUR['price'])
    currenteur_str = "{:.2f}".format(currenteur)
    message=message+"-------------------------------------------------------------------\n"
    message=message+f"Invested Capital: <i>{invested_str}$ </i>| <i>{investedeur_str}€ </i>\n"
    message=message+"-------------------------------------------------------------------\n"
    message=message+f"Current Capital: <b>{current_str}$ </b>| <b>{currenteur_str}€ </b>\n"
    message=message+"-------------------------------------------------------------------\n"
    # message=message+"------------------------------------\n"

    totalprofituer=total_profit/float(USD2EUR['price'])
    variation = (currenteur-investedeur)/investedeur
    
    variation_str = "{:.2f}".format(variation*100)
    totalprofit_str =  "{:.2f}".format(total_profit)
    totalprofiteur_str =  "{:.2f}".format(totalprofituer)
    if total_profit>=0:
        message=message+f"🟩 <b>Total</b>: <b>+{totalprofit_str}$</b> | <b>{variation_str}%</b> | <b>+{totalprofiteur_str}€</b>\n"
    else:        
        message=message+f"🟥 <b>Total</b>: <i>{totalprofit_str}$</i> | <i>{variation_str}%</i> | <i>{totalprofiteur_str}€</i>\n"
    return message