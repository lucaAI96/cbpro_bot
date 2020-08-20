import abc
import threading


"""
An abstract base class for a trading system.

Args:
    client (cbpro.authenticated_client): an authenticated client that can interact with the Coinbase Pro API
    crypto (arr(str)): id of crypto currency (e.g. 'BTC', 'ETH')
    cash (arr(str)): id of cash currency (e.g. 'USD', 'EUR')
    time_frame (int):
    system_id (int):
    system_label (str): descriptive name for the system
"""

class TradingSystem(abc.ABC):

    def __init__(self, client, crypto, cash, time_frame, system_id, system_label):
        self.client = client
        self.crypto = crypto
        self.cash = cash
        self.product_id = '-'.join((crypto, cash))
        self.time_frame = time_frame
        self.system_id = system_id
        self.system_label = system_label
        thread = threading.Thread(target=self.system_loop)
        thread.start()

    @abc.abstractmethod
    def place_buy_order(self):
        pass

    @abc.abstractmethod
    def place_sell_order(self):
        pass

    @abc.abstractmethod
    def system_loop(self):
        pass