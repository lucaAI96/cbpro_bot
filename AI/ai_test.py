from cbpro_bot.DataProcessing.make_data_set import insert_mean
import re


"""
Class that tests AI strategies on historic data (pandas df).

Args:
    ai (AI): The AI algorithm to test.
    df (pandas DataFrame): Historic data containing: ["time", "low", "high", "open", "close", "volume"]
"""
class AITest():

    def __init__(self, ai, df):
        self.ai = ai
        self.df = df
        self.buying_fee = ai.buying_fee
        self.selling_fee = ai.selling_fee

    def run_test(self):
        print(f"Running test for {str(self.ai)}.")
        if re.match(r"^mean_reversion_[0-9]*_[0-9]*$", str(self.ai)):
            print("\n")
            return self.test_mean_reversion()
        else:
            print("Error: unsupported AI method.")

    def test_mean_reversion(self):
        def add_means():
            insert_mean(self.df, self.ai.fast_mean)
            insert_mean(self.df, self.ai.slow_mean)

        def delete_means():
            for col in self.df.columns:
                if re.match(r".*mean", col):
                    del self.df[col]

        assert re.match(r"^mean_reversion_[0-9]*_[0-9]*$", str(self.ai))
        delete_means()
        add_means()
        spendings = 0
        returns = 0
        last_trade = "sell"  # always start with buy
        last_price = 0  # to allow removal if last trade is also a buy
        for i in range(1, len(self.df)):
            res = self.ai.predict(self.df[i - 1:i + 1])
            if last_trade is "sell" and res is "buy":
                price = self.df["close"].iloc[i]
                print(f"buying at {price}.")
                spendings += price * (1 + self.buying_fee)
                last_price = price * (1 + self.buying_fee)
                last_trade = "buy"
            if last_trade is "buy" and res is "sell":
                price = self.df["close"].iloc[i]
                print(f"selling at {price}.")
                returns += price * (1 - self.selling_fee)
                last_price = price * (1 - self.selling_fee)
                last_trade = "sell"
        if last_trade is "buy":  # always end with sell
            print("Undo last buy.")
            spendings -= last_price
        gains = (returns / spendings) - 1.0
        print("\nResults:")
        print(f"spendings: \t{spendings}")
        print(f"returns: \t{returns}")
        print(f"gains: \t\t{gains}")

        report = TestReport(str(self.ai), spendings, returns, gains)
        return report


"""
Report for tests:

Args:
    method (str): AI method
    spendings (float): total spendings during test in base currency
    returns (float): total returns during test in base currency
    gains (float): gains during test in percent
"""
class TestReport():

    def build_report(self):
        self.report["method"] = self.method
        self.report["spendings"] = self.spendings
        self.report["returns"] = self.returns
        self.report["gains"] = self.gains

    def __init__(self, method, spendings, returns, gains):
        self.report = dict()
        self.method = method
        self.spendings = spendings
        self.returns = returns
        self.gains = gains
        self.build_report()

    def print(self):
        for key in self.report.keys():
            print(f"{key:<12}: {self.report[key]}")