import cbpro
import json
import time


'''
Coinbase Pro Trade Bot
by Luca Mueller
version = 0.01
'''
class TradeBot:
    '''
    Needs api_config.json with API key / secret / passphrase.
    '''
    def __init__(self):
        with open('api_config.json') as json_file:
            config = json.load(json_file)
        self.key = config["COINBASE_API_KEY"]
        self.secret = config["COINBASE_API_SECRET"]
        self.passphrase = config["COINBASE_API_PASSPHRASE"]
        self.auth_client = cbpro.AuthenticatedClient(self.key, self.secret, self.passphrase,
                                                api_url="https://api-public.sandbox.pro.coinbase.com")
        self.accounts = self.auth_client.get_accounts()
        self.currencies = {"crypto": [], "cash": []}
        self.funds = dict()
        self.order_book = dict()

    '''
    Returns a list of all currencies currently used by the trade bot.
    '''
    def get_currencies(self):
        return self.currencies["crypto"].copy() + self.currencies["cash"].copy()

    '''
    Update information for all accounts. Each currency is represented by one account.
    '''
    def update_accounts(self):
        self.accounts = self.auth_client.get_accounts()

    '''
    Update the funds dict which stores available funds for each currency used by the trade bot.
    '''
    def update_funds(self):
        for account in self.accounts:
            if account["currency"] in self.get_currencies():
                key = account["currency"]
                balance = account["balance"]
                self.funds[key] = balance

    def update_order_book(self, level=1):
        for crypto in self.currencies["crypto"]:
            for cash in self.currencies["cash"]:
                pair = '-'.join((crypto, cash))
                self.order_book[pair] = self.auth_client.get_product_order_book(pair, level=level)

    '''
    Add a currency to the trade bot so it can be traded. Also add available funds of that currency to the funds dict.
    '''
    def add_currency(self, type=None, name=None):  # type = 'crypto' or 'cash'
        if type in self.currencies.keys() and name not in self.get_currencies():
            self.currencies[type].append(name)
            self.update_accounts()
            self.update_funds()
            self.update_order_book()
        else:
            print(f"Cannot add currency {name} of type {type} to currencies.")
            if type not in self.currencies.keys():
                print(f"Currency type {type} is invalid. Use 'crypto' or 'cash'.")
            elif name in self.get_currencies():
                print(f"Currency {name} was added already.")
            else:
                print("Unknown error.")

    '''
    Returns a dict with available funds for each currency used by the trade bot.
    '''
    def get_funds(self):
        return self.funds.copy()

    '''
    Get the last trade for a pair of crypto and cash currencies.
    Returns fields:
    - trade_id
    - price
    - size
    - time
    - bid
    - ask
    - volume
    '''
    def get_last_trade(self, crypto=None, cash=None):
        return self.auth_client.get_product_ticker(product_id='-'.join((crypto, cash)))

    '''
    Show what the trade bot does.
    '''
    def __str__(self):
        c = self.get_currencies()
        return f"This bot trades: {c}"





########################################################################################################################

trade_bot = TradeBot()
trade_bot.add_currency(type="crypto", name="BTC")
trade_bot.add_currency(type="cash", name="EUR")

print(trade_bot)
print(f"funds: {trade_bot.get_funds()}")
print(trade_bot.order_book)