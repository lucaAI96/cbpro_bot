
class StupidAI:
    def __init__(self, buy_thr, sell_thr):
        self.buy_thr = buy_thr
        self.sell_thr = sell_thr

    def check_buy(self, delta):
        if delta >= self.buy_thr:
            print(f"Delta: {delta}")
            return True
        else:
            return False

    def check_sell(self, delta):
        if delta <= self.sell_thr:
            print(f"Delta: {delta}")
            return True
        else:
            return False