# -*- coding: utf-8 -*-
#%%
from urllib.request import urlopen
from bs4 import BeautifulSoup
import ssl
import pandas as pd
import numpy as np
ssl._create_default_https_context = ssl._create_unverified_context

def stock_price_df(stock_num):
  """
  [input]
  stock_num: 銘柄番号 or "[銘柄番号]/yyyy"
  [return]
  Pandas DataFrame
  """
  # URLの指定
  html = urlopen(f"https://kabuoji3.com/stock/{stock_num}/")
  # テーブルを指定
  bsObj = BeautifulSoup(html,"html.parser")
  table = bsObj.find_all("tr")
  list_= [str(table_).replace("</td>\n<td>", ",").replace("<tr>\n<td>", "").replace("</td>\n</tr>", "").split(",") for table_ in table if "日付" not in str(table_)  ]
  assert len(list_) > 0 , "銘柄番号を確認してください。see https://kabuoji3.com/stock/7/"
  df = pd.DataFrame(list_, columns= ["date",'open', 'high', 'low', 'close', 'volume', 'close_adjust']).set_index("date").astype(float)
  df.index = pd.to_datetime(df.index) 
  return df

def naive_shite_or_not(stock_num, one_day_up = 15., one_day_down = 10., train_set_days = 20):
  df = stock_price_df(stock_num)
  df["one_day_diff_ratio"] = df["close"].diff(1).fillna(0)
  df["one_day_diff_ratio"] = 100*df["one_day_diff_ratio"]/df["close"]
  
  ratio_max = df["one_day_diff_ratio"].max()
  day_max = df[df.one_day_diff_ratio == ratio_max].index
  ratio_min = df["one_day_diff_ratio"].min()
  day_min = df[df.one_day_diff_ratio == ratio_min].index
  # 
  print("#"*13)
  print(f"{stock_num}銘柄はこんな感じ")
  print(f"{round(ratio_max,1)} % の１日値上がりを記録 @ {day_max[0]}")
  print(f"{round(ratio_min,1)} % の１日値下がりを記録 @ {day_min[0]}")
  df["train_set"] = 0 
  if ratio_max >= one_day_up and ratio_min <= -1*one_day_down and day_max < day_min:
    print("仕手現象あり？")
    train_index = [index for index in df.index if index <  df[df.one_day_diff_ratio == ratio_max].index]
    train_index = train_index[:train_set_days] 
    assert len(train_index) == train_set_days, "ごめんなさい。ピークの２０営業日前が観察できません。手動でお願いします"
    df.loc[train_index, ["train_set"]] = 1
    return 1, df
  else:
    print("仕手現象なし？")
    return 0, df

if __name__ == '__main__':
  #%%
  # チャートを確認
  import matplotlib.pyplot as plt
  plt.style.use('ggplot')
  #from ipywidgets import interact # インタラクティブにトレーニング期間を修正したい
  import mpl_finance as mpf
  import matplotlib.dates as mdates
  from matplotlib.dates import date2num
  
  #stock_num = input("銘柄番号を入れてね:") # トヨタ： 7203
  stock_num = 4592 # サンバイオ
  #df = stock_price_df(stock_num)
  flag, df = naive_shite_or_not(stock_num)
  #画像作成
  df_ = df.copy()
  df_.index = date2num(df_.index)
  data = df_.reset_index().values
  fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(12, 7), sharex=True,
                         gridspec_kw={'height_ratios': [3, 1]})
  

  mpf.candlestick_ohlc(axes[0], data, width=2, alpha=0.5, colorup='r', colordown='b')
  axes[0].plot(df_.index, df_['close'].rolling(4).mean(),linewidth = 1.0)
  axes[0].plot(df_.index, df_['close'].rolling(13).mean(),linewidth = 1.0)
  axes[0].plot(df_.index, df_['close'].rolling(26).mean(),linewidth = 1.0)
  axes[1].bar(df_.index, df_['volume'], width=4, color='navy')

  axes[0].grid()
  axes[1].grid()
  locator = mdates.AutoDateLocator()
  axes[0].xaxis.set_major_locator(locator)
  axes[0].xaxis.set_major_formatter(mdates.AutoDateFormatter(locator))
  
  if df_.train_set.max() > 0:
    start_index = df_.query("train_set > 0").head(1).index[0]
    end_index = df_.query("train_set > 0").tail(1).index[0]
    axes[0].axvspan(start_index, end_index, alpha=0.5, color='green')

  
#%%
  # 急騰定義
  df["one_day_diff_ratio"].hist(bins=100)



# %%
