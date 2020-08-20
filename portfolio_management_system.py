from client import Client
from trading_system import TradingSystem
from ai import StupidAI
import time
import sys
import pandas as pd
import numpy as np


"""
Management System that extends class TradingSystem.

Args:
    crypto (str): id of crypto currency (e.g. 'BTC', 'ETH')
    cash (str): id of cash currency (e.g. 'USD', 'EUR')
    time_frame (int):
    system_id (int):
    system_label (str): descriptive name for the system
    buy_order_size (float): amount of cash used per buy order
    sell_order_size (float): amount of crypto used per sell order
"""

class PortfolioManagementSystem(TradingSystem):

    def __init__(self, crypto, cash, time_frame, system_id, system_label, buy_order_size=10.00, sell_order_size=0.01):
        super().__init__(Client(api_config='api_config.json'), crypto, cash, time_frame, system_id, system_label)
        self.buy_order_size = buy_order_size                # funds param for buy order
        self.sell_order_size = sell_order_size              # size param for sell order
        self.accounts = self.client.get_accounts()          # see update_accounts
        self.funds = dict()                                 # see update_funds
        self.update_funds()
        self.order_book = dict()                            # see update_order_book
        self.update_order_book()
        self.AI = StupidAI(0.01, -0.01)

    def place_buy_order(self):
        print("placing buy order...")
        self.update_accounts()
        self.update_funds()

        if self.funds[self.cash] >= self.buy_order_size:   # funds >= buy_order_size
            pass
        else:                                                   # insufficient funds
            return "Insufficient funds"

        msg = self.client.place_market_order(product_id=self.product_id,
                                       side='buy',
                                       funds=str(self.buy_order_size))

        return msg

    def place_sell_order(self):
        print("placing sell order...")
        self.update_accounts()
        self.update_funds()

        if self.funds[self.crypto] >= self.sell_order_size: # funds >= sell_order_size
            pass
        else:                                                       # insufficient funds
            return "Insufficient funds"

        msg = self.client.place_market_order(product_id=self.product_id,
                                       side='sell',
                                       size=str(self.sell_order_size))

        return msg

    """
    Returns a list of all currencies currently used by the trade bot.
    """
    def get_currencies(self):
        return [self.crypto, self.cash].copy()

    """
    Update information for all accounts. Each currency is represented by one account.
    """
    def update_accounts(self):
        self.accounts = self.client.get_accounts()

    """
    Update the funds dict which stores available funds for each currency used by the trade bot.
    """
    def update_funds(self):
        self.update_accounts()
        for account in self.accounts:
            if account["currency"] in self.get_currencies():
                key = account["currency"]
                balance = float(account["balance"])
                self.funds[key] = balance

    """
    Update local order book for all currencies.
    Order book is of shape:
        {<crypto>-<cash>: {'bids': [[...]], 'asks': [[...]], 'sequence': ...}}
    Higher levels yield more information.
    """
    def update_order_book(self, level=1):
        new_order_book = self.client.get_product_order_book(self.product_id, level=level)
        if "message" not in new_order_book.keys():  # 'NotFound' message is returned if currency pair is not available
            self.order_book[self.product_id] = new_order_book

    """
    Add a currency to the trade bot so it can be traded. Also add available funds of that currency to the funds dict.
    """
    def add_currency(self, type=None, name=None):  # type = 'crypto' or 'cash'
        if type == "crypto":
            self.crypto = name
        elif type == "cash":
            self.cash = name
        else:
            print(f"Error: Cannot add currency {name} of type {type}")
            return
        self.update_funds()
        self.update_order_book()

    """
    Returns a dict with available funds for each currency used by the trade bot.
    """
    def get_funds(self):
        return self.funds.copy()

    """
    Get the last trade for a pair of crypto and cash currencies.
    Returns fields:
        trade_id, price, size, time, bid, ask, volume
    """
    def get_last_trade(self, crypto=None, cash=None):
        return self.client.get_product_ticker(product_id='-'.join((crypto, cash)))

    """
    Show what the trade bot does.
    """
    def __str__(self):
        c = self.get_currencies()
        return f"This bot trades: {c}"

    def system_loop(self):
        print("Start Trading Bot")
        # Variables for weekly close
        this_close = 0
        last_close = 0
        delta = 0
        day_count = 0
        while(True):
            # Wait a day to request more data
            time.sleep(5 * 1 * 1)
            self.update_funds()
            print(f"funds: {self.get_funds()}")
            print(self.order_book)

            last_close = this_close
            this_close = float(self.get_last_trade('BTC', 'EUR')["price"])

            if last_close != 0:
                #sys.exit()
                delta = this_close - last_close

            msg = None

            if self.AI.check_buy(delta):
                msg = self.place_buy_order()
            elif self.AI.check_sell(delta):
                msg = self.place_sell_order()

            if msg:
                print(msg)


            # TODO: replace this stuff
            '''# Request EoD data for IBM
            data_req = self.api.get_barset('IBM', timeframe='1D', limit=1).df
            # Construct dataframe to predict
            x = pd.DataFrame(
                data=[[
                    data_req['IBM']['close'][0]]], columns='Close'.split()
            )
            if(day_count == 7):
                day_count = 0
                last_weeks_close = this_weeks_close
                this_weeks_close = x['Close']
                delta = this_weeks_close - last_weeks_close

                # AI choosing to buy, sell, or hold
                if np.around(self.AI.network.predict([delta])) <= -.5:
                    self.place_sell_order()

                elif np.around(self.AI.network.predict([delta]) >= .5):
                    self.place_buy_order()'''