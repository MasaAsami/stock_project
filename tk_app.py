# -*- coding: utf-8 -*-
#app用
import numpy as np
import tkinter as tk
import tkinter.ttk as ttk
from matplotlib.backends.backend_tkagg  import FigureCanvasTkAgg
import util.price_geter as pget
from functools import partial

# チャートつくるため
import matplotlib.pyplot as plt
plt.style.use('ggplot')
import mpl_finance as mpf
import matplotlib.dates as mdates
from matplotlib.dates import date2num

class Application(tk.Frame):
  def __init__(self,master):
    super().__init__(master)
    self.pack()
    self.df = None

    master.geometry("800x900")
    master.title("Stock_checker")
    #エントリー
    self.fig, self.axes = plt.subplots(nrows=2, ncols=1, figsize=(12, 7), sharex=True,
                          gridspec_kw={'height_ratios': [3, 1]})
    self.canvas = FigureCanvasTkAgg(self.fig, master=master)
    self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
    self.canvas.draw()
    # ラベル
    self.lbl = tk.Label(text='銘柄番号 or 銘柄番号/YYYY')
    self.lbl.place(x=30, y=45)
    # テキストボックス
    self.box0 = tk.Entry(width=20)
    self.box0.place(x=200, y=45)
    self.box0.insert(tk.END,"4592") # 処置地
    
    # 教師データを登録
    self.lbl_ = tk.Label(text='教師データ = 1 ?')
    self.lbl_.place(x=500, y=45)
    self.val_radio = tk.StringVar()
    self.val_radio.set("yes")
    self.yesRadio = tk.Radiobutton(text = "yes",value="1",variable=self.val_radio)
    self.yesRadio.place(x=650, y=45)
    self.noRadio = tk.Radiobutton(text = "no",value="0",variable=self.val_radio)
    self.noRadio.place(x=700, y=45)

    #グラフ作成ボタン    
    self.button = tk.Button(master, text=u'グラフ作成', width=50)    
    self.button.bind("<Button-1>",self.button_clicked)
    self.button.pack(expand=1)
    
    self.table_button = tk.Button(master=master, text="データを見る",command = self.table_open ,width=50)
    self.table_button.pack(expand=1)
    
    self.save_button = tk.Button(master=master, text="csvで保存" ,width=50)
    self.save_button.pack(expand=1)
    
    self.quit_button = tk.Button(master=master, text="終了", command=self._quit, width=10)
    self.quit_button.pack(anchor=tk.E,expand=1)
      
  def plot_price(self, stock_num):
      self.flag, self.df = pget.naive_shite_or_not(stock_num)
      #画像作成
      df = self.df.copy()
      df.index = date2num(df.index)
      data = df.reset_index().values
      #fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(12, 7), sharex=True,
      #                      gridspec_kw={'height_ratios': [3, 1]})
      
      mpf.candlestick_ohlc(self.axes[0], data, width=2, alpha=0.5, colorup='r', colordown='b')
      self.axes[0].plot(df.index, df['close'].rolling(4).mean(),linewidth = 1.0)
      self.axes[0].plot(df.index, df['close'].rolling(13).mean(),linewidth = 1.0)
      self.axes[0].plot(df.index, df['close'].rolling(26).mean(),linewidth = 1.0)
      self.axes[1].bar(df.index, df['volume'], width=4, color='navy')
      self.axes[0].grid()
      self.axes[1].grid()
      locator = mdates.AutoDateLocator()
      self.axes[0].xaxis.set_major_locator(locator)
      self.axes[0].xaxis.set_major_formatter(mdates.AutoDateFormatter(locator))
    
      #if start_num != end_num:
      #  self.axes[0].axvspan(self.df.index[start_num], self.df.index[end_num], alpha=0.5, color='red')
      #appに表示
      self.canvas.draw()
        
  # button1クリック時の処理
  def button_clicked(self,event):
      self.axes[0].clear()  # figをクリア
      self.axes[1].clear() # figをクリア
      stock_num = self.box0.get() # ボタンの内容を反映
      #グラフ描画
      self.plot_price(stock_num)
      
  def table_open(self):
    #ウィンドウ立ち上げ
    win2 = tk.Toplevel(master = self.master)
    win2.geometry("900x300")
    win2.title(f"{self.box0.get()}銘柄")
    #表を作る
    tree = ttk.Treeview(win2)
    
    #taking all the columns heading in a variable"df_col".
    df = self.df.reset_index()
    df_col = df.columns.values

    #all the column name are generated dynamically.
    tree["columns"]=(df_col)
    counter = len(df)
    #generating for loop to create columns and give heading to them through df_col var.
    
    for x in range(len(df_col)):
      tree.column(x, width=100 )
      tree.heading(x, text=df_col[x])
    #generating for loop to print values of dataframe in treeview column. 
    for i in range(counter):
      tree.insert('', 0, values=[df.loc[i,[df_col_]].values[0] for df_col_ in df_col])
        
    tree.pack(fill=tk.BOTH, side=tk.LEFT, expand=1)
    win2.mainloop()
  
  def _quit(self):
    win = tk.Tk() # 一回上書き
    win.quit()     # stops mainloop
    win.destroy()  # this is necessary on Windows to prevent
                      # Fatal Python Error: PyEval_RestoreThread: NULL tstate

def main():
  win = tk.Tk()
  app = Application(master=win)
  app.mainloop()


if __name__ == "__main__":
    main()