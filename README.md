# CryptoWalletBot

A Telegram Bot with a wallet functionality for crypto-assets. It keeps track of your assets and displays charts and reports on demand. Moreover, the user can toggle volatility notifications, alerting him when the market price of his asset change rapidely. Financial data is queried through the *Binance API*

## Requirements
This bot is intended to be used by **only one user**: it therefore requires a host platform to run (the author is hosting his personal bot on a RaspberryPI) and the API keys for a Telegram Bot and a Binance account. [Here](https://www.binance.com/en/support/faq/360002502072) is the guide for obtaining the API keys from binance, and [here](https://core.telegram.org/bots#6-botfather) is how to create a new Telegram bot and how to obtain its API token,

The bot cannot therefore handle too many requests at a time withoud noticeble delays, and it is as a matter of facts thought to be used from a single user or, at max, from a small group of people, always minding that multiple contemporary requests may easily result in unwanted/unexpected outputs.

The code has been tested on *Python 3.9.5*. Here is the list of the required dependencies, installable with:
```
pip install python-telegram-bot 
pip install python-binance 
pip install mplfinance
pip install numpy
pip install pandas 
```
***Note:** If you are hosting this program on a RaspberryPI , make sure that you install Python 3, as you may get automatically installed Python 2.7.x*


## How to startup the bot 
Once the dependencies has been installed and the 3 API keys are available, the only thing to do is to make the keys available to the code, so that the connections with Binance and Telegram are estabilished correctly. To do this, format the file `data/api_keys.txt` as follows (debending on the status of this Github repository, **you may need to create *api_keys.txt* **:
```
telegram_bot_token
binance_api_public_key
binance_api_private_key
```
Now you are all set! Just run the `main.py` file with Python

If the Bot is launched correctly, these three lines should be visible:
```
>> [Current Date and Time]-BOT:  Loading Telegram bot: SUCCESS
>> [Current Date and Time]-BOT:  Loading Binance Client: SUCCESS
>> [Current Date and Time]-BOT:  Callbacks initialized. Polling started
```

## Usage
Once the  bot is up and running, the main menu will always be available at the `/home` commmand:

![Home Menu](https://github.com/alberto-rota/CryptoWallet-TelegramBot/blob/main/menu_README.png)

Here is an overview  of the main functions of the bot:
- 💰Set Wallet: From here the user can specify his crypto assets in terms of quantity and buy-price, used from the bot to calculate prifits/losses based on the current price
- 💵My Wallet💵: Displays a wallet report and the chart of the crypto assets on different timescales
- 💹Check Asset💹: Displays the chart for any cryptocurrency on any timescale supported by binance (see the "🚁Help" command for the list of supported queries). *Note: This function does not require a wallet*
- 🔔Notifications: The user can recieve daily reports of his wallet and/or notifications when the current price for the assets in his wallet increase or decrease rapidly 

Please check the "🚁Help" button or type `/help` in the chat to get informations live from the bot. 

### Supplementary information about some of the bot tasks
- The charts sent by the bot are saved in a daily buffer in the `savedfigs` folder, which is periodically emptied every night at 00:00. The graphs are always available from the Telegram chat
- The wallet of a user is saved on a *csv* file in the *data/wallets* folder with the following filname syntax: `data/wallets/xxxxxxxxx.csv` (xxxxxxxxx is the telegram id of the user whos saves the wallet)
- The preferences for recieving notifications are saved in the file `data/notification_settings.csv`. The syntax of such file is very clear 
- Daily notifications of wallet reports are sent at 9.00 PM (1 daily notification) and 12.00 AM (2 daily notifications) every day 
- The major bot operations are logged in the console with a datetime stamp and the used ID

## Contributing
Issues can be opened from the link  provided by the bot at the "📢Report an Issue" button or from  the command `/report`.

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
Please make sure to update tests as appropriate.

## License
[GNU GPL3.0](https://choosealicense.com/licenses/gpl-3.0/)

## Copyright
©2021, Alberto Rota

mailto:alberto_rota@outlook.com
