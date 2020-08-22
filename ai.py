import abc


"""
Abstract base class for AI.
"""
class AI(abc.ABC):
    def __init__(self, model):
        self.model = model

    @abc.abstractmethod
    def predict(self, data):
        pass


"""
Stupid AI for debugging.
"""
class StupidAI():
    def __init__(self, buy_thr, sell_thr):
        self.buy_thr = buy_thr
        self.sell_thr = sell_thr

    def check_buy(self, delta):
        if delta >= self.buy_thr:
            return True
        else:
            return False

    def check_sell(self, delta):
        if delta <= self.sell_thr:
            return True
        else:
            return False