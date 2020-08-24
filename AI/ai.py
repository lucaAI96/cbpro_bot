import abc


"""
Abstract base class for AI.
"""
class AI(abc.ABC):
    def __init__(self, buying_fee, selling_fee):
        self.buy = "buy"
        self.sell = "sell"
        self.wait = "wait"
        self.buying_fee = buying_fee
        self.selling_fee = selling_fee

    @abc.abstractmethod
    def predict(self, data):
        pass

    @abc.abstractmethod
    def __str__(self):
        pass


"""
Mean Reversion AI

Buy when fast mean drops below slow mean.
Sell when fast mean peaks above slow mean.
"""
class MeanReversion(AI):

    def __init__(self, fast_mean, slow_mean, buying_fee=0.005, selling_fee=0.005):
        super().__init__(buying_fee, selling_fee)
        self.fast_mean = fast_mean
        self.slow_mean = slow_mean

    # takes a pandas dataframe with columns for means
    def predict(self, data):
        if data[f"{self.fast_mean}_mean"].iloc[-1] <= data[f"{self.slow_mean}_mean"].iloc[-1] and \
                    data[f"{self.fast_mean}_mean"].iloc[-2] > data[f"{self.slow_mean}_mean"].iloc[-2]:
            return self.buy

        if data[f"{self.fast_mean}_mean"].iloc[-1] >= data[f"{self.slow_mean}_mean"].iloc[-1] and \
                    data[f"{self.fast_mean}_mean"].iloc[-2] < data[f"{self.slow_mean}_mean"].iloc[-2]:
            return self.sell

        else:
            return self.wait

    def __str__(self):
        return f"mean_reversion_{self.fast_mean}_{self.slow_mean}"