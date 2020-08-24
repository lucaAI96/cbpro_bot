import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import time
import re
import cbpro

# Time slices for granularity param (sec)
min_1 = 60
min_5 = 300
min_15 = 900
hr_1 = 3600
hr_6 = 21600
hr_24 = 86400

# Time labels
time_labels = {hr_24: "day",
               hr_6: "6hr",
               hr_1: "1hr",
               min_15: "15min",
               min_5: "5min",
               min_1: "1min"}

# Create Public Client
public_client = cbpro.PublicClient()

# convert timestamps
def unix_to_utc_time(timestamp):
    return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

# create pandas dataframe from historic coinbase data
def data_to_df(data):
    # columns returned for historic rates
    cols = ["time", "low", "high", "open", "close", "volume"]
    df = pd.DataFrame(data=data, columns=cols)
    df = df.iloc[::-1]
    df["utc_time"] = df["time"].apply(unix_to_utc_time)
    df = df.set_index("utc_time")
    return df

# plot close prices (with high and low)
def plot_data(df, time_unit="Days", price_unit="EUR", n_ticks=15, hilo=True):
    plt.figure(figsize=(20, 15))
    plt.plot(df.index, df["close"], "k.-", label="close")
    if hilo:
        plt.plot(df.index, df["low"], "r-", label="low")
        plt.plot(df.index, df["high"], "g-", label="high")
        plt.fill_between(df.index, df["low"], df["close"], color="r")
        plt.fill_between(df.index, df["high"], df["close"], color="g")
    plt.xlabel(f"time [{time_unit}]")
    if n_ticks != 0 and n_ticks != 1:
        tick_spacing = len(df) // (n_ticks-1)
        plt.xticks([i for i in range(len(df)) if i % tick_spacing == 0],
                   [i for i in range(len(df)) if i % tick_spacing == 0])
    else:
        plt.xticks([])
    plt.ylabel(f"price [{price_unit}]")
    plt.legend(fontsize="x-large")

# create a dataset for a pair of crypto and base currency
import time

def build_data_set(crypto='BTC', cash='EUR', granularity=hr_24, interval_size=3000):
    max_request_length = 300
    product_id = '-'.join((crypto, cash))
    n_requests = interval_size // max_request_length
    if n_requests % interval_size == 0:
        n_requests -= 1
    data = public_client.get_product_historic_rates(product_id, granularity=granularity)
    last_ts = data[-1][0]
    end = last_ts - granularity
    start = end - granularity * max_request_length
    end = unix_to_utc_time(end)
    start = unix_to_utc_time(start)
    for n in range(n_requests):
        #print(end)
        time.sleep(1)   #requsets/s are limited
        new_data = public_client.get_product_historic_rates(product_id,
                                                            granularity=granularity,
                                                            start=start,
                                                            end=end)
        try:
            data.extend(new_data)
            if data[-1] == "message":
                data = data[:len(data)-1]
            last_ts = new_data[-1][0]
            end = last_ts - granularity
            start = end - granularity * max_request_length
            end = unix_to_utc_time(end)
            start = unix_to_utc_time(start)
        except:
            print(f"Could not fetch data between {start} and {end}")
            break
    try:
        df = data_to_df(data)
        print("Done.")
    except:
        print("Error: incompatible data. \nLast Entry:")
        print(data[-1])
        return
    return df

# find missing values in dataset
def check_missing_values(df, granularity, verbose=False):
    missing = list()
    for row in range(1, len(df)):
        if df[row:row+1]["time"].values - df[row-1:row]["time"].values != granularity:
            t = unix_to_utc_time(df[row:row+1]["time"].values - granularity)
            if verbose:
                print(f"missing value at {t}")
            missing.append(t)
    return missing

# create a column that keeps the mean over a period determined by interval size
def insert_mean(df, interval_size):
    col_name = f"{interval_size}_mean"
    if col_name in df.columns:
        print(f"Column '{col_name}' already exists")
    df.insert(len(df.columns), col_name, 0)
    for i in range(interval_size, len(df)):
        df[col_name].iloc[i] = df["close"].iloc[i-interval_size:i-1].mean()

def plot_means(df, time_unit="Days", price_unit="EUR", mean_1=50, mean_2=200, n_ticks=15):
    plt.figure(figsize=(20, 15))
    plt.plot(df.index, df["close"], "k.-", label="close")
    plt.plot(df.index, df[f"{mean_1}_mean"], "r-", label=f"{mean_1}_mean")
    plt.plot(df.index, df[f"{mean_2}_mean"], "g-", label=f"{mean_2}_mean")
    #plt.fill_between(df.index, df["50_day_mean"], df["close"], color="r")
    #plt.fill_between(df.index, df["200_day_mean"], df["close"], color="g")
    plt.xlabel(f"time [{time_unit}]")
    if n_ticks != 0 and n_ticks != 1:
        tick_spacing = len(df) // (n_ticks-1)
        plt.xticks([i for i in range(len(df)) if i % tick_spacing == 0],
                   [i for i in range(len(df)) if i % tick_spacing == 0])
    else:
        plt.xticks([])
    plt.ylabel(f"price [{price_unit}]")
    plt.legend(fontsize="x-large")

# delete all means columns from df
def delete_means(df):
    for col in df.columns:
        if re.match(r".*mean", col):
            del df[col]